# {{AgentName}} - Multi-Agent Code Review System

A comprehensive code review system powered by CrewAI that uses multiple specialized AI agents to analyze code quality, security vulnerabilities, and best practices.

## 🤖 Multi-Agent Architecture

This system employs three specialized agents working together:

- **Code Analyzer Agent**: Analyzes syntax, structure, complexity, and maintainability
- **Security Auditor Agent**: Scans for vulnerabilities and security issues
- **Quality Reviewer Agent**: Reviews best practices and documentation

## ✨ Features

### 🔍 Comprehensive Code Analysis
- **Syntax Analysis**: Validates code syntax and language-specific best practices
- **Complexity Metrics**: Calculates cyclomatic complexity and cognitive load
- **Structure Analysis**: Reviews code organization and architecture
- **Performance Analysis**: Identifies potential performance bottlenecks

### 🔒 Advanced Security Scanning
- **OWASP Top 10**: Detects common web application vulnerabilities
- **Secret Detection**: Finds hard-coded passwords, API keys, and tokens
- **Injection Attacks**: Identifies SQL, command, and code injection vulnerabilities
- **Cryptographic Issues**: Spots weak encryption and hashing practices

### 📊 Quality Assessment
- **Best Practices**: Ensures adherence to coding standards
- **Documentation**: Evaluates comment quality and completeness
- **Maintainability**: Assesses code readability and structure
- **Test Coverage**: Reviews testability and testing practices

### 📈 Intelligent Reporting
- **Multiple Formats**: JSON, HTML, and Markdown reports
- **Severity Scoring**: Prioritizes issues by impact and likelihood
- **Actionable Recommendations**: Provides specific remediation steps
- **Trend Analysis**: Tracks code quality over time

## 🚀 Quick Start

### 1. Installation

```bash
# Clone or copy the template
git clone <your-repo-url>
cd {{agent_name}}

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your API keys
```

### 2. Configuration

Edit your `.env` file with the required API keys:

```env
# OpenAI (recommended)
OPENAI_API_KEY=your_openai_api_key_here

# Or Anthropic Claude
ANTHROPIC_API_KEY=your_anthropic_api_key_here
```

### 3. Basic Usage

```python
from {{agent_name}} import {{AgentName}}

# Initialize the agent
agent = {{AgentName}}(
    model_provider="openai",
    model_name="gpt-4o"
)

# Review a single file
result = agent.review_code("path/to/your/file.py")

# Review an entire directory
directory_result = agent.review_directory("path/to/project")

# Generate reports
html_report = agent.generate_report("html")
with open("code_review_report.html", "w") as f:
    f.write(html_report)
```

## 📖 Detailed Usage

### Single File Review

```python
from {{agent_name}} import {{AgentName}}

agent = {{AgentName}}()

# Comprehensive review
result = agent.review_code(
    file_path="src/main.py",
    include_security=True,
    include_quality=True
)

print(f"Overall score: {result['summary']['overall_score']}/10")
```

### Directory Review

```python
# Review multiple files
result = agent.review_directory(
    directory_path="src/",
    file_patterns=["*.py", "*.js", "*.ts"],
    recursive=True
)

print(f"Files reviewed: {result['files_reviewed']}")
```

### Custom Configuration

```python
agent = {{AgentName}}(
    model_provider="anthropic",
    model_name="claude-3-5-sonnet-20241022",
    temperature=0.1,
    max_tokens=6000
)

# Access individual agents for customization
print(agent.code_analyzer_agent.role)
print(agent.security_auditor_agent.goal)
```

### Direct Tool Usage

```python
from tools import FileAnalyzer, SecurityScanner

# Use tools independently
file_analyzer = FileAnalyzer()
analysis = file_analyzer._run("file.py", "full", True)

security_scanner = SecurityScanner()
security_report = security_scanner._run("file.py", "comprehensive", "medium")
```

## 🛠️ Tool Details

### FileAnalyzer Tool

Comprehensive code analysis including:
- Syntax validation
- Complexity calculations
- Structure assessment
- Metrics generation

```python
analyzer = FileAnalyzer()
result = analyzer._run(
    file_path="code.py",
    analysis_type="full",  # "syntax", "complexity", "structure", "full"
    include_metrics=True
)
```

### SecurityScanner Tool

Advanced security vulnerability detection:
- Vulnerability scanning
- Secret detection
- Dependency analysis
- Cryptographic review

```python
scanner = SecurityScanner()
result = scanner._run(
    file_path="code.py",
    scan_type="comprehensive",  # "vulnerabilities", "secrets", "dependencies", "comprehensive"
    severity_threshold="medium"  # "low", "medium", "high", "critical"
)
```

## 📋 Supported Languages

- **Python** (.py) - Full support with AST analysis
- **JavaScript** (.js) - Comprehensive pattern matching
- **TypeScript** (.ts) - Enhanced JS analysis
- **Java** (.java) - Basic analysis
- **C/C++** (.c, .cpp) - Basic analysis
- **Go** (.go) - Basic analysis
- **Rust** (.rs) - Basic analysis
- **Ruby** (.rb) - Basic analysis
- **PHP** (.php) - Basic analysis

## 🔧 Configuration Options

### Environment Variables

Key configuration options in `.env`:

```env
# LLM Configuration
DEFAULT_LLM_PROVIDER=openai
LLM_TEMPERATURE=0.1
LLM_MAX_TOKENS=4000

# Analysis Settings
DEFAULT_SCAN_TYPE=comprehensive
DEFAULT_SEVERITY_THRESHOLD=medium
COMPLEXITY_THRESHOLD_HIGH=10

# Performance Settings
MAX_CONCURRENT_FILES=5
ENABLE_PARALLEL_PROCESSING=true

# Output Settings
DEFAULT_REPORT_FORMAT=json
REPORTS_OUTPUT_DIR=./reports
```

### Agent Personalities

Customize agent behavior by modifying their roles and backstories:

```python
agent.code_analyzer_agent.role = "Senior Code Architect"
agent.security_auditor_agent.goal = "Find and fix security vulnerabilities"
```

## 📊 Report Formats

### JSON Report
```python
json_report = agent.generate_report("json")
```
- Structured data format
- Easy integration with other tools
- Complete analysis details

### HTML Report
```python
html_report = agent.generate_report("html")
```
- Visual presentation
- Interactive elements
- Styled output

### Markdown Report
```python
markdown_report = agent.generate_report("markdown")
```
- Documentation-friendly
- Version control compatible
- Easy to read

## 🚀 Advanced Usage

### Batch Processing

```python
import os
from pathlib import Path

agent = {{AgentName}}()

# Process multiple projects
projects = ["project1", "project2", "project3"]

for project in projects:
    if Path(project).exists():
        result = agent.review_directory(project)
        agent.save_report(f"{project}_review.html", "html")
```

### Custom Security Rules

```python
# Extend security scanner with custom patterns
from tools.security_scanner import SecurityScanner

scanner = SecurityScanner()

# Add custom vulnerability patterns
custom_patterns = {
    "custom_vuln": {
        "patterns": [r"dangerous_function\s*\("],
        "severity": "high",
        "title": "Custom Vulnerability"
    }
}

scanner.vulnerability_patterns.update(custom_patterns)
```

### Integration with CI/CD

```bash
#!/bin/bash
# ci-code-review.sh

python3 -c "
from {{agent_name}} import {{AgentName}}
agent = {{AgentName}}()
result = agent.review_directory('.')
agent.save_report('ci_review.json', 'json')

# Exit with error if critical issues found
import json
with open('ci_review.json') as f:
    data = json.load(f)

critical_count = 0
for file_result in data.values():
    if isinstance(file_result, dict) and 'analysis' in file_result:
        # Count critical issues
        pass

exit(1 if critical_count > 0 else 0)
"
```

## 🔍 Example Output

### Analysis Summary
```
OVERALL SCORE: 6.5/10
Risk Level: Medium
Findings: 12 issues found

SEVERITY BREAKDOWN:
  Critical: 1
  High: 3
  Medium: 5
  Low: 3

TOP ISSUES:
  1. SQL Injection vulnerability (Line 45)
  2. Hard-coded API key (Line 12)
  3. High cyclomatic complexity (Lines 78-95)
```

### Security Finding
```
[HIGH] Potential SQL Injection
  Line 23: query = f"SELECT * FROM users WHERE id = {user_id}"
  Description: Dynamic SQL construction without parameterization
  Recommendation: Use parameterized queries or prepared statements
  CWE: CWE-89
```

## 🎯 Best Practices

### 1. Configuration
- Use environment variables for sensitive data
- Set appropriate temperature (0.1-0.3 for consistency)
- Configure severity thresholds based on project needs

### 2. Performance
- Use parallel processing for large codebases
- Implement file size limits to avoid memory issues
- Cache results for repeated analysis

### 3. Security
- Never commit API keys to version control
- Rotate API keys regularly
- Use the lowest required permissions

### 4. Integration
- Integrate with your CI/CD pipeline
- Set up automated reports
- Track metrics over time

## 🔧 Troubleshooting

### Common Issues

**API Key Errors**
```
Error: Invalid API key
```
Solution: Check your `.env` file and ensure API keys are correctly set.

**Memory Issues**
```
Error: File too large to process
```
Solution: Adjust `MAX_FILE_SIZE_MB` in your configuration or split large files.

**Rate Limiting**
```
Error: Rate limit exceeded
```
Solution: Implement delays between requests or use a different model provider.

### Debug Mode

Enable debug mode for detailed logging:

```env
DEBUG_MODE=true
LOG_LEVEL=DEBUG
ENABLE_DETAILED_LOGGING=true
```

## 🤝 Contributing

### Adding New Tools

1. Create a new tool in the `tools/` directory
2. Inherit from `BaseTool` class
3. Implement the `_run` method
4. Add to `tools/__init__.py`

Example:
```python
from crewai.tools import BaseTool

class CustomTool(BaseTool):
    name = "custom_tool"
    description = "Description of what the tool does"

    def _run(self, parameter: str) -> str:
        # Implementation
        return "result"
```

### Extending Agent Capabilities

1. Modify agent roles and goals
2. Add new tools to agent tool lists
3. Create custom task templates
4. Implement new analysis types

## 📄 License

This project is licensed under the MIT License. See LICENSE file for details.

## 🙋‍♂️ Support

For issues, questions, or contributions:

1. Check existing documentation
2. Review example usage
3. Create an issue with detailed information
4. Provide code examples and error messages

## 🔗 Related Projects

- [CrewAI](https://github.com/joaomdmoura/crewai) - Multi-agent framework
- [LangChain](https://github.com/hwchase17/langchain) - LLM framework
- [Bandit](https://github.com/PyCQA/bandit) - Python security linter

## 📝 Changelog

### v1.0.0
- Initial release
- Multi-agent code review system
- Support for Python, JavaScript, TypeScript
- Security vulnerability scanning
- Comprehensive reporting

---

**Built with ❤️ using CrewAI and modern AI models**