import { pgTable, text, integer, real, timestamp } from "drizzle-orm/pg-core";

export const modelsTable = pgTable("models", {
  id: text("id").primaryKey(),
  name: text("name").notNull(),
  family: text("family").notNull(),
  status: text("status").notNull(),
  parameters: integer("parameters").notNull(),
  contextLength: integer("context_length").notNull(),
  architecture: text("architecture").notNull(),
  note: text("note"),
  createdAt: timestamp("created_at", { withTimezone: true }).notNull().defaultNow(),
});

export const datasetsTable = pgTable("datasets", {
  id: text("id").primaryKey(),
  name: text("name").notNull(),
  version: text("version").notNull(),
  stage: text("stage").notNull(),
  provenance: text("provenance").notNull(),
  documents: integer("documents").notNull(),
  tokens: integer("tokens").notNull(),
  license: text("license").notNull(),
  qualityScore: real("quality_score"),
  createdAt: timestamp("created_at", { withTimezone: true }).notNull().defaultNow(),
});

export const experimentsTable = pgTable("experiments", {
  id: text("id").primaryKey(),
  name: text("name").notNull(),
  hypothesis: text("hypothesis").notNull(),
  baseline: text("baseline").notNull(),
  variant: text("variant").notNull(),
  dataset: text("dataset").notNull(),
  status: text("status").notNull(),
  conclusion: text("conclusion").notNull(),
  createdAt: timestamp("created_at", { withTimezone: true }).notNull().defaultNow(),
});

export type Model = typeof modelsTable.$inferSelect;
export type Dataset = typeof datasetsTable.$inferSelect;
export type Experiment = typeof experimentsTable.$inferSelect;