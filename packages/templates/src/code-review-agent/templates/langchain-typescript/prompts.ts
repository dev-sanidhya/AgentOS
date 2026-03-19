export const PROMPTS = {
  MAIN_REVIEW_PROMPT: `You are a senior code reviewer specializing in {language} development.
Analyze the following code thoroughly and provide a comprehensive review.

File: {fileName}
Language: {language}
Configuration:
- Include Security Scan: {includeSecurityScan}
- Include Performance Analysis: {includePerformanceAnalysis}
- Strict Mode: {strictMode}
- Language Specific Rules: {languageSpecific}

Code to review:
\`\`\`{language}
{code}
\`\`\`

Please provide a detailed analysis in the following JSON format:
{{
  "overallScore": <number 1-10>,
  "analysis": {{
    "codeQuality": {{
      "score": <number 1-10>,
      "issues": [
        {{
          "type": "error|warning|suggestion",
          "line": <line_number>,
          "column": <column_number>,
          "severity": "low|medium|high|critical",
          "message": "Issue description",
          "rule": "Rule name or standard",
          "suggestion": "How to fix this issue"
        }}
      ],
      "suggestions": ["List of general suggestions"]
    }},
    "security": {{
      "score": <number 1-10>,
      "vulnerabilities": [
        {{
          "type": "Vulnerability type",
          "severity": "low|medium|high|critical",
          "line": <line_number>,
          "description": "Vulnerability description",
          "cwe": "CWE-XXX",
          "recommendation": "How to fix this vulnerability"
        }}
      ],
      "recommendations": ["Security recommendations"]
    }},
    "performance": {{
      "score": <number 1-10>,
      "bottlenecks": [
        {{
          "type": "Performance issue type",
          "line": <line_number>,
          "impact": "low|medium|high",
          "description": "Performance issue description",
          "suggestion": "How to optimize"
        }}
      ],
      "optimizations": ["Performance optimization suggestions"]
    }},
    "maintainability": {{
      "score": <number 1-10>,
      "complexity": <cyclomatic_complexity>,
      "codeSmells": ["List of code smells"],
      "refactoringTips": ["Refactoring suggestions"]
    }}
  }},
  "summary": "Brief summary of the code quality and main issues",
  "detailedFeedback": ["Detailed feedback points"]
}}

Focus on:
1. Code structure and organization
2. Best practices adherence
3. Security vulnerabilities
4. Performance implications
5. Maintainability and readability
6. Error handling
7. Type safety (for TypeScript)
8. Testing considerations`,

  SECURITY_SCAN_PROMPT: `Perform a comprehensive security analysis of the following {language} code.
Look for common vulnerabilities and security anti-patterns.

Code:
\`\`\`{language}
{code}
\`\`\`

Focus on these security categories:
1. Injection vulnerabilities (SQL, NoSQL, Command, etc.)
2. Cross-Site Scripting (XSS)
3. Authentication and session management
4. Cryptographic issues
5. Input validation
6. Secret exposure
7. Access control
8. Error handling and information disclosure

Return your findings as a JSON array of vulnerabilities:
[
  {{
    "type": "Vulnerability type",
    "severity": "low|medium|high|critical",
    "line": <line_number>,
    "description": "Detailed description",
    "cwe": "CWE identifier",
    "recommendation": "How to fix",
    "references": ["Additional resources"]
  }}
]

Be thorough but avoid false positives. Only report actual security concerns.`,

  BEST_PRACTICES_PROMPT: `Validate the following {language} code against industry best practices and coding standards.
{framework ? `Framework: ${framework}` : ''}

Code:
\`\`\`{language}
{code}
\`\`\`

Check for:
1. Naming conventions
2. Code organization and structure
3. Documentation and comments
4. Error handling
5. Resource management
6. Design patterns usage
7. SOLID principles adherence
8. Framework-specific best practices
9. Testing considerations
10. Performance best practices

Return findings as a JSON array:
[
  {{
    "type": "error|warning|suggestion",
    "line": <line_number>,
    "severity": "low|medium|high|critical",
    "message": "Issue description",
    "rule": "Best practice rule",
    "suggestion": "Improvement suggestion"
  }}
]

Consider the specific language and framework conventions.`,

  COMPLEXITY_ANALYSIS_PROMPT: `Analyze the complexity of the following {language} code.

Code:
\`\`\`{language}
{code}
\`\`\`

Provide analysis for:
1. Cyclomatic complexity
2. Cognitive complexity
3. Nesting levels
4. Function/method length
5. Parameter counts
6. Code duplication

Return analysis in JSON format:
{{
  "cyclomaticComplexity": <number>,
  "cognitiveComplexity": <number>,
  "maxNestingLevel": <number>,
  "averageFunctionLength": <number>,
  "complexityScore": <number 1-10>,
  "recommendations": ["Complexity reduction suggestions"]
}}

Suggest specific refactoring strategies to reduce complexity.`,

  PERFORMANCE_ANALYSIS_PROMPT: `Analyze the performance characteristics of the following {language} code.

Code:
\`\`\`{language}
{code}
\`\`\`

Look for:
1. Algorithmic complexity issues
2. Memory usage patterns
3. I/O operations efficiency
4. Database query optimization
5. Caching opportunities
6. Async/await usage
7. Loop optimization
8. Resource allocation

Return analysis in JSON format:
{{
  "performanceScore": <number 1-10>,
  "bottlenecks": [
    {{
      "type": "Bottleneck type",
      "line": <line_number>,
      "severity": "low|medium|high",
      "description": "Performance issue",
      "suggestion": "Optimization suggestion"
    }}
  ],
  "optimizations": ["General optimization suggestions"]
}}

Focus on practical, actionable performance improvements.`,

  TYPESCRIPT_SPECIFIC_PROMPT: `Additional TypeScript-specific analysis for the code:

Code:
\`\`\`typescript
{code}
\`\`\`

Check for:
1. Type safety and annotations
2. Interface and type definitions
3. Generic usage
4. Enum usage
5. Union and intersection types
6. Strict mode compliance
7. Declaration file considerations
8. Compiler configuration adherence

Provide TypeScript-specific feedback focusing on type safety and modern TypeScript features.`,

  JAVASCRIPT_SPECIFIC_PROMPT: `Additional JavaScript-specific analysis for the code:

Code:
\`\`\`javascript
{code}
\`\`\`

Check for:
1. ES6+ feature usage
2. Async/await vs Promises
3. Module system usage
4. Variable declarations (var vs let/const)
5. Arrow function usage
6. Destructuring opportunities
7. Template literals usage
8. Modern JavaScript patterns

Focus on modern JavaScript best practices and ES6+ features.`,

  PYTHON_SPECIFIC_PROMPT: `Additional Python-specific analysis for the code:

Code:
\`\`\`python
{code}
\`\`\`

Check for:
1. PEP 8 compliance
2. Type hints usage
3. Exception handling patterns
4. List comprehensions vs loops
5. Generator usage
6. Context managers
7. Pythonic patterns
8. Import organization

Focus on Pythonic code style and Python best practices.`,

  SUMMARY_PROMPT: `Generate a concise summary of the code review findings:

Analysis Results: {analysisResults}

Provide:
1. Overall assessment (1-2 sentences)
2. Top 3 priority issues to address
3. Overall recommendation (approve/needs changes/reject)
4. Estimated effort to address issues

Keep the summary professional and actionable.`
};

export const LANGUAGE_PROMPTS = {
  typescript: PROMPTS.TYPESCRIPT_SPECIFIC_PROMPT,
  javascript: PROMPTS.JAVASCRIPT_SPECIFIC_PROMPT,
  python: PROMPTS.PYTHON_SPECIFIC_PROMPT,
};

export const SEVERITY_DESCRIPTIONS = {
  critical: 'Critical issues that must be fixed before deployment',
  high: 'High priority issues that should be addressed soon',
  medium: 'Medium priority issues that should be addressed',
  low: 'Low priority issues or suggestions for improvement'
};

export const SCORING_CRITERIA = {
  excellent: { min: 9, description: 'Excellent code quality with minimal issues' },
  good: { min: 7, description: 'Good code quality with minor improvements needed' },
  fair: { min: 5, description: 'Fair code quality with several improvements needed' },
  poor: { min: 3, description: 'Poor code quality with significant issues' },
  critical: { min: 0, description: 'Critical issues that prevent safe deployment' }
};