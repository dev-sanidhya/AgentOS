import { Tool } from '@langchain/core/tools';
import { z } from 'zod';

export interface FileAnalysisResult {
  language: string;
  fileSize: number;
  lineCount: number;
  complexity: number;
  maintainabilityIndex: number;
  codeSmells: string[];
  suggestions: string[];
  metrics: {
    cyclomaticComplexity: number;
    cognitiveComplexity: number;
    linesOfCode: number;
    duplicateLines: number;
    testCoverage?: number;
  };
}

export class FileAnalyzerTool extends Tool {
  name = 'file_analyzer';
  description = 'Analyzes code files for quality metrics, complexity, and maintainability';

  schema = z.object({
    code: z.string().describe('The source code to analyze'),
    fileName: z.string().describe('The name of the file being analyzed'),
    language: z.string().describe('The programming language of the code'),
  });

  async _call(input: z.infer<typeof this.schema>): Promise<string> {
    try {
      const analysis = await this.analyzeFile(input.code, input.fileName, input.language);
      return JSON.stringify(analysis, null, 2);
    } catch (error) {
      return `File analysis failed: ${error instanceof Error ? error.message : String(error)}`;
    }
  }

  private async analyzeFile(code: string, fileName: string, language: string): Promise<FileAnalysisResult> {
    const lines = code.split('\n');
    const lineCount = lines.length;
    const fileSize = Buffer.byteLength(code, 'utf8');

    // Calculate basic metrics
    const cyclomaticComplexity = this.calculateCyclomaticComplexity(code, language);
    const cognitiveComplexity = this.calculateCognitiveComplexity(code, language);
    const duplicateLines = this.findDuplicateLines(lines);
    const codeSmells = this.detectCodeSmells(code, language);
    const maintainabilityIndex = this.calculateMaintainabilityIndex(
      cyclomaticComplexity,
      lineCount,
      duplicateLines
    );

    const suggestions = this.generateSuggestions(
      cyclomaticComplexity,
      cognitiveComplexity,
      codeSmells,
      language
    );

    return {
      language,
      fileSize,
      lineCount,
      complexity: Math.max(cyclomaticComplexity, cognitiveComplexity),
      maintainabilityIndex,
      codeSmells,
      suggestions,
      metrics: {
        cyclomaticComplexity,
        cognitiveComplexity,
        linesOfCode: this.countLinesOfCode(lines),
        duplicateLines,
      },
    };
  }

  private calculateCyclomaticComplexity(code: string, language: string): number {
    // Basic cyclomatic complexity calculation
    let complexity = 1; // Base complexity

    const patterns = this.getComplexityPatterns(language);

    for (const pattern of patterns) {
      const matches = code.match(new RegExp(pattern, 'g'));
      if (matches) {
        complexity += matches.length;
      }
    }

    return complexity;
  }

  private calculateCognitiveComplexity(code: string, language: string): number {
    // Basic cognitive complexity calculation
    let complexity = 0;
    let nestingLevel = 0;

    const lines = code.split('\n');
    const patterns = this.getCognitiveComplexityPatterns(language);

    for (const line of lines) {
      const trimmed = line.trim();

      // Check for nesting increase
      if (this.isNestingIncrease(trimmed, language)) {
        nestingLevel++;
      }

      // Check for nesting decrease
      if (this.isNestingDecrease(trimmed, language)) {
        nestingLevel = Math.max(0, nestingLevel - 1);
      }

      // Check for cognitive complexity patterns
      for (const pattern of patterns) {
        if (new RegExp(pattern).test(trimmed)) {
          complexity += 1 + nestingLevel;
        }
      }
    }

    return complexity;
  }

  private getComplexityPatterns(language: string): string[] {
    const basePatterns = [
      '\\bif\\b', '\\belse\\b', '\\bwhile\\b', '\\bfor\\b',
      '\\bswitch\\b', '\\bcase\\b', '\\bcatch\\b', '\\btry\\b'
    ];

    switch (language.toLowerCase()) {
      case 'javascript':
      case 'typescript':
        return [
          ...basePatterns,
          '\\?.*:', // ternary operator
          '\\|\\||&&', // logical operators
        ];
      case 'python':
        return [
          ...basePatterns.map(p => p.replace('\\b', '\\b')),
          '\\bexcept\\b', '\\bfinally\\b',
        ];
      case 'java':
      case 'c#':
        return [
          ...basePatterns,
          '\\bfinally\\b',
        ];
      default:
        return basePatterns;
    }
  }

  private getCognitiveComplexityPatterns(language: string): string[] {
    switch (language.toLowerCase()) {
      case 'javascript':
      case 'typescript':
        return [
          '\\bif\\b', '\\belse if\\b', '\\bwhile\\b', '\\bfor\\b',
          '\\bswitch\\b', '\\bcatch\\b', '\\?.*:',
          '\\|\\||&&',
        ];
      case 'python':
        return [
          '\\bif\\b', '\\belif\\b', '\\bwhile\\b', '\\bfor\\b',
          '\\bexcept\\b', '\\band\\b', '\\bor\\b',
        ];
      default:
        return [
          '\\bif\\b', '\\belse\\b', '\\bwhile\\b', '\\bfor\\b',
          '\\bswitch\\b', '\\bcatch\\b',
        ];
    }
  }

  private isNestingIncrease(line: string, language: string): boolean {
    const patterns = ['{', '\\bif\\b', '\\bwhile\\b', '\\bfor\\b', '\\btry\\b'];
    return patterns.some(pattern => new RegExp(pattern).test(line));
  }

  private isNestingDecrease(line: string, language: string): boolean {
    return line.includes('}') || line.trim() === '';
  }

  private findDuplicateLines(lines: string[]): number {
    const lineMap = new Map<string, number>();
    let duplicates = 0;

    for (const line of lines) {
      const trimmed = line.trim();
      if (trimmed && !trimmed.startsWith('//') && !trimmed.startsWith('#')) {
        const count = lineMap.get(trimmed) || 0;
        lineMap.set(trimmed, count + 1);
        if (count > 0) {
          duplicates++;
        }
      }
    }

    return duplicates;
  }

  private countLinesOfCode(lines: string[]): number {
    return lines.filter(line => {
      const trimmed = line.trim();
      return trimmed &&
             !trimmed.startsWith('//') &&
             !trimmed.startsWith('#') &&
             !trimmed.startsWith('/*') &&
             !trimmed.startsWith('*') &&
             !trimmed.startsWith('*/');
    }).length;
  }

  private detectCodeSmells(code: string, language: string): string[] {
    const smells: string[] = [];
    const lines = code.split('\n');

    // Long method detection
    if (lines.length > 50) {
      smells.push('Long method detected - consider breaking into smaller functions');
    }

    // Long parameter list
    const longParamPattern = /\([^)]{100,}\)/;
    if (longParamPattern.test(code)) {
      smells.push('Long parameter list - consider using object parameters');
    }

    // Magic numbers
    const magicNumberPattern = /\b(?!0|1|2|10|100|1000)\d{3,}\b/g;
    const magicNumbers = code.match(magicNumberPattern);
    if (magicNumbers && magicNumbers.length > 3) {
      smells.push('Magic numbers detected - consider using named constants');
    }

    // Deep nesting
    let maxNesting = 0;
    let currentNesting = 0;
    for (const line of lines) {
      if (line.includes('{')) currentNesting++;
      if (line.includes('}')) currentNesting--;
      maxNesting = Math.max(maxNesting, currentNesting);
    }
    if (maxNesting > 4) {
      smells.push('Deep nesting detected - consider refactoring to reduce complexity');
    }

    // Language-specific smells
    switch (language.toLowerCase()) {
      case 'javascript':
      case 'typescript':
        if (code.includes('var ')) {
          smells.push('Use of var keyword - prefer let or const');
        }
        if (code.includes('== ') || code.includes('!= ')) {
          smells.push('Non-strict equality operators - use === or !==');
        }
        break;
      case 'python':
        if (code.includes('except:')) {
          smells.push('Bare except clause - specify exception types');
        }
        break;
    }

    return smells;
  }

  private calculateMaintainabilityIndex(
    complexity: number,
    linesOfCode: number,
    duplicateLines: number
  ): number {
    // Simplified maintainability index calculation
    // Real formula: 171 - 5.2 * ln(HalsteadVolume) - 0.23 * CyclomaticComplexity - 16.2 * ln(LinesOfCode)
    // Simplified version for this implementation
    const complexityPenalty = complexity * 2;
    const sizePenalty = Math.log(linesOfCode) * 5;
    const duplicationPenalty = duplicateLines * 0.5;

    const index = Math.max(0, 100 - complexityPenalty - sizePenalty - duplicationPenalty);
    return Math.round(index);
  }

  private generateSuggestions(
    cyclomaticComplexity: number,
    cognitiveComplexity: number,
    codeSmells: string[],
    language: string
  ): string[] {
    const suggestions: string[] = [];

    if (cyclomaticComplexity > 10) {
      suggestions.push('Consider breaking down complex functions into smaller, more focused functions');
    }

    if (cognitiveComplexity > 15) {
      suggestions.push('Reduce cognitive complexity by simplifying control flow and reducing nesting');
    }

    if (codeSmells.length > 0) {
      suggestions.push('Address detected code smells to improve maintainability');
    }

    // Language-specific suggestions
    switch (language.toLowerCase()) {
      case 'javascript':
      case 'typescript':
        suggestions.push('Consider using modern ES6+ features for cleaner code');
        suggestions.push('Add proper error handling and type checking');
        break;
      case 'python':
        suggestions.push('Follow PEP 8 style guidelines');
        suggestions.push('Consider using type hints for better code documentation');
        break;
      case 'java':
        suggestions.push('Consider using design patterns for better code organization');
        suggestions.push('Ensure proper exception handling');
        break;
    }

    return suggestions;
  }
}

export const fileAnalyzer = new FileAnalyzerTool();