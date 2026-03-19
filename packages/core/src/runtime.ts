import { randomUUID } from 'crypto';
import {
  AgentDefinition,
  AgentContext,
  AgentExecutionResult,
  Tool,
  ToolCallResult,
  AgentStatus,
  AgentMemory,
} from './types';

/**
 * Simple in-memory storage for agent memory
 */
class InMemoryAgentMemory implements AgentMemory {
  private storage = new Map<string, any>();

  async store(key: string, value: any): Promise<void> {
    this.storage.set(key, value);
  }

  async retrieve(key: string): Promise<any> {
    return this.storage.get(key);
  }

  async clear(): Promise<void> {
    this.storage.clear();
  }
}

/**
 * Agent Runtime - Core execution engine for running agents
 */
export class AgentRuntime {
  private tools = new Map<string, Tool>();
  private eventHandlers = new Map<string, Set<Function>>();

  constructor(tools: Tool[] = []) {
    tools.forEach(tool => this.registerTool(tool));
  }

  /**
   * Register a tool that agents can use
   */
  registerTool(tool: Tool): void {
    this.tools.set(tool.name, tool);
  }

  /**
   * Get a registered tool
   */
  getTool(name: string): Tool | undefined {
    return this.tools.get(name);
  }

  /**
   * Subscribe to execution events
   */
  on(event: string, handler: Function): void {
    if (!this.eventHandlers.has(event)) {
      this.eventHandlers.set(event, new Set());
    }
    this.eventHandlers.get(event)!.add(handler);
  }

  /**
   * Emit an event to all subscribers
   */
  private emit(event: string, data: any): void {
    const handlers = this.eventHandlers.get(event);
    if (handlers) {
      handlers.forEach(handler => {
        try {
          handler(data);
        } catch (error) {
          console.error(`Error in event handler for ${event}:`, error);
        }
      });
    }
  }

  /**
   * Execute a tool and track the result
   */
  private async executeTool(
    tool: Tool,
    params: any,
    context: AgentContext
  ): Promise<ToolCallResult> {
    const startTime = Date.now();

    this.emit('tool:start', {
      executionId: context.executionId,
      toolName: tool.name,
      input: params,
    });

    try {
      // Validate parameters if schema is provided
      if (tool.parameters) {
        params = tool.parameters.parse(params);
      }

      const output = await tool.execute(params, context);
      const duration = Date.now() - startTime;

      const result: ToolCallResult = {
        toolName: tool.name,
        input: params,
        output,
        duration,
      };

      this.emit('tool:complete', {
        executionId: context.executionId,
        ...result,
      });

      return result;
    } catch (error) {
      const duration = Date.now() - startTime;
      const result: ToolCallResult = {
        toolName: tool.name,
        input: params,
        output: null,
        duration,
        error: error instanceof Error ? error.message : String(error),
      };

      this.emit('tool:error', {
        executionId: context.executionId,
        ...result,
      });

      return result;
    }
  }

  /**
   * Execute an agent with the given input
   */
  async execute(
    agent: AgentDefinition,
    input: string,
    metadata?: Record<string, any>
  ): Promise<AgentExecutionResult> {
    const executionId = randomUUID();
    const startTime = Date.now();
    const toolCalls: ToolCallResult[] = [];

    // Create execution context
    const context: AgentContext = {
      executionId,
      timestamp: new Date(),
      input,
      metadata,
      tools: this.tools,
      memory: new InMemoryAgentMemory(),
      emit: (event: string, data: any) => this.emit(event, { executionId, ...data }),
    };

    this.emit('agent:start', {
      executionId,
      agentName: agent.name,
      input,
      metadata,
    });

    try {
      // Run initialization hook
      if (agent.onInit) {
        await agent.onInit(context);
      }

      // Run before execute hook
      if (agent.onBeforeExecute) {
        await agent.onBeforeExecute(context);
      }

      // Execute the agent
      this.emit('agent:executing', { executionId });
      const output = await agent.execute(input, context);

      const duration = Date.now() - startTime;

      const result: AgentExecutionResult = {
        executionId,
        status: 'success',
        input,
        output,
        toolCalls,
        duration,
        timestamp: context.timestamp,
      };

      // Run after execute hook
      if (agent.onAfterExecute) {
        await agent.onAfterExecute(result, context);
      }

      this.emit('agent:complete', result);

      return result;
    } catch (error) {
      const duration = Date.now() - startTime;

      const result: AgentExecutionResult = {
        executionId,
        status: 'error',
        input,
        error: error instanceof Error ? error.message : String(error),
        toolCalls,
        duration,
        timestamp: context.timestamp,
      };

      // Run error hook
      if (agent.onError) {
        try {
          await agent.onError(error as Error, context);
        } catch (hookError) {
          console.error('Error in onError hook:', hookError);
        }
      }

      this.emit('agent:error', result);

      return result;
    }
  }

  /**
   * Validate that all required tools for an agent are registered
   */
  validateAgent(agent: AgentDefinition): { valid: boolean; missingTools: string[] } {
    const missingTools = agent.tools.filter(toolName => !this.tools.has(toolName));

    return {
      valid: missingTools.length === 0,
      missingTools,
    };
  }
}
