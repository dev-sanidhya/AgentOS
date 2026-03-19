# {{AgentName}} - Raw Python Code Review Agent

A comprehensive, framework-agnostic code review agent that uses direct LLM API calls and modular tools for in-depth code analysis. Perfect for teams that want minimal dependencies while maintaining maximum control over the review process.

## Features

- **Multi-Language Support**: Python, JavaScript, TypeScript, Java, C++, PHP, and more
- **Comprehensive Analysis**: File metrics, security scanning, and quality assessment
- **Modular Architecture**: Independent tools that can be used separately
- **Direct API Integration**: No wrapper libraries, direct calls to OpenAI and Anthropic
- **Security Focus**: Built-in vulnerability detection and risk assessment
- **Detailed Reporting**: Line-by-line feedback with actionable recommendations
- **Minimal Dependencies**: Only requires `requests` and `python-dotenv`

## Installation

1. **Clone or copy the template files**
2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
3. **Configure API keys** (copy `.env.example` to `.env`):
   ```bash
   cp .env.example .env
   ```
   Edit `.env` and add your API key:
   ```
   OPENAI_API_KEY=sk-your-openai-key-here
   # OR
   ANTHROPIC_API_KEY=sk-ant-your-anthropic-key-here
   ```

## Quick Start

### Basic Usage

```python
from {{agent_name}} import {{AgentName}}

# Create reviewer
reviewer = {{AgentName}}(model="gpt-4", verbose=True)

# Review a single file
result = reviewer.review_file("path/to/your/code.py")
print(f"Quality Score: {result.quality_score}/10")
print(f"Security Score: {result.security_score}/10")
print(result.review)

# Review multiple files
result = reviewer.review_files(["file1.py", "file2.py", "file3.py"])

# Review entire directory
result = reviewer.review_directory("src/", ["*.py", "*.js"])
```

### Quick Functions

```python
from {{agent_name}} import review_file, review_files, security_scan

# Quick file review
review = review_file("code.py", model="gpt-4")

# Quick security scan
security_report = security_scan("code.py")
print(f"Security issues found: {security_report.total_issues}")
```

## Architecture

The agent is built with a modular architecture:

```
{{agent_name}}.py              # Main agent class
tools/
├── __init__.py               # Tools package
├── file_analyzer.py          # File analysis and metrics
├── security_scanner.py       # Security vulnerability detection
└── llm_client.py            # Direct LLM API client
```

### Core Components

#### 1. File Analyzer (`tools.FileAnalyzer`)
- **File metrics calculation**: LOC, complexity, functions, classes
- **Language detection**: Automatic programming language identification
- **Code issue detection**: Style violations, anti-patterns
- **Multi-file discovery**: Intelligent file finding with filters

#### 2. Security Scanner (`tools.SecurityScanner`)
- **Vulnerability detection**: SQL injection, XSS, command injection
- **Crypto analysis**: Weak algorithms, insecure random generation
- **Secret scanning**: Hardcoded passwords, API keys, tokens
- **Language-specific checks**: Python, JavaScript, Java, PHP patterns

#### 3. LLM Client (`tools.LLMClient`)
- **Multi-provider support**: OpenAI and Anthropic APIs
- **Direct HTTP requests**: No wrapper library dependencies
- **Automatic retries**: Robust error handling and rate limiting
- **Cost estimation**: Token usage and cost tracking

## Configuration

### Supported Models

#### OpenAI Models
- `gpt-3.5-turbo` (fast, cost-effective)
- `gpt-4` (high quality, recommended)
- `gpt-4-turbo` (latest, balanced)

#### Anthropic Models
- `claude-3-haiku-20240307` (fast)
- `claude-3-sonnet-20240229` (balanced)
- `claude-3-opus-20240229` (highest quality)

### Custom Configuration

```python
from tools import LLMConfig

config = LLMConfig(
    model="gpt-4",
    temperature=0.3,
    max_tokens=4000,
    max_retries=3
)

reviewer = {{AgentName}}(
    model="gpt-4",
    temperature=0.2,
    verbose=True,
    max_tokens=6000
)
```

## Detailed Usage Examples

### 1. Single File Review

```python
from {{agent_name}} import {{AgentName}}

reviewer = {{AgentName}}(model="gpt-4", verbose=True)
result = reviewer.review_file("example.py")

print(f"File: {result.file_or_files}")
print(f"Language: {result.language}")
print(f"Quality Score: {result.quality_score}/10")
print(f"Security Score: {result.security_score}/10")
print(f"Issues: {result.issues_found}")
print(f"Security Issues: {result.security_issues}")
print(f"Duration: {result.duration:.1f}s")

# Access detailed metrics
if result.file_metrics:
    print(f"Lines of Code: {result.file_metrics.lines_of_code}")
    print(f"Complexity: {result.file_metrics.cyclomatic_complexity}")
    print(f"Functions: {result.file_metrics.function_count}")

# Access security report
if result.security_report:
    print(f"Risk Score: {result.security_report.risk_score}/100")
    for issue in result.security_report.issues:
        print(f"  {issue.severity}: {issue.message}")
```

### 2. Directory Analysis

```python
# Review Python files in src directory
result = reviewer.review_directory(
    directory="src/",
    file_patterns=["*.py"],
    max_files=20
)

# Review all supported files
result = reviewer.review_directory("project/")
```

### 3. Security-Focused Scanning

```python
# Quick security scan
security_report = reviewer.quick_security_scan("app.py")

print(f"Risk Level: {security_report.risk_score}/100")
print(f"Critical Issues: {security_report.critical_issues}")
print(f"High Issues: {security_report.high_issues}")

for issue in security_report.issues:
    print(f"Line {issue.line_number}: {issue.message}")
    print(f"  Recommendation: {issue.recommendation}")
```

### 4. Using Individual Tools

```python
from tools import FileAnalyzer, SecurityScanner, LLMClient

# File analysis only
analyzer = FileAnalyzer()
analysis = analyzer.analyze_file("code.py")
print(f"Metrics: {analysis['metrics']}")

# Security scanning only
scanner = SecurityScanner()
with open("code.py") as f:
    content = f.read()
report = scanner.scan_file("code.py", content, "Python")

# LLM client only
client = LLMClient()
response = client.generate_structured_review(content, "Python", "code.py")
print(response.content)
```

## Review Output Format

The agent provides structured reviews with these sections:

1. **Summary**: Brief overview of the code's purpose
2. **Quality Score**: 1-10 rating with justification
3. **Critical Issues**: Bugs and errors that need immediate attention
4. **Security Concerns**: Vulnerabilities and risky patterns
5. **Performance Issues**: Bottlenecks and inefficiencies
6. **Best Practices**: Adherence to language conventions
7. **Maintainability**: Code readability and documentation
8. **Suggestions**: Specific improvement recommendations
9. **Positive Aspects**: Well-written parts to acknowledge
10. **Overall Recommendation**: Approve/Request Changes/Needs Discussion

### Enhanced Analysis

- **File Metrics**: LOC, complexity, function/class counts
- **Security Analysis**: Risk scores, vulnerability categories
- **Code Issues**: Line-by-line problem identification
- **Cross-File Analysis**: Multi-file dependency and consistency checks

## Supported Languages

The agent supports analysis for:

| Language | Extension | Security Scanning | Metrics |
|----------|-----------|------------------|---------|
| Python | `.py` | ✅ | ✅ |
| JavaScript | `.js` | ✅ | ✅ |
| TypeScript | `.ts` | ✅ | ✅ |
| React | `.jsx`, `.tsx` | ✅ | ✅ |
| Java | `.java` | ✅ | ✅ |
| C/C++ | `.c`, `.cpp` | ⚠️ | ✅ |
| C# | `.cs` | ⚠️ | ✅ |
| PHP | `.php` | ✅ | ✅ |
| Ruby | `.rb` | ⚠️ | ✅ |
| Go | `.go` | ⚠️ | ✅ |
| Others | Various | ⚠️ | ✅ |

✅ = Full support, ⚠️ = Basic support

## Error Handling

The agent includes comprehensive error handling:

```python
result = reviewer.review_file("nonexistent.py")
if not result.success:
    print(f"Review failed: {result.error}")
```

Common error scenarios:
- File not found or unreadable
- Unsupported file types
- API key not configured
- Network/API errors
- Large file limitations

## Performance Considerations

- **File Size Limit**: 1MB per file for analysis, 500KB for directory scanning
- **Rate Limiting**: Built-in delays between API calls
- **Token Management**: Automatic content truncation for large files
- **Batch Processing**: Efficient multi-file analysis

## Security Best Practices

The security scanner detects:

### Critical Issues (Severity: Critical)
- Code injection vulnerabilities (`eval`, `exec`)
- Command injection risks
- Unsafe deserialization
- Hardcoded API keys and secrets

### High Issues (Severity: High)
- SQL injection patterns
- Cross-site scripting (XSS)
- Path traversal vulnerabilities
- Weak authentication mechanisms

### Medium Issues (Severity: Medium)
- Weak cryptographic algorithms
- Insecure random number generation
- Information disclosure risks

### Low Issues (Severity: Low)
- Missing input validation
- Insufficient logging
- Configuration issues

## Troubleshooting

### API Key Issues
```python
# Test API connection
reviewer = {{AgentName}}()
test_result = reviewer.test_connection()
if not test_result['success']:
    print(f"Connection failed: {test_result['error']}")
```

### Checking Available Models
```python
from tools import LLMClient

client = LLMClient()
models = client.get_available_models()
print("Available models:", models)

# Validate API keys
keys = client.validate_api_keys()
print("API keys configured:", keys)
```

### Debug Mode
```python
# Enable verbose logging
reviewer = {{AgentName}}(verbose=True)
```

## Contributing

To extend the agent:

1. **Add Language Support**: Update `FileAnalyzer.supported_extensions`
2. **Security Patterns**: Add patterns to `SecurityScanner`
3. **New Providers**: Extend `LLMClient` with additional APIs
4. **Custom Metrics**: Enhance `FileMetrics` calculation

## License

This code review agent is part of the Sub-Agents Library template system.

---

## Example Output

```
🚀 MyCodeReviewer - Comprehensive Code Review Agent
============================================================

🔗 Testing API connection...
✅ Connected to gpt-4 (response time: 1.2s)

🔍 Starting comprehensive review of: example.py
  📊 Analyzing file structure and metrics...
  🔒 Scanning for security vulnerabilities...
  🤖 Generating AI-powered code review...
✅ Review completed in 8.3s
   Quality Score: 8/10
   Security Score: 9/10
   Issues Found: 3
   Security Issues: 1

============================================================
📋 COMPREHENSIVE CODE REVIEW RESULTS
============================================================
File: example.py
Language: Python
Quality Score: 8/10
Security Score: 9/10
Issues Found: 3
Security Issues: 1
Duration: 8.3s
Success: True

File Metrics:
  Lines of Code: 156
  Functions: 8
  Classes: 2
  Complexity: 12

📝 Detailed Review:
------------------------------------------------------------
## Summary
This Python file implements a data processing utility with file I/O operations and basic error handling...

## Quality Score: 8/10
The code demonstrates good structure and readability with room for improvement in error handling...
```