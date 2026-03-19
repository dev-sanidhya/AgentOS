"""
Security Scanner Tool for CrewAI Code Review Agent

A comprehensive security analysis tool for detecting vulnerabilities,
security issues, and potential threats in code files.

Author: {{author_name}}
Created: {{creation_date}}
"""

import re
import os
import ast
import json
import hashlib
from pathlib import Path
from typing import Dict, List, Any, Optional, Set, Tuple
from datetime import datetime
from dataclasses import dataclass

from crewai.tools import BaseTool
from pydantic import BaseModel, Field


class SecurityScanInput(BaseModel):
    """Input schema for security scan tool."""
    file_path: str = Field(description="Path to the file to scan for security issues")
    scan_type: str = Field(
        default="comprehensive",
        description="Type of scan: 'vulnerabilities', 'secrets', 'dependencies', or 'comprehensive'"
    )
    severity_threshold: str = Field(
        default="medium",
        description="Minimum severity level to report: 'low', 'medium', 'high', 'critical'"
    )


@dataclass
class SecurityFinding:
    """Data class for security findings."""
    id: str
    title: str
    description: str
    severity: str
    line_number: int
    code_snippet: str
    cwe_id: Optional[str] = None
    recommendation: str = ""
    confidence: str = "medium"


class SecurityScanner(BaseTool):
    """
    CrewAI tool for comprehensive security analysis.

    This tool provides security scanning capabilities including:
    - OWASP Top 10 vulnerability detection
    - Secret and credential scanning
    - Injection attack vector analysis
    - Authentication and authorization issues
    - Data handling and privacy concerns
    - Cryptographic weakness detection
    """

    name: str = "security_scanner"
    description: str = """
    Scan code files for security vulnerabilities and potential threats.

    This tool can detect:
    - SQL injection vulnerabilities
    - Cross-site scripting (XSS) issues
    - Command injection risks
    - Hard-coded secrets and credentials
    - Insecure cryptographic practices
    - Authentication and authorization flaws
    - Input validation issues
    - Path traversal vulnerabilities

    Input parameters:
    - file_path: Path to the file to scan
    - scan_type: Type of scan to perform
    - severity_threshold: Minimum severity level to report
    """
    args_schema: type[BaseModel] = SecurityScanInput

    def __init__(self):
        super().__init__()
        self.severity_levels = {"low": 1, "medium": 2, "high": 3, "critical": 4}
        self.findings = []
        self._initialize_security_patterns()

    def _initialize_security_patterns(self):
        """Initialize security vulnerability patterns."""
        self.vulnerability_patterns = {
            "sql_injection": {
                "patterns": [
                    r"(?i)(execute|exec)\s*\(\s*[\"'].*\+.*[\"']\s*\)",
                    r"(?i)query\s*=\s*[\"'][^\"']*\+[^\"']*[\"']",
                    r"(?i)sql\s*=.*\+.*",
                    r"(?i)(select|insert|update|delete)\s+.*\+.*",
                    r"cursor\.execute\s*\([^)]*\+[^)]*\)"
                ],
                "severity": "high",
                "cwe": "CWE-89",
                "title": "Potential SQL Injection"
            },
            "xss": {
                "patterns": [
                    r"(?i)innerHTML\s*=\s*.*\+.*",
                    r"(?i)document\.write\s*\(.*\+.*\)",
                    r"(?i)eval\s*\([^)]*request\.[^)]*\)",
                    r"(?i)render_template_string\s*\([^)]*\+[^)]*\)"
                ],
                "severity": "medium",
                "cwe": "CWE-79",
                "title": "Potential Cross-Site Scripting (XSS)"
            },
            "command_injection": {
                "patterns": [
                    r"(?i)(os\.system|subprocess\.call|subprocess\.run)\s*\([^)]*\+[^)]*\)",
                    r"(?i)eval\s*\([^)]*input[^)]*\)",
                    r"(?i)exec\s*\([^)]*input[^)]*\)",
                    r"(?i)shell_exec\s*\([^)]*\$[^)]*\)",
                    r"(?i)system\s*\([^)]*\+[^)]*\)"
                ],
                "severity": "critical",
                "cwe": "CWE-78",
                "title": "Potential Command Injection"
            },
            "path_traversal": {
                "patterns": [
                    r"(?i)open\s*\([^)]*\+[^)]*\)",
                    r"(?i)file\s*\([^)]*\.\.[^)]*\)",
                    r"(?i)include\s*\([^)]*\.\.[^)]*\)",
                    r"(?i)readfile\s*\([^)]*\+[^)]*\)"
                ],
                "severity": "medium",
                "cwe": "CWE-22",
                "title": "Potential Path Traversal"
            }
        }

        self.secret_patterns = {
            "api_key": {
                "patterns": [
                    r"(?i)(api[_-]?key|apikey)\s*[=:]\s*['\"][a-zA-Z0-9_-]{20,}['\"]",
                    r"(?i)key\s*[=:]\s*['\"][a-zA-Z0-9_-]{32,}['\"]"
                ],
                "severity": "high",
                "title": "Hard-coded API Key"
            },
            "password": {
                "patterns": [
                    r"(?i)(password|passwd|pwd)\s*[=:]\s*['\"][^'\"]{6,}['\"]",
                    r"(?i)pass\s*[=:]\s*['\"][a-zA-Z0-9@#$%^&*]{8,}['\"]"
                ],
                "severity": "critical",
                "title": "Hard-coded Password"
            },
            "private_key": {
                "patterns": [
                    r"-----BEGIN\s+(RSA\s+)?PRIVATE\s+KEY-----",
                    r"-----BEGIN\s+OPENSSH\s+PRIVATE\s+KEY-----"
                ],
                "severity": "critical",
                "title": "Private Key in Code"
            },
            "token": {
                "patterns": [
                    r"(?i)(access[_-]?token|accesstoken)\s*[=:]\s*['\"][a-zA-Z0-9_-]{20,}['\"]",
                    r"(?i)(bearer|jwt)\s+[a-zA-Z0-9_-]+\.[a-zA-Z0-9_-]+\.[a-zA-Z0-9_-]+"
                ],
                "severity": "high",
                "title": "Hard-coded Access Token"
            },
            "database_url": {
                "patterns": [
                    r"(?i)(mysql|postgresql|mongodb)://[^/\s]+:[^@\s]+@[^/\s]+",
                    r"(?i)database[_-]?url\s*[=:]\s*['\"][^'\"]*://[^'\"]*['\"]"
                ],
                "severity": "medium",
                "title": "Database Connection String"
            }
        }

        self.insecure_functions = {
            "python": [
                "eval", "exec", "compile", "input", "__import__",
                "os.system", "subprocess.call", "pickle.load", "yaml.load"
            ],
            "javascript": [
                "eval", "setTimeout", "setInterval", "Function",
                "document.write", "innerHTML", "outerHTML"
            ],
            "php": [
                "eval", "exec", "system", "shell_exec", "passthru",
                "file_get_contents", "include", "require"
            ]
        }

    def _run(
        self,
        file_path: str,
        scan_type: str = "comprehensive",
        severity_threshold: str = "medium"
    ) -> str:
        """
        Execute security scan.

        Args:
            file_path: Path to the file to scan
            scan_type: Type of scan to perform
            severity_threshold: Minimum severity level to report

        Returns:
            JSON string containing security scan results
        """
        try:
            # Validate file exists
            if not os.path.exists(file_path):
                return f"Error: File {file_path} does not exist"

            # Read file content
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
            except UnicodeDecodeError:
                try:
                    with open(file_path, 'r', encoding='latin-1') as f:
                        content = f.read()
                except Exception as e:
                    return f"Error reading file: {str(e)}"

            # Clear previous findings
            self.findings = []

            # Perform scans based on type
            file_info = self._get_file_info(file_path)

            if scan_type in ["vulnerabilities", "comprehensive"]:
                self._scan_vulnerabilities(content, file_info)

            if scan_type in ["secrets", "comprehensive"]:
                self._scan_secrets(content)

            if scan_type in ["dependencies", "comprehensive"]:
                self._scan_dependencies(content, file_info)

            # Additional comprehensive scans
            if scan_type == "comprehensive":
                self._scan_crypto_issues(content, file_info)
                self._scan_authentication_issues(content, file_info)
                self._scan_input_validation(content, file_info)

            # Filter by severity threshold
            threshold_level = self.severity_levels[severity_threshold]
            filtered_findings = [
                finding for finding in self.findings
                if self.severity_levels[finding.severity] >= threshold_level
            ]

            # Generate scan result
            scan_result = {
                "file_path": file_path,
                "timestamp": datetime.now().isoformat(),
                "scan_type": scan_type,
                "severity_threshold": severity_threshold,
                "findings_count": len(filtered_findings),
                "findings": [self._finding_to_dict(f) for f in filtered_findings],
                "summary": self._generate_security_summary(filtered_findings),
                "recommendations": self._generate_recommendations(filtered_findings)
            }

            return self._format_security_result(scan_result)

        except Exception as e:
            return f"Security scan failed: {str(e)}"

    def _get_file_info(self, file_path: str) -> Dict[str, Any]:
        """Get file information for context."""
        file_path_obj = Path(file_path)
        return {
            "name": file_path_obj.name,
            "extension": file_path_obj.suffix,
            "language": self._detect_language(file_path_obj.suffix)
        }

    def _detect_language(self, extension: str) -> str:
        """Detect programming language from file extension."""
        language_map = {
            '.py': 'python',
            '.js': 'javascript',
            '.ts': 'typescript',
            '.php': 'php',
            '.java': 'java',
            '.c': 'c',
            '.cpp': 'cpp',
            '.cs': 'csharp',
            '.rb': 'ruby',
            '.go': 'go'
        }
        return language_map.get(extension, 'unknown')

    def _scan_vulnerabilities(self, content: str, file_info: Dict[str, Any]):
        """Scan for common vulnerabilities."""
        lines = content.splitlines()

        for vuln_type, vuln_data in self.vulnerability_patterns.items():
            for pattern in vuln_data["patterns"]:
                for line_num, line in enumerate(lines, 1):
                    matches = re.finditer(pattern, line)
                    for match in matches:
                        finding = SecurityFinding(
                            id=self._generate_finding_id(vuln_type, line_num),
                            title=vuln_data["title"],
                            description=f"Potential {vuln_type} vulnerability detected",
                            severity=vuln_data["severity"],
                            line_number=line_num,
                            code_snippet=line.strip(),
                            cwe_id=vuln_data.get("cwe"),
                            recommendation=self._get_vulnerability_recommendation(vuln_type),
                            confidence="medium"
                        )
                        self.findings.append(finding)

        # Language-specific vulnerability checks
        language = file_info.get("language", "unknown")
        if language in self.insecure_functions:
            self._scan_insecure_functions(content, language)

    def _scan_secrets(self, content: str):
        """Scan for hard-coded secrets and credentials."""
        lines = content.splitlines()

        for secret_type, secret_data in self.secret_patterns.items():
            for pattern in secret_data["patterns"]:
                for line_num, line in enumerate(lines, 1):
                    matches = re.finditer(pattern, line)
                    for match in matches:
                        # Additional validation for false positives
                        if self._is_likely_secret(match.group(), secret_type):
                            finding = SecurityFinding(
                                id=self._generate_finding_id(secret_type, line_num),
                                title=secret_data["title"],
                                description=f"Hard-coded {secret_type} detected",
                                severity=secret_data["severity"],
                                line_number=line_num,
                                code_snippet=self._obfuscate_secret(line.strip()),
                                recommendation=f"Move {secret_type} to environment variables or secure storage",
                                confidence="high"
                            )
                            self.findings.append(finding)

    def _scan_dependencies(self, content: str, file_info: Dict[str, Any]):
        """Scan for dependency-related security issues."""
        language = file_info.get("language", "unknown")

        if language == "python":
            self._scan_python_dependencies(content)
        elif language in ["javascript", "typescript"]:
            self._scan_js_dependencies(content)

    def _scan_python_dependencies(self, content: str):
        """Scan Python dependencies for known vulnerabilities."""
        # Look for imports of potentially vulnerable packages
        vulnerable_packages = {
            "pickle": "Use alternatives like json for data serialization",
            "yaml": "Use yaml.safe_load() instead of yaml.load()",
            "subprocess": "Be careful with shell=True parameter",
            "os": "Avoid os.system() and similar functions"
        }

        lines = content.splitlines()
        for line_num, line in enumerate(lines, 1):
            for package, recommendation in vulnerable_packages.items():
                if re.search(rf"\b(import\s+{package}|from\s+{package}\s+import)", line):
                    # Check for specific risky usage
                    if package == "yaml" and "yaml.load(" in content and "Loader=" not in content:
                        finding = SecurityFinding(
                            id=self._generate_finding_id("yaml_unsafe", line_num),
                            title="Unsafe YAML Loading",
                            description="Using yaml.load() without specifying a Loader is dangerous",
                            severity="medium",
                            line_number=line_num,
                            code_snippet=line.strip(),
                            cwe_id="CWE-502",
                            recommendation="Use yaml.safe_load() or specify a safe Loader",
                            confidence="high"
                        )
                        self.findings.append(finding)

    def _scan_js_dependencies(self, content: str):
        """Scan JavaScript dependencies for security issues."""
        # Look for dangerous JavaScript patterns
        dangerous_patterns = [
            (r"jQuery.*\.html\s*\(.*\+", "Potential XSS via jQuery.html()"),
            (r"location\.href\s*=.*\+", "Potential open redirect"),
            (r"window\.open\s*\(.*\+", "Potential XSS via window.open"),
        ]

        lines = content.splitlines()
        for pattern, description in dangerous_patterns:
            for line_num, line in enumerate(lines, 1):
                if re.search(pattern, line):
                    finding = SecurityFinding(
                        id=self._generate_finding_id("js_security", line_num),
                        title="JavaScript Security Issue",
                        description=description,
                        severity="medium",
                        line_number=line_num,
                        code_snippet=line.strip(),
                        recommendation="Validate and sanitize user input",
                        confidence="medium"
                    )
                    self.findings.append(finding)

    def _scan_crypto_issues(self, content: str, file_info: Dict[str, Any]):
        """Scan for cryptographic weaknesses."""
        crypto_patterns = [
            (r"(?i)(md5|sha1)\s*\(", "Weak hash algorithm", "Use SHA-256 or stronger"),
            (r"(?i)des\s*\(", "Weak encryption", "Use AES or stronger encryption"),
            (r"(?i)random\s*\(", "Weak random number generation", "Use cryptographically secure random"),
        ]

        lines = content.splitlines()
        for pattern, title, recommendation in crypto_patterns:
            for line_num, line in enumerate(lines, 1):
                if re.search(pattern, line):
                    finding = SecurityFinding(
                        id=self._generate_finding_id("crypto_weak", line_num),
                        title=title,
                        description="Cryptographic weakness detected",
                        severity="medium",
                        line_number=line_num,
                        code_snippet=line.strip(),
                        recommendation=recommendation,
                        confidence="medium"
                    )
                    self.findings.append(finding)

    def _scan_authentication_issues(self, content: str, file_info: Dict[str, Any]):
        """Scan for authentication and authorization issues."""
        auth_patterns = [
            (r"(?i)password\s*==\s*['\"][^'\"]*['\"]", "Hard-coded password comparison"),
            (r"(?i)if.*user.*==.*admin", "Potential privilege escalation"),
            (r"(?i)session\s*\[\s*['\"]admin['\"]", "Direct session manipulation"),
        ]

        lines = content.splitlines()
        for pattern, description in auth_patterns:
            for line_num, line in enumerate(lines, 1):
                if re.search(pattern, line):
                    finding = SecurityFinding(
                        id=self._generate_finding_id("auth_issue", line_num),
                        title="Authentication Issue",
                        description=description,
                        severity="medium",
                        line_number=line_num,
                        code_snippet=line.strip(),
                        recommendation="Implement proper authentication and authorization",
                        confidence="medium"
                    )
                    self.findings.append(finding)

    def _scan_input_validation(self, content: str, file_info: Dict[str, Any]):
        """Scan for input validation issues."""
        input_patterns = [
            (r"(?i)(request\.get|request\[|params\[|$_GET|$_POST).*without.*validation", "Unvalidated input"),
            (r"(?i)int\s*\(\s*(input|request)", "Unsafe type conversion"),
        ]

        # Look for user input usage without validation
        lines = content.splitlines()
        for line_num, line in enumerate(lines, 1):
            # Generic input detection
            if re.search(r"(?i)(input\s*\(|request\.|params\.|args\.)", line):
                # Check if there's validation nearby
                context_lines = content.splitlines()[max(0, line_num-3):line_num+2]
                has_validation = any(
                    re.search(r"(?i)(validate|sanitize|clean|escape|filter)", context_line)
                    for context_line in context_lines
                )

                if not has_validation:
                    finding = SecurityFinding(
                        id=self._generate_finding_id("input_validation", line_num),
                        title="Potential Input Validation Issue",
                        description="User input used without apparent validation",
                        severity="low",
                        line_number=line_num,
                        code_snippet=line.strip(),
                        recommendation="Validate and sanitize all user input",
                        confidence="low"
                    )
                    self.findings.append(finding)

    def _scan_insecure_functions(self, content: str, language: str):
        """Scan for usage of insecure functions."""
        if language not in self.insecure_functions:
            return

        insecure_funcs = self.insecure_functions[language]
        lines = content.splitlines()

        for line_num, line in enumerate(lines, 1):
            for func in insecure_funcs:
                if func in line and not line.strip().startswith('#'):
                    finding = SecurityFinding(
                        id=self._generate_finding_id("insecure_function", line_num),
                        title=f"Insecure Function: {func}",
                        description=f"Usage of potentially dangerous function: {func}",
                        severity="medium",
                        line_number=line_num,
                        code_snippet=line.strip(),
                        recommendation=self._get_function_alternative(func),
                        confidence="medium"
                    )
                    self.findings.append(finding)

    def _is_likely_secret(self, text: str, secret_type: str) -> bool:
        """Determine if detected pattern is likely a real secret."""
        # Simple heuristics to reduce false positives
        if secret_type == "password":
            # Skip common placeholder passwords
            placeholders = ["password", "123456", "admin", "test", "example"]
            return not any(placeholder in text.lower() for placeholder in placeholders)

        if secret_type == "api_key":
            # API keys should be long enough and contain alphanumeric characters
            key_part = re.search(r'["\']([^"\']+)["\']', text)
            if key_part:
                key_value = key_part.group(1)
                return len(key_value) >= 20 and re.search(r'[a-zA-Z]', key_value) and re.search(r'[0-9]', key_value)

        return True

    def _obfuscate_secret(self, line: str) -> str:
        """Obfuscate secrets in code snippets."""
        # Replace potential secrets with asterisks
        patterns = [
            (r'(["\'])[^"\']{8,}(["\'])', r'\1********\2'),
            (r'(=\s*)[^"\'\s]{20,}', r'\1********')
        ]

        obfuscated = line
        for pattern, replacement in patterns:
            obfuscated = re.sub(pattern, replacement, obfuscated)

        return obfuscated

    def _get_vulnerability_recommendation(self, vuln_type: str) -> str:
        """Get specific recommendations for vulnerability types."""
        recommendations = {
            "sql_injection": "Use parameterized queries or prepared statements",
            "xss": "Sanitize user input and use proper output encoding",
            "command_injection": "Avoid dynamic command construction, use safe APIs",
            "path_traversal": "Validate file paths and use safe file access methods"
        }
        return recommendations.get(vuln_type, "Review and secure the code")

    def _get_function_alternative(self, func_name: str) -> str:
        """Get safer alternatives for insecure functions."""
        alternatives = {
            "eval": "Use ast.literal_eval() for safe evaluation",
            "exec": "Avoid dynamic code execution",
            "os.system": "Use subprocess.run() with proper arguments",
            "pickle.load": "Use json or other safe serialization formats",
            "yaml.load": "Use yaml.safe_load() instead",
            "setTimeout": "Use requestAnimationFrame for animations",
            "innerHTML": "Use textContent or createElement",
            "document.write": "Use DOM manipulation methods"
        }
        return alternatives.get(func_name, "Use a safer alternative")

    def _generate_finding_id(self, finding_type: str, line_number: int) -> str:
        """Generate unique finding ID."""
        return hashlib.md5(f"{finding_type}_{line_number}_{datetime.now().isoformat()}".encode()).hexdigest()[:8]

    def _finding_to_dict(self, finding: SecurityFinding) -> Dict[str, Any]:
        """Convert finding to dictionary."""
        return {
            "id": finding.id,
            "title": finding.title,
            "description": finding.description,
            "severity": finding.severity,
            "line_number": finding.line_number,
            "code_snippet": finding.code_snippet,
            "cwe_id": finding.cwe_id,
            "recommendation": finding.recommendation,
            "confidence": finding.confidence
        }

    def _generate_security_summary(self, findings: List[SecurityFinding]) -> Dict[str, Any]:
        """Generate summary of security findings."""
        severity_counts = {"low": 0, "medium": 0, "high": 0, "critical": 0}

        for finding in findings:
            severity_counts[finding.severity] += 1

        risk_score = (
            severity_counts["critical"] * 10 +
            severity_counts["high"] * 7 +
            severity_counts["medium"] * 4 +
            severity_counts["low"] * 1
        )

        if risk_score == 0:
            risk_level = "Low"
        elif risk_score <= 10:
            risk_level = "Medium"
        elif risk_score <= 25:
            risk_level = "High"
        else:
            risk_level = "Critical"

        return {
            "total_findings": len(findings),
            "severity_breakdown": severity_counts,
            "risk_score": risk_score,
            "risk_level": risk_level,
            "most_common_issues": self._get_most_common_issues(findings)
        }

    def _get_most_common_issues(self, findings: List[SecurityFinding]) -> List[str]:
        """Get most common security issues."""
        issue_counts = {}
        for finding in findings:
            issue_type = finding.title
            issue_counts[issue_type] = issue_counts.get(issue_type, 0) + 1

        # Return top 3 most common issues
        sorted_issues = sorted(issue_counts.items(), key=lambda x: x[1], reverse=True)
        return [issue for issue, count in sorted_issues[:3]]

    def _generate_recommendations(self, findings: List[SecurityFinding]) -> List[str]:
        """Generate prioritized recommendations."""
        recommendations = []

        # Critical and high severity recommendations first
        critical_high = [f for f in findings if f.severity in ["critical", "high"]]
        if critical_high:
            recommendations.append("Address critical and high severity vulnerabilities immediately")

        # Check for patterns
        has_injection = any("injection" in f.title.lower() for f in findings)
        if has_injection:
            recommendations.append("Implement input validation and parameterized queries")

        has_secrets = any("secret" in f.title.lower() or "password" in f.title.lower() for f in findings)
        if has_secrets:
            recommendations.append("Move sensitive data to environment variables or secure storage")

        has_crypto = any("crypto" in f.description.lower() or "hash" in f.title.lower() for f in findings)
        if has_crypto:
            recommendations.append("Update cryptographic implementations to use stronger algorithms")

        # General recommendations
        if len(findings) > 5:
            recommendations.append("Consider implementing automated security testing in CI/CD pipeline")

        if not recommendations:
            recommendations.append("Continue following security best practices")

        return recommendations[:5]  # Limit to top 5 recommendations

    def _format_security_result(self, scan_result: Dict[str, Any]) -> str:
        """Format security scan result as readable string."""
        output = []
        output.append("=" * 60)
        output.append("SECURITY SCAN REPORT")
        output.append("=" * 60)

        # Basic info
        output.append(f"File: {scan_result['file_path']}")
        output.append(f"Scan Type: {scan_result['scan_type']}")
        output.append(f"Timestamp: {scan_result['timestamp']}")
        output.append("")

        # Summary
        summary = scan_result["summary"]
        output.append("SECURITY SUMMARY:")
        output.append(f"  Total Findings: {summary['total_findings']}")
        output.append(f"  Risk Level: {summary['risk_level']}")
        output.append(f"  Risk Score: {summary['risk_score']}")
        output.append("")

        # Severity breakdown
        severity = summary["severity_breakdown"]
        if any(severity.values()):
            output.append("SEVERITY BREAKDOWN:")
            output.append(f"  Critical: {severity['critical']}")
            output.append(f"  High: {severity['high']}")
            output.append(f"  Medium: {severity['medium']}")
            output.append(f"  Low: {severity['low']}")
            output.append("")

        # Findings
        if scan_result["findings"]:
            output.append("SECURITY FINDINGS:")
            output.append("-" * 40)

            for finding in scan_result["findings"]:
                output.append(f"[{finding['severity'].upper()}] {finding['title']}")
                output.append(f"  Line {finding['line_number']}: {finding['code_snippet']}")
                output.append(f"  Description: {finding['description']}")
                output.append(f"  Recommendation: {finding['recommendation']}")
                if finding.get('cwe_id'):
                    output.append(f"  CWE: {finding['cwe_id']}")
                output.append("")

        # Recommendations
        if scan_result["recommendations"]:
            output.append("RECOMMENDATIONS:")
            for i, rec in enumerate(scan_result["recommendations"], 1):
                output.append(f"  {i}. {rec}")
            output.append("")

        output.append("=" * 60)
        return "\n".join(output)


# Example usage
if __name__ == "__main__":
    scanner = SecurityScanner()

    # Example usage
    test_file = "example.py"
    result = scanner._run(test_file, "comprehensive", "low")
    print(result)