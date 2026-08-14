import { pgTable, text, integer, real, boolean, timestamp } from "drizzle-orm/pg-core";

export const trainingRunsTable = pgTable("training_runs", {
  id: text("id").primaryKey(),
  status: text("status").notNull(),
  model: text("model").notNull(),
  dataset: text("dataset").notNull(),
  device: text("device").notNull(),
  maxSteps: integer("max_steps").notNull(),
  seed: integer("seed").notNull(),
  resumedFromRunId: text("resumed_from_run_id"),
  startedAt: timestamp("started_at", { withTimezone: true }).notNull().defaultNow(),
  completedAt: timestamp("completed_at", { withTimezone: true }),
  checkpointPath: text("checkpoint_path"),
  measured: boolean("measured").notNull().default(true),
  error: text("error"),
});

export const trainingMetricsTable = pgTable("training_metrics", {
  id: text("id").primaryKey(),
  runId: text("run_id").notNull(),
  step: integer("step").notNull(),
  trainingLoss: real("training_loss").notNull(),
  validationLoss: real("validation_loss"),
  learningRate: real("learning_rate").notNull(),
  tokensProcessed: integer("tokens_processed").notNull(),
  tokensPerSecond: real("tokens_per_second").notNull(),
  elapsedSeconds: real("elapsed_seconds"),
  createdAt: timestamp("created_at", { withTimezone: true }).notNull().defaultNow(),
});

export type TrainingRun = typeof trainingRunsTable.$inferSelect;
export type TrainingMetric = typeof trainingMetricsTable.$inferSelect;