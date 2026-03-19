import { AgentDefinition, AgentContext } from '@agent-platform/core';
import { readFileTool, listFilesTool } from '../tools/file-tools';

/**
 * Review code files
 */
async function reviewCode(
  codes: Array<{ path: string; content: string }>,
  context: AgentContext
): Promise<
  Array<{
    path: string;
    issues: Array<{ severity: string; type: string; message: string; line?: number }>;
    score: number;
    positives: string[];
  }>
> {
  const reviews = [];

  for (const code of codes) {
    context.emit?.('agent:thinking', {
      message: `Analyzing ${code.path}...`,
    });

    const review = await analyzeCodeFile(code.path, code.content, context);
    reviews.push(review);
  }

  return reviews;
}

/**
 * Analyze a single code file
 */
async function analyzeCodeFile(
  filePath: string,
  content: string,
  context: AgentContext
): Promise<{
  path: string;
  issues: Array<{ severity: string; type: string; message: string; line?: number }>;
  score: number;
  positives: string[];
}> {
  const issues: Array<{ severity: string; type: string; message: string; line?: number }> = [];
  const positives: string[] = [];

  const lines = content.split('\n');

  // Code Quality Checks
  // 1. Check for very long functions
  let currentFunction = '';
  let functionStartLine = 0;
  let functionLineCount = 0;

  for (let i = 0; i < lines.length; i++) {
    const line = lines[i];

    // Detect function starts (simple heuristic)
    if (/function\s+\w+|const\s+\w+\s*=.*=>|\w+\s*\(.*\)\s*{/.test(line)) {
      if (functionLineCount > 50) {
        issues.push({
          severity: 'Medium',
          type: 'Code Quality',
          message: `Function is very long (${functionLineCount} lines). Consider breaking it into smaller functions.`,
          line: functionStartLine,
        });
      }
      currentFunction = line.trim();
      functionStartLine = i + 1;
      functionLineCount = 0;
    }

    functionLineCount++;

    // 2. Check for TODO/FIXME comments
    if (/TODO|FIXME|HACK|XXX/.test(line)) {
      issues.push({
        severity: 'Low',
        type: 'Technical Debt',
        message: `Found unresolved comment: ${line.trim()}`,
        line: i + 1,
      });
    }

    // 3. Check for console.log (in production code)
    if (/console\.(log|warn|error|debug)/.test(line) && !line.includes('//')) {
      issues.push({
        severity: 'Low',
        type: 'Code Quality',
        message: 'Debug console statement should be removed before production',
        line: i + 1,
      });
    }

    // 4. Check for potential security issues
    if (/eval\(|innerHTML|dangerouslySetInnerHTML/.test(line)) {
      issues.push({
        severity: 'Critical',
        type: 'Security',
        message: 'Potential XSS vulnerability detected. Avoid using eval() or dangerouslySetInnerHTML',
        line: i + 1,
      });
    }

    // 5. Check for hardcoded credentials
    if (/(password|api_key|secret|token)\s*=\s*['"][^'"]+['"]/.test(line.toLowerCase())) {
      issues.push({
        severity: 'Critical',
        type: 'Security',
        message: 'Potential hardcoded credential detected. Use environment variables instead.',
        line: i + 1,
      });
    }

    // 6. Check for empty catch blocks
    if (/catch\s*\(.*\)\s*{\s*}/.test(line)) {
      issues.push({
        severity: 'High',
        type: 'Error Handling',
        message: 'Empty catch block. Always handle errors appropriately.',
        line: i + 1,
      });
    }
  }

  // Positive observations
  if (content.includes('test(') || content.includes('describe(') || content.includes('it(')) {
    positives.push('Contains test cases - good test coverage');
  }

  if (content.includes('async') && content.includes('await')) {
    positives.push('Uses modern async/await syntax');
  }

  if (content.includes('interface ') || content.includes('type ')) {
    positives.push('Uses TypeScript types for better type safety');
  }

  if (/\/\*\*[\s\S]*?\*\//.test(content)) {
    positives.push('Includes JSDoc/documentation comments');
  }

  // Calculate score (1-10)
  let score = 10;
  score -= issues.filter(i => i.severity === 'Critical').length * 2;
  score -= issues.filter(i => i.severity === 'High').length * 1;
  score -= issues.filter(i => i.severity === 'Medium').length * 0.5;
  score = Math.max(1, Math.min(10, score));

  return {
    path: filePath,
    issues,
    score: Math.round(score * 10) / 10,
    positives,
  };
}

/**
 * Generate comprehensive review report
 */
function generateReport(
  reviews: Array<{
    path: string;
    issues: Array<{ severity: string; type: string; message: string; line?: number }>;
    score: number;
    positives: string[];
  }>,
  totalFiles: number
): string {
  let report = `# Code Review Report\n\n`;

  // Summary
  const avgScore = reviews.reduce((sum, r) => sum + r.score, 0) / reviews.length;
  const totalIssues = reviews.reduce((sum, r) => sum + r.issues.length, 0);
  const criticalIssues = reviews.reduce(
    (sum, r) => sum + r.issues.filter(i => i.severity === 'Critical').length,
    0
  );

  report += `## Summary\n\n`;
  report += `- **Files Reviewed**: ${totalFiles}\n`;
  report += `- **Overall Quality Score**: ${avgScore.toFixed(1)}/10\n`;
  report += `- **Total Issues Found**: ${totalIssues}\n`;
  report += `- **Critical Issues**: ${criticalIssues}\n\n`;

  // File-by-file reviews
  for (const review of reviews) {
    report += `## File: \`${review.path}\`\n\n`;
    report += `**Quality Score**: ${review.score}/10\n\n`;

    // Critical Issues
    const critical = review.issues.filter(i => i.severity === 'Critical');
    if (critical.length > 0) {
      report += `### 🚨 Critical Issues\n\n`;
      for (const issue of critical) {
        report += `- **[${issue.type}]** `;
        if (issue.line) report += `Line ${issue.line}: `;
        report += `${issue.message}\n`;
      }
      report += `\n`;
    }

    // High/Medium Issues
    const important = review.issues.filter(
      i => i.severity === 'High' || i.severity === 'Medium'
    );
    if (important.length > 0) {
      report += `### ⚠️ Improvements Needed\n\n`;
      for (const issue of important) {
        report += `- **[${issue.type}]** `;
        if (issue.line) report += `Line ${issue.line}: `;
        report += `${issue.message}\n`;
      }
      report += `\n`;
    }

    // Positive Observations
    if (review.positives.length > 0) {
      report += `### ✅ Positive Observations\n\n`;
      for (const positive of review.positives) {
        report += `- ${positive}\n`;
      }
      report += `\n`;
    }

    report += `---\n\n`;
  }

  // Recommendations
  report += `## 📋 Recommendations\n\n`;

  if (criticalIssues > 0) {
    report += `1. **Address Critical Issues Immediately**: Focus on security vulnerabilities and bugs first\n`;
  }

  report += `2. **Code Quality**: ${
    avgScore >= 8
      ? 'Maintain current high standards'
      : avgScore >= 6
        ? 'Good foundation, focus on refactoring long functions'
        : 'Consider comprehensive refactoring'
  }\n`;
  report += `3. **Testing**: ${
    reviews.some(r => r.positives.some(p => p.includes('test')))
      ? 'Good test coverage, keep it up'
      : 'Add unit tests for better reliability'
  }\n`;
  report += `4. **Documentation**: Add comments for complex logic and maintain JSDoc for public APIs\n\n`;

  report += `---\n`;
  report += `*Review conducted by Agent Platform Code Review Agent*\n`;

  return report;
}

/**
 * Code Review Agent
 *
 * A comprehensive code reviewer that can:
 * - Analyze code quality and structure
 * - Identify bugs and potential issues
 * - Suggest improvements and best practices
 * - Check for security vulnerabilities
 * - Review coding standards compliance
 *
 * Best for: Pull request reviews, code quality audits, mentoring
 */
const codeReviewAgent: AgentDefinition = {
  name: 'code-review-agent',
  version: '1.0.0',
  description: 'AI-powered code reviewer that analyzes code quality, security, and best practices',
  author: 'Agent Platform',
  tags: ['code-review', 'quality', 'security', 'best-practices'],

  systemPrompt: `You are an expert code reviewer with deep knowledge of software engineering best practices, design patterns, and security.

Your Review Process:
1. **Code Quality**: Assess readability, maintainability, and structure
2. **Logic & Correctness**: Identify bugs, edge cases, and logical errors
3. **Performance**: Spot inefficiencies and optimization opportunities
4. **Security**: Flag potential vulnerabilities and unsafe practices
5. **Best Practices**: Check adherence to language-specific conventions
6. **Testing**: Evaluate test coverage and quality

Review Principles:
- Be constructive and educational
- Explain WHY something is an issue
- Suggest specific improvements with examples
- Prioritize issues (Critical, High, Medium, Low)
- Acknowledge good code patterns
- Consider context and trade-offs

Output Format:
## Summary
- Brief overview of the code
- Overall quality assessment (1-10)

## Critical Issues
- Security vulnerabilities
- Bugs that could cause failures

## Improvements
- Code quality suggestions
- Performance optimizations
- Best practice recommendations

## Positive Observations
- Well-implemented patterns
- Good practices to highlight

## Recommendations
- Actionable next steps
- Resources for improvement`,

  tools: ['read-file', 'list-files'],

  config: {
    model: 'claude-sonnet-4',
    provider: 'anthropic',
    temperature: 0.3, // Lower temperature for more consistent, focused reviews
    maxTokens: 4000,
  },

  async onInit(context: AgentContext) {
    // Register file tools
    if (!context.tools.has('read-file')) {
      context.tools.set('read-file', readFileTool);
    }
    if (!context.tools.has('list-files')) {
      context.tools.set('list-files', listFilesTool);
    }
  },

  async execute(input: string, context: AgentContext): Promise<string> {
    try {
      context.emit?.('agent:thinking', {
        message: 'Analyzing request...',
      });

      // Determine if input is a file path or directory
      const target = input.trim();

      let codesToReview: Array<{ path: string; content: string }> = [];

      // Try to read as a file first
      const readTool = context.tools.get('read-file');
      const listTool = context.tools.get('list-files');

      if (!readTool) {
        throw new Error('File reading tools not available');
      }

      try {
        context.emit?.('agent:thinking', {
          message: `Reading ${target}...`,
        });

        const fileContent = await readTool.execute({ filePath: target }, context);
        codesToReview.push({
          path: target,
          content: fileContent.content,
        });
      } catch (error) {
        // If reading as file fails, try as directory
        if (listTool) {
          try {
            const fileList = await listTool.execute(
              {
                dirPath: target,
                recursive: true,
                pattern: '\\.(ts|js|tsx|jsx|py|java|go|rs)$',
              },
              context
            );

            // Read first few files to avoid overwhelming
            const filesToRead = fileList.files.slice(0, 5);

            for (const filePath of filesToRead) {
              try {
                const content = await readTool.execute({ filePath }, context);
                codesToReview.push({
                  path: filePath,
                  content: content.content,
                });
              } catch (readError) {
                // Skip files that can't be read
                continue;
              }
            }
          } catch (listError) {
            throw new Error(
              `Could not read "${target}" as file or directory. Please provide a valid file path.`
            );
          }
        }
      }

      if (codesToReview.length === 0) {
        return 'No code files found to review. Please provide a valid file path or directory.';
      }

      context.emit?.('agent:thinking', {
        message: `Reviewing ${codesToReview.length} file(s)...`,
      });

      // Perform comprehensive review
      const reviews = await reviewCode(codesToReview, context);

      // Generate final report
      return generateReport(reviews, codesToReview.length);
    } catch (error) {
      context.emit?.('agent:error', {
        message: `Code review failed: ${error}`,
      });

      return `I encountered an error during code review: ${error}\n\nPlease check the file path and try again.`;
    }
  },
};

export default codeReviewAgent;
