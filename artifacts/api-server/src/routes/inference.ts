import { Router, type IRouter, type RequestHandler } from "express";
import { spawn } from "node:child_process";
import path from "node:path";
import { RunInferenceBody, RunInferenceResponse } from "@workspace/api-zod";
import { getAuth } from "@clerk/express";
import { resolveServingAuthority } from "../lib/servingAuthority";

const router: IRouter = Router();

const requireResearchRole: RequestHandler = (req, res, next) => {
  const auth = getAuth(req);
  if (!auth.isAuthenticated) {
    res.status(401).json({ error: "Sign in to run D0 inference." });
    return;
  }
  next();
};

router.get("/auth-status", (req, res) => {
  const auth = getAuth(req);

  res.json({
    authenticated: auth.isAuthenticated === true,
    authStateAvailable: auth !== undefined && auth !== null,
  });
});

router.post("/inference", requireResearchRole, async (req, res, next) => {
  try {
    const input = RunInferenceBody.parse(req.body);
    const servingAuthority = await resolveServingAuthority();
    const repositoryRoot = path.resolve(process.cwd(), "../..");
    const python = path.join(repositoryRoot, ".pythonlibs", "bin", "python");
    const command = process.env.PYTHON_BIN || python;
    const script = path.join(repositoryRoot, "ml", "run_inference.py");
    const child = spawn(command, [script, "--checkpoint", servingAuthority.checkpointAbsolutePath, "--prompt", input.prompt, "--max-tokens", String(input.maxTokens ?? 24), "--temperature", String(input.temperature ?? 0.8)], {
      cwd: repositoryRoot,
      env: { ...process.env, PYTHONPATH: path.join(repositoryRoot, "ml") },
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
          checkpoint: servingAuthority.checkpointPath,
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