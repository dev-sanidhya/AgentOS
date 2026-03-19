"""
Security Scanner Tool for Code Review Agent

This module provides security vulnerability detection capabilities for the code review agent.
It identifies common security issues across multiple programming languages without requiring
external security scanning tools.
"""

import re
import os
import json
import hashlib
from pathlib import Path
from typing import Dict, List, Any, Optional, Set
from dataclasses import dataclass
from urllib.parse import urlparse


@dataclass
class SecurityIssue:
    """Represents a security vulnerability found during scanning."""
    line_number: int
    column: int
    severity: str  # "critical", "high", "medium", "low"
    category: str  # e.g., "injection", "crypto", "auth", "data_exposure"
    cwe_id: Optional[str]  # Common Weakness Enumeration ID
    message: str
    evidence: str
    recommendation: str


@dataclass
class SecurityReport:
    """Security scan report."""
    file_path: str
    language: str
    total_issues: int
    critical_issues: int
    high_issues: int
    medium_issues: int
    low_issues: int
    issues: List[SecurityIssue]
    risk_score: int  # 0-100


class SecurityScanner:
    """Comprehensive security vulnerability scanner."""

    def __init__(self):
        self.security_patterns = self._load_security_patterns()
        self.crypto_patterns = self._load_crypto_patterns()
        self.injection_patterns = self._load_injection_patterns()

    def scan_file(self, file_path: str, content: str, language: str) -> SecurityReport:
        """
        Perform comprehensive security scan of a file.

        Args:
            file_path: Path to the file being scanned
            content: File content to scan
            language: Programming language of the file

        Returns:
            SecurityReport with vulnerability details
        """
        issues = []

        # Generic security issues
        issues.extend(self._scan_hardcoded_secrets(content, file_path))
        issues.extend(self._scan_crypto_issues(content, language))
        issues.extend(self._scan_injection_vulnerabilities(content, language))
        issues.extend(self._scan_path_traversal(content, language))
        issues.extend(self._scan_insecure_random(content, language))
        issues.extend(self._scan_weak_authentication(content, language))

        # Language-specific scans
        if language == 'Python':
            issues.extend(self._scan_python_security(content))
        elif language in ['JavaScript', 'TypeScript']:
            issues.extend(self._scan_javascript_security(content))
        elif language == 'Java':
            issues.extend(self._scan_java_security(content))
        elif language == 'PHP':
            issues.extend(self._scan_php_security(content))

        # Calculate severity counts
        critical_count = len([i for i in issues if i.severity == 'critical'])
        high_count = len([i for i in issues if i.severity == 'high'])
        medium_count = len([i for i in issues if i.severity == 'medium'])
        low_count = len([i for i in issues if i.severity == 'low'])

        # Calculate risk score (0-100)
        risk_score = min(100, critical_count * 25 + high_count * 10 + medium_count * 5 + low_count * 1)

        return SecurityReport(
            file_path=file_path,
            language=language,
            total_issues=len(issues),
            critical_issues=critical_count,
            high_issues=high_count,
            medium_issues=medium_count,
            low_issues=low_count,
            issues=issues,
            risk_score=risk_score
        )

    def _scan_hardcoded_secrets(self, content: str, file_path: str) -> List[SecurityIssue]:
        """Scan for hardcoded secrets and sensitive information."""
        issues = []
        lines = content.splitlines()

        # Patterns for various types of secrets
        secret_patterns = {
            'AWS Access Key': (r'AKIA[0-9A-Z]{16}', 'critical', 'CWE-798'),
            'AWS Secret Key': (r'[A-Za-z0-9/+=]{40}', 'critical', 'CWE-798'),
            'GitHub Token': (r'ghp_[A-Za-z0-9]{36}', 'critical', 'CWE-798'),
            'Generic API Key': (r'(?i)(api[_-]?key|apikey)["\'\s]*[:=]["\'\s]*([a-z0-9]{20,})', 'high', 'CWE-798'),
            'Password': (r'(?i)(password|pwd)["\'\s]*[:=]["\'\s]*["\']([^"\']{8,})["\']', 'high', 'CWE-798'),
            'Database URL': (r'(?i)(database_url|db_url)["\'\s]*[:=]["\'\s]*["\']([^"\']*://[^"\']+)["\']', 'medium', 'CWE-798'),
            'JWT Token': (r'eyJ[A-Za-z0-9_-]*\.[A-Za-z0-9_-]*\.[A-Za-z0-9_-]*', 'high', 'CWE-798'),
            'Private Key': (r'-----BEGIN [A-Z ]+PRIVATE KEY-----', 'critical', 'CWE-798'),
        }

        for line_num, line in enumerate(lines, 1):
            # Skip comments (basic detection)
            if line.strip().startswith(('#', '//', '/*', '*', '<!--')):
                continue

            for secret_type, (pattern, severity, cwe) in secret_patterns.items():
                matches = re.finditer(pattern, line)
                for match in matches:
                    # Additional validation to reduce false positives
                    if self._is_likely_secret(line, match.group(0)):
                        issues.append(SecurityIssue(
                            line_number=line_num,
                            column=match.start() + 1,
                            severity=severity,
                            category="data_exposure",
                            cwe_id=cwe,
                            message=f"Hardcoded {secret_type.lower()} detected",
                            evidence=line.strip()[:100] + "..." if len(line.strip()) > 100 else line.strip(),
                            recommendation=f"Move {secret_type.lower()} to environment variables or secure configuration"
                        ))

        return issues

    def _scan_crypto_issues(self, content: str, language: str) -> List[SecurityIssue]:
        """Scan for cryptographic vulnerabilities."""
        issues = []
        lines = content.splitlines()

        # Weak/deprecated cryptographic algorithms
        weak_crypto = {
            'MD5': ('medium', 'CWE-327'),
            'SHA1': ('medium', 'CWE-327'),
            'DES': ('high', 'CWE-327'),
            'RC4': ('high', 'CWE-327'),
            'MD4': ('high', 'CWE-327'),
        }

        # Insecure random number generation
        weak_random_patterns = {
            'Python': [r'random\.random\(\)', r'random\.randint\('],
            'JavaScript': [r'Math\.random\(\)'],
            'Java': [r'new Random\(\)', r'Math\.random\(\)'],
            'PHP': [r'rand\(\)', r'mt_rand\(\)'],
        }

        for line_num, line in enumerate(lines, 1):
            line_lower = line.lower()

            # Check for weak crypto algorithms
            for algo, (severity, cwe) in weak_crypto.items():
                if algo.lower() in line_lower:
                    issues.append(SecurityIssue(
                        line_number=line_num,
                        column=line_lower.find(algo.lower()) + 1,
                        severity=severity,
                        category="crypto",
                        cwe_id=cwe,
                        message=f"Weak cryptographic algorithm: {algo}",
                        evidence=line.strip(),
                        recommendation=f"Use stronger alternatives (SHA-256, AES, etc.) instead of {algo}"
                    ))

            # Check for weak random number generation
            if language in weak_random_patterns:
                for pattern in weak_random_patterns[language]:
                    if re.search(pattern, line):
                        issues.append(SecurityIssue(
                            line_number=line_num,
                            column=re.search(pattern, line).start() + 1,
                            severity="medium",
                            category="crypto",
                            cwe_id="CWE-338",
                            message="Insecure random number generation",
                            evidence=line.strip(),
                            recommendation="Use cryptographically secure random number generators"
                        ))

        return issues

    def _scan_injection_vulnerabilities(self, content: str, language: str) -> List[SecurityIssue]:
        """Scan for injection vulnerabilities."""
        issues = []
        lines = content.splitlines()

        # SQL injection patterns
        sql_injection_patterns = [
            r'(?i)(select|insert|update|delete|drop|create|alter)\s+.*\+.*["\']',
            r'(?i)query.*\+.*["\']',
            r'(?i)execute.*\+.*["\']',
            r'(?i)sql.*%.*["\']',
        ]

        # Command injection patterns
        command_injection_patterns = {
            'Python': [r'os\.system\(.*\+', r'subprocess\.call\(.*\+', r'eval\(.*\+'],
            'JavaScript': [r'eval\(.*\+', r'Function\(.*\+', r'setTimeout\(.*\+'],
            'Java': [r'Runtime\.getRuntime\(\)\.exec\(.*\+'],
            'PHP': [r'exec\(.*\$', r'system\(.*\$', r'shell_exec\(.*\$', r'eval\(.*\$'],
        }

        # XSS patterns (for web languages)
        xss_patterns = {
            'JavaScript': [r'innerHTML.*\+', r'outerHTML.*\+', r'document\.write\(.*\+'],
            'PHP': [r'echo.*\$[^;]*;', r'print.*\$[^;]*;'],
        }

        for line_num, line in enumerate(lines, 1):
            # SQL injection
            for pattern in sql_injection_patterns:
                if re.search(pattern, line):
                    issues.append(SecurityIssue(
                        line_number=line_num,
                        column=re.search(pattern, line).start() + 1,
                        severity="high",
                        category="injection",
                        cwe_id="CWE-89",
                        message="Potential SQL injection vulnerability",
                        evidence=line.strip(),
                        recommendation="Use parameterized queries or prepared statements"
                    ))

            # Command injection
            if language in command_injection_patterns:
                for pattern in command_injection_patterns[language]:
                    if re.search(pattern, line):
                        issues.append(SecurityIssue(
                            line_number=line_num,
                            column=re.search(pattern, line).start() + 1,
                            severity="critical",
                            category="injection",
                            cwe_id="CWE-78",
                            message="Potential command injection vulnerability",
                            evidence=line.strip(),
                            recommendation="Avoid dynamic command execution; use safe alternatives"
                        ))

            # XSS
            if language in xss_patterns:
                for pattern in xss_patterns[language]:
                    if re.search(pattern, line):
                        issues.append(SecurityIssue(
                            line_number=line_num,
                            column=re.search(pattern, line).start() + 1,
                            severity="high",
                            category="injection",
                            cwe_id="CWE-79",
                            message="Potential cross-site scripting (XSS) vulnerability",
                            evidence=line.strip(),
                            recommendation="Sanitize and escape user input before output"
                        ))

        return issues

    def _scan_path_traversal(self, content: str, language: str) -> List[SecurityIssue]:
        """Scan for path traversal vulnerabilities."""
        issues = []
        lines = content.splitlines()

        path_traversal_patterns = {
            'Python': [r'open\(["\'].*\.\./.*["\']', r'file\(["\'].*\.\./.*["\']'],
            'JavaScript': [r'fs\.readFile\(["\'].*\.\./.*["\']'],
            'Java': [r'new File\(["\'].*\.\./.*["\']'],
            'PHP': [r'file_get_contents\(["\'].*\.\./.*["\']', r'include["\'].*\.\./.*["\']'],
        }

        if language in path_traversal_patterns:
            for line_num, line in enumerate(lines, 1):
                for pattern in path_traversal_patterns[language]:
                    if re.search(pattern, line):
                        issues.append(SecurityIssue(
                            line_number=line_num,
                            column=re.search(pattern, line).start() + 1,
                            severity="high",
                            category="path_traversal",
                            cwe_id="CWE-22",
                            message="Potential path traversal vulnerability",
                            evidence=line.strip(),
                            recommendation="Validate and sanitize file paths; use allowlists for safe paths"
                        ))

        return issues

    def _scan_insecure_random(self, content: str, language: str) -> List[SecurityIssue]:
        """Scan for insecure random number usage."""
        issues = []
        lines = content.splitlines()

        # Patterns that suggest cryptographic use of random numbers
        crypto_contexts = [
            r'(?i)(password|token|session|key|salt|nonce|csrf)',
            r'(?i)(encrypt|decrypt|hash|sign)',
            r'(?i)(auth|login|verify)',
        ]

        weak_random_funcs = {
            'Python': [r'random\.'],
            'JavaScript': [r'Math\.random'],
            'Java': [r'Math\.random', r'Random\(\)'],
            'PHP': [r'rand\(', r'mt_rand\('],
        }

        if language in weak_random_funcs:
            for line_num, line in enumerate(lines, 1):
                # Check if line contains weak random function
                for func_pattern in weak_random_funcs[language]:
                    if re.search(func_pattern, line):
                        # Check if it's in a cryptographic context
                        line_context = line.lower()
                        for crypto_pattern in crypto_contexts:
                            if re.search(crypto_pattern, line_context):
                                issues.append(SecurityIssue(
                                    line_number=line_num,
                                    column=re.search(func_pattern, line).start() + 1,
                                    severity="medium",
                                    category="crypto",
                                    cwe_id="CWE-338",
                                    message="Cryptographically weak random number generator",
                                    evidence=line.strip(),
                                    recommendation="Use cryptographically secure random generators for security-sensitive operations"
                                ))
                                break

        return issues

    def _scan_weak_authentication(self, content: str, language: str) -> List[SecurityIssue]:
        """Scan for weak authentication patterns."""
        issues = []
        lines = content.splitlines()

        # Patterns indicating weak authentication
        weak_auth_patterns = [
            (r'(?i)password\s*==\s*["\'][^"\']*["\']', "Hardcoded password comparison", "high", "CWE-798"),
            (r'(?i)if.*password.*==.*["\']', "Hardcoded password in condition", "high", "CWE-798"),
            (r'(?i)auth.*==.*["\']admin["\']', "Hardcoded admin check", "medium", "CWE-798"),
            (r'(?i)token\s*==\s*["\'][^"\']*["\']', "Hardcoded token comparison", "high", "CWE-798"),
        ]

        for line_num, line in enumerate(lines, 1):
            for pattern, message, severity, cwe in weak_auth_patterns:
                if re.search(pattern, line):
                    issues.append(SecurityIssue(
                        line_number=line_num,
                        column=re.search(pattern, line).start() + 1,
                        severity=severity,
                        category="auth",
                        cwe_id=cwe,
                        message=message,
                        evidence=line.strip(),
                        recommendation="Use secure authentication mechanisms with proper hashing and salting"
                    ))

        return issues

    def _scan_python_security(self, content: str) -> List[SecurityIssue]:
        """Python-specific security scanning."""
        issues = []
        lines = content.splitlines()

        python_patterns = [
            (r'pickle\.loads?\(', "Pickle deserialization vulnerability", "critical", "CWE-502"),
            (r'yaml\.load\(', "Unsafe YAML loading", "high", "CWE-502"),
            (r'eval\(', "Code injection via eval()", "critical", "CWE-94"),
            (r'exec\(', "Code injection via exec()", "critical", "CWE-94"),
            (r'__import__\(', "Dynamic import", "medium", "CWE-94"),
            (r'input\(.*\)', "Unsafe input() in Python 2", "medium", "CWE-20"),
        ]

        for line_num, line in enumerate(lines, 1):
            for pattern, message, severity, cwe in python_patterns:
                if re.search(pattern, line):
                    issues.append(SecurityIssue(
                        line_number=line_num,
                        column=re.search(pattern, line).start() + 1,
                        severity=severity,
                        category="injection",
                        cwe_id=cwe,
                        message=message,
                        evidence=line.strip(),
                        recommendation="Use safer alternatives or add proper input validation"
                    ))

        return issues

    def _scan_javascript_security(self, content: str) -> List[SecurityIssue]:
        """JavaScript/TypeScript-specific security scanning."""
        issues = []
        lines = content.splitlines()

        js_patterns = [
            (r'eval\(', "Code injection via eval()", "critical", "CWE-94"),
            (r'Function\(.*\)', "Dynamic function creation", "high", "CWE-94"),
            (r'setTimeout\(.*["\'].*["\'].*\)', "Code injection via setTimeout", "high", "CWE-94"),
            (r'setInterval\(.*["\'].*["\'].*\)', "Code injection via setInterval", "high", "CWE-94"),
            (r'document\.write\(', "XSS via document.write", "medium", "CWE-79"),
            (r'innerHTML.*=.*\+', "XSS via innerHTML", "high", "CWE-79"),
        ]

        for line_num, line in enumerate(lines, 1):
            for pattern, message, severity, cwe in js_patterns:
                if re.search(pattern, line):
                    issues.append(SecurityIssue(
                        line_number=line_num,
                        column=re.search(pattern, line).start() + 1,
                        severity=severity,
                        category="injection",
                        cwe_id=cwe,
                        message=message,
                        evidence=line.strip(),
                        recommendation="Use safer alternatives or add proper input sanitization"
                    ))

        return issues

    def _scan_java_security(self, content: str) -> List[SecurityIssue]:
        """Java-specific security scanning."""
        issues = []
        lines = content.splitlines()

        java_patterns = [
            (r'Runtime\.getRuntime\(\)\.exec\(', "Command injection risk", "high", "CWE-78"),
            (r'Class\.forName\(', "Dynamic class loading", "medium", "CWE-470"),
            (r'ObjectInputStream\.readObject\(', "Unsafe deserialization", "critical", "CWE-502"),
            (r'System\.getProperty\(.*\)', "System property access", "low", "CWE-200"),
        ]

        for line_num, line in enumerate(lines, 1):
            for pattern, message, severity, cwe in java_patterns:
                if re.search(pattern, line):
                    issues.append(SecurityIssue(
                        line_number=line_num,
                        column=re.search(pattern, line).start() + 1,
                        severity=severity,
                        category="injection",
                        cwe_id=cwe,
                        message=message,
                        evidence=line.strip(),
                        recommendation="Use safer alternatives or add proper validation"
                    ))

        return issues

    def _scan_php_security(self, content: str) -> List[SecurityIssue]:
        """PHP-specific security scanning."""
        issues = []
        lines = content.splitlines()

        php_patterns = [
            (r'eval\(', "Code injection via eval()", "critical", "CWE-94"),
            (r'exec\(', "Command injection via exec()", "critical", "CWE-78"),
            (r'system\(', "Command injection via system()", "critical", "CWE-78"),
            (r'shell_exec\(', "Command injection via shell_exec()", "critical", "CWE-78"),
            (r'passthru\(', "Command injection via passthru()", "critical", "CWE-78"),
            (r'file_get_contents\(\$', "File inclusion vulnerability", "high", "CWE-98"),
            (r'include.*\$', "File inclusion vulnerability", "high", "CWE-98"),
            (r'require.*\$', "File inclusion vulnerability", "high", "CWE-98"),
            (r'unserialize\(', "Unsafe deserialization", "critical", "CWE-502"),
        ]

        for line_num, line in enumerate(lines, 1):
            for pattern, message, severity, cwe in php_patterns:
                if re.search(pattern, line):
                    issues.append(SecurityIssue(
                        line_number=line_num,
                        column=re.search(pattern, line).start() + 1,
                        severity=severity,
                        category="injection",
                        cwe_id=cwe,
                        message=message,
                        evidence=line.strip(),
                        recommendation="Use safer alternatives or add proper input validation"
                    ))

        return issues

    def _is_likely_secret(self, line: str, potential_secret: str) -> bool:
        """Determine if a potential secret is likely to be a real secret."""
        # Skip common false positives
        false_positives = [
            'example', 'test', 'demo', 'placeholder', 'TODO', 'FIXME',
            'your_key_here', 'replace_me', 'change_me'
        ]

        line_lower = line.lower()
        secret_lower = potential_secret.lower()

        for fp in false_positives:
            if fp in line_lower or fp in secret_lower:
                return False

        # Too short to be a real secret
        if len(potential_secret) < 8:
            return False

        # All same character is likely not a real secret
        if len(set(potential_secret)) < 3:
            return False

        return True

    def _load_security_patterns(self) -> Dict[str, Any]:
        """Load security pattern definitions."""
        return {
            "sensitive_functions": {
                "Python": ["eval", "exec", "compile", "__import__", "pickle.loads"],
                "JavaScript": ["eval", "Function", "setTimeout", "setInterval"],
                "Java": ["Runtime.exec", "Class.forName", "ObjectInputStream.readObject"],
                "PHP": ["eval", "exec", "system", "shell_exec", "passthru", "unserialize"]
            }
        }

    def _load_crypto_patterns(self) -> Dict[str, Any]:
        """Load cryptographic pattern definitions."""
        return {
            "weak_algorithms": ["MD5", "SHA1", "DES", "RC4", "MD4"],
            "strong_algorithms": ["SHA-256", "SHA-512", "AES", "RSA", "ECDSA"]
        }

    def _load_injection_patterns(self) -> Dict[str, List[str]]:
        """Load injection pattern definitions."""
        return {
            "sql_injection": [
                r"(?i)(select|insert|update|delete).*\+.*['\"]",
                r"(?i)query.*\+.*['\"]",
                r"(?i)execute.*\+.*['\"]"
            ],
            "command_injection": [
                r"(?i)(system|exec|shell_exec).*\$",
                r"(?i)Runtime\.getRuntime\(\)\.exec.*\+"
            ],
            "xss": [
                r"innerHTML.*\+",
                r"outerHTML.*\+",
                r"document\.write.*\+"
            ]
        }