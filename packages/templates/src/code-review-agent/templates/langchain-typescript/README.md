# {{AgentName}} - LangChain TypeScript Code Review Agent

A comprehensive code review agent built with LangChain TypeScript that provides automated code analysis, security scanning, and quality assessment for multiple programming languages.

## Features

- **🔍 Comprehensive Code Analysis**: Analyzes code quality, structure, and maintainability
- **🔒 Security Vulnerability Detection**: Identifies common security issues and vulnerabilities
- **⚡ Performance Analysis**: Detects performance bottlenecks and optimization opportunities
- **📏 Complexity Metrics**: Calculates cyclomatic and cognitive complexity
- **🎯 Best Practices Validation**: Validates code against industry standards
- **🌐 Multi-Language Support**: Supports JavaScript, TypeScript, Python, Java, and more
- **🤖 Multiple AI Providers**: Works with OpenAI and Anthropic models
- **📊 Detailed Scoring**: Provides 1-10 scoring with detailed explanations
- **📋 Compliance Mapping**: Maps findings to OWASP and CWE standards

## Prerequisites

- Node.js 18.0.0 or higher
- npm or yarn
- API key for OpenAI or Anthropic

## Installation

1. **Clone or download the template**
2. **Install dependencies:**
   ```bash
   npm install
   ```

3. **Set up environment variables:**
   ```bash
   cp .env.example .env
   ```
   Edit `.env` with your API keys and configuration.

4. **Build the project:**
   ```bash
   npm run build
   ```

## Configuration

### Environment Variables

```env
# Choose your AI provider
OPENAI_API_KEY=sk-your-openai-api-key-here
ANTHROPIC_API_KEY=your-anthropic-api-key-here
DEFAULT_MODEL_PROVIDER=openai

# Model Configuration
OPENAI_MODEL=gpt-4
ANTHROPIC_MODEL=claude-3-sonnet-20240229

# Review Settings
INCLUDE_SECURITY_SCAN=true
INCLUDE_PERFORMANCE_ANALYSIS=true
STRICT_MODE=false
LANGUAGE_SPECIFIC_RULES=true
```

### Model Configuration

```typescript
const modelConfig: ModelConfig = {
  provider: 'openai', // or 'anthropic'
  model: 'gpt-4',
  temperature: 0.1,
  maxTokens: 4000,
};
```

### Review Configuration

```typescript
const reviewConfig: ReviewConfig = {
  includeSecurityScan: true,
  includePerformanceAnalysis: true,
  strictMode: false,
  languageSpecific: true,
  customRules: ['no-console', 'prefer-const']
};
```

## Usage

### Basic Code Review

```typescript
import { {{AgentName}} } from './{{agent_name}}.js';

const agent = new {{AgentName}}(modelConfig, reviewConfig);

const code = `
function calculateTotal(items) {
  let total = 0;
  for (let i = 0; i < items.length; i++) {
    total += items[i].price;
  }
  return total;
}
`;

const result = await agent.reviewCode(code, 'calculator.js', 'javascript');

console.log('Overall Score:', result.overallScore);
console.log('Issues Found:', result.analysis.codeQuality.issues.length);
console.log('Summary:', result.summary);
```

### Security Scanning

```typescript
// Quick security scan
const vulnerabilities = await agent.quickSecurityScan(code, 'javascript');

console.log(`Found ${vulnerabilities.length} security issues:`);
vulnerabilities.forEach(vuln => {
  console.log(`- ${vuln.type} (${vuln.severity}): ${vuln.description}`);
});
```

### Best Practices Validation

```typescript
const issues = await agent.validateBestPractices(code, 'javascript', 'react');

issues.forEach(issue => {
  console.log(`Line ${issue.line}: ${issue.message}`);
  console.log(`Suggestion: ${issue.suggestion}`);
});
```

### Multiple File Review

```typescript
const files = [
  { code: jsCode, fileName: 'utils.js', language: 'javascript' },
  { code: pyCode, fileName: 'api.py', language: 'python' },
  { code: tsCode, fileName: 'service.ts', language: 'typescript' }
];

const results = await agent.reviewMultipleFiles(files);

results.forEach((result, fileName) => {
  console.log(`${fileName}: Score ${result.overallScore}/10`);
});
```

## API Reference

### {{AgentName}} Class

#### Constructor

```typescript
constructor(modelConfig: ModelConfig, reviewConfig?: ReviewConfig)
```

#### Methods

##### `reviewCode(code: string, fileName: string, language: string): Promise<CodeReviewResult>`

Performs comprehensive code review including quality, security, and performance analysis.

##### `quickSecurityScan(code: string, language: string): Promise<SecurityVulnerability[]>`

Performs rapid security vulnerability scanning.

##### `getQualityScore(code: string, language: string): Promise<number>`

Returns overall quality score (1-10).

##### `validateBestPractices(code: string, language: string, framework?: string): Promise<CodeIssue[]>`

Validates code against best practices and coding standards.

##### `reviewMultipleFiles(files: FileInput[]): Promise<Map<string, CodeReviewResult>>`

Reviews multiple files in batch.

##### `updateConfig(newConfig: Partial<ReviewConfig>): void`

Updates review configuration.

##### `getConfig(): ReviewConfig`

Gets current configuration.

### Types

#### CodeReviewResult

```typescript
interface CodeReviewResult {
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
```

#### SecurityVulnerability

```typescript
interface SecurityVulnerability {
  type: string;
  severity: 'low' | 'medium' | 'high' | 'critical';
  line: number;
  description: string;
  cwe?: string;
  recommendation: string;
}
```

#### CodeIssue

```typescript
interface CodeIssue {
  type: 'error' | 'warning' | 'suggestion';
  line: number;
  column?: number;
  severity: 'low' | 'medium' | 'high' | 'critical';
  message: string;
  rule?: string;
  suggestion?: string;
}
```

## Supported Languages

- **JavaScript** - ES6+, Node.js, React, Vue, Angular
- **TypeScript** - All TypeScript features, strict mode
- **Python** - PEP 8, type hints, frameworks
- **Java** - Modern Java, Spring Boot, Android
- **Go** - Idiomatic Go patterns
- **Rust** - Safe Rust practices
- **C#** - .NET Core, frameworks
- **C++** - Modern C++ standards

## Security Checks

The agent performs comprehensive security analysis including:

### OWASP Top 10 (2021)

- A01:2021 – Broken Access Control
- A02:2021 – Cryptographic Failures
- A03:2021 – Injection
- A04:2021 – Insecure Design
- A05:2021 – Security Misconfiguration
- A06:2021 – Vulnerable Components
- A07:2021 – Authentication Failures
- A08:2021 – Software and Data Integrity Failures
- A09:2021 – Security Logging Monitoring Failures
- A10:2021 – Server-Side Request Forgery

### Common Vulnerability Types

- SQL Injection (CWE-89)
- Cross-Site Scripting (CWE-79)
- Command Injection (CWE-78)
- Path Traversal (CWE-22)
- Weak Cryptography (CWE-326)
- Hard-coded Secrets (CWE-798)
- Buffer Overflow (CWE-120)
- Race Conditions (CWE-362)

## Quality Metrics

### Code Quality Scoring

- **9-10**: Excellent - Production ready with minimal issues
- **7-8**: Good - Minor improvements needed
- **5-6**: Fair - Several improvements required
- **3-4**: Poor - Significant issues present
- **1-2**: Critical - Major problems, not deployment ready

### Complexity Analysis

- **Cyclomatic Complexity**: Control flow complexity measurement
- **Cognitive Complexity**: Human comprehension difficulty
- **Nesting Levels**: Code structure depth analysis
- **Function Length**: Method size evaluation
- **Maintainability Index**: Overall maintainability score

## Examples

Run the example script to see the agent in action:

```bash
npm run dev example.ts
```

This will demonstrate:
- Basic code review
- Security scanning
- Best practices validation
- Multi-file analysis
- Error handling
- Configuration management

## Development

### Building

```bash
npm run build
```

### Testing

```bash
npm test
```

### Linting

```bash
npm run lint
npm run lint:fix
```

### Type Checking

```bash
npm run type-check
```

## Error Handling

The agent includes comprehensive error handling:

```typescript
try {
  const result = await agent.reviewCode(code, fileName, language);
  // Handle successful review
} catch (error) {
  console.error('Review failed:', error.message);
  // Handle error appropriately
}
```

Common error scenarios:
- Invalid API keys
- Unsupported file types
- Rate limit exceeded
- Network connectivity issues
- Malformed code input

## Performance Considerations

- **Rate Limiting**: Respects API provider rate limits
- **Batch Processing**: Efficiently handles multiple files
- **Caching**: Implements intelligent caching for repeated analyses
- **Timeout Handling**: Configurable timeouts for long-running analyses
- **Memory Management**: Optimized for large codebases

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Run linting and tests
6. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For issues and questions:
1. Check the documentation
2. Review existing issues
3. Create a new issue with detailed information

## Changelog

### v1.0.0
- Initial release
- LangChain TypeScript integration
- OpenAI and Anthropic support
- Multi-language code analysis
- Security vulnerability detection
- Performance analysis
- Best practices validation
- Comprehensive documentation

## Roadmap

- [ ] Additional AI provider support (Cohere, HuggingFace)
- [ ] Custom rule engine
- [ ] IDE integrations (VS Code, JetBrains)
- [ ] CI/CD pipeline integration
- [ ] Web dashboard
- [ ] Team collaboration features
- [ ] Advanced reporting formats
- [ ] Machine learning model fine-tuning