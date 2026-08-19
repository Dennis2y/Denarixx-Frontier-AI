import { Router, type IRouter, type RequestHandler } from "express";
import { spawn } from "node:child_process";
import path from "node:path";
import { eq, desc } from "drizzle-orm";
import { RunInferenceBody, RunInferenceResponse } from "@workspace/api-zod";
import { db, trainingRunsTable } from "@workspace/db";
import { getAuth } from "@clerk/express";
import { seedResearchData } from "./research";

const router: IRouter = Router();

const requireResearchRole: RequestHandler = (req, res, next) => {
  const auth = getAuth(req);
  if (!auth.isAuthenticated) {
    res.status(401).json({ error: "Sign in to run D0 inference." });
    return;
  }
  next();
};

router.post("/inference", requireResearchRole, async (req, res, next) => {
  try {
    await seedResearchData();
    const input = RunInferenceBody.parse(req.body);
    const [run] = await db.select().from(trainingRunsTable).where(eq(trainingRunsTable.status, "complete")).orderBy(desc(trainingRunsTable.completedAt)).limit(1);
    if (!run?.checkpointPath) {
      res.status(409).json({ error: "Run a complete D0 experiment before inference." });
      return;
    }
    const python = path.join(process.cwd(), ".pythonlibs", "bin", "python");
    const command = process.env.PYTHON_BIN || python;
    const script = path.resolve(process.cwd(), "ml", "run_inference.py");
    const child = spawn(command, [script, "--checkpoint", run.checkpointPath, "--prompt", input.prompt, "--max-tokens", String(input.maxTokens ?? 24), "--temperature", String(input.temperature ?? 0.8)], {
      cwd: process.cwd(),
      env: { ...process.env, PYTHONPATH: path.resolve(process.cwd(), "ml") },
    });
    let output = "";
    child.stdout.on("data", (chunk: Buffer) => {
      output += chunk.toString();
    });
    child.stderr.on("data", (chunk: Buffer) => {
      output += chunk.toString();
    });
    child.on("close", (code) => {
      try {
        const payload = JSON.parse(output.trim().split("\n").at(-1) ?? "{}");
        if (code !== 0 || payload.status !== "complete") {
          res.status(500).json({ error: payload.error ?? "Inference process failed." });
          return;
        }
        res.json(RunInferenceResponse.parse({
          model: "denarixx-d0-baseline",
          checkpoint: run.checkpointPath,
          prompt: input.prompt,
          output: payload.output,
          measured: true,
          tokensGenerated: payload.tokensGenerated,
          latencyMs: payload.latencyMs,
          tokensPerSecond: payload.tokensPerSecond,
        }));
      } catch (error) {
        next(error);
      }
    });
  } catch (error) {
    next(error);
  }
});

export default router;