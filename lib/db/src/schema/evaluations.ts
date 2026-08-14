import { pgTable, text, real, timestamp } from "drizzle-orm/pg-core";

export const evaluationsTable = pgTable("evaluations", {
  id: text("id").primaryKey(),
  benchmark: text("benchmark").notNull(),
  benchmarkVersion: text("benchmark_version").notNull(),
  model: text("model").notNull(),
  checkpoint: text("checkpoint").notNull(),
  score: real("score"),
  source: text("source").notNull(),
  status: text("status").notNull(),
  evaluatedAt: timestamp("evaluated_at", { withTimezone: true }).notNull().defaultNow(),
  rawResults: text("raw_results").notNull(),
});

export type Evaluation = typeof evaluationsTable.$inferSelect;