"""
File Analyzer Tool for CrewAI Code Review Agent

A comprehensive tool for analyzing code files including syntax checking,
complexity analysis, and structural evaluation.

Author: {{author_name}}
Created: {{creation_date}}
"""

import ast
import os
import re
import subprocess
from pathlib import Path
from typing import Dict, List, Any, Optional, Union
from datetime import datetime

from crewai.tools import BaseTool
from pydantic import BaseModel, Field


class FileAnalysisInput(BaseModel):
    """Input schema for file analysis tool."""
    file_path: str = Field(description="Path to the file to analyze")
    analysis_type: str = Field(
        default="full",
        description="Type of analysis: 'syntax', 'complexity', 'structure', or 'full'"
    )
    include_metrics: bool = Field(
        default=True,
        description="Whether to include detailed metrics"
    )


class FileAnalyzer(BaseTool):
    """
    CrewAI tool for comprehensive file analysis.

    This tool provides detailed analysis of code files including:
    - Syntax validation
    - Complexity metrics (cyclomatic complexity, cognitive complexity)
    - Code structure analysis
    - Style and formatting checks
    - Import and dependency analysis
    """

    name: str = "file_analyzer"
    description: str = """
    Analyze code files for syntax, complexity, structure, and quality metrics.

    This tool can:
    - Check syntax validity
    - Calculate complexity metrics
    - Analyze code structure and organization
    - Identify code smells and anti-patterns
    - Generate comprehensive analysis reports

    Input parameters:
    - file_path: Path to the file to analyze
    - analysis_type: Type of analysis ('syntax', 'complexity', 'structure', 'full')
    - include_metrics: Whether to include detailed metrics
    """
    args_schema: type[BaseModel] = FileAnalysisInput

    def __init__(self):
        super().__init__()
        self.supported_languages = {
            '.py': 'python',
            '.js': 'javascript',
            '.ts': 'typescript',
            '.java': 'java',
            '.cpp': 'cpp',
            '.c': 'c',
            '.go': 'go',
            '.rs': 'rust',
            '.rb': 'ruby',
            '.php': 'php'
        }

    def _run(
        self,
        file_path: str,
        analysis_type: str = "full",
        include_metrics: bool = True
    ) -> str:
        """
        Execute file analysis.

        Args:
            file_path: Path to the file to analyze
            analysis_type: Type of analysis to perform
            include_metrics: Whether to include detailed metrics

        Returns:
            JSON string containing analysis results
        """
        try:
            # Validate file exists
            if not os.path.exists(file_path):
                return f"Error: File {file_path} does not exist"

            # Get file information
            file_info = self._get_file_info(file_path)

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

            # Perform analysis based on type
            analysis_result = {
                "file_info": file_info,
                "timestamp": datetime.now().isoformat(),
                "analysis_type": analysis_type
            }

            if analysis_type in ["syntax", "full"]:
                analysis_result["syntax_analysis"] = self._analyze_syntax(file_path, content)

            if analysis_type in ["complexity", "full"]:
                analysis_result["complexity_analysis"] = self._analyze_complexity(file_path, content)

            if analysis_type in ["structure", "full"]:
                analysis_result["structure_analysis"] = self._analyze_structure(file_path, content)

            if include_metrics:
                analysis_result["metrics"] = self._calculate_metrics(file_path, content)

            # Add overall assessment
            analysis_result["assessment"] = self._generate_assessment(analysis_result)

            return self._format_analysis_result(analysis_result)

        except Exception as e:
            return f"Analysis failed: {str(e)}"

    def _get_file_info(self, file_path: str) -> Dict[str, Any]:
        """Get basic file information."""
        file_path_obj = Path(file_path)
        stats = file_path_obj.stat()

        return {
            "name": file_path_obj.name,
            "extension": file_path_obj.suffix,
            "size_bytes": stats.st_size,
            "language": self.supported_languages.get(file_path_obj.suffix, "unknown"),
            "last_modified": datetime.fromtimestamp(stats.st_mtime).isoformat()
        }

    def _analyze_syntax(self, file_path: str, content: str) -> Dict[str, Any]:
        """Analyze file syntax."""
        file_ext = Path(file_path).suffix
        syntax_result = {
            "is_valid": True,
            "errors": [],
            "warnings": [],
            "language_specific": {}
        }

        if file_ext == '.py':
            syntax_result.update(self._analyze_python_syntax(content))
        elif file_ext in ['.js', '.ts']:
            syntax_result.update(self._analyze_javascript_syntax(content, file_ext))
        else:
            syntax_result.update(self._analyze_generic_syntax(content))

        return syntax_result

    def _analyze_python_syntax(self, content: str) -> Dict[str, Any]:
        """Analyze Python syntax specifically."""
        result = {
            "is_valid": True,
            "errors": [],
            "warnings": [],
            "language_specific": {
                "python_version_compatibility": [],
                "import_analysis": {},
                "function_definitions": 0,
                "class_definitions": 0
            }
        }

        try:
            # Parse AST
            tree = ast.parse(content)

            # Count definitions
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    result["language_specific"]["function_definitions"] += 1
                elif isinstance(node, ast.ClassDef):
                    result["language_specific"]["class_definitions"] += 1

            # Analyze imports
            imports = []
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        imports.append(alias.name)
                elif isinstance(node, ast.ImportFrom):
                    module = node.module if node.module else ""
                    for alias in node.names:
                        imports.append(f"{module}.{alias.name}")

            result["language_specific"]["import_analysis"] = {
                "total_imports": len(imports),
                "unique_imports": list(set(imports)),
                "potential_issues": self._check_import_issues(imports)
            }

        except SyntaxError as e:
            result["is_valid"] = False
            result["errors"].append(f"Syntax error at line {e.lineno}: {e.msg}")
        except Exception as e:
            result["warnings"].append(f"Analysis warning: {str(e)}")

        return result

    def _analyze_javascript_syntax(self, content: str, file_ext: str) -> Dict[str, Any]:
        """Analyze JavaScript/TypeScript syntax."""
        result = {
            "is_valid": True,
            "errors": [],
            "warnings": [],
            "language_specific": {
                "is_typescript": file_ext == '.ts',
                "function_count": 0,
                "class_count": 0,
                "import_count": 0
            }
        }

        # Basic syntax checks
        try:
            # Count functions
            function_patterns = [
                r'function\s+\w+',
                r'const\s+\w+\s*=\s*\(',
                r'let\s+\w+\s*=\s*\(',
                r'var\s+\w+\s*=\s*\(',
                r'\w+\s*:\s*function',
                r'=>'
            ]

            for pattern in function_patterns:
                matches = re.findall(pattern, content)
                result["language_specific"]["function_count"] += len(matches)

            # Count classes
            class_matches = re.findall(r'class\s+\w+', content)
            result["language_specific"]["class_count"] = len(class_matches)

            # Count imports
            import_matches = re.findall(r'import\s+.*from|require\s*\(', content)
            result["language_specific"]["import_count"] = len(import_matches)

        except Exception as e:
            result["warnings"].append(f"Analysis warning: {str(e)}")

        return result

    def _analyze_generic_syntax(self, content: str) -> Dict[str, Any]:
        """Generic syntax analysis for unsupported languages."""
        return {
            "is_valid": True,
            "errors": [],
            "warnings": ["Generic analysis - language-specific checks not available"],
            "language_specific": {
                "line_count": len(content.splitlines()),
                "character_count": len(content)
            }
        }

    def _analyze_complexity(self, file_path: str, content: str) -> Dict[str, Any]:
        """Analyze code complexity."""
        file_ext = Path(file_path).suffix

        complexity_result = {
            "cyclomatic_complexity": 0,
            "cognitive_complexity": 0,
            "nesting_depth": 0,
            "complexity_score": 0,
            "complexity_rating": "Unknown",
            "hotspots": []
        }

        if file_ext == '.py':
            complexity_result.update(self._calculate_python_complexity(content))
        else:
            complexity_result.update(self._calculate_generic_complexity(content))

        # Calculate overall complexity score (1-10)
        cc = complexity_result["cyclomatic_complexity"]
        if cc <= 5:
            complexity_result["complexity_score"] = min(3, max(1, cc))
            complexity_result["complexity_rating"] = "Low"
        elif cc <= 10:
            complexity_result["complexity_score"] = min(6, max(4, cc - 2))
            complexity_result["complexity_rating"] = "Moderate"
        elif cc <= 20:
            complexity_result["complexity_score"] = min(8, max(7, cc - 10))
            complexity_result["complexity_rating"] = "High"
        else:
            complexity_result["complexity_score"] = min(10, max(9, cc - 15))
            complexity_result["complexity_rating"] = "Very High"

        return complexity_result

    def _calculate_python_complexity(self, content: str) -> Dict[str, Any]:
        """Calculate complexity for Python code."""
        try:
            tree = ast.parse(content)

            complexity_visitor = ComplexityVisitor()
            complexity_visitor.visit(tree)

            return {
                "cyclomatic_complexity": complexity_visitor.cyclomatic_complexity,
                "cognitive_complexity": complexity_visitor.cognitive_complexity,
                "nesting_depth": complexity_visitor.max_nesting_depth,
                "function_complexities": complexity_visitor.function_complexities,
                "hotspots": complexity_visitor.get_hotspots()
            }

        except Exception as e:
            return {
                "cyclomatic_complexity": 0,
                "cognitive_complexity": 0,
                "nesting_depth": 0,
                "error": f"Complexity calculation failed: {str(e)}"
            }

    def _calculate_generic_complexity(self, content: str) -> Dict[str, Any]:
        """Generic complexity calculation."""
        lines = content.splitlines()

        # Count decision points (approximation)
        decision_keywords = ['if', 'else', 'elif', 'while', 'for', 'switch', 'case', 'catch', '&&', '||']
        cyclomatic = 1  # Base complexity

        for line in lines:
            for keyword in decision_keywords:
                cyclomatic += line.count(keyword)

        # Calculate nesting depth
        max_depth = 0
        current_depth = 0

        for line in lines:
            stripped = line.strip()
            if any(keyword in stripped for keyword in ['if', 'for', 'while', 'function', 'class']):
                current_depth += 1
                max_depth = max(max_depth, current_depth)
            # Simple approximation for closing braces
            if '}' in line or 'end' in stripped:
                current_depth = max(0, current_depth - 1)

        return {
            "cyclomatic_complexity": cyclomatic,
            "cognitive_complexity": cyclomatic,  # Approximation
            "nesting_depth": max_depth
        }

    def _analyze_structure(self, file_path: str, content: str) -> Dict[str, Any]:
        """Analyze code structure."""
        lines = content.splitlines()

        structure_result = {
            "total_lines": len(lines),
            "code_lines": 0,
            "comment_lines": 0,
            "blank_lines": 0,
            "average_line_length": 0,
            "longest_line": 0,
            "indentation_style": "unknown",
            "functions": [],
            "classes": [],
            "code_organization": {}
        }

        # Analyze line types
        code_lines = 0
        comment_lines = 0
        blank_lines = 0
        total_length = 0

        for line in lines:
            stripped = line.strip()
            if not stripped:
                blank_lines += 1
            elif stripped.startswith('#') or stripped.startswith('//') or stripped.startswith('*'):
                comment_lines += 1
            else:
                code_lines += 1

            total_length += len(line)
            structure_result["longest_line"] = max(structure_result["longest_line"], len(line))

        structure_result.update({
            "code_lines": code_lines,
            "comment_lines": comment_lines,
            "blank_lines": blank_lines,
            "average_line_length": total_length / len(lines) if lines else 0
        })

        # Detect indentation style
        structure_result["indentation_style"] = self._detect_indentation_style(content)

        # Language-specific structure analysis
        file_ext = Path(file_path).suffix
        if file_ext == '.py':
            structure_result.update(self._analyze_python_structure(content))

        return structure_result

    def _detect_indentation_style(self, content: str) -> str:
        """Detect indentation style (tabs vs spaces)."""
        lines = content.splitlines()
        tab_count = 0
        space_count = 0

        for line in lines:
            if line.startswith('\t'):
                tab_count += 1
            elif line.startswith('    '):
                space_count += 1

        if tab_count > space_count:
            return "tabs"
        elif space_count > tab_count:
            return "spaces (4)"
        else:
            return "mixed or unclear"

    def _analyze_python_structure(self, content: str) -> Dict[str, Any]:
        """Analyze Python-specific structure."""
        try:
            tree = ast.parse(content)

            functions = []
            classes = []

            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    functions.append({
                        "name": node.name,
                        "line": node.lineno,
                        "args_count": len(node.args.args),
                        "is_method": isinstance(node, ast.FunctionDef) and hasattr(node, 'decorator_list')
                    })
                elif isinstance(node, ast.ClassDef):
                    classes.append({
                        "name": node.name,
                        "line": node.lineno,
                        "methods": [n.name for n in node.body if isinstance(n, ast.FunctionDef)]
                    })

            return {
                "functions": functions,
                "classes": classes,
                "code_organization": {
                    "has_main_guard": "if __name__ == '__main__'" in content,
                    "docstrings_present": self._count_docstrings(tree),
                    "import_organization": "good" if self._check_import_organization(content) else "needs improvement"
                }
            }

        except Exception:
            return {"functions": [], "classes": [], "code_organization": {}}

    def _count_docstrings(self, tree: ast.AST) -> int:
        """Count docstrings in Python AST."""
        count = 0
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.ClassDef, ast.Module)):
                if (node.body and isinstance(node.body[0], ast.Expr) and
                    isinstance(node.body[0].value, ast.Str)):
                    count += 1
        return count

    def _check_import_organization(self, content: str) -> bool:
        """Check if imports are well-organized."""
        lines = content.splitlines()
        in_import_section = True
        found_non_import = False

        for line in lines:
            stripped = line.strip()
            if not stripped or stripped.startswith('#'):
                continue

            if stripped.startswith(('import ', 'from ')):
                if found_non_import:
                    return False  # Import after non-import code
            else:
                found_non_import = True
                in_import_section = False

        return True

    def _calculate_metrics(self, file_path: str, content: str) -> Dict[str, Any]:
        """Calculate additional code metrics."""
        lines = content.splitlines()

        metrics = {
            "maintainability_index": 0,
            "code_to_comment_ratio": 0,
            "duplicate_lines": 0,
            "technical_debt_minutes": 0,
            "readability_score": 0
        }

        # Calculate code-to-comment ratio
        code_lines = sum(1 for line in lines if line.strip() and not line.strip().startswith(('#', '//', '*')))
        comment_lines = sum(1 for line in lines if line.strip().startswith(('#', '//', '*')))

        if comment_lines > 0:
            metrics["code_to_comment_ratio"] = code_lines / comment_lines
        else:
            metrics["code_to_comment_ratio"] = float('inf')

        # Detect duplicate lines
        line_counts = {}
        for line in lines:
            stripped = line.strip()
            if stripped and not stripped.startswith(('#', '//', '*')):
                line_counts[stripped] = line_counts.get(stripped, 0) + 1

        metrics["duplicate_lines"] = sum(count - 1 for count in line_counts.values() if count > 1)

        # Simple readability score (1-10)
        avg_line_length = sum(len(line) for line in lines) / len(lines) if lines else 0
        if avg_line_length <= 80:
            readability = 8
        elif avg_line_length <= 120:
            readability = 6
        else:
            readability = 4

        # Adjust for comment ratio
        if comment_lines / len(lines) >= 0.2:
            readability += 1

        metrics["readability_score"] = min(10, readability)

        # Estimate technical debt (simplified)
        complexity_penalty = max(0, (metrics.get("cyclomatic_complexity", 0) - 10) * 5)
        duplicate_penalty = metrics["duplicate_lines"] * 2
        metrics["technical_debt_minutes"] = complexity_penalty + duplicate_penalty

        return metrics

    def _check_import_issues(self, imports: List[str]) -> List[str]:
        """Check for potential import issues."""
        issues = []

        # Check for known problematic imports
        problematic = ['os.system', 'eval', 'exec', 'input', '__import__']
        for imp in imports:
            if any(prob in imp for prob in problematic):
                issues.append(f"Potentially dangerous import: {imp}")

        # Check for unused-looking imports
        if len(imports) > 20:
            issues.append("High number of imports - consider refactoring")

        return issues

    def _generate_assessment(self, analysis_result: Dict[str, Any]) -> Dict[str, Any]:
        """Generate overall assessment of the code."""
        assessment = {
            "overall_score": 5,  # Default neutral score
            "strengths": [],
            "weaknesses": [],
            "recommendations": [],
            "priority_issues": []
        }

        # Analyze syntax
        syntax = analysis_result.get("syntax_analysis", {})
        if not syntax.get("is_valid", True):
            assessment["weaknesses"].append("Syntax errors present")
            assessment["priority_issues"].extend(syntax.get("errors", []))
            assessment["overall_score"] -= 2

        # Analyze complexity
        complexity = analysis_result.get("complexity_analysis", {})
        complexity_score = complexity.get("complexity_score", 5)

        if complexity_score <= 3:
            assessment["strengths"].append("Low complexity - easy to understand")
            assessment["overall_score"] += 1
        elif complexity_score >= 8:
            assessment["weaknesses"].append("High complexity - difficult to maintain")
            assessment["recommendations"].append("Consider refactoring complex functions")
            assessment["overall_score"] -= 1

        # Analyze structure
        structure = analysis_result.get("structure_analysis", {})
        comment_ratio = structure.get("comment_lines", 0) / max(structure.get("total_lines", 1), 1)

        if comment_ratio >= 0.2:
            assessment["strengths"].append("Well-documented code")
            assessment["overall_score"] += 0.5
        elif comment_ratio < 0.1:
            assessment["weaknesses"].append("Insufficient documentation")
            assessment["recommendations"].append("Add more comments and docstrings")

        # Analyze metrics
        metrics = analysis_result.get("metrics", {})
        readability = metrics.get("readability_score", 5)

        if readability >= 8:
            assessment["strengths"].append("Highly readable code")
        elif readability <= 4:
            assessment["weaknesses"].append("Poor readability")
            assessment["recommendations"].append("Improve code formatting and line length")

        # Final score adjustment
        assessment["overall_score"] = max(1, min(10, round(assessment["overall_score"], 1)))

        return assessment

    def _format_analysis_result(self, analysis_result: Dict[str, Any]) -> str:
        """Format analysis result as a readable string."""
        output = []
        output.append("=" * 60)
        output.append(f"FILE ANALYSIS REPORT")
        output.append("=" * 60)

        # File info
        file_info = analysis_result["file_info"]
        output.append(f"File: {file_info['name']}")
        output.append(f"Language: {file_info['language']}")
        output.append(f"Size: {file_info['size_bytes']} bytes")
        output.append(f"Last Modified: {file_info['last_modified']}")
        output.append("")

        # Assessment
        assessment = analysis_result.get("assessment", {})
        output.append(f"OVERALL SCORE: {assessment.get('overall_score', 'N/A')}/10")
        output.append("")

        # Syntax Analysis
        if "syntax_analysis" in analysis_result:
            syntax = analysis_result["syntax_analysis"]
            output.append("SYNTAX ANALYSIS:")
            output.append(f"  Valid: {syntax.get('is_valid', 'Unknown')}")
            if syntax.get("errors"):
                output.append("  Errors:")
                for error in syntax["errors"]:
                    output.append(f"    - {error}")
            if syntax.get("warnings"):
                output.append("  Warnings:")
                for warning in syntax["warnings"]:
                    output.append(f"    - {warning}")
            output.append("")

        # Complexity Analysis
        if "complexity_analysis" in analysis_result:
            complexity = analysis_result["complexity_analysis"]
            output.append("COMPLEXITY ANALYSIS:")
            output.append(f"  Cyclomatic Complexity: {complexity.get('cyclomatic_complexity', 'N/A')}")
            output.append(f"  Complexity Rating: {complexity.get('complexity_rating', 'Unknown')}")
            output.append(f"  Max Nesting Depth: {complexity.get('nesting_depth', 'N/A')}")
            output.append("")

        # Structure Analysis
        if "structure_analysis" in analysis_result:
            structure = analysis_result["structure_analysis"]
            output.append("STRUCTURE ANALYSIS:")
            output.append(f"  Total Lines: {structure.get('total_lines', 'N/A')}")
            output.append(f"  Code Lines: {structure.get('code_lines', 'N/A')}")
            output.append(f"  Comment Lines: {structure.get('comment_lines', 'N/A')}")
            output.append(f"  Indentation: {structure.get('indentation_style', 'Unknown')}")
            output.append("")

        # Assessment Summary
        if assessment:
            if assessment.get("strengths"):
                output.append("STRENGTHS:")
                for strength in assessment["strengths"]:
                    output.append(f"  + {strength}")
                output.append("")

            if assessment.get("weaknesses"):
                output.append("WEAKNESSES:")
                for weakness in assessment["weaknesses"]:
                    output.append(f"  - {weakness}")
                output.append("")

            if assessment.get("recommendations"):
                output.append("RECOMMENDATIONS:")
                for rec in assessment["recommendations"]:
                    output.append(f"  → {rec}")
                output.append("")

        output.append("=" * 60)
        return "\n".join(output)


class ComplexityVisitor(ast.NodeVisitor):
    """AST visitor for calculating code complexity metrics."""

    def __init__(self):
        self.cyclomatic_complexity = 1  # Base complexity
        self.cognitive_complexity = 0
        self.nesting_depth = 0
        self.current_depth = 0
        self.max_nesting_depth = 0
        self.function_complexities = {}
        self.current_function = None

    def visit_FunctionDef(self, node):
        """Visit function definition."""
        old_function = self.current_function
        old_complexity = self.cyclomatic_complexity

        self.current_function = node.name
        self.cyclomatic_complexity = 1  # Reset for function

        self.generic_visit(node)

        self.function_complexities[node.name] = self.cyclomatic_complexity
        self.cyclomatic_complexity += old_complexity
        self.current_function = old_function

    def visit_If(self, node):
        """Visit if statement."""
        self.cyclomatic_complexity += 1
        self.cognitive_complexity += 1
        self.current_depth += 1
        self.max_nesting_depth = max(self.max_nesting_depth, self.current_depth)

        self.generic_visit(node)
        self.current_depth -= 1

    def visit_For(self, node):
        """Visit for loop."""
        self.cyclomatic_complexity += 1
        self.cognitive_complexity += 1
        self.current_depth += 1
        self.max_nesting_depth = max(self.max_nesting_depth, self.current_depth)

        self.generic_visit(node)
        self.current_depth -= 1

    def visit_While(self, node):
        """Visit while loop."""
        self.cyclomatic_complexity += 1
        self.cognitive_complexity += 1
        self.current_depth += 1
        self.max_nesting_depth = max(self.max_nesting_depth, self.current_depth)

        self.generic_visit(node)
        self.current_depth -= 1

    def visit_Try(self, node):
        """Visit try statement."""
        self.cyclomatic_complexity += len(node.handlers)
        self.cognitive_complexity += len(node.handlers)
        self.generic_visit(node)

    def get_hotspots(self) -> List[Dict[str, Any]]:
        """Get complexity hotspots."""
        hotspots = []
        for func_name, complexity in self.function_complexities.items():
            if complexity > 10:
                hotspots.append({
                    "function": func_name,
                    "complexity": complexity,
                    "severity": "high" if complexity > 15 else "medium"
                })
        return hotspots


# Example usage
if __name__ == "__main__":
    analyzer = FileAnalyzer()

    # Example usage
    test_file = "example.py"
    result = analyzer._run(test_file, "full", True)
    print(result)