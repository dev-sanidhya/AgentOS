#!/usr/bin/env python3
"""
{{AgentName}} Usage Examples

This file demonstrates how to use the {{AgentName}} multi-agent code review system
with various configuration options and use cases.

Author: {{author_name}}
Created: {{creation_date}}
"""

import os
import sys
import json
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add the current directory to Python path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import the main agent class
from {{agent_name}} import {{AgentName}}


def example_1_basic_file_review():
    """
    Example 1: Basic single file review using default settings.
    """
    print("=" * 60)
    print("EXAMPLE 1: Basic File Review")
    print("=" * 60)

    # Initialize the agent with default OpenAI settings
    agent = {{AgentName}}(
        model_provider="openai",
        model_name="gpt-4o",
        temperature=0.1
    )

    # Create a sample Python file to review
    sample_code = '''
import os
import subprocess

def process_user_input(user_input):
    # Potential security issue: SQL injection vulnerability
    query = f"SELECT * FROM users WHERE name = '{user_input}'"

    # Another security issue: command injection
    os.system(f"echo {user_input}")

    # Hard-coded password
    password = "admin123"

    return query

def calculate_complexity(numbers):
    # High complexity function
    result = 0
    for i in range(len(numbers)):
        for j in range(len(numbers)):
            if i != j:
                for k in range(len(numbers)):
                    if k != i and k != j:
                        if numbers[i] + numbers[j] == numbers[k]:
                            result += 1
    return result
'''

    # Write sample code to a temporary file
    temp_file = "temp_example.py"
    with open(temp_file, 'w') as f:
        f.write(sample_code)

    try:
        # Perform code review
        print("Reviewing sample Python file...")
        result = agent.review_code(temp_file)

        # Display results
        if "error" in result:
            print(f"Error: {result['error']}")
        else:
            print(f"Review completed successfully!")
            print(f"File: {result['file_path']}")
            print(f"Timestamp: {result['timestamp']}")
            print(f"Summary: {result['summary']}")
            print("\nFor detailed results, check the agent.review_results")

    finally:
        # Cleanup
        if os.path.exists(temp_file):
            os.remove(temp_file)

    print("\n")


def example_2_anthropic_with_custom_settings():
    """
    Example 2: Using Anthropic Claude with custom settings.
    """
    print("=" * 60)
    print("EXAMPLE 2: Anthropic Claude with Custom Settings")
    print("=" * 60)

    # Initialize agent with Anthropic Claude
    agent = {{AgentName}}(
        model_provider="anthropic",
        model_name="claude-3-5-sonnet-20241022",
        temperature=0.0,  # More deterministic
        max_tokens=6000   # Longer responses
    )

    # Sample JavaScript code with security issues
    js_code = '''
function validateUser(username, password) {
    // XSS vulnerability
    document.getElementById("welcome").innerHTML = "Welcome " + username;

    // Hard-coded API key
    const apiKey = "sk-1234567890abcdefghijklmnopqrstuvwxyz";

    // Unsafe eval usage
    eval("console.log('User: " + username + "')");

    return true;
}

function processData(data) {
    // Complex nested loops
    for (let i = 0; i < data.length; i++) {
        for (let j = 0; j < data[i].length; j++) {
            for (let k = 0; k < data[i][j].length; k++) {
                for (let l = 0; l < data[i][j][k].length; l++) {
                    if (data[i][j][k][l] > 100) {
                        data[i][j][k][l] = 100;
                    }
                }
            }
        }
    }
    return data;
}
'''

    temp_file = "temp_example.js"
    with open(temp_file, 'w') as f:
        f.write(js_code)

    try:
        print("Reviewing JavaScript file with Anthropic Claude...")
        result = agent.review_code(
            temp_file,
            include_security=True,
            include_quality=True
        )

        if "error" not in result:
            print("Review completed successfully!")

            # Generate and save a detailed report
            report = agent.generate_report("markdown")
            with open("example_2_report.md", 'w') as f:
                f.write(report)
            print("Detailed report saved to: example_2_report.md")

    finally:
        if os.path.exists(temp_file):
            os.remove(temp_file)

    print("\n")


def example_3_directory_review():
    """
    Example 3: Review an entire directory of code files.
    """
    print("=" * 60)
    print("EXAMPLE 3: Directory Review")
    print("=" * 60)

    # Create a temporary directory with multiple files
    temp_dir = Path("temp_project")
    temp_dir.mkdir(exist_ok=True)

    # Create multiple sample files
    files = {
        "main.py": '''
import requests
import json

API_KEY = "secret-key-12345"  # Security issue

def fetch_user_data(user_id):
    # SQL injection vulnerability
    query = f"SELECT * FROM users WHERE id = {user_id}"

    response = requests.get(f"https://api.example.com/users/{user_id}")
    return response.json()

def process_data(data):
    # Complex function
    result = []
    for item in data:
        if item["status"] == "active":
            for category in item["categories"]:
                if category["priority"] > 5:
                    result.append(item)
    return result
''',
        "utils.py": '''
import os
import hashlib

def hash_password(password):
    # Using weak hash algorithm
    return hashlib.md5(password.encode()).hexdigest()

def execute_command(cmd):
    # Command injection vulnerability
    os.system(cmd)

def validate_input(data):
    # Good practice: input validation
    if not isinstance(data, str):
        raise ValueError("Input must be a string")
    if len(data) > 1000:
        raise ValueError("Input too long")
    return True
''',
        "config.js": '''
const config = {
    // Hard-coded secrets
    database: {
        host: "localhost",
        user: "admin",
        password: "admin123",
        port: 5432
    },

    api: {
        key: "sk-1234567890abcdef",
        endpoint: "https://api.example.com"
    }
};

// XSS vulnerability
function displayMessage(msg) {
    document.getElementById("output").innerHTML = msg;
}

module.exports = config;
'''
    }

    # Write files
    for filename, content in files.items():
        file_path = temp_dir / filename
        with open(file_path, 'w') as f:
            f.write(content)

    try:
        # Initialize agent
        agent = {{AgentName}}(
            model_provider="openai",
            model_name="gpt-4o"
        )

        print(f"Reviewing directory: {temp_dir}")

        # Review entire directory
        result = agent.review_directory(
            str(temp_dir),
            file_patterns=["*.py", "*.js"],
            recursive=True
        )

        print(f"Directory review completed!")
        print(f"Files reviewed: {result['files_reviewed']}")
        print(f"Timestamp: {result['timestamp']}")

        # Generate comprehensive report
        html_report = agent.generate_report("html")
        with open("directory_review_report.html", 'w') as f:
            f.write(html_report)
        print("HTML report saved to: directory_review_report.html")

        # Print summary
        summary = result.get("summary", {})
        print(f"\nSummary:")
        print(f"  Successful reviews: {summary.get('successful_reviews', 0)}")
        print(f"  Failed reviews: {summary.get('failed_reviews', 0)}")

    finally:
        # Cleanup
        import shutil
        if temp_dir.exists():
            shutil.rmtree(temp_dir)

    print("\n")


def example_4_security_focused_review():
    """
    Example 4: Security-focused review with custom severity threshold.
    """
    print("=" * 60)
    print("EXAMPLE 4: Security-Focused Review")
    print("=" * 60)

    # Sample code with various security issues
    security_test_code = '''
import pickle
import yaml
import subprocess
import os
from flask import Flask, request

app = Flask(__name__)

# Multiple security vulnerabilities
SECRET_KEY = "hardcoded-secret-key-123"
DATABASE_PASSWORD = "admin123"
API_TOKEN = "sk-1234567890abcdefghijklmnop"

def unsafe_deserialization(data):
    # Unsafe pickle usage
    return pickle.loads(data)

def yaml_loading(content):
    # Unsafe YAML loading
    return yaml.load(content)

@app.route('/execute')
def execute_command():
    # Command injection
    cmd = request.args.get('cmd')
    return subprocess.run(cmd, shell=True, capture_output=True, text=True)

@app.route('/file')
def read_file():
    # Path traversal vulnerability
    filename = request.args.get('file')
    with open(f"uploads/{filename}", 'r') as f:
        return f.read()

def authenticate(username, password):
    # SQL injection
    query = f"SELECT * FROM users WHERE username='{username}' AND password='{password}'"
    # ... database execution
    return True

if __name__ == "__main__":
    app.run(debug=True)  # Debug mode in production
'''

    temp_file = "security_test.py"
    with open(temp_file, 'w') as f:
        f.write(security_test_code)

    try:
        # Initialize agent
        agent = {{AgentName}}(
            model_provider="openai",
            model_name="gpt-4o",
            temperature=0.0  # Deterministic for security analysis
        )

        print("Performing security-focused review...")

        # Review with focus on security
        result = agent.review_code(
            temp_file,
            include_security=True,
            include_quality=False  # Focus only on security
        )

        if "error" not in result:
            print("Security review completed!")

            # Extract security findings
            analysis = result.get("analysis", {})
            if "security_audit" in analysis:
                print("\nSecurity findings detected!")
                print("Check the detailed report for remediation steps.")

            # Generate security report
            json_report = agent.generate_report("json")
            with open("security_report.json", 'w') as f:
                f.write(json_report)
            print("Security report saved to: security_report.json")

    finally:
        if os.path.exists(temp_file):
            os.remove(temp_file)

    print("\n")


def example_5_tool_usage():
    """
    Example 5: Direct tool usage without full agent orchestration.
    """
    print("=" * 60)
    print("EXAMPLE 5: Direct Tool Usage")
    print("=" * 60)

    from tools import FileAnalyzer, SecurityScanner

    # Sample code for analysis
    sample_code = '''
def fibonacci(n):
    if n <= 1:
        return n
    else:
        return fibonacci(n-1) + fibonacci(n-2)

def main():
    # Hardcoded password
    db_password = "mypassword123"

    # Calculate fibonacci
    result = fibonacci(30)
    print(f"Fibonacci result: {result}")

    # Command execution
    import os
    os.system("ls -la")

if __name__ == "__main__":
    main()
'''

    temp_file = "tool_test.py"
    with open(temp_file, 'w') as f:
        f.write(sample_code)

    try:
        print("Using File Analyzer tool directly...")

        # Use FileAnalyzer directly
        file_analyzer = FileAnalyzer()
        analysis_result = file_analyzer._run(
            file_path=temp_file,
            analysis_type="full",
            include_metrics=True
        )
        print("File Analysis Result:")
        print(analysis_result)

        print("\n" + "="*40 + "\n")

        print("Using Security Scanner tool directly...")

        # Use SecurityScanner directly
        security_scanner = SecurityScanner()
        security_result = security_scanner._run(
            file_path=temp_file,
            scan_type="comprehensive",
            severity_threshold="low"
        )
        print("Security Scan Result:")
        print(security_result)

    finally:
        if os.path.exists(temp_file):
            os.remove(temp_file)

    print("\n")


def example_6_configuration_and_customization():
    """
    Example 6: Advanced configuration and customization options.
    """
    print("=" * 60)
    print("EXAMPLE 6: Advanced Configuration")
    print("=" * 60)

    # Custom agent configuration
    custom_agent = {{AgentName}}(
        model_provider="openai",
        model_name="gpt-4o",
        temperature=0.05,    # Very low for consistent results
        max_tokens=8000      # Extended context for detailed analysis
    )

    # You can also customize agent behavior by modifying the agents directly
    # This shows how to access and potentially modify agent properties
    print(f"Code Analyzer Agent Role: {custom_agent.code_analyzer_agent.role}")
    print(f"Security Auditor Agent Goal: {custom_agent.security_auditor_agent.goal}")
    print(f"Quality Reviewer Agent Backstory: {custom_agent.quality_reviewer_agent.backstory[:100]}...")

    # Example of generating different report formats
    sample_code = "print('Hello, World!')"
    temp_file = "simple_test.py"

    with open(temp_file, 'w') as f:
        f.write(sample_code)

    try:
        result = custom_agent.review_code(temp_file)

        if "error" not in result:
            # Generate reports in different formats
            formats = ["json", "markdown", "html"]
            for fmt in formats:
                report = custom_agent.generate_report(fmt)
                output_file = f"custom_report.{fmt}"
                with open(output_file, 'w') as f:
                    f.write(report)
                print(f"Report generated: {output_file}")

    finally:
        if os.path.exists(temp_file):
            os.remove(temp_file)

    print("\n")


def main():
    """
    Main function to run all examples.
    """
    print("{{AgentName}} - Usage Examples")
    print("=" * 60)
    print(f"Python version: {sys.version}")
    print(f"Current directory: {os.getcwd()}")
    print()

    # Check if API keys are configured
    openai_key = os.getenv("OPENAI_API_KEY")
    anthropic_key = os.getenv("ANTHROPIC_API_KEY")

    if not openai_key and not anthropic_key:
        print("⚠️  Warning: No API keys found in environment variables.")
        print("   Please set OPENAI_API_KEY or ANTHROPIC_API_KEY in your .env file.")
        print("   Some examples may not work without proper API configuration.")
        print()

    # Run examples
    examples = [
        ("Basic File Review", example_1_basic_file_review),
        ("Anthropic with Custom Settings", example_2_anthropic_with_custom_settings),
        ("Directory Review", example_3_directory_review),
        ("Security-Focused Review", example_4_security_focused_review),
        ("Direct Tool Usage", example_5_tool_usage),
        ("Advanced Configuration", example_6_configuration_and_customization),
    ]

    for name, example_func in examples:
        try:
            print(f"Running: {name}")
            example_func()
            print(f"✓ {name} completed successfully")
        except Exception as e:
            print(f"✗ {name} failed: {str(e)}")
        print()

    print("All examples completed!")
    print("\nGenerated files:")
    generated_files = [
        "example_2_report.md",
        "directory_review_report.html",
        "security_report.json",
        "custom_report.json",
        "custom_report.markdown",
        "custom_report.html"
    ]

    for file in generated_files:
        if os.path.exists(file):
            print(f"  - {file}")

    print("\nTo clean up generated files, run:")
    print("rm -f *.md *.html *.json")


if __name__ == "__main__":
    main()