"""
Security scanner tool for detecting vulnerabilities and security issues in code.
Performs static analysis to identify common security patterns and vulnerabilities.
"""

import re
import hashlib
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path

from langchain.tools import BaseTool
from pydantic import BaseModel, Field


class SecurityScannerInput(BaseModel):
    """Input schema for the SecurityScanner tool."""
    code_content: str = Field(description="The code content to scan for security issues")
    file_path: Optional[str] = Field(default="", description="Path to the file being scanned")
    language: Optional[str] = Field(default="", description="Programming language of the code")


class SecurityScannerTool(BaseTool):
    """
    Tool for scanning code for security vulnerabilities and issues.

    This tool detects:
    - SQL injection vulnerabilities
    - XSS vulnerabilities
    - Hardcoded secrets and credentials
    - Insecure cryptographic practices
    - Input validation issues
    - Authentication/authorization problems
    - File system security issues
    - Network security issues
    """

    name: str = "security_scanner"
    description: str = """Scan code for security vulnerabilities and issues.
    Input should be a JSON with: {"code_content": "code to scan", "file_path": "optional/path", "language": "optional language"}"""

    args_schema: type[BaseModel] = SecurityScannerInput

    def _run(self, code_content: str, file_path: str = "", language: str = "") -> str:
        """
        Scan the provided code content for security vulnerabilities.

        Args:
            code_content: The code to scan
            file_path: Optional file path
            language: Optional language hint

        Returns:
            Security scan report
        """
        try:
            # Auto-detect language if not provided
            if not language:
                language = self._detect_language(code_content, file_path)

            vulnerabilities = {
                "sql_injection": self._check_sql_injection(code_content, language),
                "xss_vulnerabilities": self._check_xss_vulnerabilities(code_content, language),
                "hardcoded_secrets": self._check_hardcoded_secrets(code_content),
                "crypto_issues": self._check_crypto_issues(code_content, language),
                "input_validation": self._check_input_validation(code_content, language),
                "auth_issues": self._check_auth_issues(code_content, language),
                "file_security": self._check_file_security(code_content, language),
                "network_security": self._check_network_security(code_content, language),
                "injection_attacks": self._check_injection_attacks(code_content, language),
                "insecure_defaults": self._check_insecure_defaults(code_content, language)
            }

            # Calculate risk score
            risk_score = self._calculate_risk_score(vulnerabilities)

            return self._format_security_report(vulnerabilities, risk_score, file_path, language)

        except Exception as e:
            return f"Error during security scan: {str(e)}"

    def _detect_language(self, code_content: str, file_path: str) -> str:
        """Detect the programming language."""
        if file_path:
            extension = Path(file_path).suffix.lower()
            lang_map = {
                '.py': 'python',
                '.js': 'javascript',
                '.ts': 'typescript',
                '.java': 'java',
                '.go': 'go',
                '.rs': 'rust',
                '.cpp': 'cpp',
                '.c': 'c',
                '.cs': 'csharp',
                '.php': 'php',
                '.rb': 'ruby',
                '.sql': 'sql'
            }
            if extension in lang_map:
                return lang_map[extension]

        # Heuristic detection
        content_lower = code_content.lower()
        if "def " in content_lower and "import " in content_lower:
            return "python"
        elif "function " in content_lower and ("var " in content_lower or "const " in content_lower):
            return "javascript"
        elif "class " in content_lower and "public static void main" in content_lower:
            return "java"

        return "unknown"

    def _check_sql_injection(self, code_content: str, language: str) -> List[Dict[str, Any]]:
        """Check for SQL injection vulnerabilities."""
        vulnerabilities = []

        # Common SQL injection patterns
        patterns = [
            # String concatenation with user input
            r'(SELECT|INSERT|UPDATE|DELETE).*\+.*',
            r'(SELECT|INSERT|UPDATE|DELETE).*%.*',
            r'(SELECT|INSERT|UPDATE|DELETE).*format\(',
            r'(SELECT|INSERT|UPDATE|DELETE).*\.format\(',

            # Direct user input in SQL
            r'(SELECT|INSERT|UPDATE|DELETE).*request\.',
            r'(SELECT|INSERT|UPDATE|DELETE).*input\(',
            r'(SELECT|INSERT|UPDATE|DELETE).*argv',
            r'(SELECT|INSERT|UPDATE|DELETE).*sys\.argv',

            # Dangerous SQL construction
            r'execute\s*\(\s*["\'].*\+',
            r'query\s*\(\s*["\'].*\+',
            r'sql\s*=.*\+'
        ]

        for pattern in patterns:
            matches = re.finditer(pattern, code_content, re.IGNORECASE | re.MULTILINE)
            for match in matches:
                line_num = code_content[:match.start()].count('\n') + 1
                vulnerabilities.append({
                    'type': 'SQL Injection',
                    'severity': 'HIGH',
                    'line': line_num,
                    'description': 'Potential SQL injection vulnerability detected',
                    'code_snippet': match.group(0)[:100],
                    'recommendation': 'Use parameterized queries or prepared statements'
                })

        # Language-specific checks
        if language == 'python':
            vulnerabilities.extend(self._check_python_sql_injection(code_content))
        elif language == 'php':
            vulnerabilities.extend(self._check_php_sql_injection(code_content))

        return vulnerabilities

    def _check_python_sql_injection(self, code_content: str) -> List[Dict[str, Any]]:
        """Check Python-specific SQL injection patterns."""
        vulnerabilities = []

        # Check for string formatting in SQL
        patterns = [
            r'cursor\.execute\s*\(\s*["\'].*%',
            r'cursor\.execute\s*\(\s*.*\.format\(',
            r'connection\.execute\s*\(\s*["\'].*%',
            r'session\.execute\s*\(\s*["\'].*%'
        ]

        for pattern in patterns:
            matches = re.finditer(pattern, code_content, re.IGNORECASE)
            for match in matches:
                line_num = code_content[:match.start()].count('\n') + 1
                vulnerabilities.append({
                    'type': 'SQL Injection',
                    'severity': 'HIGH',
                    'line': line_num,
                    'description': 'Python SQL injection via string formatting',
                    'code_snippet': match.group(0),
                    'recommendation': 'Use parameterized queries with ? or %s placeholders'
                })

        return vulnerabilities

    def _check_php_sql_injection(self, code_content: str) -> List[Dict[str, Any]]:
        """Check PHP-specific SQL injection patterns."""
        vulnerabilities = []

        # Check for PHP SQL injection patterns
        patterns = [
            r'mysql_query\s*\(\s*["\'].*\$',
            r'mysqli_query\s*\(\s*.*\$',
            r'\$pdo->query\s*\(\s*["\'].*\$'
        ]

        for pattern in patterns:
            matches = re.finditer(pattern, code_content, re.IGNORECASE)
            for match in matches:
                line_num = code_content[:match.start()].count('\n') + 1
                vulnerabilities.append({
                    'type': 'SQL Injection',
                    'severity': 'HIGH',
                    'line': line_num,
                    'description': 'PHP SQL injection via direct variable inclusion',
                    'code_snippet': match.group(0),
                    'recommendation': 'Use prepared statements with PDO or mysqli'
                })

        return vulnerabilities

    def _check_xss_vulnerabilities(self, code_content: str, language: str) -> List[Dict[str, Any]]:
        """Check for Cross-Site Scripting vulnerabilities."""
        vulnerabilities = []

        # Common XSS patterns
        patterns = [
            # Direct output of user input
            r'(innerHTML|outerHTML)\s*=\s*.*request\.',
            r'document\.write\s*\(\s*.*request\.',
            r'echo\s+\$_(GET|POST|REQUEST)',
            r'print\s+\$_(GET|POST|REQUEST)',
            r'response\.write\s*\(\s*request\.',

            # Unescaped template variables
            r'\{\{\s*.*request\.',
            r'\{\{\s*.*user\.',
            r'\$\{.*request\.',

            # Direct HTML generation with user input
            r'<.*\+.*request\.',
            r'<.*\+.*input\(',
        ]

        for pattern in patterns:
            matches = re.finditer(pattern, code_content, re.IGNORECASE | re.MULTILINE)
            for match in matches:
                line_num = code_content[:match.start()].count('\n') + 1
                vulnerabilities.append({
                    'type': 'XSS (Cross-Site Scripting)',
                    'severity': 'HIGH',
                    'line': line_num,
                    'description': 'Potential XSS vulnerability - unescaped user input',
                    'code_snippet': match.group(0)[:100],
                    'recommendation': 'Sanitize and escape all user input before output'
                })

        # Language-specific XSS checks
        if language == 'javascript':
            vulnerabilities.extend(self._check_js_xss(code_content))
        elif language == 'python':
            vulnerabilities.extend(self._check_python_xss(code_content))

        return vulnerabilities

    def _check_js_xss(self, code_content: str) -> List[Dict[str, Any]]:
        """Check JavaScript-specific XSS patterns."""
        vulnerabilities = []

        patterns = [
            r'\.innerHTML\s*=\s*.*\.value',
            r'\.outerHTML\s*=\s*.*\.value',
            r'document\.write\s*\(.*\.value',
            r'eval\s*\(.*\.value',
            r'\$\(.*\)\.html\s*\(.*\.value'
        ]

        for pattern in patterns:
            matches = re.finditer(pattern, code_content, re.IGNORECASE)
            for match in matches:
                line_num = code_content[:match.start()].count('\n') + 1
                vulnerabilities.append({
                    'type': 'DOM-based XSS',
                    'severity': 'HIGH',
                    'line': line_num,
                    'description': 'DOM-based XSS via direct HTML manipulation',
                    'code_snippet': match.group(0),
                    'recommendation': 'Use textContent instead of innerHTML, or sanitize input'
                })

        return vulnerabilities

    def _check_python_xss(self, code_content: str) -> List[Dict[str, Any]]:
        """Check Python-specific XSS patterns."""
        vulnerabilities = []

        patterns = [
            r'return\s+.*request\.',
            r'render_template_string\s*\(\s*.*request\.',
            r'Markup\s*\(\s*.*request\.',
            r'safe\s*\(\s*.*request\.'
        ]

        for pattern in patterns:
            matches = re.finditer(pattern, code_content, re.IGNORECASE)
            for match in matches:
                line_num = code_content[:match.start()].count('\n') + 1
                vulnerabilities.append({
                    'type': 'Template XSS',
                    'severity': 'HIGH',
                    'line': line_num,
                    'description': 'Template-based XSS via unescaped user input',
                    'code_snippet': match.group(0),
                    'recommendation': 'Use Jinja2 autoescaping or escape() function'
                })

        return vulnerabilities

    def _check_hardcoded_secrets(self, code_content: str) -> List[Dict[str, Any]]:
        """Check for hardcoded secrets and credentials."""
        vulnerabilities = []

        # Common secret patterns
        secret_patterns = [
            (r'password\s*=\s*["\'][^"\']{4,}["\']', 'Hardcoded Password', 'MEDIUM'),
            (r'api_?key\s*=\s*["\'][^"\']{10,}["\']', 'Hardcoded API Key', 'HIGH'),
            (r'secret_?key\s*=\s*["\'][^"\']{10,}["\']', 'Hardcoded Secret Key', 'HIGH'),
            (r'private_?key\s*=\s*["\'][^"\']{10,}["\']', 'Hardcoded Private Key', 'CRITICAL'),
            (r'token\s*=\s*["\'][^"\']{10,}["\']', 'Hardcoded Token', 'HIGH'),
            (r'auth\w*\s*=\s*["\'][^"\']{8,}["\']', 'Hardcoded Auth Credential', 'HIGH'),

            # Database connection strings
            (r'(mongodb|mysql|postgresql)://[^"\']*:[^"\']*@', 'Database Connection String', 'CRITICAL'),
            (r'CONN_STR\s*=\s*["\'][^"\']*password[^"\']*["\']', 'Database Connection String', 'CRITICAL'),

            # Cloud service keys
            (r'AKIA[0-9A-Z]{16}', 'AWS Access Key', 'CRITICAL'),
            (r'[0-9a-zA-Z/+=]{40}', 'Potential AWS Secret Key', 'HIGH'),
            (r'sk_live_[0-9a-zA-Z]{24}', 'Stripe Live Secret Key', 'CRITICAL'),
            (r'sk_test_[0-9a-zA-Z]{24}', 'Stripe Test Secret Key', 'MEDIUM'),

            # Generic high-entropy strings (potential secrets)
            (r'["\'][a-zA-Z0-9/+=]{32,}["\']', 'High Entropy String (Potential Secret)', 'LOW')
        ]

        for pattern, vuln_type, severity in secret_patterns:
            matches = re.finditer(pattern, code_content, re.IGNORECASE)
            for match in matches:
                line_num = code_content[:match.start()].count('\n') + 1

                # Skip common false positives
                matched_text = match.group(0).lower()
                if any(fp in matched_text for fp in ['example', 'demo', 'test', 'placeholder', 'xxx', '***']):
                    continue

                vulnerabilities.append({
                    'type': vuln_type,
                    'severity': severity,
                    'line': line_num,
                    'description': f'{vuln_type} found in code',
                    'code_snippet': '***REDACTED***',  # Don't expose the actual secret
                    'recommendation': 'Use environment variables or secure vault for secrets'
                })

        return vulnerabilities

    def _check_crypto_issues(self, code_content: str, language: str) -> List[Dict[str, Any]]:
        """Check for cryptographic security issues."""
        vulnerabilities = []

        # Weak cryptographic algorithms
        weak_crypto_patterns = [
            (r'MD5\s*\(', 'Weak Hash Algorithm (MD5)', 'MEDIUM'),
            (r'SHA1\s*\(', 'Weak Hash Algorithm (SHA1)', 'MEDIUM'),
            (r'DES\s*\(', 'Weak Encryption (DES)', 'HIGH'),
            (r'RC4\s*\(', 'Weak Encryption (RC4)', 'HIGH'),
            (r'ECB\s*\(', 'Weak Cipher Mode (ECB)', 'MEDIUM'),

            # Weak random number generation
            (r'random\(\)', 'Weak Random Number Generator', 'MEDIUM'),
            (r'Math\.random\(\)', 'Weak Random Number Generator', 'MEDIUM'),

            # Hardcoded cryptographic constants
            (r'salt\s*=\s*["\'][^"\']{1,8}["\']', 'Weak/Hardcoded Salt', 'HIGH'),
            (r'iv\s*=\s*["\'][^"\']{1,16}["\']', 'Hardcoded IV', 'HIGH'),

            # Insecure SSL/TLS
            (r'verify_mode\s*=\s*ssl\.CERT_NONE', 'Disabled SSL Certificate Verification', 'HIGH'),
            (r'verify\s*=\s*False', 'Disabled SSL Verification', 'HIGH'),
            (r'ssl_verify\s*=\s*False', 'Disabled SSL Verification', 'HIGH')
        ]

        for pattern, vuln_type, severity in weak_crypto_patterns:
            matches = re.finditer(pattern, code_content, re.IGNORECASE)
            for match in matches:
                line_num = code_content[:match.start()].count('\n') + 1
                vulnerabilities.append({
                    'type': vuln_type,
                    'severity': severity,
                    'line': line_num,
                    'description': f'{vuln_type} detected',
                    'code_snippet': match.group(0),
                    'recommendation': 'Use strong cryptographic algorithms and proper key management'
                })

        return vulnerabilities

    def _check_input_validation(self, code_content: str, language: str) -> List[Dict[str, Any]]:
        """Check for input validation issues."""
        vulnerabilities = []

        # Missing input validation patterns
        patterns = [
            (r'request\.(GET|POST|form)\[.*\]', 'Unvalidated User Input', 'MEDIUM'),
            (r'argv\[', 'Unvalidated Command Line Input', 'MEDIUM'),
            (r'input\(\)', 'Unvalidated User Input', 'MEDIUM'),
            (r'\$_(GET|POST|REQUEST)\[', 'Unvalidated User Input', 'MEDIUM'),

            # Dangerous functions with user input
            (r'eval\s*\(\s*.*request\.', 'Code Injection via eval()', 'CRITICAL'),
            (r'exec\s*\(\s*.*request\.', 'Code Injection via exec()', 'CRITICAL'),
            (r'system\s*\(\s*.*request\.', 'Command Injection', 'CRITICAL'),
            (r'shell_exec\s*\(\s*.*\$_', 'Command Injection', 'CRITICAL'),

            # File path traversal
            (r'open\s*\(\s*.*request\.', 'Path Traversal', 'HIGH'),
            (r'file_get_contents\s*\(\s*.*\$_', 'Path Traversal', 'HIGH'),
            (r'readFile\s*\(\s*.*request\.', 'Path Traversal', 'HIGH')
        ]

        for pattern, vuln_type, severity in patterns:
            matches = re.finditer(pattern, code_content, re.IGNORECASE)
            for match in matches:
                line_num = code_content[:match.start()].count('\n') + 1
                vulnerabilities.append({
                    'type': vuln_type,
                    'severity': severity,
                    'line': line_num,
                    'description': f'{vuln_type} - user input not properly validated',
                    'code_snippet': match.group(0)[:100],
                    'recommendation': 'Implement proper input validation and sanitization'
                })

        return vulnerabilities

    def _check_auth_issues(self, code_content: str, language: str) -> List[Dict[str, Any]]:
        """Check for authentication and authorization issues."""
        vulnerabilities = []

        # Authentication issues
        auth_patterns = [
            (r'if\s+.*password\s*==\s*["\'][^"\']*["\']', 'Hardcoded Password Check', 'HIGH'),
            (r'if\s+.*user\s*==\s*["\']admin["\']', 'Hardcoded Admin Check', 'MEDIUM'),
            (r'session\[.*\]\s*=\s*True', 'Insecure Session Management', 'MEDIUM'),
            (r'logged_in\s*=\s*True', 'Insecure Authentication State', 'MEDIUM'),

            # Missing authentication checks
            (r'@app\.route.*methods=\[.*POST.*\]', 'Potential Missing Auth Check', 'LOW'),
            (r'def\s+delete_', 'Potential Missing Auth Check', 'LOW'),
            (r'def\s+admin_', 'Potential Missing Auth Check', 'MEDIUM'),

            # Weak session management
            (r'session_id\s*=\s*\d+', 'Weak Session ID', 'MEDIUM'),
            (r'session_timeout\s*=\s*\d{1,3}', 'Short Session Timeout', 'LOW')
        ]

        for pattern, vuln_type, severity in auth_patterns:
            matches = re.finditer(pattern, code_content, re.IGNORECASE)
            for match in matches:
                line_num = code_content[:match.start()].count('\n') + 1
                vulnerabilities.append({
                    'type': vuln_type,
                    'severity': severity,
                    'line': line_num,
                    'description': f'{vuln_type} detected',
                    'code_snippet': match.group(0)[:100],
                    'recommendation': 'Implement proper authentication and authorization mechanisms'
                })

        return vulnerabilities

    def _check_file_security(self, code_content: str, language: str) -> List[Dict[str, Any]]:
        """Check for file system security issues."""
        vulnerabilities = []

        # File security patterns
        patterns = [
            (r'chmod\s+777', 'Overly Permissive File Permissions', 'HIGH'),
            (r'umask\s*\(\s*0\s*\)', 'Insecure umask Setting', 'MEDIUM'),
            (r'open\s*\(\s*["\'][^"\']*\.\./["\']', 'Path Traversal', 'HIGH'),
            (r'include\s*\(\s*\$_.*\)', 'File Inclusion Vulnerability', 'CRITICAL'),
            (r'require\s*\(\s*\$_.*\)', 'File Inclusion Vulnerability', 'CRITICAL'),
            (r'file_get_contents\s*\(\s*.*\$_', 'Arbitrary File Read', 'HIGH'),
            (r'unlink\s*\(\s*.*request\.', 'Arbitrary File Deletion', 'CRITICAL'),
            (r'rmdir\s*\(\s*.*request\.', 'Arbitrary Directory Deletion', 'CRITICAL')
        ]

        for pattern, vuln_type, severity in patterns:
            matches = re.finditer(pattern, code_content, re.IGNORECASE)
            for match in matches:
                line_num = code_content[:match.start()].count('\n') + 1
                vulnerabilities.append({
                    'type': vuln_type,
                    'severity': severity,
                    'line': line_num,
                    'description': f'{vuln_type} detected',
                    'code_snippet': match.group(0)[:100],
                    'recommendation': 'Implement proper file access controls and validation'
                })

        return vulnerabilities

    def _check_network_security(self, code_content: str, language: str) -> List[Dict[str, Any]]:
        """Check for network security issues."""
        vulnerabilities = []

        # Network security patterns
        patterns = [
            (r'http://[^"\']*', 'Unencrypted HTTP Connection', 'MEDIUM'),
            (r'ftp://[^"\']*', 'Unencrypted FTP Connection', 'MEDIUM'),
            (r'telnet\s*\(', 'Unencrypted Telnet Connection', 'HIGH'),
            (r'socket\.socket\s*\(.*SOCK_STREAM\)', 'Raw Socket Usage', 'LOW'),
            (r'bind\s*\(\s*["\']0\.0\.0\.0["\']', 'Binding to All Interfaces', 'MEDIUM'),
            (r'listen\s*\(\s*0\.0\.0\.0', 'Listening on All Interfaces', 'MEDIUM'),
            (r'allow_hosts\s*=\s*\[\s*["\']\*["\']', 'Allow All Hosts', 'HIGH'),
            (r'CORS\s*\(\s*.*origins\s*=\s*["\']\*["\']', 'Overly Permissive CORS', 'MEDIUM')
        ]

        for pattern, vuln_type, severity in patterns:
            matches = re.finditer(pattern, code_content, re.IGNORECASE)
            for match in matches:
                line_num = code_content[:match.start()].count('\n') + 1
                vulnerabilities.append({
                    'type': vuln_type,
                    'severity': severity,
                    'line': line_num,
                    'description': f'{vuln_type} detected',
                    'code_snippet': match.group(0)[:100],
                    'recommendation': 'Use secure network protocols and proper access controls'
                })

        return vulnerabilities

    def _check_injection_attacks(self, code_content: str, language: str) -> List[Dict[str, Any]]:
        """Check for various injection attack vectors."""
        vulnerabilities = []

        # Command injection patterns
        patterns = [
            (r'os\.system\s*\(\s*.*\+', 'Command Injection', 'CRITICAL'),
            (r'subprocess\s*\.\s*(call|run|Popen)\s*\(\s*.*\+', 'Command Injection', 'CRITICAL'),
            (r'shell_exec\s*\(\s*.*\$_', 'Command Injection', 'CRITICAL'),
            (r'exec\s*\(\s*.*\$_', 'Command Injection', 'CRITICAL'),
            (r'system\s*\(\s*.*\$_', 'Command Injection', 'CRITICAL'),

            # LDAP injection
            (r'ldap_search\s*\(\s*.*\$_', 'LDAP Injection', 'HIGH'),

            # XML injection
            (r'xml\.parse\s*\(\s*.*request\.', 'XML Injection', 'HIGH'),
            (r'ElementTree\s*\.\s*parse\s*\(\s*.*request\.', 'XML Injection', 'HIGH'),

            # NoSQL injection
            (r'find\s*\(\s*\{.*request\.', 'NoSQL Injection', 'HIGH'),
            (r'aggregate\s*\(\s*.*request\.', 'NoSQL Injection', 'HIGH')
        ]

        for pattern, vuln_type, severity in patterns:
            matches = re.finditer(pattern, code_content, re.IGNORECASE)
            for match in matches:
                line_num = code_content[:match.start()].count('\n') + 1
                vulnerabilities.append({
                    'type': vuln_type,
                    'severity': severity,
                    'line': line_num,
                    'description': f'{vuln_type} vulnerability detected',
                    'code_snippet': match.group(0)[:100],
                    'recommendation': 'Use parameterized queries and input sanitization'
                })

        return vulnerabilities

    def _check_insecure_defaults(self, code_content: str, language: str) -> List[Dict[str, Any]]:
        """Check for insecure default configurations."""
        vulnerabilities = []

        # Insecure defaults
        patterns = [
            (r'debug\s*=\s*True', 'Debug Mode Enabled', 'HIGH'),
            (r'DEBUG\s*=\s*True', 'Debug Mode Enabled', 'HIGH'),
            (r'app\.run\s*\(\s*.*debug\s*=\s*True', 'Debug Mode Enabled', 'HIGH'),
            (r'ssl_context\s*=\s*None', 'SSL Context Disabled', 'HIGH'),
            (r'verify_ssl\s*=\s*False', 'SSL Verification Disabled', 'HIGH'),
            (r'check_hostname\s*=\s*False', 'Hostname Verification Disabled', 'MEDIUM'),
            (r'autocommit\s*=\s*True', 'Database Autocommit Enabled', 'LOW'),
            (r'timeout\s*=\s*None', 'No Timeout Set', 'LOW'),
            (r'max_connections\s*=\s*-1', 'Unlimited Connections', 'MEDIUM')
        ]

        for pattern, vuln_type, severity in patterns:
            matches = re.finditer(pattern, code_content, re.IGNORECASE)
            for match in matches:
                line_num = code_content[:match.start()].count('\n') + 1
                vulnerabilities.append({
                    'type': vuln_type,
                    'severity': severity,
                    'line': line_num,
                    'description': f'{vuln_type} in configuration',
                    'code_snippet': match.group(0),
                    'recommendation': 'Review and harden default configurations'
                })

        return vulnerabilities

    def _calculate_risk_score(self, vulnerabilities: Dict[str, List[Dict[str, Any]]]) -> Dict[str, Any]:
        """Calculate overall risk score based on vulnerabilities found."""
        severity_weights = {
            'CRITICAL': 10,
            'HIGH': 7,
            'MEDIUM': 4,
            'LOW': 1
        }

        total_score = 0
        vuln_counts = {'CRITICAL': 0, 'HIGH': 0, 'MEDIUM': 0, 'LOW': 0}

        for category, vulns in vulnerabilities.items():
            for vuln in vulns:
                severity = vuln.get('severity', 'LOW')
                total_score += severity_weights.get(severity, 1)
                vuln_counts[severity] += 1

        # Risk level determination
        if total_score >= 30:
            risk_level = "CRITICAL"
        elif total_score >= 20:
            risk_level = "HIGH"
        elif total_score >= 10:
            risk_level = "MEDIUM"
        elif total_score > 0:
            risk_level = "LOW"
        else:
            risk_level = "MINIMAL"

        return {
            'score': total_score,
            'level': risk_level,
            'counts': vuln_counts,
            'total_vulnerabilities': sum(vuln_counts.values())
        }

    def _format_security_report(self, vulnerabilities: Dict[str, List[Dict[str, Any]]],
                              risk_score: Dict[str, Any], file_path: str, language: str) -> str:
        """Format the security scan results into a readable report."""
        report = []

        report.append("=== SECURITY SCAN REPORT ===\n")

        if file_path:
            report.append(f"File: {file_path}")
        report.append(f"Language: {language}")
        report.append(f"Risk Level: {risk_score['level']}")
        report.append(f"Risk Score: {risk_score['score']}")
        report.append(f"Total Vulnerabilities: {risk_score['total_vulnerabilities']}")
        report.append("")

        # Summary by severity
        if risk_score['total_vulnerabilities'] > 0:
            report.append("SEVERITY BREAKDOWN:")
            for severity in ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW']:
                count = risk_score['counts'][severity]
                if count > 0:
                    report.append(f"  • {severity}: {count}")
            report.append("")

        # Detailed vulnerabilities
        for category, vulns in vulnerabilities.items():
            if vulns:
                category_name = category.replace('_', ' ').title()
                report.append(f"{category_name.upper()}:")

                # Sort by severity
                severity_order = {'CRITICAL': 0, 'HIGH': 1, 'MEDIUM': 2, 'LOW': 3}
                vulns_sorted = sorted(vulns, key=lambda x: severity_order.get(x.get('severity', 'LOW'), 3))

                for vuln in vulns_sorted:
                    severity = vuln.get('severity', 'LOW')
                    line = vuln.get('line', 'Unknown')
                    description = vuln.get('description', '')
                    recommendation = vuln.get('recommendation', '')

                    report.append(f"  • [{severity}] Line {line}: {description}")
                    if recommendation:
                        report.append(f"    Recommendation: {recommendation}")

                report.append("")

        if risk_score['total_vulnerabilities'] == 0:
            report.append("✅ No security vulnerabilities detected!")
        else:
            report.append("RECOMMENDATIONS:")
            report.append("1. Review and address all CRITICAL and HIGH severity issues immediately")
            report.append("2. Implement proper input validation and sanitization")
            report.append("3. Use environment variables for sensitive configuration")
            report.append("4. Follow security best practices for your programming language")
            report.append("5. Consider using static analysis tools in your CI/CD pipeline")

        return "\n".join(report)