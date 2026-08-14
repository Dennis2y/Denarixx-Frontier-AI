import { Router, type IRouter } from "express";
import { desc } from "drizzle-orm";
import { ListEvaluationsResponse } from "@workspace/api-zod";
import { db, evaluationsTable } from "@workspace/db";
import { seedResearchData } from "./research";

const router: IRouter = Router();

router.get("/evaluations", async (_req, res, next) => {
  try {
    await seedResearchData();
    const rows = await db.select().from(evaluationsTable).orderBy(desc(evaluationsTable.evaluatedAt));
    res.json(ListEvaluationsResponse.parse(rows.map((row) => ({
      ...row,
      evaluatedAt: row.evaluatedAt.toISOString(),
    }))));
  } catch (error) {
    next(error);
  }
});

export default router;