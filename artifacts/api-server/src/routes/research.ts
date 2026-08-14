import { Router, type IRouter, type RequestHandler } from "express";
import { randomUUID } from "node:crypto";
import { and, desc, eq } from "drizzle-orm";
import {
  CreateExperimentBody,
  CreateExperimentResponse,
  GetResearchOverviewResponse,
  ListDatasetsResponse,
  ListExperimentsResponse,
  ListModelsResponse,
} from "@workspace/api-zod";
import {
  db,
  datasetsTable,
  evaluationsTable,
  experimentsTable,
  modelsTable,
  trainingRunsTable,
} from "@workspace/db";
import { getAuth } from "@clerk/express";

const router: IRouter = Router();
let seedPromise: Promise<void> | undefined;

async function seedResearchData() {
  if (!seedPromise) {
    seedPromise = (async () => {
      await db
        .insert(modelsTable)
        .values({
          id: "denarixx-d0-baseline",
          name: "D0 Baseline",
          family: "denarixx-d0",
          status: "experimental",
          parameters: 128000,
          contextLength: 32,
          architecture: "Causal transformer · 2 layers · 4 heads",
          note: "Tiny CPU-compatible research model. Not a frontier model.",
        })
        .onConflictDoNothing();
      await db
        .insert(datasetsTable)
        .values({
          id: "denarixx-local-dev-v1",
          name: "Denarixx Local Development Corpus",
          version: "v1",
          stage: "training-ready",
          provenance: "Authored local corpus for pipeline validation",
          documents: 6,
          tokens: 1050,
          license: "Denarixx internal / local development",
          qualityScore: 1,
        })
        .onConflictDoNothing();
      await db
        .insert(experimentsTable)
        .values({
          id: "d0-pipeline-validation",
          name: "D0 pipeline validation",
          hypothesis: "A tiny causal transformer can complete the owned training lifecycle on CPU.",
          baseline: "Untrained D0 initialization",
          variant: "D0 Baseline · 2 layers · 64 hidden",
          dataset: "Denarixx Local Development Corpus v1",
          status: "active",
          conclusion: "Pending first measured run",
        })
        .onConflictDoNothing();
    })();
  }
  await seedPromise;
}

const requireResearchRole: RequestHandler = (req, res, next) => {
  const auth = getAuth(req);
  if (!auth.isAuthenticated) {
    res.status(401).json({ error: "Sign in to modify research records." });
    return;
  }
  next();
};

router.get("/research/overview", async (_req, res, next) => {
  try {
    await seedResearchData();
    const [models, datasets, experiments, runs, evaluations] = await Promise.all([
      db.select().from(modelsTable),
      db.select().from(datasetsTable),
      db.select().from(experimentsTable),
      db.select().from(trainingRunsTable).orderBy(desc(trainingRunsTable.startedAt)).limit(1),
      db.select().from(evaluationsTable),
    ]);
    const latestRun = runs[0]
      ? {
          id: runs[0].id,
          status: runs[0].status,
          model: runs[0].model,
          dataset: runs[0].dataset,
          device: runs[0].device,
          maxSteps: runs[0].maxSteps,
          seed: runs[0].seed,
          startedAt: runs[0].startedAt.toISOString(),
          completedAt: runs[0].completedAt?.toISOString() ?? null,
          metrics: [],
          checkpointPath: runs[0].checkpointPath,
          measured: runs[0].measured,
          error: runs[0].error,
        }
      : null;
    const data = GetResearchOverviewResponse.parse({
      program: "DENARIXX D0",
      models: models.length,
      datasets: datasets.length,
      experiments: experiments.length,
      trainingRuns: await db.select().from(trainingRunsTable).then((rows) => rows.length),
      evaluations: evaluations.length,
      systemStatus: "control plane online",
      latestRun,
      milestones: [
        { id: "d0.1", label: "D0.1", status: runs.some((run) => run.status === "complete") ? "complete" : "active", description: "Train a tiny language model successfully." },
        { id: "d0.2", label: "D0.2", status: runs.some((run) => run.checkpointPath) ? "complete" : "planned", description: "Demonstrate checkpoint and resume." },
        { id: "d0.3", label: "D0.3", status: "planned", description: "Train a custom tokenizer." },
        { id: "d0.4", label: "D0.4", status: evaluations.length ? "complete" : "planned", description: "Complete independent evaluation." },
        { id: "d0.5", label: "D0.5", status: runs.some((run) => run.checkpointPath) ? "active" : "planned", description: "Serve D0 through the Denarixx inference API." },
      ],
    });
    res.json(data);
  } catch (error) {
    next(error);
  }
});

router.get("/models", async (_req, res, next) => {
  try {
    await seedResearchData();
    const rows = await db.select().from(modelsTable);
    res.json(ListModelsResponse.parse(rows));
  } catch (error) {
    next(error);
  }
});

router.get("/datasets", async (_req, res, next) => {
  try {
    await seedResearchData();
    const rows = await db.select().from(datasetsTable);
    res.json(ListDatasetsResponse.parse(rows));
  } catch (error) {
    next(error);
  }
});

router.get("/experiments", async (_req, res, next) => {
  try {
    await seedResearchData();
    const rows = await db.select().from(experimentsTable).orderBy(desc(experimentsTable.createdAt));
    res.json(ListExperimentsResponse.parse(rows.map((row) => ({ ...row, createdAt: row.createdAt.toISOString() }))));
  } catch (error) {
    next(error);
  }
});

router.post("/experiments", requireResearchRole, async (req, res, next) => {
  try {
    await seedResearchData();
    const input = CreateExperimentBody.parse(req.body);
    const [row] = await db
      .insert(experimentsTable)
      .values({
        id: randomUUID(),
        ...input,
        status: "planned",
        conclusion: "Not yet evaluated",
      })
      .returning();
    res.status(201).json(CreateExperimentResponse.parse({ ...row, createdAt: row.createdAt.toISOString() }));
  } catch (error) {
    next(error);
  }
});

export { seedResearchData };
export default router;