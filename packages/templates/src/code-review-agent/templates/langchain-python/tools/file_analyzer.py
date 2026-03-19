"""
Code analysis tool for comprehensive code review.
Analyzes code quality, structure, patterns, and best practices.
"""

import ast
import re
import os
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path

from langchain.tools import BaseTool
from pydantic import BaseModel, Field


class FileAnalyzerInput(BaseModel):
    """Input schema for the FileAnalyzer tool."""
    code_content: str = Field(description="The code content to analyze")
    file_path: Optional[str] = Field(default="", description="Path to the file being analyzed")
    language: Optional[str] = Field(default="", description="Programming language of the code")


class CodeAnalyzerTool(BaseTool):
    """
    Tool for analyzing code quality, structure, and best practices.

    This tool provides:
    - Code complexity analysis
    - Function/method analysis
    - Variable naming analysis
    - Code structure analysis
    - Best practices checking
    - Performance pattern detection
    """

    name: str = "code_analyzer"
    description: str = """Analyze code for quality, complexity, and best practices.
    Input should be a JSON with: {"code_content": "code to analyze", "file_path": "optional/path", "language": "optional language"}"""

    args_schema: type[BaseModel] = FileAnalyzerInput

    def _run(self, code_content: str, file_path: str = "", language: str = "") -> str:
        """
        Analyze the provided code content.

        Args:
            code_content: The code to analyze
            file_path: Optional file path
            language: Optional language hint

        Returns:
            Detailed analysis report
        """
        try:
            # Auto-detect language if not provided
            if not language:
                language = self._detect_language(code_content, file_path)

            analysis_result = {
                "file_path": file_path,
                "language": language,
                "metrics": self._calculate_metrics(code_content, language),
                "complexity": self._analyze_complexity(code_content, language),
                "structure": self._analyze_structure(code_content, language),
                "naming": self._analyze_naming(code_content, language),
                "best_practices": self._check_best_practices(code_content, language),
                "performance": self._analyze_performance(code_content, language),
                "maintainability": self._assess_maintainability(code_content, language)
            }

            return self._format_analysis_result(analysis_result)

        except Exception as e:
            return f"Error analyzing code: {str(e)}"

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
                '.php': 'php'
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

    def _calculate_metrics(self, code_content: str, language: str) -> Dict[str, Any]:
        """Calculate basic code metrics."""
        lines = code_content.split('\n')

        metrics = {
            "total_lines": len(lines),
            "non_empty_lines": len([line for line in lines if line.strip()]),
            "comment_lines": self._count_comment_lines(lines, language),
            "code_lines": 0,
            "average_line_length": 0,
            "max_line_length": 0
        }

        code_lines = [line for line in lines if line.strip() and not self._is_comment_line(line.strip(), language)]
        metrics["code_lines"] = len(code_lines)

        if code_lines:
            metrics["average_line_length"] = sum(len(line) for line in code_lines) / len(code_lines)
            metrics["max_line_length"] = max(len(line) for line in code_lines)

        return metrics

    def _count_comment_lines(self, lines: List[str], language: str) -> int:
        """Count comment lines based on language."""
        comment_count = 0
        comment_patterns = {
            'python': [r'^\s*#', r'^\s*"""', r'^\s*\'\'\''],
            'javascript': [r'^\s*//', r'^\s*/\*', r'^\s*\*'],
            'typescript': [r'^\s*//', r'^\s*/\*', r'^\s*\*'],
            'java': [r'^\s*//', r'^\s*/\*', r'^\s*\*'],
            'c': [r'^\s*//', r'^\s*/\*', r'^\s*\*'],
            'cpp': [r'^\s*//', r'^\s*/\*', r'^\s*\*'],
            'go': [r'^\s*//', r'^\s*/\*', r'^\s*\*']
        }

        patterns = comment_patterns.get(language, [r'^\s*//', r'^\s*#'])

        for line in lines:
            if any(re.match(pattern, line) for pattern in patterns):
                comment_count += 1

        return comment_count

    def _is_comment_line(self, line: str, language: str) -> bool:
        """Check if a line is a comment."""
        comment_starts = {
            'python': ['#', '"""', "'''"],
            'javascript': ['//', '/*'],
            'typescript': ['//', '/*'],
            'java': ['//', '/*'],
            'c': ['//', '/*'],
            'cpp': ['//', '/*'],
            'go': ['//', '/*']
        }

        starts = comment_starts.get(language, ['//', '#'])
        return any(line.startswith(start) for start in starts)

    def _analyze_complexity(self, code_content: str, language: str) -> Dict[str, Any]:
        """Analyze code complexity."""
        complexity = {
            "cyclomatic_complexity": self._calculate_cyclomatic_complexity(code_content, language),
            "nesting_depth": self._calculate_nesting_depth(code_content, language),
            "function_count": self._count_functions(code_content, language),
            "class_count": self._count_classes(code_content, language)
        }

        return complexity

    def _calculate_cyclomatic_complexity(self, code_content: str, language: str) -> int:
        """Calculate cyclomatic complexity (simplified)."""
        # Simplified complexity calculation based on control flow statements
        complexity_keywords = {
            'python': ['if', 'elif', 'else', 'for', 'while', 'try', 'except', 'and', 'or'],
            'javascript': ['if', 'else', 'for', 'while', 'switch', 'case', 'try', 'catch', '&&', '||'],
            'typescript': ['if', 'else', 'for', 'while', 'switch', 'case', 'try', 'catch', '&&', '||'],
            'java': ['if', 'else', 'for', 'while', 'switch', 'case', 'try', 'catch', '&&', '||'],
            'go': ['if', 'else', 'for', 'switch', 'case', 'defer', '&&', '||']
        }

        keywords = complexity_keywords.get(language, ['if', 'else', 'for', 'while'])

        complexity = 1  # Base complexity
        for keyword in keywords:
            pattern = r'\b' + re.escape(keyword) + r'\b'
            matches = re.findall(pattern, code_content, re.IGNORECASE)
            complexity += len(matches)

        return min(complexity, 50)  # Cap at reasonable level

    def _calculate_nesting_depth(self, code_content: str, language: str) -> int:
        """Calculate maximum nesting depth."""
        lines = code_content.split('\n')
        max_depth = 0
        current_depth = 0

        if language == 'python':
            # Python uses indentation
            for line in lines:
                stripped = line.lstrip()
                if stripped:
                    indent = len(line) - len(stripped)
                    depth = indent // 4  # Assuming 4-space indentation
                    max_depth = max(max_depth, depth)
        else:
            # Brace-based languages
            for line in lines:
                current_depth += line.count('{') - line.count('}')
                max_depth = max(max_depth, current_depth)

        return max_depth

    def _count_functions(self, code_content: str, language: str) -> int:
        """Count function definitions."""
        function_patterns = {
            'python': [r'^\s*def\s+\w+'],
            'javascript': [r'function\s+\w+', r'^\s*\w+\s*:\s*function', r'^\s*\w+\s*=>\s*'],
            'typescript': [r'function\s+\w+', r'^\s*\w+\s*:\s*function', r'^\s*\w+\s*=>\s*'],
            'java': [r'(public|private|protected)?\s*(static)?\s*\w+\s+\w+\s*\('],
            'go': [r'func\s+\w+'],
            'c': [r'^\s*\w+\s+\w+\s*\('],
            'cpp': [r'^\s*\w+\s+\w+\s*\(']
        }

        patterns = function_patterns.get(language, [r'function\s+\w+', r'def\s+\w+'])

        count = 0
        for pattern in patterns:
            matches = re.findall(pattern, code_content, re.MULTILINE | re.IGNORECASE)
            count += len(matches)

        return count

    def _count_classes(self, code_content: str, language: str) -> int:
        """Count class definitions."""
        class_patterns = {
            'python': [r'^\s*class\s+\w+'],
            'javascript': [r'class\s+\w+'],
            'typescript': [r'class\s+\w+', r'interface\s+\w+'],
            'java': [r'(public|private)?\s*class\s+\w+'],
            'go': [r'type\s+\w+\s+struct'],
            'cpp': [r'class\s+\w+'],
            'c': [r'typedef\s+struct']
        }

        patterns = class_patterns.get(language, [r'class\s+\w+'])

        count = 0
        for pattern in patterns:
            matches = re.findall(pattern, code_content, re.MULTILINE | re.IGNORECASE)
            count += len(matches)

        return count

    def _analyze_structure(self, code_content: str, language: str) -> Dict[str, Any]:
        """Analyze code structure."""
        structure = {
            "imports_at_top": self._check_imports_at_top(code_content, language),
            "consistent_indentation": self._check_consistent_indentation(code_content, language),
            "function_length_issues": self._check_function_lengths(code_content, language),
            "line_length_issues": self._check_line_lengths(code_content)
        }

        return structure

    def _check_imports_at_top(self, code_content: str, language: str) -> bool:
        """Check if imports are at the top of the file."""
        lines = [line.strip() for line in code_content.split('\n') if line.strip()]

        import_patterns = {
            'python': [r'^import\s+', r'^from\s+.*import'],
            'javascript': [r'^import\s+', r'^const\s+.*=\s*require'],
            'typescript': [r'^import\s+'],
            'java': [r'^import\s+'],
            'go': [r'^import\s+']
        }

        patterns = import_patterns.get(language, [r'^import\s+'])

        # Find first import and first non-import code line
        first_import_line = -1
        first_code_line = -1

        for i, line in enumerate(lines):
            if any(re.match(pattern, line) for pattern in patterns):
                if first_import_line == -1:
                    first_import_line = i
            elif not line.startswith('#') and not line.startswith('//') and line:
                if first_code_line == -1:
                    first_code_line = i
                break

        # Imports should come before other code
        return first_import_line == -1 or first_code_line == -1 or first_import_line < first_code_line

    def _check_consistent_indentation(self, code_content: str, language: str) -> bool:
        """Check for consistent indentation."""
        lines = code_content.split('\n')
        indents = []

        for line in lines:
            if line.strip():  # Non-empty line
                indent = len(line) - len(line.lstrip())
                if indent > 0:
                    indents.append(indent)

        if not indents:
            return True

        # Check if all indents are multiples of the smallest indent
        min_indent = min(indents)
        return all(indent % min_indent == 0 for indent in indents)

    def _check_function_lengths(self, code_content: str, language: str) -> List[str]:
        """Check for overly long functions."""
        issues = []

        if language == 'python':
            try:
                tree = ast.parse(code_content)
                for node in ast.walk(tree):
                    if isinstance(node, ast.FunctionDef):
                        func_length = node.end_lineno - node.lineno + 1 if hasattr(node, 'end_lineno') else 0
                        if func_length > 50:  # Functions longer than 50 lines
                            issues.append(f"Function '{node.name}' is {func_length} lines long (consider breaking it down)")
            except:
                pass  # Ignore parsing errors

        return issues

    def _check_line_lengths(self, code_content: str) -> List[str]:
        """Check for overly long lines."""
        issues = []
        lines = code_content.split('\n')

        for i, line in enumerate(lines, 1):
            if len(line) > 120:  # Lines longer than 120 characters
                issues.append(f"Line {i} is {len(line)} characters long (recommended max: 120)")

        return issues[:5]  # Return first 5 issues

    def _analyze_naming(self, code_content: str, language: str) -> Dict[str, Any]:
        """Analyze naming conventions."""
        naming = {
            "naming_issues": self._check_naming_conventions(code_content, language),
            "descriptive_names": self._check_descriptive_names(code_content, language)
        }

        return naming

    def _check_naming_conventions(self, code_content: str, language: str) -> List[str]:
        """Check naming conventions."""
        issues = []

        if language == 'python':
            # Check for snake_case in Python
            functions = re.findall(r'def\s+(\w+)', code_content)
            for func in functions:
                if not re.match(r'^[a-z_][a-z0-9_]*$', func):
                    issues.append(f"Function '{func}' should use snake_case naming")

            # Check for PascalCase classes
            classes = re.findall(r'class\s+(\w+)', code_content)
            for cls in classes:
                if not re.match(r'^[A-Z][a-zA-Z0-9]*$', cls):
                    issues.append(f"Class '{cls}' should use PascalCase naming")

        elif language in ['javascript', 'typescript']:
            # Check for camelCase in JavaScript/TypeScript
            functions = re.findall(r'function\s+(\w+)', code_content)
            for func in functions:
                if not re.match(r'^[a-z][a-zA-Z0-9]*$', func):
                    issues.append(f"Function '{func}' should use camelCase naming")

        return issues[:5]  # Return first 5 issues

    def _check_descriptive_names(self, code_content: str, language: str) -> List[str]:
        """Check for descriptive variable names."""
        issues = []

        # Find short variable names that might not be descriptive
        variables = re.findall(r'\b([a-z]{1,2})\b', code_content.lower())
        common_short = {'i', 'j', 'k', 'x', 'y', 'z', 'id', 'db', 'ui'}

        for var in set(variables):
            if len(var) <= 2 and var not in common_short:
                issues.append(f"Variable '{var}' might not be descriptive enough")

        return issues[:3]  # Return first 3 issues

    def _check_best_practices(self, code_content: str, language: str) -> List[str]:
        """Check for best practices violations."""
        issues = []

        if language == 'python':
            issues.extend(self._check_python_best_practices(code_content))
        elif language in ['javascript', 'typescript']:
            issues.extend(self._check_js_best_practices(code_content))
        elif language == 'java':
            issues.extend(self._check_java_best_practices(code_content))

        return issues

    def _check_python_best_practices(self, code_content: str) -> List[str]:
        """Check Python-specific best practices."""
        issues = []

        # Check for bare except clauses
        if re.search(r'except\s*:', code_content):
            issues.append("Use specific exception types instead of bare 'except:'")

        # Check for mutable default arguments
        if re.search(r'def\s+\w+\([^)]*=\s*\[\]', code_content):
            issues.append("Avoid mutable default arguments (use None instead)")

        # Check for global variables
        if re.search(r'^global\s+\w+', code_content, re.MULTILINE):
            issues.append("Consider avoiding global variables")

        return issues

    def _check_js_best_practices(self, code_content: str) -> List[str]:
        """Check JavaScript/TypeScript best practices."""
        issues = []

        # Check for var usage (prefer let/const)
        if re.search(r'\bvar\s+', code_content):
            issues.append("Use 'let' or 'const' instead of 'var'")

        # Check for == instead of ===
        if re.search(r'(?<!=)==(?!=)', code_content):
            issues.append("Use strict equality (===) instead of loose equality (==)")

        return issues

    def _check_java_best_practices(self, code_content: str) -> List[str]:
        """Check Java best practices."""
        issues = []

        # Check for System.out.println in production code
        if re.search(r'System\.out\.print', code_content):
            issues.append("Consider using a logging framework instead of System.out.println")

        return issues

    def _analyze_performance(self, code_content: str, language: str) -> List[str]:
        """Analyze for performance issues."""
        issues = []

        if language == 'python':
            # Check for inefficient string concatenation
            if re.search(r'\+\s*=\s*.*\+', code_content):
                issues.append("Consider using string methods like join() for multiple string concatenations")

        elif language in ['javascript', 'typescript']:
            # Check for inefficient DOM queries
            if re.search(r'document\.getElementById.*loop', code_content, re.DOTALL):
                issues.append("Cache DOM queries outside of loops for better performance")

        return issues

    def _assess_maintainability(self, code_content: str, language: str) -> Dict[str, Any]:
        """Assess code maintainability."""
        metrics = self._calculate_metrics(code_content, language)
        complexity = self._analyze_complexity(code_content, language)

        # Calculate maintainability index (simplified)
        # Based on Halstead metrics and cyclomatic complexity
        code_lines = metrics.get("code_lines", 1)
        cyclomatic = complexity.get("cyclomatic_complexity", 1)

        # Simple maintainability score (0-100)
        maintainability_score = max(0, 100 - (cyclomatic * 2) - (code_lines / 10))

        if maintainability_score > 80:
            level = "High"
        elif maintainability_score > 60:
            level = "Medium"
        else:
            level = "Low"

        return {
            "score": round(maintainability_score, 1),
            "level": level,
            "factors": {
                "complexity": "High" if cyclomatic > 10 else "Acceptable",
                "size": "Large" if code_lines > 100 else "Acceptable"
            }
        }

    def _format_analysis_result(self, analysis: Dict[str, Any]) -> str:
        """Format the analysis result into a readable report."""
        report = []

        report.append("=== CODE ANALYSIS REPORT ===\n")

        if analysis["file_path"]:
            report.append(f"File: {analysis['file_path']}")
        report.append(f"Language: {analysis['language']}")
        report.append("")

        # Metrics
        metrics = analysis["metrics"]
        report.append("METRICS:")
        report.append(f"  • Total lines: {metrics['total_lines']}")
        report.append(f"  • Code lines: {metrics['code_lines']}")
        report.append(f"  • Comment lines: {metrics['comment_lines']}")
        report.append(f"  • Average line length: {metrics['average_line_length']:.1f}")
        report.append(f"  • Max line length: {metrics['max_line_length']}")
        report.append("")

        # Complexity
        complexity = analysis["complexity"]
        report.append("COMPLEXITY:")
        report.append(f"  • Cyclomatic complexity: {complexity['cyclomatic_complexity']}")
        report.append(f"  • Max nesting depth: {complexity['nesting_depth']}")
        report.append(f"  • Functions: {complexity['function_count']}")
        report.append(f"  • Classes: {complexity['class_count']}")
        report.append("")

        # Structure issues
        structure = analysis["structure"]
        if not structure["imports_at_top"]:
            report.append("STRUCTURE ISSUES:")
            report.append("  • Imports should be at the top of the file")

        if not structure["consistent_indentation"]:
            report.append("  • Inconsistent indentation detected")

        for issue in structure["function_length_issues"]:
            report.append(f"  • {issue}")

        for issue in structure["line_length_issues"]:
            report.append(f"  • {issue}")

        # Naming issues
        naming = analysis["naming"]
        if naming["naming_issues"] or naming["descriptive_names"]:
            report.append("\nNAMING ISSUES:")
            for issue in naming["naming_issues"]:
                report.append(f"  • {issue}")
            for issue in naming["descriptive_names"]:
                report.append(f"  • {issue}")

        # Best practices
        if analysis["best_practices"]:
            report.append("\nBEST PRACTICES:")
            for practice in analysis["best_practices"]:
                report.append(f"  • {practice}")

        # Performance
        if analysis["performance"]:
            report.append("\nPERFORMANCE:")
            for perf in analysis["performance"]:
                report.append(f"  • {perf}")

        # Maintainability
        maintainability = analysis["maintainability"]
        report.append(f"\nMAINTAINABILITY:")
        report.append(f"  • Score: {maintainability['score']}/100 ({maintainability['level']})")
        report.append(f"  • Complexity: {maintainability['factors']['complexity']}")
        report.append(f"  • Size: {maintainability['factors']['size']}")

        return "\n".join(report)