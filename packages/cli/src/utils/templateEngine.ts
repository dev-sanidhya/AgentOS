import fs from 'fs';
import path from 'path';

export interface TemplateVariable {
  name: string;
  value: string;
  transform?: 'kebab' | 'camel' | 'pascal' | 'snake' | 'upper' | 'lower';
}

export interface TemplateProcessingOptions {
  variables: Record<string, string>;
  sourceDir: string;
  targetDir: string;
  overwrite?: boolean;
  verbose?: boolean;
}

export interface ProcessedFile {
  sourcePath: string;
  targetPath: string;
  processed: boolean;
  skipped?: boolean;
  reason?: string;
}

export interface TemplateEngineResult {
  success: boolean;
  processedFiles: ProcessedFile[];
  skippedFiles: ProcessedFile[];
  errors: string[];
}

export class TemplateEngine {
  private variables: Record<string, any> = {};
  private verbose: boolean = false;

  constructor(variables: Record<string, string> = {}, verbose: boolean = false) {
    this.variables = this.expandVariables(variables);
    this.verbose = verbose;
  }

  async processTemplate(options: TemplateProcessingOptions): Promise<TemplateEngineResult> {
    const result: TemplateEngineResult = {
      success: true,
      processedFiles: [],
      skippedFiles: [],
      errors: []
    };

    try {
      // Ensure target directory exists
      if (!fs.existsSync(options.targetDir)) {
        fs.mkdirSync(options.targetDir, { recursive: true });
      }

      // Update variables
      this.variables = this.expandVariables(options.variables);

      // Process all files in source directory
      await this.processDirectory(options.sourceDir, options.targetDir, options, result);

    } catch (error) {
      result.success = false;
      result.errors.push(`Template processing failed: ${error instanceof Error ? error.message : String(error)}`);
    }

    return result;
  }

  private async processDirectory(
    sourceDir: string,
    targetDir: string,
    options: TemplateProcessingOptions,
    result: TemplateEngineResult
  ): Promise<void> {
    const entries = fs.readdirSync(sourceDir, { withFileTypes: true });

    for (const entry of entries) {
      const sourcePath = path.join(sourceDir, entry.name);
      const processedName = this.processVariables(entry.name);
      const targetPath = path.join(targetDir, processedName);

      try {
        if (entry.isDirectory()) {
          // Create directory and recurse
          if (!fs.existsSync(targetPath)) {
            fs.mkdirSync(targetPath, { recursive: true });
          }
          await this.processDirectory(sourcePath, targetPath, options, result);

        } else if (entry.isFile()) {
          // Process file
          const processed = await this.processFile(sourcePath, targetPath, options);

          if (processed.processed) {
            result.processedFiles.push(processed);
          } else {
            result.skippedFiles.push(processed);
          }
        }
      } catch (error) {
        const errorMsg = `Error processing ${sourcePath}: ${error instanceof Error ? error.message : String(error)}`;
        result.errors.push(errorMsg);

        if (this.verbose) {
          console.error(`❌ ${errorMsg}`);
        }
      }
    }
  }

  private async processFile(
    sourcePath: string,
    targetPath: string,
    options: TemplateProcessingOptions
  ): Promise<ProcessedFile> {
    const processed: ProcessedFile = {
      sourcePath,
      targetPath,
      processed: false
    };

    try {
      // Check if target file already exists
      if (fs.existsSync(targetPath) && !options.overwrite) {
        processed.skipped = true;
        processed.reason = 'File already exists';
        return processed;
      }

      // Read source file
      const content = fs.readFileSync(sourcePath, 'utf-8');

      // Process variables in content
      const processedContent = this.processVariables(content);

      // Ensure target directory exists
      const targetDir = path.dirname(targetPath);
      if (!fs.existsSync(targetDir)) {
        fs.mkdirSync(targetDir, { recursive: true });
      }

      // Write processed content
      fs.writeFileSync(targetPath, processedContent, 'utf-8');

      processed.processed = true;

      if (this.verbose) {
        console.log(`✅ Processed: ${path.relative(process.cwd(), targetPath)}`);
      }

    } catch (error) {
      processed.skipped = true;
      processed.reason = error instanceof Error ? error.message : String(error);
    }

    return processed;
  }

  private expandVariables(variables: Record<string, string>): Record<string, any> {
    const expanded: Record<string, any> = { ...variables };

    // Add transformed versions of each variable
    for (const [key, value] of Object.entries(variables)) {
      expanded[key] = value;
      expanded[`${key}_kebab`] = this.toKebabCase(value);
      expanded[`${key}_camel`] = this.toCamelCase(value);
      expanded[`${key}_pascal`] = this.toPascalCase(value);
      expanded[`${key}_snake`] = this.toSnakeCase(value);
      expanded[`${key}_upper`] = value.toUpperCase();
      expanded[`${key}_lower`] = value.toLowerCase();
    }

    // Add common derived variables if agent_name is provided
    if (variables.agent_name) {
      const agentName = variables.agent_name;
      expanded.agentName = this.toCamelCase(agentName);
      expanded.AgentName = this.toPascalCase(agentName);
      expanded.AGENT_NAME = this.toSnakeCase(agentName).toUpperCase();
      expanded['agent-name'] = this.toKebabCase(agentName);
    }

    // Add timestamp and date variables
    const now = new Date();
    expanded.timestamp = now.toISOString();
    expanded.date = now.toISOString().split('T')[0];
    expanded.year = now.getFullYear().toString();

    return expanded;
  }

  private processVariables(content: string): string {
    let processed = content;

    // Replace {{variable}} patterns
    const variablePattern = /\{\{([^}]+)\}\}/g;
    processed = processed.replace(variablePattern, (match, variableName) => {
      const trimmed = variableName.trim();

      if (this.variables.hasOwnProperty(trimmed)) {
        return String(this.variables[trimmed]);
      }

      // If variable not found, leave as-is or return empty based on preference
      if (this.verbose) {
        console.warn(`⚠️  Variable not found: ${trimmed}`);
      }
      return match; // Leave unchanged if variable not found
    });

    return processed;
  }

  // String transformation utilities
  private toCamelCase(str: string): string {
    return str
      .replace(/[-_\s]+/g, ' ')
      .split(' ')
      .map((word, index) =>
        index === 0
          ? word.toLowerCase()
          : word.charAt(0).toUpperCase() + word.slice(1).toLowerCase()
      )
      .join('');
  }

  private toPascalCase(str: string): string {
    return str
      .replace(/[-_\s]+/g, ' ')
      .split(' ')
      .map(word => word.charAt(0).toUpperCase() + word.slice(1).toLowerCase())
      .join('');
  }

  private toKebabCase(str: string): string {
    return str
      .replace(/[A-Z]/g, letter => `-${letter.toLowerCase()}`)
      .replace(/[-_\s]+/g, '-')
      .replace(/^-/, '')
      .toLowerCase();
  }

  private toSnakeCase(str: string): string {
    return str
      .replace(/[A-Z]/g, letter => `_${letter.toLowerCase()}`)
      .replace(/[-\s]+/g, '_')
      .replace(/^_/, '')
      .toLowerCase();
  }

  // Utility methods for external use
  public getExpandedVariables(): Record<string, any> {
    return { ...this.variables };
  }

  public previewProcessing(content: string, variables?: Record<string, string>): string {
    if (variables) {
      const tempEngine = new TemplateEngine(variables, this.verbose);
      return tempEngine.processVariables(content);
    }
    return this.processVariables(content);
  }

  public validateVariables(requiredVariables: string[]): { valid: boolean; missing: string[] } {
    const missing = requiredVariables.filter(variable =>
      !this.variables.hasOwnProperty(variable)
    );

    return {
      valid: missing.length === 0,
      missing
    };
  }
}

// Convenience function for quick template processing
export async function processTemplate(
  sourceDir: string,
  targetDir: string,
  variables: Record<string, string>,
  options: Partial<TemplateProcessingOptions> = {}
): Promise<TemplateEngineResult> {
  const templateEngine = new TemplateEngine(variables, options.verbose || false);

  return await templateEngine.processTemplate({
    sourceDir,
    targetDir,
    variables,
    overwrite: options.overwrite || false,
    verbose: options.verbose || false
  });
}

// Utility function to preview variable replacements
export function previewTemplate(
  content: string,
  variables: Record<string, string>
): string {
  const engine = new TemplateEngine(variables);
  return engine.previewProcessing(content);
}