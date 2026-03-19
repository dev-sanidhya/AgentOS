"""
{{AgentName}} Usage Examples

This file demonstrates various ways to use the code review agent,
from basic usage to advanced configurations and individual tool usage.
"""

import os
import time
from pathlib import Path
from {{agent_name}} import {{AgentName}}, review_file, review_files, security_scan
from tools import FileAnalyzer, SecurityScanner, LLMClient, Models


def example_1_basic_usage():
    """Example 1: Basic file review"""
    print("=" * 60)
    print("EXAMPLE 1: Basic File Review")
    print("=" * 60)

    # Create a simple test file
    test_code = '''
def calculate_discount(price, percentage):
    """Calculate discount amount."""
    if percentage < 0 or percentage > 100:
        raise ValueError("Invalid percentage")

    discount = price * (percentage / 100)
    return discount

def process_order(items, discount_percent=0):
    """Process an order with optional discount."""
    total = sum(item['price'] for item in items)
    discount = calculate_discount(total, discount_percent)
    return total - discount

# Example usage
if __name__ == "__main__":
    items = [
        {"name": "Widget", "price": 10.99},
        {"name": "Gadget", "price": 25.50}
    ]

    final_total = process_order(items, 10)
    print(f"Total after discount: ${final_total:.2f}")
'''

    # Write test file
    with open("test_code.py", "w") as f:
        f.write(test_code)

    try:
        # Basic review
        print("\\n🔍 Performing basic review...")
        reviewer = {{AgentName}}(model="gpt-4", verbose=True)
        result = reviewer.review_file("test_code.py")

        print(f"\\nResults:")
        print(f"- Quality Score: {result.quality_score}/10")
        print(f"- Security Score: {result.security_score}/10")
        print(f"- Issues Found: {result.issues_found}")
        print(f"- Duration: {result.duration:.1f}s")

        # Show first few lines of review
        review_lines = result.review.split('\\n')[:10]
        print(f"\\nReview Preview:")
        for line in review_lines:
            print(f"  {line}")
        print("  ...")

    finally:
        # Cleanup
        if os.path.exists("test_code.py"):
            os.remove("test_code.py")


def example_2_security_focused():
    """Example 2: Security-focused scanning"""
    print("\\n" + "=" * 60)
    print("EXAMPLE 2: Security-Focused Scanning")
    print("=" * 60)

    # Create code with security issues
    insecure_code = '''
import os
import subprocess

# Hardcoded credentials (BAD!)
DATABASE_URL = "postgresql://admin:password123@localhost/mydb"
API_KEY = "sk-1234567890abcdef"

def execute_command(user_input):
    """Execute user command - DANGEROUS!"""
    # Command injection vulnerability
    result = os.system(user_input)
    return result

def get_user_data(user_id):
    """Get user data with SQL injection risk"""
    # SQL injection vulnerability
    query = f"SELECT * FROM users WHERE id = '{user_id}'"
    return query

def process_file(filename):
    """Process file - path traversal risk"""
    # Path traversal vulnerability
    with open(f"/uploads/{filename}", "r") as f:
        return f.read()

# Weak random for session tokens
import random
session_token = str(random.randint(1000000, 9999999))
'''

    with open("insecure_code.py", "w") as f:
        f.write(insecure_code)

    try:
        print("\\n🔒 Performing security-focused scan...")

        # Security scan only
        security_report = security_scan("insecure_code.py")

        print(f"\\nSecurity Analysis Results:")
        print(f"- Total Issues: {security_report.total_issues}")
        print(f"- Critical: {security_report.critical_issues}")
        print(f"- High: {security_report.high_issues}")
        print(f"- Medium: {security_report.medium_issues}")
        print(f"- Low: {security_report.low_issues}")
        print(f"- Risk Score: {security_report.risk_score}/100")

        print(f"\\nTop Security Issues:")
        for i, issue in enumerate(security_report.issues[:3], 1):
            print(f"{i}. Line {issue.line_number}: {issue.message}")
            print(f"   Severity: {issue.severity.upper()}")
            print(f"   Category: {issue.category}")
            print(f"   Recommendation: {issue.recommendation}")
            print()

        # Full review with security context
        print("\\n🤖 Performing full review with security focus...")
        reviewer = {{AgentName}}(model="gpt-4", verbose=False)
        result = reviewer.review_file("insecure_code.py")

        print(f"\\nOverall Scores:")
        print(f"- Quality: {result.quality_score}/10")
        print(f"- Security: {result.security_score}/10")

    finally:
        if os.path.exists("insecure_code.py"):
            os.remove("insecure_code.py")


def example_3_multi_file_review():
    """Example 3: Multi-file review"""
    print("\\n" + "=" * 60)
    print("EXAMPLE 3: Multi-File Review")
    print("=" * 60)

    # Create multiple related files
    files_to_create = {
        "models.py": '''
class User:
    def __init__(self, username, email):
        self.username = username
        self.email = email
        self.is_active = True

    def deactivate(self):
        self.is_active = False

class Product:
    def __init__(self, name, price, category):
        self.name = name
        self.price = price
        self.category = category
        self.in_stock = True
''',
        "utils.py": '''
import re
from models import User

def validate_email(email):
    pattern = r'^[\\w\\.-]+@[\\w\\.-]+\\.\\w+$'
    return re.match(pattern, email) is not None

def format_currency(amount):
    return f"${amount:.2f}"

def calculate_tax(subtotal, tax_rate=0.08):
    return subtotal * tax_rate
''',
        "main.py": '''
from models import User, Product
from utils import validate_email, format_currency, calculate_tax

def create_user(username, email):
    if not validate_email(email):
        raise ValueError("Invalid email format")
    return User(username, email)

def process_purchase(products, tax_rate=0.08):
    subtotal = sum(product.price for product in products)
    tax = calculate_tax(subtotal, tax_rate)
    total = subtotal + tax

    return {
        'subtotal': format_currency(subtotal),
        'tax': format_currency(tax),
        'total': format_currency(total)
    }

if __name__ == "__main__":
    # Example usage
    user = create_user("john_doe", "john@example.com")
    products = [
        Product("Widget", 19.99, "gadgets"),
        Product("Tool", 35.50, "hardware")
    ]

    result = process_purchase(products)
    print(f"Purchase total: {result['total']}")
'''
    }

    # Create the files
    created_files = []
    try:
        for filename, content in files_to_create.items():
            with open(filename, "w") as f:
                f.write(content)
            created_files.append(filename)

        print(f"\\n📁 Created {len(created_files)} related files")

        # Multi-file review
        print("\\n🔍 Performing multi-file review...")
        reviewer = {{AgentName}}(model="gpt-4", verbose=True)
        result = reviewer.review_files(created_files)

        print(f"\\nMulti-File Review Results:")
        print(f"- Files Reviewed: {len(created_files)}")
        print(f"- Overall Quality: {result.quality_score}/10")
        print(f"- Overall Security: {result.security_score}/10")
        print(f"- Total Issues: {result.issues_found}")
        print(f"- Security Issues: {result.security_issues}")

        # Show review summary
        review_lines = result.review.split('\\n')[:15]
        print(f"\\nReview Summary:")
        for line in review_lines:
            print(f"  {line}")
        print("  ...")

    finally:
        # Cleanup
        for filename in created_files:
            if os.path.exists(filename):
                os.remove(filename)


def example_4_individual_tools():
    """Example 4: Using individual tools"""
    print("\\n" + "=" * 60)
    print("EXAMPLE 4: Individual Tool Usage")
    print("=" * 60)

    sample_code = '''
import json
import hashlib
from datetime import datetime

class DataProcessor:
    """Process and validate data."""

    def __init__(self, config_file="config.json"):
        self.config = self.load_config(config_file)
        self.processed_count = 0

    def load_config(self, filename):
        """Load configuration from JSON file."""
        try:
            with open(filename, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return {"default": True}
        except json.JSONDecodeError:
            raise ValueError("Invalid JSON configuration")

    def hash_data(self, data, algorithm="sha256"):
        """Hash data using specified algorithm."""
        if algorithm == "md5":  # Weak algorithm!
            hasher = hashlib.md5()
        else:
            hasher = hashlib.sha256()

        hasher.update(data.encode())
        return hasher.hexdigest()

    def process_batch(self, data_list):
        """Process a batch of data."""
        results = []

        for item in data_list:
            if self.validate_item(item):
                processed = self.transform_item(item)
                results.append(processed)
                self.processed_count += 1
            else:
                print(f"Skipping invalid item: {item}")

        return results

    def validate_item(self, item):
        """Validate a single data item."""
        return isinstance(item, dict) and 'id' in item and 'value' in item

    def transform_item(self, item):
        """Transform a valid item."""
        return {
            'id': item['id'],
            'value': item['value'],
            'processed_at': datetime.now().isoformat(),
            'hash': self.hash_data(str(item))
        }

    def get_stats(self):
        """Get processing statistics."""
        return {
            'processed_count': self.processed_count,
            'last_run': datetime.now().isoformat()
        }
'''

    with open("sample_code.py", "w") as f:
        f.write(sample_code)

    try:
        print("\\n🔧 Using FileAnalyzer directly...")

        # 1. File Analyzer
        analyzer = FileAnalyzer()
        analysis = analyzer.analyze_file("sample_code.py")

        if analysis['success']:
            metrics = analysis['metrics']
            print(f"  ✅ File Analysis Complete")
            print(f"     Language: {analysis['language']}")
            print(f"     Lines of Code: {metrics.lines_of_code}")
            print(f"     Comments: {metrics.lines_of_comments}")
            print(f"     Functions: {metrics.function_count}")
            print(f"     Classes: {metrics.class_count}")
            print(f"     Complexity: {metrics.cyclomatic_complexity}")
            print(f"     Issues Found: {len(analysis['issues'])}")

        print("\\n🔒 Using SecurityScanner directly...")

        # 2. Security Scanner
        scanner = SecurityScanner()
        with open("sample_code.py", "r") as f:
            content = f.read()

        security_report = scanner.scan_file("sample_code.py", content, "Python")
        print(f"  ✅ Security Scan Complete")
        print(f"     Total Issues: {security_report.total_issues}")
        print(f"     Risk Score: {security_report.risk_score}/100")

        if security_report.issues:
            print(f"     Top Issue: {security_report.issues[0].message}")

        print("\\n🤖 Using LLMClient directly...")

        # 3. LLM Client
        client = LLMClient()

        # Test connection
        test_result = client.test_connection()
        if test_result['success']:
            print(f"  ✅ LLM Connection: {test_result['model']}")

        # Generate structured review
        response = client.generate_structured_review(content, "Python", "sample_code.py")
        if response.success:
            print(f"  ✅ Review Generated")
            print(f"     Response Time: {response.response_time:.1f}s")
            print(f"     Tokens Used: {response.tokens_used}")
            print(f"     Estimated Cost: ${response.cost_estimate:.4f}")

            # Show first few lines
            lines = response.content.split('\\n')[:5]
            print(f"     Preview:")
            for line in lines:
                print(f"       {line}")
            print(f"       ...")

    finally:
        if os.path.exists("sample_code.py"):
            os.remove("sample_code.py")


def example_5_advanced_configuration():
    """Example 5: Advanced configuration and model comparison"""
    print("\\n" + "=" * 60)
    print("EXAMPLE 5: Advanced Configuration")
    print("=" * 60)

    # Create test code
    test_code = '''
def fibonacci(n):
    """Calculate fibonacci number recursively."""
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)

def fibonacci_optimized(n, memo={}):
    """Optimized fibonacci with memoization."""
    if n in memo:
        return memo[n]
    if n <= 1:
        return n
    memo[n] = fibonacci_optimized(n-1, memo) + fibonacci_optimized(n-2, memo)
    return memo[n]
'''

    with open("fib_code.py", "w") as f:
        f.write(test_code)

    try:
        print("\\n🔧 Testing different configurations...")

        # Test different models (if API keys available)
        models_to_test = ["gpt-3.5-turbo", "gpt-4"]

        for model in models_to_test:
            print(f"\\n📊 Testing with {model}...")

            try:
                reviewer = {{AgentName}}(
                    model=model,
                    temperature=0.1,  # Low temperature for consistent results
                    verbose=False,
                    max_tokens=2000
                )

                start_time = time.time()
                result = reviewer.review_file("fib_code.py")
                duration = time.time() - start_time

                print(f"  Model: {model}")
                print(f"  Quality Score: {result.quality_score}/10")
                print(f"  Duration: {duration:.1f}s")
                print(f"  Success: {result.success}")

                if not result.success:
                    print(f"  Error: {result.error}")

            except Exception as e:
                print(f"  ❌ Failed with {model}: {str(e)}")

        # Test with custom LLM configuration
        print(f"\\n⚙️ Testing custom LLM configuration...")

        from tools import LLMConfig

        custom_config = LLMConfig(
            model="gpt-4",
            temperature=0.5,
            max_tokens=3000,
            max_retries=2,
            retry_delay=0.5
        )

        custom_client = LLMClient(custom_config)

        # Test the custom configuration
        test_result = custom_client.test_connection()
        print(f"  Custom Config Test: {'✅ Success' if test_result['success'] else '❌ Failed'}")

    finally:
        if os.path.exists("fib_code.py"):
            os.remove("fib_code.py")


def example_6_directory_analysis():
    """Example 6: Directory analysis"""
    print("\\n" + "=" * 60)
    print("EXAMPLE 6: Directory Analysis")
    print("=" * 60)

    # Create a sample project structure
    os.makedirs("sample_project", exist_ok=True)
    os.makedirs("sample_project/src", exist_ok=True)
    os.makedirs("sample_project/tests", exist_ok=True)

    project_files = {
        "sample_project/src/__init__.py": "",
        "sample_project/src/calculator.py": '''
def add(a, b):
    """Add two numbers."""
    return a + b

def subtract(a, b):
    """Subtract two numbers."""
    return a - b

def multiply(a, b):
    """Multiply two numbers."""
    return a * b

def divide(a, b):
    """Divide two numbers."""
    if b == 0:
        raise ValueError("Cannot divide by zero")
    return a / b
''',
        "sample_project/tests/test_calculator.py": '''
import unittest
from src.calculator import add, subtract, multiply, divide

class TestCalculator(unittest.TestCase):
    def test_add(self):
        self.assertEqual(add(2, 3), 5)

    def test_subtract(self):
        self.assertEqual(subtract(5, 3), 2)

    def test_multiply(self):
        self.assertEqual(multiply(3, 4), 12)

    def test_divide(self):
        self.assertEqual(divide(10, 2), 5)

    def test_divide_by_zero(self):
        with self.assertRaises(ValueError):
            divide(10, 0)

if __name__ == '__main__':
    unittest.main()
''',
        "sample_project/main.py": '''
from src.calculator import add, subtract, multiply, divide

def main():
    """Simple calculator demo."""
    print("Calculator Demo")
    print(f"2 + 3 = {add(2, 3)}")
    print(f"10 - 4 = {subtract(10, 4)}")
    print(f"5 * 6 = {multiply(5, 6)}")
    print(f"15 / 3 = {divide(15, 3)}")

if __name__ == "__main__":
    main()
'''
    }

    try:
        # Create project files
        for filepath, content in project_files.items():
            with open(filepath, "w") as f:
                f.write(content)

        print(f"\\n📁 Created sample project with {len(project_files)} files")

        # Analyze the directory
        print("\\n🔍 Analyzing project directory...")
        reviewer = {{AgentName}}(verbose=True)

        result = reviewer.review_directory(
            directory="sample_project",
            file_patterns=["*.py"],
            max_files=10
        )

        print(f"\\nDirectory Analysis Results:")
        print(f"- Files Analyzed: {result.file_or_files}")
        print(f"- Overall Quality: {result.quality_score}/10")
        print(f"- Overall Security: {result.security_score}/10")
        print(f"- Total Issues: {result.issues_found}")
        print(f"- Security Issues: {result.security_issues}")
        print(f"- Analysis Duration: {result.duration:.1f}s")

    finally:
        # Cleanup
        import shutil
        if os.path.exists("sample_project"):
            shutil.rmtree("sample_project")


def main():
    """Run all examples."""
    print("🚀 {{AgentName}} - Comprehensive Examples")
    print("=" * 60)

    examples = [
        example_1_basic_usage,
        example_2_security_focused,
        example_3_multi_file_review,
        example_4_individual_tools,
        example_5_advanced_configuration,
        example_6_directory_analysis,
    ]

    for i, example in enumerate(examples, 1):
        try:
            print(f"\\n🎯 Running Example {i}...")
            example()
        except Exception as e:
            print(f"❌ Example {i} failed: {str(e)}")
            print("This might be due to missing API keys or network issues.")

    print("\\n" + "=" * 60)
    print("🎉 Examples completed!")
    print("\\nTo run individual examples:")
    for i, example in enumerate(examples, 1):
        print(f"  python -c \"from example import {example.__name__}; {example.__name__}()\"")


if __name__ == "__main__":
    main()