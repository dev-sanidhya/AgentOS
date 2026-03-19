import { ChatOpenAI } from '@langchain/openai';
import { ChatAnthropic } from '@langchain/anthropic';
import { PromptTemplate } from '@langchain/core/prompts';
import { LLMChain } from 'langchain/chains';
import { BaseLanguageModel } from '@langchain/core/language_models/base';
import { Tool } from '@langchain/core/tools';
import { AgentExecutor } from 'langchain/agents';
import { initializeAgentExecutorWithOptions } from 'langchain/agents';
import { fileAnalyzer, securityScanner } from './tools/index.js';
import { PROMPTS } from './prompts.js';

export interface CodeReviewResult {
  overallScore: number;
  analysis: {
    codeQuality: {
      score: number;
      issues: CodeIssue[];
      suggestions: string[];
    };
    security: {
      score: number;
      vulnerabilities: SecurityVulnerability[];
      recommendations: string[];
    };
    performance: {
      score: number;
      bottlenecks: PerformanceIssue[];
      optimizations: string[];
    };
    maintainability: {
      score: number;
      complexity: number;
      codeSmells: string[];
      refactoringTips: string[];
    };
  };
  summary: string;
  detailedFeedback: string[];
}

export interface CodeIssue {
  type: 'error' | 'warning' | 'suggestion';
  line: number;
  column?: number;
  severity: 'low' | 'medium' | 'high' | 'critical';
  message: string;
  rule?: string;
  suggestion?: string;
}

export interface SecurityVulnerability {
  type: string;
  severity: 'low' | 'medium' | 'high' | 'critical';
  line: number;
  description: string;
  cwe?: string;
  recommendation: string;
}

export interface PerformanceIssue {
  type: string;
  line: number;
  impact: 'low' | 'medium' | 'high';
  description: string;
  suggestion: string;
}

export interface ReviewConfig {
  includeSecurityScan: boolean;
  includePerformanceAnalysis: boolean;
  strictMode: boolean;
  languageSpecific: boolean;
  customRules?: string[];
}

export interface ModelConfig {
  provider: 'openai' | 'anthropic';
  model: string;
  temperature?: number;
  maxTokens?: number;
}

export class {{AgentName}} {
  private llm: BaseLanguageModel;
  private tools: Tool[];
  private executor: AgentExecutor | null = null;
  private config: ReviewConfig;

  constructor(modelConfig: ModelConfig, reviewConfig: ReviewConfig = {
    includeSecurityScan: true,
    includePerformanceAnalysis: true,
    strictMode: false,
    languageSpecific: true
  }) {
    this.config = reviewConfig;
    this.llm = this.initializeModel(modelConfig);
    this.tools = [fileAnalyzer, securityScanner];
    this.initializeAgent();
  }

  private initializeModel(config: ModelConfig): BaseLanguageModel {
    const baseConfig = {
      temperature: config.temperature || 0.1,
      maxTokens: config.maxTokens || 4000,
    };

    switch (config.provider) {
      case 'openai':
        return new ChatOpenAI({
          modelName: config.model || 'gpt-4',
          ...baseConfig,
        });
      case 'anthropic':
        return new ChatAnthropic({
          model: config.model || 'claude-3-sonnet-20240229',
          ...baseConfig,
        });
      default:
        throw new Error(`Unsupported model provider: ${config.provider}`);
    }
  }

  private async initializeAgent(): Promise<void> {
    this.executor = await initializeAgentExecutorWithOptions(this.tools, this.llm, {
      agentType: 'structured-chat-zero-shot-react-description',
      verbose: false,
      maxIterations: 10,
    });
  }

  /**
   * Review code with comprehensive analysis
   */
  async reviewCode(
    code: string,
    fileName: string,
    language: string
  ): Promise<CodeReviewResult> {
    try {
      if (!this.executor) {
        throw new Error('Agent not initialized');
      }

      const prompt = PromptTemplate.fromTemplate(PROMPTS.MAIN_REVIEW_PROMPT);
      const formattedPrompt = await prompt.format({
        code,
        fileName,
        language,
        includeSecurityScan: this.config.includeSecurityScan,
        includePerformanceAnalysis: this.config.includePerformanceAnalysis,
        strictMode: this.config.strictMode,
        languageSpecific: this.config.languageSpecific,
      });

      const result = await this.executor.invoke({
        input: formattedPrompt,
      });

      return this.parseReviewResult(result.output);
    } catch (error) {
      throw new Error(`Code review failed: ${error instanceof Error ? error.message : String(error)}`);
    }
  }

  /**
   * Analyze multiple files
   */
  async reviewMultipleFiles(
    files: Array<{ code: string; fileName: string; language: string }>
  ): Promise<Map<string, CodeReviewResult>> {
    const results = new Map<string, CodeReviewResult>();

    for (const file of files) {
      try {
        const result = await this.reviewCode(file.code, file.fileName, file.language);
        results.set(file.fileName, result);
      } catch (error) {
        console.error(`Failed to review ${file.fileName}:`, error);
        // Continue with other files
      }
    }

    return results;
  }

  /**
   * Quick security scan only
   */
  async quickSecurityScan(code: string, language: string): Promise<SecurityVulnerability[]> {
    try {
      if (!this.executor) {
        throw new Error('Agent not initialized');
      }

      const prompt = PromptTemplate.fromTemplate(PROMPTS.SECURITY_SCAN_PROMPT);
      const formattedPrompt = await prompt.format({ code, language });

      const result = await this.executor.invoke({
        input: formattedPrompt,
      });

      return this.parseSecurityResult(result.output);
    } catch (error) {
      throw new Error(`Security scan failed: ${error instanceof Error ? error.message : String(error)}`);
    }
  }

  /**
   * Get code quality score
   */
  async getQualityScore(code: string, language: string): Promise<number> {
    try {
      const review = await this.reviewCode(code, 'temp.file', language);
      return review.overallScore;
    } catch (error) {
      console.error('Failed to get quality score:', error);
      return 0;
    }
  }

  /**
   * Validate code against best practices
   */
  async validateBestPractices(
    code: string,
    language: string,
    framework?: string
  ): Promise<CodeIssue[]> {
    try {
      if (!this.executor) {
        throw new Error('Agent not initialized');
      }

      const prompt = PromptTemplate.fromTemplate(PROMPTS.BEST_PRACTICES_PROMPT);
      const formattedPrompt = await prompt.format({
        code,
        language,
        framework: framework || 'generic',
      });

      const result = await this.executor.invoke({
        input: formattedPrompt,
      });

      return this.parseBestPracticesResult(result.output);
    } catch (error) {
      throw new Error(`Best practices validation failed: ${error instanceof Error ? error.message : String(error)}`);
    }
  }

  private parseReviewResult(output: string): CodeReviewResult {
    try {
      // Try to parse as JSON first
      const jsonMatch = output.match(/\{[\s\S]*\}/);
      if (jsonMatch) {
        return JSON.parse(jsonMatch[0]);
      }

      // Fallback to manual parsing
      return this.manualParseReviewResult(output);
    } catch (error) {
      throw new Error(`Failed to parse review result: ${error instanceof Error ? error.message : String(error)}`);
    }
  }

  private manualParseReviewResult(output: string): CodeReviewResult {
    // Manual parsing logic for when JSON parsing fails
    const scoreMatch = output.match(/overall score[:\s]*(\d+(?:\.\d+)?)/i);
    const overallScore = scoreMatch ? parseFloat(scoreMatch[1]) : 5;

    return {
      overallScore,
      analysis: {
        codeQuality: {
          score: overallScore,
          issues: [],
          suggestions: this.extractSuggestions(output),
        },
        security: {
          score: overallScore,
          vulnerabilities: [],
          recommendations: [],
        },
        performance: {
          score: overallScore,
          bottlenecks: [],
          optimizations: [],
        },
        maintainability: {
          score: overallScore,
          complexity: 5,
          codeSmells: [],
          refactoringTips: [],
        },
      },
      summary: this.extractSummary(output),
      detailedFeedback: [output],
    };
  }

  private parseSecurityResult(output: string): SecurityVulnerability[] {
    // Parse security scan results
    const vulnerabilities: SecurityVulnerability[] = [];

    try {
      const jsonMatch = output.match(/\[[\s\S]*\]/);
      if (jsonMatch) {
        return JSON.parse(jsonMatch[0]);
      }
    } catch (error) {
      console.error('Failed to parse security result as JSON:', error);
    }

    return vulnerabilities;
  }

  private parseBestPracticesResult(output: string): CodeIssue[] {
    // Parse best practices validation results
    const issues: CodeIssue[] = [];

    try {
      const jsonMatch = output.match(/\[[\s\S]*\]/);
      if (jsonMatch) {
        return JSON.parse(jsonMatch[0]);
      }
    } catch (error) {
      console.error('Failed to parse best practices result as JSON:', error);
    }

    return issues;
  }

  private extractSuggestions(output: string): string[] {
    const suggestions: string[] = [];
    const lines = output.split('\n');

    for (const line of lines) {
      if (line.includes('suggest') || line.includes('recommend') || line.includes('consider')) {
        suggestions.push(line.trim());
      }
    }

    return suggestions;
  }

  private extractSummary(output: string): string {
    const lines = output.split('\n');
    const summaryLines = lines.slice(0, 3);
    return summaryLines.join(' ').trim();
  }

  /**
   * Update review configuration
   */
  updateConfig(newConfig: Partial<ReviewConfig>): void {
    this.config = { ...this.config, ...newConfig };
  }

  /**
   * Get current configuration
   */
  getConfig(): ReviewConfig {
    return { ...this.config };
  }
}

export default {{AgentName}};