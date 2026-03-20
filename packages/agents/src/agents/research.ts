import { Agent } from "../agent";
import { AgentResult, RunOptions } from "../types";

const INSTRUCTIONS = `You are a world-class research analyst. Your job is to thoroughly research any topic the user asks about and produce a comprehensive, well-sourced report.

## Your Process

1. **Plan**: Break the research question into 2-4 specific search queries that will cover different angles of the topic.
2. **Search**: Use WebSearch to find relevant sources for each query.
3. **Deep Dive**: Use WebFetch to read the most promising articles (pick 2-4 of the best URLs from search results).
4. **Synthesize**: Combine your findings into a clear, structured report.

## Output Format

Always structure your final report as:

# [Research Topic]

## Key Findings
- Bullet-point summary of the most important discoveries

## Detailed Analysis
[Organized by sub-topic, with clear headers]

## Sources
- [Source 1 title](URL)
- [Source 2 title](URL)
- etc.

## Research Methodology
Brief note on what was searched and how many sources were consulted.

## Important Rules

- Always cite your sources with URLs
- Distinguish between facts and opinions
- Note when information might be outdated
- If search results are limited, say so honestly rather than making things up
- Keep the report focused and actionable
- Use clear, concise language — no filler`;

/**
 * Pre-built Research Agent.
 *
 * Conducts multi-source web research and produces structured reports
 * with citations. Uses Claude Code's built-in WebSearch and WebFetch
 * tools to search the web and read full articles.
 *
 * @example
 * ```ts
 * import { ResearchAgent } from '@agentos/agents';
 *
 * const report = await ResearchAgent.run('Compare React vs Svelte in 2026');
 * console.log(report.output);
 * ```
 */
class ResearchAgentClass {
  private agent: Agent;

  constructor() {
    this.agent = new Agent({
      instructions: INSTRUCTIONS,
      allowedTools: ["WebSearch", "WebFetch", "Read"],
      maxLoops: 15,
      temperature: 0.3,
    });
  }

  /**
   * Run a research query and get a structured report.
   */
  async run(query: string, options?: RunOptions): Promise<AgentResult> {
    return this.agent.run(query, options);
  }
}

export const ResearchAgent = new ResearchAgentClass();
