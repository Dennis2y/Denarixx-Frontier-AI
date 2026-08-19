import { Router, type IRouter, type RequestHandler } from "express";
import { randomUUID } from "node:crypto";
import { spawn } from "node:child_process";
import path from "node:path";
import { desc, eq } from "drizzle-orm";
import {
  ListTrainingRunsResponse,
  StartTrainingRunBody,
  StartTrainingRunResponse,
} from "@workspace/api-zod";
import {
  db,
  evaluationsTable,
  trainingMetricsTable,
  trainingRunsTable,
} from "@workspace/db";
import { getAuth } from "@clerk/express";
import { seedResearchData } from "./research";

const router: IRouter = Router();

const requireResearchRole: RequestHandler = (req, res, next) => {
  const auth = getAuth(req);
  if (!auth.isAuthenticated) {
    res.status(401).json({ error: "Sign in to start a research run." });
    return;
  }
  next();
};

function mapRun(row: typeof trainingRunsTable.$inferSelect, metrics: Array<typeof trainingMetricsTable.$inferSelect>) {
  return {
    id: row.id,
    status: row.status,
    model: row.model,
    dataset: row.dataset,
    device: row.device,
    maxSteps: row.maxSteps,
    seed: row.seed,
    resumedFromRunId: row.resumedFromRunId,
    startedAt: row.startedAt.toISOString(),
    completedAt: row.completedAt?.toISOString() ?? null,
    checkpointPath: row.checkpointPath,
    measured: row.measured,
    error: row.error,
    metrics: metrics.map((metric) => ({
      step: metric.step,
      trainingLoss: metric.trainingLoss,
      validationLoss: metric.validationLoss,
      learningRate: metric.learningRate,
      tokensProcessed: metric.tokensProcessed,
      tokensPerSecond: metric.tokensPerSecond,
    })),
  };
}

router.get("/training-runs", async (_req, res, next) => {
  try {
    await seedResearchData();
    const rows = await db.select().from(trainingRunsTable).orderBy(desc(trainingRunsTable.startedAt));
    const data = await Promise.all(
      rows.map(async (row) => mapRun(row, await db.select().from(trainingMetricsTable).where(eq(trainingMetricsTable.runId, row.id)))),
    );
    res.json(ListTrainingRunsResponse.parse(data));
  } catch (error) {
    next(error);
  }
});

router.post("/training-runs", requireResearchRole, async (req, res, next) => {
  try {
    await seedResearchData();
    const input = StartTrainingRunBody.parse(req.body ?? {});
    let resumeCheckpointPath: string | undefined;
    let resumedFromRunId: string | null = input.resumeFromRunId ?? null;
    let seed = input.seed ?? 42;
    if (resumedFromRunId) {
      const [sourceRun] = await db
        .select()
        .from(trainingRunsTable)
        .where(eq(trainingRunsTable.id, resumedFromRunId))
        .limit(1);
      if (!sourceRun || sourceRun.status !== "complete" || !sourceRun.checkpointPath) {
        res.status(409).json({ error: "Resume requires a complete run with a checkpoint." });
        return;
      }
      if ((input.maxSteps ?? 20) <= sourceRun.maxSteps) {
        res.status(400).json({ error: `Resume maxSteps must be greater than ${sourceRun.maxSteps}.` });
        return;
      }
      resumeCheckpointPath = sourceRun.checkpointPath;
      seed = sourceRun.seed;
    }
    const id = randomUUID();
    const startedAt = new Date();
    const [row] = await db
      .insert(trainingRunsTable)
      .values({
        id,
        status: "queued",
        model: "denarixx-d0-baseline",
        dataset: "denarixx-local-dev-v1",
        device: "pending",
        maxSteps: input.maxSteps ?? 20,
        seed,
        resumedFromRunId,
        startedAt,
        measured: true,
      })
      .returning();
    runTrainingProcess(id, row.maxSteps, row.seed, resumeCheckpointPath);
    res.status(202).json(
      StartTrainingRunResponse.parse({
        ...mapRun(row, []),
        startedAt: startedAt.toISOString(),
      }),
    );
  } catch (error) {
    next(error);
  }
});

function runTrainingProcess(runId: string, maxSteps: number, seed: number, resumeCheckpointPath?: string) {
  const command = process.env.PYTHON_BIN || "python3";
  const script = path.resolve(process.cwd(), "ml", "run_experiment.py");
  const checkpointDir = path.resolve(process.cwd(), "artifacts", "api-server", "data", "checkpoints");
  const args = [script, "--max-steps", String(maxSteps), "--seed", String(seed), "--checkpoint-dir", checkpointDir, "--run-id", runId];
  if (resumeCheckpointPath) args.push("--resume-checkpoint", resumeCheckpointPath);

  const child = spawn(command, args, {
    cwd: process.cwd(),
    env: { ...process.env, PYTHONPATH: path.resolve(process.cwd(), "ml") },
  });

  let output = "";
  let spawnFailed = false;

  child.on("spawn", () => {
    void db
      .update(trainingRunsTable)
      .set({
        status: "running",
        device: "pending",
        error: null,
      })
      .where(eq(trainingRunsTable.id, runId))
      .catch((error) => {
        console.error("Unable to mark training run as running", error);
      });
  });

  child.on("error", (error) => {
    spawnFailed = true;

    void db
      .update(trainingRunsTable)
      .set({
        status: "failed",
        error: `Unable to start Python training process: ${error.message}`,
        completedAt: new Date(),
      })
      .where(eq(trainingRunsTable.id, runId))
      .catch((persistError) => {
        console.error("Unable to persist training spawn failure", persistError);
      });
  });
  child.stdout.on("data", (chunk: Buffer) => {
    output += chunk.toString();
  });
  child.stderr.on("data", (chunk: Buffer) => {
    output += chunk.toString();
  });
  child.on("close", async (code) => {
    if (spawnFailed) {
      return;
    }

    try {
      const payload = JSON.parse(output.trim().split("\n").at(-1) ?? "{}") as {
        status: string;
        error?: string;
        device?: string;
        checkpointPath?: string;
        metrics?: Array<{
          step: number;
          trainingLoss: number;
          learningRate: number;
          tokensProcessedThisRun: number;
          tokensPerSecond: number;
          gradientNorm: number;
          elapsedSeconds: number;
        }>;
        finalEvaluation?: {
          average_loss: number;
          perplexity: number;
          batches_evaluated: number;
          tokens_evaluated: number;
        };
      };
      if (code !== 0 || payload.status !== "complete") {
        await db.update(trainingRunsTable).set({
          status: "failed",
          error: payload.error ?? `training process exited with ${code}`,
          completedAt: new Date(),
        }).where(eq(trainingRunsTable.id, runId));
        return;
      }
      await db.update(trainingRunsTable).set({
        status: "complete",
        device: payload.device ?? "cpu",
        completedAt: new Date(),
        checkpointPath: payload.checkpointPath ?? null,
      }).where(eq(trainingRunsTable.id, runId));
      if (payload.metrics) {
        await db.insert(trainingMetricsTable).values(payload.metrics.map((metric) => ({
          id: randomUUID(),
          runId,
          step: metric.step,
          trainingLoss: metric.trainingLoss,
          validationLoss: payload.finalEvaluation?.average_loss ?? null,
          learningRate: metric.learningRate,
          tokensProcessed: metric.tokensProcessedThisRun,
          tokensPerSecond: metric.tokensPerSecond,
          elapsedSeconds: metric.elapsedSeconds,
        })));
        const latest = payload.metrics.at(-1);
        await db.insert(evaluationsTable).values({
          id: randomUUID(),
          benchmark: "D0 validation loss",
          benchmarkVersion: "v1",
          model: "denarixx-d0-baseline",
          checkpoint: payload.checkpointPath ?? "unknown",
          score: payload.finalEvaluation?.average_loss ?? null,
          source: "Denarixx measured",
          status: "complete",
          rawResults: JSON.stringify({
            metric: "validation_loss",
            value: payload.finalEvaluation?.average_loss ?? null,
            perplexity: payload.finalEvaluation?.perplexity ?? null,
            batchesEvaluated: payload.finalEvaluation?.batches_evaluated ?? null,
            tokensEvaluated: payload.finalEvaluation?.tokens_evaluated ?? null,
            runId,
          }),
        });
      }
    } catch (error) {
      await db.update(trainingRunsTable).set({
        status: "failed",
        error: error instanceof Error ? error.message : "Unable to persist training result",
        completedAt: new Date(),
      }).where(eq(trainingRunsTable.id, runId));
    }
  });
}

export default router;