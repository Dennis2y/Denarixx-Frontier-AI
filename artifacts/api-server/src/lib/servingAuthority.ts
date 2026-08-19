import { createHash } from "node:crypto";
import { createReadStream } from "node:fs";
import { readFile, stat } from "node:fs/promises";
import path from "node:path";

const DEFAULT_AUTHORITY_PATH =
  "local-evidence/d0-milestones/d0.5/SERVING_AUTHORITY.json";

const ALLOWED_CHECKPOINT_ROOT = "local-checkpoints";
const ALLOWED_EVIDENCE_ROOT = "local-evidence";

interface ServingAuthorityMetadata {
  schemaVersion: number;
  stage: string;
  status: string;
  authorityType: string;
  checkpoint: string;
  checkpointSha256: string;
  promotionAuthority: string;
  promotionAuthoritySha256: string;
  promotionStage: string;
  promotionStatus: string;
  promotionReason: string;
  previousServingCheckpoint: string;
  previousServingCheckpointSha256: string;
  trainingRunsAuthoritative: boolean;
  requiresFailClosedVerification: boolean;
}

interface PromotionAuthorityMetadata {
  stage: string;
  status: string;
  formalPass: boolean;
  formalExecutionCompleted: boolean;
  post008Closed: boolean;
  authorizationConsumed: boolean;
  authorizedExecutionCount: number;
  retryPermitted: boolean;
  trainingExecutedDuringClosure: boolean;
  checkpointModifiedDuringClosure: boolean;
  formalEvidenceModifiedDuringClosure: boolean;
  aggregateResponseLossImprovementPassed: boolean;
  allFiveFamiliesRetentionPassed: boolean;
  minimumCandidateExactMatchesPassed: boolean;
  strictExactMatchImprovementPassed: boolean;
  promotedAcceptedCheckpoint: string;
  promotedAcceptedCheckpointSha256: string;
  previousAcceptedBaseline: string;
  previousAcceptedBaselineSha256: string;
  promotionReason: string;
}

export interface ServingAuthority {
  checkpointPath: string;
  checkpointAbsolutePath: string;
  checkpointSha256: string;
  acceptancePath: string;
}

function isSha256(value: unknown): value is string {
  return (
    typeof value === "string" &&
    /^[a-f0-9]{64}$/.test(value)
  );
}

function isServingAuthorityMetadata(
  value: unknown,
): value is ServingAuthorityMetadata {
  if (typeof value !== "object" || value === null) {
    return false;
  }

  const record = value as Record<string, unknown>;

  return (
    record.schemaVersion === 1 &&
    record.stage === "D0.5" &&
    record.status === "ACTIVE" &&
    record.authorityType === "FORMAL_PROMOTION" &&
    typeof record.checkpoint === "string" &&
    record.checkpoint.length > 0 &&
    isSha256(record.checkpointSha256) &&
    typeof record.promotionAuthority === "string" &&
    record.promotionAuthority.length > 0 &&
    isSha256(record.promotionAuthoritySha256) &&
    record.promotionStage === "D0-POST-008" &&
    record.promotionStatus ===
      "formal-closure-complete-candidate-promoted" &&
    record.promotionReason ===
      "passed-frozen-d0-post008-formal-adjudication" &&
    typeof record.previousServingCheckpoint === "string" &&
    record.previousServingCheckpoint.length > 0 &&
    isSha256(record.previousServingCheckpointSha256) &&
    record.trainingRunsAuthoritative === false &&
    record.requiresFailClosedVerification === true
  );
}

function isPromotionAuthorityMetadata(
  value: unknown,
): value is PromotionAuthorityMetadata {
  if (typeof value !== "object" || value === null) {
    return false;
  }

  const record = value as Record<string, unknown>;

  return (
    record.stage === "D0-POST-008" &&
    record.status ===
      "formal-closure-complete-candidate-promoted" &&
    record.formalPass === true &&
    record.formalExecutionCompleted === true &&
    record.post008Closed === true &&
    record.authorizationConsumed === true &&
    record.authorizedExecutionCount === 1 &&
    record.retryPermitted === false &&
    record.trainingExecutedDuringClosure === false &&
    record.checkpointModifiedDuringClosure === false &&
    record.formalEvidenceModifiedDuringClosure === false &&
    record.aggregateResponseLossImprovementPassed === true &&
    record.allFiveFamiliesRetentionPassed === true &&
    record.minimumCandidateExactMatchesPassed === true &&
    record.strictExactMatchImprovementPassed === true &&
    typeof record.promotedAcceptedCheckpoint === "string" &&
    record.promotedAcceptedCheckpoint.length > 0 &&
    isSha256(record.promotedAcceptedCheckpointSha256) &&
    typeof record.previousAcceptedBaseline === "string" &&
    record.previousAcceptedBaseline.length > 0 &&
    isSha256(record.previousAcceptedBaselineSha256) &&
    record.promotionReason ===
      "passed-frozen-d0-post008-formal-adjudication"
  );
}

async function sha256File(filePath: string): Promise<string> {
  return await new Promise<string>((resolve, reject) => {
    const hash = createHash("sha256");
    const stream = createReadStream(filePath);

    stream.on("error", reject);
    stream.on("data", (chunk) => {
      hash.update(chunk);
    });
    stream.on("end", () => {
      resolve(hash.digest("hex"));
    });
  });
}

function resolveConfinedPath(
  repositoryRoot: string,
  relativePath: string,
  allowedRootName: string,
  label: string,
): string {
  if (path.isAbsolute(relativePath)) {
    throw new Error(
      `Serving authority rejected: ${label} path must be repository-relative.`,
    );
  }

  const allowedRoot = path.resolve(
    repositoryRoot,
    allowedRootName,
  );

  const resolved = path.resolve(
    repositoryRoot,
    relativePath,
  );

  const relativeToAllowedRoot = path.relative(
    allowedRoot,
    resolved,
  );

  if (
    relativeToAllowedRoot === "" ||
    relativeToAllowedRoot === ".." ||
    relativeToAllowedRoot.startsWith(`..${path.sep}`) ||
    path.isAbsolute(relativeToAllowedRoot)
  ) {
    throw new Error(
      `Serving authority rejected: ${label} is outside ${allowedRootName}.`,
    );
  }

  return resolved;
}

async function readRegularFile(
  absolutePath: string,
  displayPath: string,
  label: string,
): Promise<string> {
  let fileStat;

  try {
    fileStat = await stat(absolutePath);
  } catch {
    throw new Error(
      `Serving authority unavailable: ${label} ${displayPath} does not exist.`,
    );
  }

  if (!fileStat.isFile()) {
    throw new Error(
      `Serving authority rejected: ${label} ${displayPath} is not a regular file.`,
    );
  }

  try {
    return await readFile(absolutePath, "utf8");
  } catch {
    throw new Error(
      `Serving authority unavailable: cannot read ${label} ${displayPath}.`,
    );
  }
}

function parseJson(
  raw: string,
  displayPath: string,
  label: string,
): unknown {
  try {
    return JSON.parse(raw);
  } catch {
    throw new Error(
      `Serving authority rejected: ${label} ${displayPath} is not valid JSON.`,
    );
  }
}

export async function resolveServingAuthority(
  repositoryRoot = path.resolve(process.cwd(), "../.."),
  authorityRelativePath = DEFAULT_AUTHORITY_PATH,
): Promise<ServingAuthority> {
  const authorityAbsolutePath = resolveConfinedPath(
    repositoryRoot,
    authorityRelativePath,
    ALLOWED_EVIDENCE_ROOT,
    "authority",
  );

  const rawAuthority = await readRegularFile(
    authorityAbsolutePath,
    authorityRelativePath,
    "authority",
  );

  const parsedAuthority = parseJson(
    rawAuthority,
    authorityRelativePath,
    "authority",
  );

  if (!isServingAuthorityMetadata(parsedAuthority)) {
    throw new Error(
      "Serving authority rejected: authority metadata is malformed.",
    );
  }

  const promotionAbsolutePath = resolveConfinedPath(
    repositoryRoot,
    parsedAuthority.promotionAuthority,
    ALLOWED_EVIDENCE_ROOT,
    "promotion authority",
  );

  let promotionStat;

  try {
    promotionStat = await stat(promotionAbsolutePath);
  } catch {
    throw new Error(
      `Serving authority unavailable: promotion authority ${parsedAuthority.promotionAuthority} does not exist.`,
    );
  }

  if (!promotionStat.isFile()) {
    throw new Error(
      `Serving authority rejected: promotion authority ${parsedAuthority.promotionAuthority} is not a regular file.`,
    );
  }

  const actualPromotionSha256 = await sha256File(
    promotionAbsolutePath,
  );

  if (
    actualPromotionSha256 !==
    parsedAuthority.promotionAuthoritySha256
  ) {
    throw new Error(
      "Serving authority rejected: promotion authority SHA-256 does not match serving authority metadata.",
    );
  }

  let rawPromotion: string;

  try {
    rawPromotion = await readFile(
      promotionAbsolutePath,
      "utf8",
    );
  } catch {
    throw new Error(
      `Serving authority unavailable: cannot read promotion authority ${parsedAuthority.promotionAuthority}.`,
    );
  }

  const parsedPromotion = parseJson(
    rawPromotion,
    parsedAuthority.promotionAuthority,
    "promotion authority",
  );

  if (!isPromotionAuthorityMetadata(parsedPromotion)) {
    throw new Error(
      "Serving authority rejected: promotion authority metadata is malformed or not formally closed.",
    );
  }

  if (
    parsedPromotion.promotedAcceptedCheckpoint !==
    parsedAuthority.checkpoint
  ) {
    throw new Error(
      "Serving authority rejected: promoted checkpoint does not match serving authority.",
    );
  }

  if (
    parsedPromotion.promotedAcceptedCheckpointSha256 !==
    parsedAuthority.checkpointSha256
  ) {
    throw new Error(
      "Serving authority rejected: promoted checkpoint SHA-256 does not match serving authority.",
    );
  }

  if (
    parsedPromotion.previousAcceptedBaseline !==
      parsedAuthority.previousServingCheckpoint ||
    parsedPromotion.previousAcceptedBaselineSha256 !==
      parsedAuthority.previousServingCheckpointSha256
  ) {
    throw new Error(
      "Serving authority rejected: previous serving baseline does not match promotion provenance.",
    );
  }

  if (
    parsedPromotion.promotionReason !==
    parsedAuthority.promotionReason
  ) {
    throw new Error(
      "Serving authority rejected: promotion reason does not match promotion provenance.",
    );
  }

  const checkpointAbsolutePath = resolveConfinedPath(
    repositoryRoot,
    parsedAuthority.checkpoint,
    ALLOWED_CHECKPOINT_ROOT,
    "checkpoint",
  );

  let checkpointStat;

  try {
    checkpointStat = await stat(checkpointAbsolutePath);
  } catch {
    throw new Error(
      `Serving authority unavailable: checkpoint ${parsedAuthority.checkpoint} does not exist.`,
    );
  }

  if (!checkpointStat.isFile()) {
    throw new Error(
      `Serving authority rejected: checkpoint ${parsedAuthority.checkpoint} is not a regular file.`,
    );
  }

  const actualCheckpointSha256 = await sha256File(
    checkpointAbsolutePath,
  );

  if (
    actualCheckpointSha256 !==
    parsedAuthority.checkpointSha256
  ) {
    throw new Error(
      "Serving authority rejected: checkpoint SHA-256 does not match serving authority metadata.",
    );
  }

  return {
    checkpointPath: parsedAuthority.checkpoint,
    checkpointAbsolutePath,
    checkpointSha256: actualCheckpointSha256,
    acceptancePath: authorityRelativePath,
  };
}
