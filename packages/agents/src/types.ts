/**
 * A tool that an agent can use during execution.
 *
 * Note: With the Claude Agent SDK, tools are handled by Claude Code's
 * built-in tool system (Read, Write, Bash, WebSearch, etc.). Custom tools
 * defined here are passed as instructions in the system prompt.
 */
export interface AgentTool {
  /** Tool name (must be unique within an agent) */
  name: string;
  /** Human-readable description of what the tool does */
  description: string;
  /** JSON Schema describing the tool's input parameters */
  input_schema: {
    type: "object";
    properties: Record<string, unknown>;
    required?: string[];
  };
  /** Execute the tool with the given input. Returns a string result. */
  execute: (input: Record<string, unknown>) => Promise<string>;
}

/**
 * Configuration for an agent's behavior.
 */
export interface AgentConfig {
  /** The Claude model to use */
  model?: string;
  /** System prompt that defines the agent's personality and behavior */
  instructions: string;
  /**
   * Claude Agent SDK built-in tools to allow.
   * e.g. ['Read', 'Write', 'Bash', 'WebSearch', 'WebFetch', 'Grep', 'Glob']
   * If not specified, all default Claude Code tools are available.
   */
  allowedTools?: string[];
  /** Maximum number of agentic loop iterations (prevents runaway costs) */
  maxLoops?: number;
  /** Maximum tokens per response */
  maxTokens?: number;
  /** Temperature for generation (0-1) */
  temperature?: number;
}

/**
 * Options passed to agent.run()
 */
export interface RunOptions {
  /** Override output format */
  outputFormat?: "markdown" | "json" | "text";
  /** Callback for streaming partial results */
  onProgress?: (event: ProgressEvent) => void;
  /** Additional context to include with the input */
  context?: string;
  /** Override max loops for this run */
  maxLoops?: number;
}

/**
 * Progress events emitted during agent execution.
 */
export interface ProgressEvent {
  type: "thinking" | "tool_call" | "tool_result" | "text";
  /** Tool name (for tool_call/tool_result events) */
  tool?: string;
  /** Tool input (for tool_call events) */
  input?: Record<string, unknown>;
  /** Content of the event */
  content: string;
  /** Timestamp */
  timestamp: number;
}

/**
 * Result returned from agent.run()
 */
export interface AgentResult {
  /** The agent's final text output */
  output: string;
  /** Whether execution completed successfully */
  success: boolean;
  /** Error message if success is false */
  error?: string;
  /** Tool calls made during execution */
  toolCalls: ToolCallRecord[];
  /** Total tokens used */
  tokensUsed: {
    input: number;
    output: number;
    total: number;
  };
  /** Estimated cost in USD */
  cost: number;
  /** Execution duration in milliseconds */
  duration: number;
  /** Number of agentic loops executed */
  loops: number;
}

/**
 * Record of a tool call made during execution.
 */
export interface ToolCallRecord {
  tool: string;
  input: Record<string, unknown>;
  output: string;
  duration: number;
  success: boolean;
}

/**
 * Global configuration for the AgentOS library.
 */
export interface GlobalConfig {
  /** Anthropic API key (or AgentOS proxy key) */
  apiKey?: string;
  /** OAuth token from Claude Max/Pro plan (from `claude setup-token`) */
  oauthToken?: string;
  /** Base URL for API calls (for proxy support) */
  baseUrl?: string;
  /** Default model for all agents */
  defaultModel?: string;
  /** Global max loops limit */
  maxLoops?: number;
  /** Enable verbose logging */
  verbose?: boolean;
  /** Maximum spend per agent run in USD (circuit breaker) */
  maxSpendPerRun?: number;
  /** Global rate limit: max concurrent agent runs */
  maxConcurrentRuns?: number;
}

/**
 * Streaming event emitted during agent execution.
 */
export interface StreamEvent {
  type: "text_delta" | "tool_start" | "tool_end" | "error" | "done";
  /** Partial text content (for text_delta) */
  delta?: string;
  /** Tool name (for tool_start/tool_end) */
  tool?: string;
  /** Tool input (for tool_start) */
  input?: Record<string, unknown>;
  /** Tool result (for tool_end) */
  result?: string;
  /** Error message (for error) */
  error?: string;
  /** Final result (for done) */
  finalResult?: AgentResult;
}
