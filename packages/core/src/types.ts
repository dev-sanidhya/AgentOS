import { z } from 'zod';

/**
 * Agent execution status
 */
export type AgentStatus = 'idle' | 'running' | 'success' | 'error';

/**
 * Supported AI model providers
 */
export type ModelProvider = 'openai' | 'anthropic' | 'custom';

/**
 * Agent configuration schema
 */
export const AgentConfigSchema = z.object({
  model: z.string().default('claude-sonnet-4'),
  provider: z.enum(['openai', 'anthropic', 'custom']).default('anthropic'),
  temperature: z.number().min(0).max(2).default(0.7),
  maxTokens: z.number().positive().default(4000),
  topP: z.number().min(0).max(1).optional(),
  frequencyPenalty: z.number().min(-2).max(2).optional(),
  presencePenalty: z.number().min(-2).max(2).optional(),
});

export type AgentConfig = z.infer<typeof AgentConfigSchema>;

/**
 * Tool definition for agent capabilities
 */
export interface Tool {
  name: string;
  description: string;
  parameters?: z.ZodSchema;
  execute: (params: any, context: AgentContext) => Promise<any>;
}

/**
 * Agent execution context
 */
export interface AgentContext {
  executionId: string;
  timestamp: Date;
  input: string;
  metadata?: Record<string, any>;
  tools: Map<string, Tool>;
  memory?: AgentMemory;
  emit?: (event: string, data: any) => void;
}

/**
 * Agent memory interface
 */
export interface AgentMemory {
  store: (key: string, value: any) => Promise<void>;
  retrieve: (key: string) => Promise<any>;
  clear: () => Promise<void>;
}

/**
 * Tool execution result
 */
export interface ToolCallResult {
  toolName: string;
  input: any;
  output: any;
  duration: number;
  error?: string;
}

/**
 * Agent execution result
 */
export interface AgentExecutionResult {
  executionId: string;
  status: AgentStatus;
  input: string;
  output?: string;
  error?: string;
  toolCalls: ToolCallResult[];
  tokensUsed?: number;
  cost?: number;
  duration: number;
  timestamp: Date;
}

/**
 * Agent definition interface
 */
export interface AgentDefinition {
  name: string;
  version?: string;
  description: string;
  author?: string;
  tags?: string[];

  // Agent behavior
  systemPrompt: string;
  tools: string[]; // Tool names that this agent uses
  config: AgentConfig;

  // Lifecycle hooks
  onInit?: (context: AgentContext) => Promise<void>;
  onBeforeExecute?: (context: AgentContext) => Promise<void>;
  onAfterExecute?: (result: AgentExecutionResult, context: AgentContext) => Promise<void>;
  onError?: (error: Error, context: AgentContext) => Promise<void>;

  // Main execution function
  execute: (input: string, context: AgentContext) => Promise<string>;
}

/**
 * Agent manifest for publishing/sharing
 */
export interface AgentManifest {
  name: string;
  version: string;
  description: string;
  author: string;
  license: string;
  tags: string[];
  requirements: {
    tools: string[];
    models: string[];
    dependencies?: Record<string, string>;
  };
  examples: Array<{
    input: string;
    output: string;
    description?: string;
  }>;
  metrics?: {
    downloads?: number;
    rating?: number;
    successRate?: number;
  };
}

/**
 * Agent registry entry
 */
export interface AgentRegistryEntry {
  manifest: AgentManifest;
  definition: AgentDefinition;
  installedAt?: Date;
  localPath?: string;
}
