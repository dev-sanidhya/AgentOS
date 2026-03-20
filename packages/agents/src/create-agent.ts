import { query } from "@anthropic-ai/claude-agent-sdk";
import { Agent } from "./agent";
import { AgentResult, RunOptions } from "./types";
import { resolveAuth, getConfig } from "./config";

/**
 * Structured specification for a custom agent.
 */
export interface AgentSpec {
  /** What the agent should do */
  task: string;
  /** What inputs the agent expects */
  inputs?: string;
  /** What format the output should be in */
  outputs?: string;
  /** Tool names to include: 'web_search', 'web_scrape', 'read_file', 'list_files' */
  tools?: string[];
  /** Custom instructions to append */
  additionalInstructions?: string;
}

const BUILDER_PROMPT = `You are an agent configuration builder. Given a user's description of what they want an agent to do, generate a system prompt for that agent.

The system prompt you generate should:
1. Clearly define the agent's role and expertise
2. Describe the process the agent should follow (step by step)
3. Specify the output format
4. Include rules and constraints
5. Be detailed enough that the agent can work autonomously

Respond in this exact JSON format (no markdown, no code blocks, just raw JSON):
{
  "systemPrompt": "The full system prompt for the agent",
  "temperature": 0.5,
  "maxLoops": 10
}`;

/**
 * Create a custom agent from a plain English description or structured spec.
 *
 * Uses the Claude Agent SDK to generate agent configurations.
 *
 * @example
 * ```ts
 * // From a description
 * const agent = await createAgent(
 *   'An agent that monitors tech news and summarizes the top stories each day'
 * );
 * const summary = await agent.run('What happened in tech today?');
 *
 * // From a structured spec
 * const agent = await createAgent({
 *   task: 'Analyze GitHub repositories',
 *   inputs: 'Repository URL or name',
 *   outputs: 'Structured report with stars, issues, activity metrics',
 *   tools: ['web_search', 'web_scrape'],
 * });
 * ```
 */
export async function createAgent(
  descriptionOrSpec: string | AgentSpec
): Promise<CustomAgent> {
  // If structured spec with enough detail, build directly without LLM
  if (typeof descriptionOrSpec !== "string" && descriptionOrSpec.tools) {
    return buildFromSpec(descriptionOrSpec);
  }

  // Use Claude Agent SDK to generate the agent configuration
  const auth = resolveAuth();
  const config = getConfig();

  const description =
    typeof descriptionOrSpec === "string"
      ? descriptionOrSpec
      : formatSpec(descriptionOrSpec);

  const builderPrompt = `${BUILDER_PROMPT}\n\nUser's description:\n${description}`;

  // Build env for the SDK subprocess
  const env: Record<string, string | undefined> = { ...process.env };
  if (auth.oauthToken) {
    env.CLAUDE_CODE_OAUTH_TOKEN = auth.oauthToken;
  } else if (auth.apiKey) {
    env.ANTHROPIC_API_KEY = auth.apiKey;
  }

  let resultText = "";

  try {
    const sdkQuery = query({
      prompt: builderPrompt,
      options: {
        model: config.defaultModel,
        maxTurns: 1,
        permissionMode: "bypassPermissions",
        allowDangerouslySkipPermissions: true,
        env,
      },
    });

    for await (const message of sdkQuery) {
      if (message.type === "result" && message.subtype === "success") {
        resultText = message.result;
      }
    }
  } catch {
    // If SDK call fails, use fallback
    resultText = "";
  }

  let agentConfig: {
    systemPrompt: string;
    temperature: number;
    maxLoops: number;
  };

  try {
    // Try to parse JSON from the result (may be wrapped in markdown)
    const jsonMatch = resultText.match(/\{[\s\S]*\}/);
    agentConfig = JSON.parse(jsonMatch?.[0] ?? resultText);
  } catch {
    // Fallback: use the description as-is
    agentConfig = {
      systemPrompt: `You are a helpful AI agent. ${description}\n\nFollow the user's instructions carefully and provide thorough, well-structured responses.`,
      temperature: 0.5,
      maxLoops: 10,
    };
  }

  const agent = new Agent({
    instructions: agentConfig.systemPrompt,
    temperature: agentConfig.temperature,
    maxLoops: agentConfig.maxLoops,
    maxTokens: 4096,
  });

  return new CustomAgent(agent, description);
}

function buildFromSpec(spec: AgentSpec): CustomAgent {
  let instructions = `You are an AI agent specialized in: ${spec.task}`;

  if (spec.inputs) {
    instructions += `\n\nExpected inputs: ${spec.inputs}`;
  }
  if (spec.outputs) {
    instructions += `\n\nExpected output format: ${spec.outputs}`;
  }
  if (spec.additionalInstructions) {
    instructions += `\n\n${spec.additionalInstructions}`;
  }

  instructions +=
    "\n\nFollow a methodical process, use your available tools when needed, and provide thorough, well-structured results.";

  const agent = new Agent({
    instructions,
    temperature: 0.5,
    maxLoops: 10,
    maxTokens: 4096,
  });

  return new CustomAgent(agent, spec.task);
}

function formatSpec(spec: AgentSpec): string {
  let desc = `Task: ${spec.task}`;
  if (spec.inputs) desc += `\nExpected inputs: ${spec.inputs}`;
  if (spec.outputs) desc += `\nExpected outputs: ${spec.outputs}`;
  if (spec.additionalInstructions)
    desc += `\nAdditional requirements: ${spec.additionalInstructions}`;
  return desc;
}

/**
 * A custom agent created via createAgent().
 */
export class CustomAgent {
  private agent: Agent;
  public readonly description: string;

  constructor(agent: Agent, description: string) {
    this.agent = agent;
    this.description = description;
  }

  async run(input: string, options?: RunOptions): Promise<AgentResult> {
    return this.agent.run(input, options);
  }
}
