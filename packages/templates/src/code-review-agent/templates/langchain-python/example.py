"""
{{AgentName}} Usage Examples

This script demonstrates various ways to use the comprehensive code review agent
for different types of code analysis tasks including security scanning,
quality scoring, and detailed code analysis.
"""

from {{agent_name}} import {{AgentName}}, review_file, review_files, CodeReviewResult
import os
import json
from dotenv import load_dotenv
from typing import List

# Load environment variables
load_dotenv()


def single_file_review_example():
    """Basic example - review a single file with detailed analysis."""
    print("🔍 Single File Review Example")
    print("=" * 50)

    try:
        # Create agent with OpenAI (or switch to "anthropic")
        reviewer = {{AgentName}}(
            model_provider="openai",
            model_name="gpt-4-turbo-preview",
            temperature=0.1,
            verbose=True
        )

        # Review this example file itself
        file_path = __file__
        print(f"Analyzing: {file_path}")

        result: CodeReviewResult = reviewer.review_file(file_path)

        print("\n📊 Review Results:")
        print(f"File: {result.file_path}")
        print(f"Language: {result.language}")
        print(f"Quality Score: {result.quality_score}/10")
        print(f"Overall Rating: {result.overall_rating}")
        print(f"Issues Found: {len(result.issues)}")
        print(f"Security Vulnerabilities: {len(result.security_vulnerabilities)}")
        print(f"Best Practice Violations: {len(result.best_practices)}")

        print(f"\nSummary:\n{result.summary}")

        # Show specific issues if any
        if result.issues:
            print(f"\nCode Issues ({len(result.issues)}):")
            for i, issue in enumerate(result.issues[:3], 1):
                print(f"{i}. {issue.get('description', 'No description')}")

        if result.security_vulnerabilities:
            print(f"\nSecurity Issues ({len(result.security_vulnerabilities)}):")
            for i, vuln in enumerate(result.security_vulnerabilities[:3], 1):
                print(f"{i}. {vuln.get('description', 'No description')}")

    except Exception as e:
        print(f"❌ Error: {e}")


def code_string_review_example():
    """Example reviewing code from a string."""
    print("\n🔍 Code String Review Example")
    print("=" * 50)

    # Sample code with intentional issues for demonstration
    sample_code = '''
def login_user(username, password):
    # SQL injection vulnerability
    query = "SELECT * FROM users WHERE username = '" + username + "' AND password = '" + password + "'"
    cursor.execute(query)

    user = cursor.fetchone()
    if user:
        # Hardcoded session secret
        session_secret = "mysecretkey123"
        session['user_id'] = user['id']
        session['secret'] = session_secret
        return True
    return False

def calculate_score(items):
    # No input validation
    total = 0
    for item in items:
        total += item.price  # No error handling for missing attribute
    return total

def get_user_data(user_id):
    # Debug mode enabled in production
    app.debug = True

    # Unescaped user input (XSS vulnerability)
    return f"<h1>Welcome {request.args.get('name')}</h1>"
'''

    try:
        reviewer = {{AgentName}}(
            model_provider="openai",
            temperature=0.1,
            verbose=True
        )

        print("Analyzing sample code with security issues...")
        result = reviewer.review_code(sample_code, "sample_login.py", "python")

        print(f"\n📊 Analysis Results:")
        print(f"Quality Score: {result.quality_score}/10")
        print(f"Overall Rating: {result.overall_rating}")
        print(f"Security Issues: {len(result.security_vulnerabilities)}")
        print(f"Code Issues: {len(result.issues)}")

        # Show security vulnerabilities
        if result.security_vulnerabilities:
            print(f"\n🚨 Security Vulnerabilities:")
            for vuln in result.security_vulnerabilities:
                severity = vuln.get('severity', 'Unknown')
                desc = vuln.get('description', 'No description')
                print(f"  [{severity}] {desc}")

        # Show performance suggestions
        if result.performance_suggestions:
            print(f"\n⚡ Performance Suggestions:")
            for perf in result.performance_suggestions:
                print(f"  • {perf.get('description', 'No description')}")

    except Exception as e:
        print(f"❌ Error: {e}")


def multiple_files_review_example():
    """Example reviewing multiple files with comparison."""
    print("\n🔍 Multiple Files Review Example")
    print("=" * 50)

    try:
        reviewer = {{AgentName}}(
            model_provider="openai",
            verbose=False  # Less verbose for multiple files
        )

        # List of files to review (filter for existing files)
        candidate_files = [
            "{{agent_name}}.py",
            "tools/file_analyzer.py",
            "tools/security_scanner.py",
            "prompts.py",
            "example.py"
        ]

        existing_files = [f for f in candidate_files if os.path.exists(f)]

        if not existing_files:
            print("⚠️  No files found to review")
            return

        print(f"Found {len(existing_files)} files to review")

        results = reviewer.review_files(existing_files[:3])  # Limit to first 3 for demo

        print(f"\n📊 Multi-File Review Summary:")
        print("-" * 40)

        for result in results:
            print(f"\nFile: {result.file_path}")
            print(f"  Language: {result.language}")
            print(f"  Quality Score: {result.quality_score}/10")
            print(f"  Rating: {result.overall_rating}")
            print(f"  Issues: {len(result.issues)}")
            print(f"  Security: {len(result.security_vulnerabilities)}")

        # Generate comprehensive report
        if results:
            report = reviewer.generate_report(results)
            print(f"\n📄 Generated Report (first 500 chars):")
            print("-" * 40)
            print(report[:500] + "..." if len(report) > 500 else report)

    except Exception as e:
        print(f"❌ Error: {e}")


def directory_review_example():
    """Example reviewing all files in a directory with filtering."""
    print("\n🔍 Directory Review Example")
    print("=" * 50)

    try:
        reviewer = {{AgentName}}(
            model_provider="openai",
            verbose=False
        )

        # Review current directory, focusing on Python files
        current_dir = "."
        results = reviewer.review_directory(
            directory_path=current_dir,
            file_extensions=['.py'],
            exclude_patterns=['__pycache__', '.git', 'venv', '.pytest_cache']
        )

        print(f"\n📊 Directory Analysis Results:")
        print(f"Files analyzed: {len(results)}")

        if results:
            # Calculate average scores
            scores = [r.quality_score for r in results]
            avg_score = sum(scores) / len(scores)

            print(f"Average quality score: {avg_score:.1f}/10")

            # Find files with issues
            files_with_security_issues = [r for r in results if r.security_vulnerabilities]
            files_with_low_scores = [r for r in results if r.quality_score < 7]

            if files_with_security_issues:
                print(f"\n🚨 Files with security issues:")
                for result in files_with_security_issues:
                    print(f"  {result.file_path}: {len(result.security_vulnerabilities)} issues")

            if files_with_low_scores:
                print(f"\n⚠️  Files needing improvement (score < 7):")
                for result in files_with_low_scores:
                    print(f"  {result.file_path}: {result.quality_score}/10")

    except Exception as e:
        print(f"❌ Error: {e}")


def git_changes_review_example():
    """Example reviewing git changes with PR-style feedback."""
    print("\n🔍 Git Changes Review Example")
    print("=" * 50)

    try:
        reviewer = {{AgentName}}(
            model_provider="openai",
            verbose=True
        )

        # Review changes compared to main branch
        result = reviewer.review_git_changes(base_branch="main")

        print(f"\n📊 Git Review Results:")
        print(f"Base Branch: {result['base_branch']}")
        print(f"Success: {result['success']}")

        if result['success']:
            print(f"Tools Used: {result['tools_used']}")
            print(f"\nReview Summary:")
            print("-" * 40)
            print(result['review'][:1000] + "..." if len(result['review']) > 1000 else result['review'])
        else:
            print(f"❌ Review failed: {result.get('error', 'Unknown error')}")
            if 'Not in a git repository' in str(result.get('error', '')):
                print("\n💡 Tip: This example requires being in a git repository")

    except Exception as e:
        print(f"❌ Error: {e}")


def anthropic_model_example():
    """Example using Anthropic's Claude model."""
    print("\n🔍 Anthropic Claude Model Example")
    print("=" * 50)

    if not os.getenv("ANTHROPIC_API_KEY"):
        print("⚠️  ANTHROPIC_API_KEY not found - skipping this example")
        return

    try:
        # Initialize with Anthropic model
        reviewer = {{AgentName}}(
            model_provider="anthropic",
            model_name="claude-3-sonnet-20240229",
            temperature=0.1,
            verbose=True
        )

        # Sample code for review
        sample_code = '''
import hashlib

def hash_password(password):
    """Hash a password using MD5 (insecure)."""
    return hashlib.md5(password.encode()).hexdigest()

class UserAuth:
    def __init__(self):
        self.users = {}

    def register(self, username, password):
        # Store password hash
        self.users[username] = hash_password(password)
        print(f"User {username} registered successfully")

    def login(self, username, password):
        if username in self.users:
            if self.users[username] == hash_password(password):
                return True
        return False
'''

        print("Analyzing authentication code with Claude...")
        result = reviewer.review_code(sample_code, "auth_example.py", "python")

        print(f"\n🤖 Claude's Analysis:")
        print(f"Quality Score: {result.quality_score}/10")
        print(f"Overall Rating: {result.overall_rating}")

        print(f"\nSummary:\n{result.summary}")

        if result.security_vulnerabilities:
            print(f"\n🛡️  Security Issues Found:")
            for vuln in result.security_vulnerabilities[:3]:
                print(f"  • {vuln.get('description', 'No description')}")

    except Exception as e:
        print(f"❌ Error with Anthropic model: {e}")


def quick_functions_example():
    """Example using convenience functions for quick analysis."""
    print("\n🔍 Quick Analysis Functions Example")
    print("=" * 50)

    try:
        # Quick single file review
        if os.path.exists("{{agent_name}}.py"):
            print("Quick file review:")
            summary = review_file(
                "{{agent_name}}.py",
                model_provider="openai",
                verbose=False
            )
            print(f"Summary: {summary[:200]}...")

        # Quick multiple files review
        files = ["example.py", "prompts.py"]
        existing_files = [f for f in files if os.path.exists(f)]

        if existing_files:
            print(f"\nQuick multi-file review ({len(existing_files)} files):")
            results = review_files(
                existing_files,
                model_provider="openai",
                verbose=False
            )

            print(f"Analyzed {len(results)} files")
            for result in results:
                print(f"  {result.file_path}: {result.quality_score}/10")

    except Exception as e:
        print(f"❌ Error: {e}")


def security_focused_example():
    """Example focusing specifically on security analysis."""
    print("\n🔍 Security-Focused Analysis Example")
    print("=" * 50)

    # Code with multiple security vulnerabilities
    vulnerable_code = '''
import os
import subprocess
import sqlite3

def execute_command(user_input):
    # Command injection vulnerability
    result = subprocess.run(f"ls {user_input}", shell=True, capture_output=True)
    return result.stdout.decode()

def get_user_data(user_id):
    conn = sqlite3.connect('users.db')
    # SQL injection vulnerability
    query = f"SELECT * FROM users WHERE id = {user_id}"
    cursor = conn.execute(query)
    return cursor.fetchall()

def authenticate(username, password):
    # Hardcoded credentials
    admin_password = "admin123"
    if username == "admin" and password == admin_password:
        return True
    return False

def generate_session_token():
    # Weak random token generation
    import random
    return str(random.randint(100000, 999999))

def save_file(filename, content):
    # Path traversal vulnerability
    with open(f"uploads/{filename}", "w") as f:
        f.write(content)
'''

    try:
        reviewer = {{AgentName}}(
            model_provider="openai",
            temperature=0.05,  # Very low for consistent security analysis
            verbose=True
        )

        print("Analyzing code with multiple security vulnerabilities...")
        result = reviewer.review_code(vulnerable_code, "vulnerable_app.py", "python")

        print(f"\n🔒 Security Analysis Results:")
        print(f"Overall Quality: {result.quality_score}/10")
        print(f"Security Vulnerabilities Found: {len(result.security_vulnerabilities)}")

        if result.security_vulnerabilities:
            print(f"\n🚨 Security Issues:")
            for i, vuln in enumerate(result.security_vulnerabilities, 1):
                severity = vuln.get('severity', 'Unknown')
                desc = vuln.get('description', 'No description')
                print(f"{i}. [{severity}] {desc}")

        print(f"\nOverall Security Assessment: {result.overall_rating}")

    except Exception as e:
        print(f"❌ Error in security analysis: {e}")


def main():
    """Main function to run examples with proper error handling."""
    # Check for API keys
    has_openai = bool(os.getenv("OPENAI_API_KEY"))
    has_anthropic = bool(os.getenv("ANTHROPIC_API_KEY"))

    if not has_openai and not has_anthropic:
        print("⚠️  Warning: No API keys found!")
        print("Please set OPENAI_API_KEY or ANTHROPIC_API_KEY in your .env file")
        print("\nExample .env file:")
        print("OPENAI_API_KEY=sk-your-openai-key-here")
        print("ANTHROPIC_API_KEY=sk-ant-your-anthropic-key-here")
        return

    print("🤖 {{AgentName}} - Comprehensive Code Review Examples")
    print("=" * 70)

    if has_openai:
        print("✅ OpenAI API key found")
    if has_anthropic:
        print("✅ Anthropic API key found")

    print("\nRunning examples...")

    try:
        # Basic examples (uncomment the ones you want to run)
        single_file_review_example()
        code_string_review_example()

        # Uncomment for more comprehensive testing:
        # multiple_files_review_example()
        # directory_review_example()
        # git_changes_review_example()
        # quick_functions_example()
        # security_focused_example()

        # Only run if Anthropic key is available
        # if has_anthropic:
        #     anthropic_model_example()

    except Exception as e:
        print(f"\n💥 Fatal error: {e}")
        print("\n🔧 Troubleshooting:")
        print("1. Verify API keys in .env file")
        print("2. Install dependencies: pip install -r requirements.txt")
        print("3. Ensure you have code files to analyze")
        print("4. For git reviews, run from a git repository")
        print("5. Check internet connection for API calls")

    print("\n✨ Examples completed! Check the output above for detailed analysis results.")


if __name__ == "__main__":
    main()