// ─── Configuration ───────────────────────────────────────────────
export { configure } from "./config";

// ─── Pre-built Agents ────────────────────────────────────────────
export {
  ResearchAgent,
  CodeReviewAgent,
  ContentWriter,
  DataAnalyst,
  CompetitorAnalyzer,
  EmailDrafter,
  SEOAuditor,
  BugTriager,
} from "./agents";

// ─── Custom Agent Builder ────────────────────────────────────────
export { createAgent } from "./create-agent";
export type { AgentSpec, CustomAgent } from "./create-agent";

// ─── Base Agent Class (for advanced users) ───────────────────────
export { Agent } from "./agent";

// ─── Types ───────────────────────────────────────────────────────
export type {
  AgentTool,
  AgentConfig,
  AgentResult,
  RunOptions,
  ProgressEvent,
  ToolCallRecord,
  GlobalConfig,
  StreamEvent,
} from "./types";
