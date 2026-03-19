/**
 * {{AgentName}} - AI Research Assistant
 *
 * An intelligent agent that conducts comprehensive research by searching
 * the web, extracting content, and synthesizing information from multiple sources.
 */

import { ChatOpenAI } from "@langchain/openai";
import { ChatAnthropic } from "@langchain/anthropic";
import { AgentExecutor, createToolCallingAgent } from "langchain/agents";
import { ChatPromptTemplate } from "@langchain/core/prompts";
import { Tool } from "langchain/tools";
import { webSearchTool, webScrapeTool } from "./tools";
import { RESEARCH_AGENT_PROMPT } from "./prompts";
import dotenv from "dotenv";

dotenv.config();

export interface ResearchResult {
  output: string;
  intermediateSteps: Array<{
    action: {
      tool: string;
      toolInput: any;
    };
    observation: string;
  }>;
  usage?: {
    totalTokens: number;
    promptTokens: number;
    completionTokens: number;
  };
}

export interface {{AgentName}}Config {
  model?: string;
  temperature?: number;
  maxIterations?: number;
  verbose?: boolean;
}

export class {{AgentName}} {
  private llm: ChatOpenAI | ChatAnthropic;
  private agent: AgentExecutor;
  private tools: Tool[];
  private config: Required<{{AgentName}}Config>;

  constructor(config: {{AgentName}}Config = {}) {
    this.config = {
      model: config.model || "gpt-4",
      temperature: config.temperature ?? 0.7,
      maxIterations: config.maxIterations || 15,
      verbose: config.verbose ?? false,
    };

    this.llm = this.createLLM();
    this.tools = this.createTools();
    this.agent = this.createAgent();
  }

  private createLLM(): ChatOpenAI | ChatAnthropic {
    const { model, temperature } = this.config;

    if (model.includes("claude")) {
      if (!process.env.ANTHROPIC_API_KEY) {
        throw new Error(
          "ANTHROPIC_API_KEY not found. Please set it in your environment or .env file."
        );
      }

      return new ChatAnthropic({
        modelName: model,
        temperature,
        anthropicApiKey: process.env.ANTHROPIC_API_KEY,
      });
    } else {
      if (!process.env.OPENAI_API_KEY) {
        throw new Error(
          "OPENAI_API_KEY not found. Please set it in your environment or .env file."
        );
      }

      return new ChatOpenAI({
        modelName: model,
        temperature,
        openAIApiKey: process.env.OPENAI_API_KEY,
      });
    }
  }

  private createTools(): Tool[] {
    return [
      webSearchTool,
      webScrapeTool,
    ];
  }

  private createAgent(): AgentExecutor {
    const prompt = ChatPromptTemplate.fromTemplate(RESEARCH_AGENT_PROMPT);

    const agent = createToolCallingAgent({
      llm: this.llm,
      tools: this.tools,
      prompt,
    });

    return new AgentExecutor({
      agent,
      tools: this.tools,
      maxIterations: this.config.maxIterations,
      verbose: this.config.verbose,
      returnIntermediateSteps: true,
    });
  }

  /**
   * Conduct research on a given query
   */
  public async research(query: string): Promise<ResearchResult> {
    if (this.config.verbose) {
      console.log(`🔍 Starting research on: "${query}"`);
    }

    try {
      const startTime = Date.now();
      const result = await this.agent.invoke({
        input: query,
      });

      const duration = Date.now() - startTime;

      if (this.config.verbose) {
        console.log(`✅ Research completed in ${duration}ms`);
        console.log(`🧮 Used ${result.intermediateSteps.length} tool calls`);
      }

      return {
        output: result.output,
        intermediateSteps: result.intermediateSteps.map((step: any) => ({
          action: {
            tool: step.action?.tool ?? "unknown",
            toolInput: step.action?.toolInput ?? {},
          },
          observation: step.observation,
        })),
      };
    } catch (error) {
      if (this.config.verbose) {
        console.error("❌ Research failed:", error);
      }
      throw error;
    }
  }

  /**
   * Quick research function (convenience method)
   */
  public static async quickResearch(
    query: string,
    config: {{AgentName}}Config = {}
  ): Promise<string> {
    const agent = new {{AgentName}}(config);
    const result = await agent.research(query);
    return result.output;
  }
}

/**
 * Convenience function for quick research
 */
export async function research(
  query: string,
  options: {{AgentName}}Config = {}
): Promise<string> {
  return {{AgentName}}.quickResearch(query, options);
}

// Export default
export default {{AgentName}};