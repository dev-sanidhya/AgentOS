import { AgentExecutor, createToolCallingAgent } from 'langchain/agents';
import { ChatOpenAI } from '@langchain/openai';
import { ChatAnthropic } from '@langchain/anthropic';
import { ChatPromptTemplate } from '@langchain/core/prompts';
import { webSearchTool } from './tools/webSearch';
import { webScrapeTool } from './tools/webScrape';
import { RESEARCH_AGENT_PROMPT } from './prompts';
import { config } from 'dotenv';

config(); // Load environment variables

export interface ResearchResult {
  output: string;
  intermediateSteps: Array<{
    action: {
      tool: string;
      toolInput: any;
    };
    observation: string;
  }>;
  logs?: string[];
}

export interface {{AgentName}}Config {
  model?: string;
  temperature?: number;
  maxIterations?: number;
  verbose?: boolean;
}

export class {{AgentName}} {
  private llm: ChatOpenAI | ChatAnthropic;
  private tools: any[];
  private agent: any;
  private executor: AgentExecutor;
  private verbose: boolean;

  constructor(config: {{AgentName}}Config = {}) {
    const {
      model = 'gpt-4',
      temperature = 0.7,
      maxIterations = 15,
      verbose = false
    } = config;

    this.verbose = verbose;
    this.llm = this.createLLM(model, temperature);
    this.tools = [webSearchTool, webScrapeTool];
    this.agent = this.createAgent();
    this.executor = new AgentExecutor({
      agent: this.agent,
      tools: this.tools,
      maxIterations,
      verbose: this.verbose,
      returnIntermediateSteps: true,
    });
  }

  private createLLM(model: string, temperature: number): ChatOpenAI | ChatAnthropic {
    if (model.startsWith('gpt')) {
      const apiKey = process.env.OPENAI_API_KEY;
      if (!apiKey) {
        throw new Error('OPENAI_API_KEY environment variable is required for OpenAI models');
      }
      return new ChatOpenAI({
        modelName: model,
        temperature,
        openAIApiKey: apiKey,
      });
    } else if (model.startsWith('claude')) {
      const apiKey = process.env.ANTHROPIC_API_KEY;
      if (!apiKey) {
        throw new Error('ANTHROPIC_API_KEY environment variable is required for Anthropic models');
      }
      return new ChatAnthropic({
        modelName: model,
        temperature,
        anthropicApiKey: apiKey,
      });
    } else {
      throw new Error(`Unsupported model: ${model}. Use OpenAI (gpt-*) or Anthropic (claude-*) models.`);
    }
  }

  private createAgent() {
    const prompt = ChatPromptTemplate.fromMessages([
      ['system', RESEARCH_AGENT_PROMPT],
      ['human', '{input}'],
      ['placeholder', '{agent_scratchpad}'],
    ]);

    return createToolCallingAgent({
      llm: this.llm,
      tools: this.tools,
      prompt,
    });
  }

  async research(query: string): Promise<ResearchResult> {
    if (this.verbose) {
      console.log(`\n🔍 Starting research for: "${query}"\n`);
    }

    try {
      const result = await this.executor.invoke({
        input: query,
      });

      if (this.verbose) {
        console.log(`\n✅ Research completed successfully\n`);
      }

      return {
        output: result.output,
        intermediateSteps: result.intermediateSteps || [],
        logs: result.logs || [],
      };
    } catch (error) {
      console.error('❌ Research failed:', error);
      throw error;
    }
  }

  async aresearch(query: string): Promise<ResearchResult> {
    return this.research(query); // Already async
  }
}

// Convenience function for quick research
export async function research(
  query: string,
  config: {{AgentName}}Config = {}
): Promise<string> {
  const agent = new {{AgentName}}(config);
  const result = await agent.research(query);
  return result.output;
}

export default {{AgentName}};