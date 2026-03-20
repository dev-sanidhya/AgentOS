import { query } from "@anthropic-ai/claude-agent-sdk";
import {
  AgentConfig,
  AgentResult,
  ProgressEvent,
  RunOptions,
  StreamEvent,
  ToolCallRecord,
} from "./types";
import { getConfig, resolveAuth } from "./config";

// Track concurrent runs for global rate limiting
let activeRuns = 0;

/**
 * Base Agent class that wraps the Claude Agent SDK.
 *
 * Uses the `query()` function from @anthropic-ai/claude-agent-sdk,
 * which runs Claude Code as a subprocess. This supports OAuth tokens
 * from Claude Max/Pro plans — no API key needed.
 *
 * @example
 * ```ts
 * const agent = new Agent({
 *   instructions: 'You are a helpful research assistant.',
 *   allowedTools: ['WebSearch', 'WebFetch', 'Read'],
 * });
 * const result = await agent.run('Find the latest AI trends');
 * ```
 */
export class Agent {
  private config: AgentConfig;

  constructor(config: AgentConfig) {
    this.config = config;
  }

  /**
   * Build environment variables for the Claude Agent SDK subprocess.
   */
  private buildEnv(): Record<string, string | undefined> {
    const auth = resolveAuth();
    const env: Record<string, string | undefined> = { ...process.env };

    if (auth.oauthToken) {
      env.CLAUDE_CODE_OAUTH_TOKEN = auth.oauthToken;
    } else if (auth.apiKey) {
      env.ANTHROPIC_API_KEY = auth.apiKey;
    }

    if (auth.baseUrl) {
      env.ANTHROPIC_BASE_URL = auth.baseUrl;
    }

    return env;
  }

  /**
   * Build the full prompt with context and format instructions.
   */
  private buildPrompt(input: string, options: RunOptions): string {
    let prompt = input;

    if (options.context) {
      prompt = `Context:\n${options.context}\n\nRequest:\n${input}`;
    }

    if (options.outputFormat === "json") {
      prompt += "\n\nReturn your final output as valid JSON.";
    } else if (options.outputFormat === "markdown") {
      prompt += "\n\nFormat your final output as clean Markdown.";
    }

    return prompt;
  }

  /**
   * Build the options object for the SDK query() call.
   */
  private buildQueryOptions(options: RunOptions) {
    const globalCfg = getConfig();
    const model = this.config.model ?? globalCfg.defaultModel;
    const maxTurns = options.maxLoops ?? this.config.maxLoops ?? globalCfg.maxLoops;
    const maxSpend = globalCfg.maxSpendPerRun;
    const env = this.buildEnv();

    const queryOptions: Record<string, unknown> = {
      model,
      maxTurns,
      maxBudgetUsd: maxSpend,
      systemPrompt: this.config.instructions,
      permissionMode: "bypassPermissions",
      allowDangerouslySkipPermissions: true,
      env,
    };

    // If specific tools are configured, only allow those
    if (this.config.allowedTools) {
      queryOptions.allowedTools = this.config.allowedTools;
    }

    return queryOptions;
  }

  /**
   * Run the agent with the given input.
   */
  async run(input: string, options: RunOptions = {}): Promise<AgentResult> {
    const startTime = Date.now();
    const globalCfg = getConfig();

    // Concurrency guard
    if (
      globalCfg.maxConcurrentRuns &&
      activeRuns >= globalCfg.maxConcurrentRuns
    ) {
      return {
        output: "",
        success: false,
        error: `Max concurrent runs (${globalCfg.maxConcurrentRuns}) exceeded. Wait for other agents to finish.`,
        toolCalls: [],
        tokensUsed: { input: 0, output: 0, total: 0 },
        cost: 0,
        duration: Date.now() - startTime,
        loops: 0,
      };
    }

    activeRuns++;

    try {
      return await this.executeWithSDK(input, options, startTime);
    } finally {
      activeRuns--;
    }
  }

  /**
   * Run the agent with streaming — yields events as they happen.
   */
  async *stream(
    input: string,
    options: RunOptions = {}
  ): AsyncGenerator<StreamEvent> {
    const startTime = Date.now();
    activeRuns++;

    try {
      const prompt = this.buildPrompt(input, options);
      const queryOptions = this.buildQueryOptions(options);
      const toolCalls: ToolCallRecord[] = [];

      const sdkQuery = query({
        prompt,
        options: queryOptions as Parameters<typeof query>[0]["options"],
      });

      let finalOutput = "";
      let totalCost = 0;
      let loops = 0;

      for await (const message of sdkQuery) {
        if (message.type === "assistant") {
          for (const block of message.message.content) {
            if ("text" in block && block.text) {
              finalOutput = block.text;
              yield { type: "text_delta", delta: block.text };
            }
            if ("name" in block) {
              yield {
                type: "tool_start",
                tool: block.name,
                input: "input" in block ? (block.input as Record<string, unknown>) : undefined,
              };
            }
          }
          loops++;
        }

        if (message.type === "result") {
          if (message.subtype === "success") {
            finalOutput = message.result;
            totalCost = message.total_cost_usd;
            loops = message.num_turns;
          }

          yield {
            type: "done",
            finalResult: {
              output: finalOutput,
              success: message.subtype === "success",
              error: message.subtype !== "success" ? ("errors" in message ? message.errors.join(", ") : "Unknown error") : undefined,
              toolCalls,
              tokensUsed: {
                input: message.usage?.input_tokens ?? 0,
                output: message.usage?.output_tokens ?? 0,
                total: (message.usage?.input_tokens ?? 0) + (message.usage?.output_tokens ?? 0),
              },
              cost: totalCost,
              duration: Date.now() - startTime,
              loops,
            },
          };
        }
      }
    } catch (err) {
      yield {
        type: "error",
        error: err instanceof Error ? err.message : String(err),
      };
    } finally {
      activeRuns--;
    }
  }

  /**
   * Execute using the Claude Agent SDK's query() function.
   */
  private async executeWithSDK(
    input: string,
    options: RunOptions,
    startTime: number
  ): Promise<AgentResult> {
    const globalCfg = getConfig();
    const prompt = this.buildPrompt(input, options);
    const queryOptions = this.buildQueryOptions(options);

    const toolCalls: ToolCallRecord[] = [];
    let finalOutput = "";
    let totalCost = 0;
    let loops = 0;
    let totalInputTokens = 0;
    let totalOutputTokens = 0;

    const emit = (event: Omit<ProgressEvent, "timestamp">) => {
      if (options.onProgress) {
        options.onProgress({ ...event, timestamp: Date.now() });
      }
      if (globalCfg.verbose) {
        const prefix =
          event.type === "tool_call"
            ? `  -> ${event.tool}()`
            : event.type === "tool_result"
              ? `  <- ${event.tool}`
              : event.type === "thinking"
                ? "  [thinking]"
                : "";
        if (prefix) {
          console.log(prefix, event.content.slice(0, 200));
        }
      }
    };

    try {
      const sdkQuery = query({
        prompt,
        options: queryOptions as Parameters<typeof query>[0]["options"],
      });

      for await (const message of sdkQuery) {
        if (message.type === "assistant") {
          for (const block of message.message.content) {
            if ("text" in block && block.text) {
              emit({ type: "text", content: block.text });
            }
            if ("name" in block) {
              const toolName = block.name;
              const toolInput = "input" in block ? (block.input as Record<string, unknown>) : {};

              emit({
                type: "tool_call",
                tool: toolName,
                input: toolInput,
                content: `Calling ${toolName}`,
              });

              toolCalls.push({
                tool: toolName,
                input: toolInput,
                output: "",
                duration: 0,
                success: true,
              });
            }
          }
        }

        if (message.type === "result") {
          if (message.subtype === "success") {
            finalOutput = message.result;
            totalCost = message.total_cost_usd;
            loops = message.num_turns;
            totalInputTokens = message.usage?.input_tokens ?? 0;
            totalOutputTokens = message.usage?.output_tokens ?? 0;
          } else {
            const errors = "errors" in message ? message.errors : [];
            return {
              output: "",
              success: false,
              error: errors.join(", ") || `Agent stopped: ${message.subtype}`,
              toolCalls,
              tokensUsed: {
                input: message.usage?.input_tokens ?? 0,
                output: message.usage?.output_tokens ?? 0,
                total: (message.usage?.input_tokens ?? 0) + (message.usage?.output_tokens ?? 0),
              },
              cost: message.total_cost_usd ?? 0,
              duration: Date.now() - startTime,
              loops: message.num_turns ?? 0,
            };
          }
        }
      }

      return {
        output: finalOutput,
        success: true,
        toolCalls,
        tokensUsed: {
          input: totalInputTokens,
          output: totalOutputTokens,
          total: totalInputTokens + totalOutputTokens,
        },
        cost: Math.round(totalCost * 10000) / 10000,
        duration: Date.now() - startTime,
        loops,
      };
    } catch (err) {
      return {
        output: "",
        success: false,
        error: err instanceof Error ? err.message : String(err),
        toolCalls,
        tokensUsed: {
          input: totalInputTokens,
          output: totalOutputTokens,
          total: totalInputTokens + totalOutputTokens,
        },
        cost: 0,
        duration: Date.now() - startTime,
        loops,
      };
    }
  }
}
