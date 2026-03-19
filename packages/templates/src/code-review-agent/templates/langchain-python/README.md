# {{AgentName}} - LangChain Python Implementation

A comprehensive AI-powered code review agent that provides detailed analysis of code quality, security vulnerabilities, performance issues, and best practices adherence with numerical scoring and actionable recommendations.

## 🚀 Features

- 🔍 **Comprehensive Analysis**: Deep code quality, structure, and maintainability assessment
- 🛡️ **Security Scanning**: Advanced vulnerability detection for multiple attack vectors
- 📊 **Quality Scoring**: Detailed numerical assessment (1-10 scale) with breakdown
- 🔧 **Multi-Language Support**: Python, JavaScript, TypeScript, Java, Go, C++, and more
- 🎯 **Specialized Tools**: Dedicated code analyzer and security scanner
- 🗃️ **Flexible Review Types**: Single files, multiple files, directories, or git changes
- 🔧 **Git Integration**: PR reviews and branch difference analysis
- 📝 **Structured Reports**: Detailed output with prioritized findings and recommendations
- ⚡ **Performance Analysis**: Algorithm complexity and optimization suggestions
- 🏗️ **Architecture Review**: Design patterns and structural analysis

## 📦 Installation

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
# Copy the environment template
cp .env.example .env

# Add your API key (choose one)
echo "OPENAI_API_KEY=sk-your-openai-key-here" >> .env
# OR
echo "ANTHROPIC_API_KEY=sk-ant-your-anthropic-key-here" >> .env
```

### 3. Get API Keys

**LLM Provider (Required):**
- [OpenAI API](https://platform.openai.com/api-keys) - For GPT-4 and GPT-3.5 models
- [Anthropic API](https://console.anthropic.com/) - For Claude models

## 🎯 Quick Start

### Simple File Review

```python
from {{agent_name}} import review_file

# Quick review of a single file
result = review_file("src/main.py")
print(f"Quality Score: {result.quality_score}/10")
print(f"Summary: {result.summary}")
```

### Code String Review

```python
from {{agent_name}} import {{AgentName}}

# Review code directly from string
reviewer = {{AgentName}}(model_provider="openai")

result = reviewer.review_code("""
def login(username, password):
    # SQL injection vulnerability
    query = "SELECT * FROM users WHERE username = '" + username + "'"
    return execute_query(query)
""", language="python")

print(f"Security Issues: {len(result.security_vulnerabilities)}")
for vuln in result.security_vulnerabilities:
    print(f"- [{vuln['severity']}] {vuln['description']}")
```

### Advanced Usage

```python
from {{agent_name}} import {{AgentName}}, CodeReviewResult

# Create reviewer with configuration
reviewer = {{AgentName}}(
    model_provider="openai",     # or "anthropic"
    model_name="gpt-4-turbo-preview",
    temperature=0.1,             # Lower = more consistent
    max_iterations=10,
    verbose=True                 # Show progress
)

# Review a single file
result = reviewer.review_file("src/auth.py")
print(f"Quality Score: {result.quality_score}/10")
print(f"Overall Rating: {result.overall_rating}")
print(f"Issues: {len(result.issues)}")
print(f"Security Vulnerabilities: {len(result.security_vulnerabilities)}")

# Review multiple files
results = reviewer.review_files([
    "src/models.py",
    "src/views.py",
    "tests/test_auth.py"
])

# Generate comprehensive report
report = reviewer.generate_report(results)
print(report)
```

### Run Examples

```bash
python example.py
```

## 📖 API Reference

### {{AgentName}} Class

```python
class {{AgentName}}:
    def __init__(
        self,
        model_provider: str = "openai",      # "openai" or "anthropic"
        model_name: Optional[str] = None,    # Specific model name
        temperature: float = 0.1,            # Response consistency
        max_tokens: int = 4000,              # Maximum response length
        api_key: Optional[str] = None,       # API key (or from env)
        max_iterations: int = 10,            # Tool usage iterations
        verbose: bool = False                # Progress logging
    )

    def review_code(
        self,
        code_content: str,
        file_path: str = "",
        language: Optional[str] = None
    ) -> CodeReviewResult

    def review_file(self, file_path: str) -> CodeReviewResult

    def review_files(self, file_paths: List[str]) -> List[CodeReviewResult]

    def review_directory(
        self,
        directory_path: str,
        file_extensions: Optional[List[str]] = None,
        exclude_patterns: Optional[List[str]] = None
    ) -> List[CodeReviewResult]

    def review_git_changes(self, base_branch: str = "main") -> Dict[str, Any]

    def generate_report(self, results: List[CodeReviewResult]) -> str
```

### CodeReviewResult Class

```python
@dataclass
class CodeReviewResult:
    file_path: str                                    # Path to analyzed file
    language: str                                     # Detected language
    quality_score: int                               # Quality score (1-10)
    issues: List[Dict[str, Any]]                     # Code quality issues
    security_vulnerabilities: List[Dict[str, Any]]   # Security issues found
    best_practices: List[Dict[str, Any]]             # Best practice violations
    performance_suggestions: List[Dict[str, Any]]    # Performance improvements
    summary: str                                     # Analysis summary
    overall_rating: str                              # Rating (Excellent/Good/Fair/Poor/Critical)
```

### Specialized Analysis Tools

```python
# The agent uses these specialized tools internally:
from tools.file_analyzer import CodeAnalyzerTool      # Code quality analysis
from tools.security_scanner import SecurityScannerTool # Security vulnerability detection
```

## 🛡️ Security Analysis

### Vulnerability Detection

The security scanner detects:

- **Injection Attacks**: SQL, NoSQL, Command, LDAP, XML injection
- **XSS Vulnerabilities**: Stored, reflected, and DOM-based XSS
- **Authentication Issues**: Weak auth, session management flaws
- **Cryptographic Problems**: Weak algorithms, key management issues
- **Input Validation**: Missing validation, path traversal
- **Configuration Issues**: Debug mode, insecure defaults

```python
# Security-focused analysis
reviewer = {{AgentName}}(model_provider="openai", temperature=0.05)

result = reviewer.review_code("""
import hashlib
password_hash = hashlib.md5(user_password.encode()).hexdigest()  # Weak hash
query = f"SELECT * FROM users WHERE id = {user_input}"         # SQL injection
""", language="python")

for vuln in result.security_vulnerabilities:
    print(f"[{vuln['severity']}] {vuln['type']}: {vuln['description']}")
    print(f"Recommendation: {vuln['recommendation']}")
```

## 📊 Code Quality Analysis

### Metrics and Scoring

```python
# Quality analysis breakdown
result = reviewer.review_file("complex_module.py")

print(f"Quality Score: {result.quality_score}/10")
print(f"Overall Rating: {result.overall_rating}")

# Detailed metrics (available in agent's internal analysis)
# - Code complexity and maintainability
# - Function/method length analysis
# - Naming convention compliance
# - Documentation coverage
# - Error handling patterns
```

### Language Support

**Fully Supported:**
- Python (.py)
- JavaScript (.js)
- TypeScript (.ts, .tsx)
- Java (.java)
- Go (.go)
- Rust (.rs)
- C/C++ (.c, .cpp, .h, .hpp)
- C# (.cs)
- PHP (.php)

**Basic Support:**
- Ruby (.rb)
- Swift (.swift)
- Kotlin (.kt)
- Scala (.scala)

## 🎯 Review Types

### 1. Single File Review

```python
reviewer = {{AgentName}}()
result = reviewer.review_file("src/payment_processor.py")

print(f"Quality: {result.quality_score}/10")
print(f"Issues: {len(result.issues)}")
print(f"Security: {len(result.security_vulnerabilities)}")
```

### 2. Multiple File Review

```python
results = reviewer.review_files([
    "src/models/user.py",
    "src/controllers/auth.py",
    "tests/test_auth.py"
])

# Get average quality score
avg_score = sum(r.quality_score for r in results) / len(results)
print(f"Average Quality: {avg_score:.1f}/10")
```

### 3. Directory Analysis

```python
results = reviewer.review_directory(
    directory_path="src/",
    file_extensions=['.py', '.js'],
    exclude_patterns=['__pycache__', 'node_modules']
)

# Generate comprehensive report
report = reviewer.generate_report(results)
```

### 4. Git Changes Review

```python
# Review PR changes
git_result = reviewer.review_git_changes(base_branch="main")

if git_result['success']:
    print("Git Review:")
    print(git_result['review'])
```

## 🧠 Analysis Capabilities

### Code Quality Assessment

- **Complexity Analysis**: Cyclomatic complexity, nesting depth
- **Structure Analysis**: Function length, class design, modularity
- **Naming Conventions**: Variable/function naming consistency
- **Documentation**: Comment coverage, docstring quality
- **Error Handling**: Exception handling patterns

### Security Vulnerability Detection

- **Input Validation**: Missing sanitization, injection vulnerabilities
- **Authentication**: Weak auth mechanisms, session management
- **Cryptography**: Weak algorithms, key management issues
- **File Security**: Path traversal, file inclusion vulnerabilities
- **Network Security**: Unencrypted connections, CORS issues

### Performance Analysis

- **Algorithm Efficiency**: Big O complexity analysis
- **Resource Usage**: Memory leaks, CPU intensive operations
- **Database**: Query optimization, N+1 problems
- **Caching**: Inefficient data access patterns

## 🔧 Available Tools

The agent uses specialized analysis tools:

### CodeAnalyzerTool
- Code metrics calculation
- Complexity analysis
- Structure assessment
- Best practices validation
- Maintainability scoring

### SecurityScannerTool
- Vulnerability pattern detection
- Hardcoded secret scanning
- Cryptographic issue detection
- Input validation analysis
- Risk scoring

## 📊 Review Output

### Structured Results

```python
result = reviewer.review_file("example.py")

# Access detailed results
print(f"File: {result.file_path}")
print(f"Language: {result.language}")
print(f"Score: {result.quality_score}/10")
print(f"Rating: {result.overall_rating}")

# Iterate through issues
for issue in result.issues:
    print(f"- {issue['type']}: {issue['description']}")

# Check security vulnerabilities
for vuln in result.security_vulnerabilities:
    severity = vuln['severity']
    description = vuln['description']
    print(f"[{severity}] {description}")
```

### Generated Reports

```python
# Multi-file analysis report
results = reviewer.review_files(["file1.py", "file2.py"])
report = reviewer.generate_report(results)

# Report includes:
# - Executive summary
# - File-by-file breakdown
# - Security vulnerability summary
# - Recommendations and next steps
```

## 🎯 Supported Models

### OpenAI Models
- `gpt-4-turbo-preview` - Latest GPT-4, best overall performance
- `gpt-4` - Most capable for thorough analysis
- `gpt-3.5-turbo` - Fast and cost-effective

### Anthropic Models
- `claude-3-sonnet-20240229` - Balanced performance (default)
- `claude-3-opus-20240229` - Most capable Claude model
- `claude-3-haiku-20240307` - Fastest option

## 🛠️ Advanced Configuration

### Environment Variables

```bash
# Model configuration
DEFAULT_MODEL_PROVIDER=openai
OPENAI_MODEL_NAME=gpt-4-turbo-preview
ANTHROPIC_MODEL_NAME=claude-3-sonnet-20240229

# Analysis settings
AGENT_TEMPERATURE=0.1
AGENT_MAX_TOKENS=4000
QUALITY_SCORE_THRESHOLD=7

# Security scanning
SECURITY_SCAN_ENABLED=true
CHECK_SQL_INJECTION=true
CHECK_XSS_VULNERABILITIES=true
CHECK_HARDCODED_SECRETS=true

# Performance settings
MAX_FILE_SIZE=51200
MAX_CONCURRENT_FILES=5
```

### Custom Analysis Focus

```python
# Security-focused review
security_reviewer = {{AgentName}}(
    model_provider="openai",
    temperature=0.05,  # Very consistent for security
    max_tokens=6000
)

# Performance-focused review
perf_reviewer = {{AgentName}}(
    model_provider="anthropic",
    temperature=0.1
)

# Quick quality check
quick_reviewer = {{AgentName}}(
    model_provider="openai",
    model_name="gpt-3.5-turbo",
    max_iterations=5
)
```

## 📁 Project Structure

```
{{agent_name}}/
├── {{agent_name}}.py           # Main agent implementation
├── tools/
│   ├── __init__.py             # Tool exports and utilities
│   ├── file_analyzer.py        # Code quality analysis tool
│   └── security_scanner.py     # Security vulnerability scanner
├── prompts.py                  # Specialized review prompts
├── example.py                 # Comprehensive usage examples
├── requirements.txt           # Python dependencies
├── .env.example              # Environment configuration template
└── README.md                 # This documentation
```

## 🔧 Troubleshooting

### Common Issues

**"No API key found"**
```bash
# Check your .env file
cat .env | grep API_KEY

# Verify key format
echo $OPENAI_API_KEY  # Should start with sk-
echo $ANTHROPIC_API_KEY  # Should start with sk-ant-
```

**"File too large" warnings**
- Files over 50KB are skipped by default
- Adjust `MAX_FILE_SIZE` in .env for larger files
- Binary files are automatically ignored

**"Git command failed"**
```bash
# Ensure you're in a git repository
git status

# Check branch exists
git branch -a | grep main
```

**Import errors**
```bash
# Reinstall dependencies
pip install -r requirements.txt

# Check Python version (requires 3.8+)
python --version
```

### Performance Optimization

```python
# For faster analysis
reviewer = {{AgentName}}(
    model_provider="openai",
    model_name="gpt-3.5-turbo",
    temperature=0.2,
    max_iterations=5,
    verbose=False
)

# For thorough analysis
reviewer = {{AgentName}}(
    model_provider="openai",
    model_name="gpt-4-turbo-preview",
    temperature=0.1,
    max_iterations=15,
    max_tokens=6000
)
```

## 🏆 Best Practices

### 1. Choose Appropriate Scope

```python
# Single file changes
reviewer.review_file("bug_fix.py")

# Feature development
reviewer.review_files(["models.py", "views.py", "tests.py"])

# Architecture review
reviewer.review_directory("src/")

# PR review
reviewer.review_git_changes("main")
```

### 2. Security-First Approach

```python
# Always check for security issues in sensitive code
security_result = reviewer.review_code(auth_code, language="python")

critical_vulns = [
    v for v in security_result.security_vulnerabilities
    if v.get('severity') in ['CRITICAL', 'HIGH']
]

if critical_vulns:
    print("❌ Critical security issues found - review required")
    for vuln in critical_vulns:
        print(f"- {vuln['description']}")
```

### 3. Quality Gates

```python
def quality_gate(file_path: str, min_score: int = 7) -> bool:
    """Quality gate for CI/CD integration."""
    result = reviewer.review_file(file_path)

    # Check quality score
    if result.quality_score < min_score:
        print(f"Quality score {result.quality_score} below threshold {min_score}")
        return False

    # Check for critical security issues
    critical_issues = [
        v for v in result.security_vulnerabilities
        if v.get('severity') == 'CRITICAL'
    ]

    if critical_issues:
        print(f"Found {len(critical_issues)} critical security issues")
        return False

    return True

# Usage in CI/CD
if not quality_gate("src/payment.py", min_score=8):
    exit(1)  # Fail the build
```

### 4. Integration Examples

**Pre-commit Hook:**
```bash
#!/bin/bash
# .git/hooks/pre-commit
python -c "
from {{agent_name}} import {{AgentName}}
import subprocess
import sys

# Get staged files
result = subprocess.run(['git', 'diff', '--cached', '--name-only', '--diff-filter=AM'],
                       capture_output=True, text=True)
staged_files = [f for f in result.stdout.strip().split('\n') if f.endswith('.py')]

if not staged_files:
    sys.exit(0)

reviewer = {{AgentName}}()
for file_path in staged_files:
    result = reviewer.review_file(file_path)
    if result.quality_score < 6 or len(result.security_vulnerabilities) > 0:
        print(f'❌ {file_path} failed quality check')
        print(f'Score: {result.quality_score}/10')
        print(f'Security issues: {len(result.security_vulnerabilities)}')
        sys.exit(1)

print('✅ All files passed quality check')
"
```

**GitHub Actions:**
```yaml
name: Code Review
on: [pull_request]

jobs:
  review:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: 3.9

    - name: Install dependencies
      run: pip install -r requirements.txt

    - name: Run code review
      env:
        OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
      run: |
        python -c "
        from {{agent_name}} import {{AgentName}}
        import os
        reviewer = {{AgentName}}()
        result = reviewer.review_git_changes('main')
        print(result['review'])
        "
```

## 📚 Advanced Usage Examples

### Custom Analysis Pipeline

```python
def comprehensive_analysis(directory: str):
    """Run comprehensive analysis pipeline."""
    reviewer = {{AgentName}}(model_provider="openai", verbose=True)

    # 1. Directory analysis
    results = reviewer.review_directory(directory)

    # 2. Generate report
    report = reviewer.generate_report(results)

    # 3. Security summary
    all_vulns = []
    for result in results:
        all_vulns.extend(result.security_vulnerabilities)

    critical_vulns = [v for v in all_vulns if v.get('severity') == 'CRITICAL']
    high_vulns = [v for v in all_vulns if v.get('severity') == 'HIGH']

    print(f"Security Summary:")
    print(f"- Critical: {len(critical_vulns)}")
    print(f"- High: {len(high_vulns)}")
    print(f"- Total: {len(all_vulns)}")

    # 4. Quality metrics
    scores = [r.quality_score for r in results]
    avg_score = sum(scores) / len(scores) if scores else 0

    print(f"Quality Summary:")
    print(f"- Average score: {avg_score:.1f}/10")
    print(f"- Files analyzed: {len(results)}")

    return report, results

# Usage
report, results = comprehensive_analysis("src/")
```

## 📄 License

MIT License

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes with comprehensive tests
4. Run quality checks: `python -m {{agent_name}} review src/`
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

## 📚 Learn More

- [LangChain Documentation](https://python.langchain.com/)
- [OpenAI API Documentation](https://platform.openai.com/docs)
- [Anthropic Claude Documentation](https://docs.anthropic.com/)
- [Security Code Review Guide](https://owasp.org/www-project-code-review-guide/)

---

**Elevate your code quality with AI-powered analysis that provides comprehensive security scanning, detailed quality assessment, and actionable recommendations for continuous improvement.**