"""
File Analysis Tool for Code Review Agent

This module provides comprehensive file analysis capabilities for the code review agent.
It includes functionality to read files, detect languages, extract metrics, and perform
basic static analysis without external dependencies.
"""

import os
import re
import ast
import json
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from collections import defaultdict


@dataclass
class FileMetrics:
    """Metrics for a code file."""
    lines_of_code: int
    lines_of_comments: int
    blank_lines: int
    cyclomatic_complexity: int
    function_count: int
    class_count: int
    max_line_length: int
    average_line_length: float


@dataclass
class CodeIssue:
    """Represents a code issue found during analysis."""
    line_number: int
    column: int
    severity: str  # "error", "warning", "info"
    issue_type: str
    message: str
    suggestion: Optional[str] = None


class FileAnalyzer:
    """Comprehensive file analysis tool for code review."""

    def __init__(self):
        self.supported_extensions = {
            '.py': 'Python',
            '.js': 'JavaScript',
            '.ts': 'TypeScript',
            '.jsx': 'React JSX',
            '.tsx': 'React TSX',
            '.java': 'Java',
            '.cpp': 'C++',
            '.c': 'C',
            '.cs': 'C#',
            '.php': 'PHP',
            '.rb': 'Ruby',
            '.go': 'Go',
            '.rs': 'Rust',
            '.swift': 'Swift',
            '.kt': 'Kotlin',
            '.scala': 'Scala',
            '.sql': 'SQL',
            '.html': 'HTML',
            '.css': 'CSS',
            '.json': 'JSON',
            '.yaml': 'YAML',
            '.yml': 'YAML',
            '.xml': 'XML',
            '.md': 'Markdown',
        }

    def analyze_file(self, file_path: str) -> Dict[str, Any]:
        """
        Perform comprehensive analysis of a single file.

        Args:
            file_path: Path to the file to analyze

        Returns:
            Dictionary containing analysis results
        """
        try:
            file_path = os.path.expanduser(file_path)

            # Validate file
            validation_result = self.validate_file(file_path)
            if not validation_result['valid']:
                return {
                    'success': False,
                    'error': validation_result['error'],
                    'file_path': file_path
                }

            # Read file content
            content = self.read_file_content(file_path)
            if content is None:
                return {
                    'success': False,
                    'error': 'Failed to read file content',
                    'file_path': file_path
                }

            # Detect language
            language = self.detect_language(file_path)

            # Calculate metrics
            metrics = self.calculate_metrics(content, language)

            # Find issues
            issues = self.find_issues(content, language, file_path)

            # Generate summary
            summary = self.generate_summary(content, language, metrics, issues)

            return {
                'success': True,
                'file_path': file_path,
                'language': language,
                'metrics': metrics,
                'issues': issues,
                'summary': summary,
                'content': content[:2000] + "..." if len(content) > 2000 else content
            }

        except Exception as e:
            return {
                'success': False,
                'error': f"Analysis failed: {str(e)}",
                'file_path': file_path
            }

    def validate_file(self, file_path: str) -> Dict[str, Any]:
        """Validate that the file can be analyzed."""
        if not os.path.exists(file_path):
            return {'valid': False, 'error': f"File does not exist: {file_path}"}

        if not os.path.isfile(file_path):
            return {'valid': False, 'error': f"Path is not a file: {file_path}"}

        # Check file size (limit to 1MB)
        file_size = os.path.getsize(file_path)
        if file_size > 1024 * 1024:
            return {'valid': False, 'error': f"File too large: {file_size} bytes (max 1MB)"}

        # Check if binary
        try:
            with open(file_path, 'rb') as f:
                chunk = f.read(1024)
                if b'\0' in chunk:
                    return {'valid': False, 'error': "Binary file detected"}
        except Exception:
            return {'valid': False, 'error': "Cannot read file"}

        return {'valid': True, 'size': file_size}

    def read_file_content(self, file_path: str) -> Optional[str]:
        """Read and return file content."""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                return f.read()
        except Exception:
            return None

    def detect_language(self, file_path: str) -> str:
        """Detect programming language from file extension."""
        ext = Path(file_path).suffix.lower()
        return self.supported_extensions.get(ext, 'Unknown')

    def calculate_metrics(self, content: str, language: str) -> FileMetrics:
        """Calculate comprehensive file metrics."""
        lines = content.splitlines()

        lines_of_code = 0
        lines_of_comments = 0
        blank_lines = 0
        max_line_length = 0
        total_line_length = 0

        comment_patterns = self._get_comment_patterns(language)

        for line in lines:
            stripped = line.strip()
            max_line_length = max(max_line_length, len(line))
            total_line_length += len(line)

            if not stripped:
                blank_lines += 1
            elif self._is_comment_line(stripped, comment_patterns):
                lines_of_comments += 1
            else:
                lines_of_code += 1

        average_line_length = total_line_length / len(lines) if lines else 0

        # Language-specific analysis
        function_count = 0
        class_count = 0
        cyclomatic_complexity = 1  # Base complexity

        if language == 'Python':
            try:
                tree = ast.parse(content)
                function_count = len([n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)])
                class_count = len([n for n in ast.walk(tree) if isinstance(n, ast.ClassDef)])
                cyclomatic_complexity = self._calculate_python_complexity(tree)
            except:
                pass
        else:
            # Basic heuristics for other languages
            function_count = self._count_functions_heuristic(content, language)
            class_count = self._count_classes_heuristic(content, language)
            cyclomatic_complexity = self._calculate_complexity_heuristic(content)

        return FileMetrics(
            lines_of_code=lines_of_code,
            lines_of_comments=lines_of_comments,
            blank_lines=blank_lines,
            cyclomatic_complexity=cyclomatic_complexity,
            function_count=function_count,
            class_count=class_count,
            max_line_length=max_line_length,
            average_line_length=average_line_length
        )

    def find_issues(self, content: str, language: str, file_path: str) -> List[CodeIssue]:
        """Find potential issues in the code."""
        issues = []
        lines = content.splitlines()

        # Generic issues
        issues.extend(self._find_generic_issues(lines))

        # Language-specific issues
        if language == 'Python':
            issues.extend(self._find_python_issues(content, lines))
        elif language in ['JavaScript', 'TypeScript']:
            issues.extend(self._find_javascript_issues(lines))
        elif language == 'Java':
            issues.extend(self._find_java_issues(lines))

        return issues

    def generate_summary(self, content: str, language: str, metrics: FileMetrics, issues: List[CodeIssue]) -> str:
        """Generate a summary of the file analysis."""
        critical_issues = len([i for i in issues if i.severity == 'error'])
        warnings = len([i for i in issues if i.severity == 'warning'])

        complexity_rating = "Low" if metrics.cyclomatic_complexity < 10 else "Medium" if metrics.cyclomatic_complexity < 20 else "High"

        summary = f"""File Analysis Summary:
- Language: {language}
- Lines of Code: {metrics.lines_of_code}
- Comments: {metrics.lines_of_comments}
- Functions: {metrics.function_count}
- Classes: {metrics.class_count}
- Cyclomatic Complexity: {metrics.cyclomatic_complexity} ({complexity_rating})
- Critical Issues: {critical_issues}
- Warnings: {warnings}
- Max Line Length: {metrics.max_line_length}"""

        return summary

    def list_files(self, directory: str = ".", patterns: List[str] = None, max_files: int = 100) -> List[str]:
        """List code files in a directory."""
        try:
            directory = os.path.expanduser(directory)
            path = Path(directory)

            if not path.exists():
                return []

            patterns = patterns or list(self.supported_extensions.keys())
            files = []

            for pattern in patterns:
                # Convert glob pattern to file extension
                if pattern.startswith('*.'):
                    ext = pattern[1:]  # Remove the *
                    if ext in self.supported_extensions:
                        files.extend(path.rglob(pattern))

            # Filter and sort
            code_files = []
            for file_path in files:
                if file_path.is_file():
                    # Skip hidden files and common ignore patterns
                    if not any(part.startswith('.') for part in file_path.parts):
                        # Skip common binary/cache files
                        skip_patterns = [
                            '__pycache__', 'node_modules', '.git', '.svn',
                            'dist', 'build', 'target', 'bin', 'obj'
                        ]

                        if not any(skip_pattern in str(file_path) for skip_pattern in skip_patterns):
                            if file_path.stat().st_size < 500 * 1024:  # 500KB limit
                                code_files.append(str(file_path.resolve()))

                if len(code_files) >= max_files:
                    break

            return sorted(code_files)

        except Exception:
            return []

    # Helper methods
    def _get_comment_patterns(self, language: str) -> List[str]:
        """Get comment patterns for a language."""
        patterns = {
            'Python': ['#'],
            'JavaScript': ['//', '/*', '*'],
            'TypeScript': ['//', '/*', '*'],
            'Java': ['//', '/*', '*'],
            'C': ['//', '/*', '*'],
            'C++': ['//', '/*', '*'],
            'C#': ['//', '/*', '*'],
            'PHP': ['//', '#', '/*', '*'],
            'Ruby': ['#'],
            'Go': ['//', '/*', '*'],
            'Rust': ['//', '/*', '*'],
            'Swift': ['//', '/*', '*'],
            'SQL': ['--', '/*', '*'],
        }
        return patterns.get(language, ['#', '//'])

    def _is_comment_line(self, line: str, patterns: List[str]) -> bool:
        """Check if a line is a comment."""
        return any(line.startswith(pattern) for pattern in patterns)

    def _calculate_python_complexity(self, tree: ast.AST) -> int:
        """Calculate cyclomatic complexity for Python code."""
        complexity = 1
        for node in ast.walk(tree):
            if isinstance(node, (ast.If, ast.While, ast.For, ast.Try, ast.With)):
                complexity += 1
            elif isinstance(node, ast.BoolOp):
                complexity += len(node.values) - 1
        return complexity

    def _count_functions_heuristic(self, content: str, language: str) -> int:
        """Count functions using heuristics."""
        patterns = {
            'JavaScript': [r'\bfunction\s+\w+', r'\w+\s*:\s*function', r'=>\s*{'],
            'TypeScript': [r'\bfunction\s+\w+', r'\w+\s*:\s*function', r'=>\s*{'],
            'Java': [r'\b(public|private|protected)?\s*(static\s+)?\w+\s+\w+\s*\('],
            'C++': [r'\w+\s+\w+\s*\(.*\)\s*{'],
            'C': [r'\w+\s+\w+\s*\(.*\)\s*{'],
        }

        if language in patterns:
            count = 0
            for pattern in patterns[language]:
                count += len(re.findall(pattern, content))
            return count
        return 0

    def _count_classes_heuristic(self, content: str, language: str) -> int:
        """Count classes using heuristics."""
        patterns = {
            'JavaScript': [r'\bclass\s+\w+'],
            'TypeScript': [r'\bclass\s+\w+'],
            'Java': [r'\bclass\s+\w+'],
            'C++': [r'\bclass\s+\w+'],
            'C#': [r'\bclass\s+\w+'],
        }

        if language in patterns:
            return len(re.findall(patterns[language][0], content))
        return 0

    def _calculate_complexity_heuristic(self, content: str) -> int:
        """Calculate complexity using heuristics."""
        complexity = 1
        complexity_keywords = [
            'if', 'while', 'for', 'switch', 'case', 'catch', 'try',
            '&&', '||', '?', 'elif', 'else if'
        ]

        for keyword in complexity_keywords:
            complexity += content.lower().count(keyword)

        return complexity

    def _find_generic_issues(self, lines: List[str]) -> List[CodeIssue]:
        """Find generic issues that apply to all languages."""
        issues = []

        for i, line in enumerate(lines, 1):
            # Long lines
            if len(line) > 120:
                issues.append(CodeIssue(
                    line_number=i,
                    column=121,
                    severity="warning",
                    issue_type="line_length",
                    message=f"Line too long ({len(line)} characters)",
                    suggestion="Break long lines for better readability"
                ))

            # Trailing whitespace
            if line.rstrip() != line:
                issues.append(CodeIssue(
                    line_number=i,
                    column=len(line.rstrip()) + 1,
                    severity="info",
                    issue_type="whitespace",
                    message="Trailing whitespace",
                    suggestion="Remove trailing whitespace"
                ))

            # Mixed tabs and spaces (basic check)
            if '\t' in line and '  ' in line:
                issues.append(CodeIssue(
                    line_number=i,
                    column=1,
                    severity="warning",
                    issue_type="indentation",
                    message="Mixed tabs and spaces",
                    suggestion="Use consistent indentation (either tabs or spaces)"
                ))

        return issues

    def _find_python_issues(self, content: str, lines: List[str]) -> List[CodeIssue]:
        """Find Python-specific issues."""
        issues = []

        try:
            tree = ast.parse(content)

            # Find bare except clauses
            for node in ast.walk(tree):
                if isinstance(node, ast.ExceptHandler) and node.type is None:
                    issues.append(CodeIssue(
                        line_number=node.lineno,
                        column=node.col_offset,
                        severity="warning",
                        issue_type="bare_except",
                        message="Bare except clause",
                        suggestion="Specify exception types to catch"
                    ))

        except SyntaxError as e:
            issues.append(CodeIssue(
                line_number=e.lineno or 1,
                column=e.offset or 1,
                severity="error",
                issue_type="syntax_error",
                message=f"Syntax error: {e.msg}",
                suggestion="Fix syntax error"
            ))

        # Check for common anti-patterns in lines
        for i, line in enumerate(lines, 1):
            stripped = line.strip()

            # eval() usage
            if 'eval(' in stripped:
                issues.append(CodeIssue(
                    line_number=i,
                    column=stripped.find('eval(') + 1,
                    severity="error",
                    issue_type="security",
                    message="Use of eval() is dangerous",
                    suggestion="Use safer alternatives like ast.literal_eval()"
                ))

            # exec() usage
            if 'exec(' in stripped:
                issues.append(CodeIssue(
                    line_number=i,
                    column=stripped.find('exec(') + 1,
                    severity="error",
                    issue_type="security",
                    message="Use of exec() is dangerous",
                    suggestion="Avoid dynamic code execution"
                ))

        return issues

    def _find_javascript_issues(self, lines: List[str]) -> List[CodeIssue]:
        """Find JavaScript/TypeScript-specific issues."""
        issues = []

        for i, line in enumerate(lines, 1):
            stripped = line.strip()

            # eval() usage
            if 'eval(' in stripped:
                issues.append(CodeIssue(
                    line_number=i,
                    column=stripped.find('eval(') + 1,
                    severity="error",
                    issue_type="security",
                    message="Use of eval() is dangerous",
                    suggestion="Use JSON.parse() or other safer alternatives"
                ))

            # == instead of ===
            if '==' in stripped and '===' not in stripped and '!=' in stripped:
                issues.append(CodeIssue(
                    line_number=i,
                    column=stripped.find('==') + 1,
                    severity="warning",
                    issue_type="comparison",
                    message="Use strict equality (===) instead of (==)",
                    suggestion="Use === for type-safe comparisons"
                ))

        return issues

    def _find_java_issues(self, lines: List[str]) -> List[CodeIssue]:
        """Find Java-specific issues."""
        issues = []

        for i, line in enumerate(lines, 1):
            stripped = line.strip()

            # System.out.println in non-main methods
            if 'System.out.print' in stripped and 'public static void main' not in stripped:
                issues.append(CodeIssue(
                    line_number=i,
                    column=stripped.find('System.out.print') + 1,
                    severity="warning",
                    issue_type="best_practice",
                    message="Avoid System.out.println in production code",
                    suggestion="Use proper logging framework"
                ))

        return issues