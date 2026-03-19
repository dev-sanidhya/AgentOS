"""
{{AgentName}} - A comprehensive code review agent using LangChain.

This agent provides:
- Code quality analysis
- Security vulnerability detection
- Best practices validation
- Performance optimization suggestions
- Code quality scoring (1-10)
- Support for multiple programming languages
"""

import os
import json
import logging
import re
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from pathlib import Path

from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain.schema import BaseMessage
from langchain.callbacks.base import BaseCallbackHandler
from langchain.tools import BaseTool
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain.prompts import ChatPromptTemplate
from langchain.schema.runnable import Runnable
from dotenv import load_dotenv

from tools.file_analyzer import CodeAnalyzerTool
from tools.security_scanner import SecurityScannerTool
from prompts import (
    CODE_REVIEW_SYSTEM_PROMPT,
    CODE_ANALYSIS_PROMPT,
    SECURITY_REVIEW_PROMPT,
    QUALITY_SCORING_PROMPT
)

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class CodeReviewResult:
    """Data class for code review results."""
    file_path: str
    language: str
    quality_score: int
    issues: List[Dict[str, Any]]
    security_vulnerabilities: List[Dict[str, Any]]
    best_practices: List[Dict[str, Any]]
    performance_suggestions: List[Dict[str, Any]]
    summary: str
    overall_rating: str

class CodeReviewCallbackHandler(BaseCallbackHandler):
    """Custom callback handler for code review operations."""

    def on_tool_start(self, serialized: Dict[str, Any], input_str: str, **kwargs) -> None:
        logger.info(f"Starting tool: {serialized.get('name', 'Unknown')}")

    def on_tool_end(self, output: str, **kwargs) -> None:
        logger.info("Tool execution completed")

    def on_tool_error(self, error: Exception, **kwargs) -> None:
        logger.error(f"Tool execution error: {error}")

class {{AgentName}}:
    """
    A comprehensive code review agent using LangChain.

    Features:
    - Multi-language code analysis
    - Security vulnerability detection
    - Code quality scoring (1-10)
    - Performance optimization suggestions
    - Best practices validation
    """

    def __init__(
        self,
        model_provider: str = "openai",
        model_name: Optional[str] = None,
        temperature: float = 0.1,
        max_tokens: int = 4000,
        api_key: Optional[str] = None,
        max_iterations: int = 10,
        verbose: bool = False
    ):
        """
        Initialize the Code Review Agent.

        Args:
            model_provider: Either "openai" or "anthropic"
            model_name: Specific model name (optional)
            temperature: Model temperature for responses
            max_tokens: Maximum tokens for responses
            api_key: API key for the model provider
            max_iterations: Maximum agent iterations
            verbose: Enable verbose logging
        """
        self.model_provider = model_provider
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.max_iterations = max_iterations
        self.verbose = verbose

        # Initialize the language model
        self.llm = self._initialize_llm(model_name, api_key)

        # Initialize tools
        self.tools = self._initialize_tools()

        # Initialize the agent
        self.agent = self._create_agent()

        # Callback handler
        self.callback_handler = CodeReviewCallbackHandler()

        logger.info(f"{{AgentName}} initialized with {model_provider} model")

    def _initialize_llm(self, model_name: Optional[str], api_key: Optional[str]) -> Runnable:
        """Initialize the language model based on provider."""
        try:
            if self.model_provider == "openai":
                model_name = model_name or "gpt-4-turbo-preview"
                return ChatOpenAI(
                    model=model_name,
                    temperature=self.temperature,
                    max_tokens=self.max_tokens,
                    api_key=api_key or os.getenv("OPENAI_API_KEY")
                )
            elif self.model_provider == "anthropic":
                model_name = model_name or "claude-3-sonnet-20240229"
                return ChatAnthropic(
                    model=model_name,
                    temperature=self.temperature,
                    max_tokens=self.max_tokens,
                    api_key=api_key or os.getenv("ANTHROPIC_API_KEY")
                )
            else:
                raise ValueError(f"Unsupported model provider: {self.model_provider}")
        except Exception as e:
            logger.error(f"Failed to initialize LLM: {e}")
            raise

    def _initialize_tools(self) -> List[BaseTool]:
        """Initialize the tools for code analysis."""
        return [
            CodeAnalyzerTool(),
            SecurityScannerTool()
        ]

    def _create_agent(self) -> AgentExecutor:
        """Create the LangChain agent."""
        try:
            # Create the prompt template
            prompt = ChatPromptTemplate.from_messages([
                ("system", CODE_REVIEW_SYSTEM_PROMPT),
                ("human", "{input}"),
                ("placeholder", "{agent_scratchpad}")
            ])

            # Create the agent
            agent = create_openai_tools_agent(
                llm=self.llm,
                tools=self.tools,
                prompt=prompt
            )

            # Create the executor
            return AgentExecutor(
                agent=agent,
                tools=self.tools,
                verbose=self.verbose,
                handle_parsing_errors=True,
                max_iterations=self.max_iterations,
                return_intermediate_steps=True
            )
        except Exception as e:
            logger.error(f"Failed to create agent: {e}")
            raise

    def review_code(
        self,
        code_content: str,
        file_path: str = "",
        language: Optional[str] = None
    ) -> CodeReviewResult:
        """
        Perform a comprehensive code review.

        Args:
            code_content: The code to review
            file_path: Path to the code file (optional)
            language: Programming language (auto-detected if not provided)

        Returns:
            CodeReviewResult with comprehensive analysis
        """
        try:
            if self.verbose:
                print(f"🔍 Starting code review for {file_path or 'provided code'}")

            # Auto-detect language if not provided
            if not language:
                language = self._detect_language(code_content, file_path)

            # Prepare the input for the agent
            review_input = {
                "input": f"""
                Please perform a comprehensive code review of the following {language} code:

                File: {file_path}
                Language: {language}

                Code:
                ```{language}
                {code_content}
                ```

                Please analyze for:
                1. Code quality and maintainability (provide a score 1-10)
                2. Security vulnerabilities
                3. Performance issues
                4. Best practices adherence
                5. Specific line-by-line feedback where applicable

                Use the available tools to perform detailed analysis.
                """
            }

            # Execute the agent
            result = self.agent.invoke(
                review_input,
                callbacks=[self.callback_handler] if not self.verbose else None
            )

            # Parse and structure the result
            return self._parse_review_result(
                result["output"],
                file_path,
                language,
                code_content
            )

        except Exception as e:
            logger.error(f"Code review failed: {e}")
            raise

    def review_file(self, file_path: str) -> CodeReviewResult:
        """
        Review a code file.

        Args:
            file_path: Path to the code file

        Returns:
            CodeReviewResult with comprehensive analysis
        """
        try:
            if self.verbose:
                print(f"🔍 Starting review of: {file_path}")

            # Validate file exists
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"File not found: {file_path}")

            # Read the file
            with open(file_path, 'r', encoding='utf-8') as f:
                code_content = f.read()

            # Detect language from file extension
            language = self._detect_language_from_extension(file_path)

            return self.review_code(code_content, file_path, language)

        except Exception as e:
            logger.error(f"Failed to review file {file_path}: {e}")
            raise

    def review_files(self, file_paths: List[str]) -> List[CodeReviewResult]:
        """
        Review multiple files.

        Args:
            file_paths: List of file paths to review

        Returns:
            List of CodeReviewResult for each file
        """
        results = []
        for file_path in file_paths:
            try:
                result = self.review_file(file_path)
                results.append(result)
                if self.verbose:
                    print(f"✅ Reviewed {file_path}")
            except Exception as e:
                logger.error(f"Failed to review {file_path}: {e}")
                continue
        return results

    def review_directory(
        self,
        directory_path: str,
        file_extensions: Optional[List[str]] = None,
        exclude_patterns: Optional[List[str]] = None
    ) -> List[CodeReviewResult]:
        """
        Review all code files in a directory.

        Args:
            directory_path: Path to the directory
            file_extensions: List of file extensions to include (optional)
            exclude_patterns: List of patterns to exclude (optional)

        Returns:
            List of CodeReviewResult for each file
        """
        try:
            if self.verbose:
                print(f"🔍 Starting directory review: {directory_path}")

            results = []
            directory = Path(directory_path)

            # Default extensions if not provided
            if not file_extensions:
                file_extensions = ['.py', '.js', '.ts', '.java', '.go', '.rs', '.cpp', '.c', '.h', '.cs', '.php']

            # Default exclude patterns
            if not exclude_patterns:
                exclude_patterns = ['node_modules', '.git', '__pycache__', '.venv', 'venv', 'build', 'dist']

            # Find all code files
            for ext in file_extensions:
                for file_path in directory.rglob(f"*{ext}"):
                    if file_path.is_file():
                        # Check exclude patterns
                        if any(pattern in str(file_path) for pattern in exclude_patterns):
                            continue

                        try:
                            result = self.review_file(str(file_path))
                            results.append(result)
                            if self.verbose:
                                print(f"✅ Reviewed {file_path}")
                        except Exception as e:
                            logger.error(f"Failed to review {file_path}: {e}")
                            continue

            return results

        except Exception as e:
            logger.error(f"Failed to review directory {directory_path}: {e}")
            raise

    def review_git_changes(self, base_branch: str = "main") -> Dict[str, Any]:
        """
        Review changes in the current git branch compared to base branch.

        Args:
            base_branch: Base branch to compare against (default: "main")

        Returns:
            Dictionary containing the review results
        """
        try:
            if self.verbose:
                print(f"🔍 Starting git changes review against: {base_branch}")

            prompt = f"""
            Please review the git changes in the current branch compared to {base_branch}.

            Use the available tools to:
            1. Identify changed files
            2. Analyze the specific changes made
            3. Focus on new/modified code quality
            4. Check for security issues in changes
            5. Provide pull request style review

            Review should cover:
            - Summary of changes made
            - Quality of new/modified code
            - Potential issues introduced
            - Impact on existing functionality
            - Testing recommendations
            - Approval recommendation (Approve/Changes Requested/Comment)
            """

            result = self.agent.invoke(
                {"input": prompt},
                callbacks=[self.callback_handler] if not self.verbose else None
            )

            return {
                "base_branch": base_branch,
                "review": result["output"],
                "tools_used": len(result.get("intermediate_steps", [])),
                "success": True
            }

        except Exception as e:
            logger.error(f"Git changes review failed: {e}")
            return {
                "base_branch": base_branch,
                "review": f"Review failed: {str(e)}",
                "success": False,
                "error": str(e)
            }

    def _detect_language(self, code_content: str, file_path: str = "") -> str:
        """Auto-detect programming language."""
        if file_path:
            return self._detect_language_from_extension(file_path)

        # Simple heuristic-based detection
        content_lower = code_content.lower()

        if "def " in content_lower and ("import " in content_lower or "from " in content_lower):
            return "python"
        elif "function " in content_lower and ("var " in content_lower or "const " in content_lower or "let " in content_lower):
            return "javascript"
        elif "interface " in content_lower or "type " in content_lower:
            return "typescript"
        elif "class " in content_lower and "public static void main" in content_lower:
            return "java"
        elif "func " in content_lower and "package " in content_lower:
            return "go"
        elif "fn " in content_lower and ("use " in content_lower or "extern " in content_lower):
            return "rust"
        elif "#include" in content_lower and ("int main" in content_lower or "void main" in content_lower):
            return "c"
        elif "#include" in content_lower and "std::" in content_lower:
            return "cpp"
        else:
            return "unknown"

    def _detect_language_from_extension(self, file_path: str) -> str:
        """Detect language from file extension."""
        extension = Path(file_path).suffix.lower()

        language_map = {
            '.py': 'python',
            '.js': 'javascript',
            '.ts': 'typescript',
            '.tsx': 'typescript',
            '.jsx': 'javascript',
            '.java': 'java',
            '.go': 'go',
            '.rs': 'rust',
            '.cpp': 'cpp',
            '.cxx': 'cpp',
            '.cc': 'cpp',
            '.c': 'c',
            '.h': 'c',
            '.hpp': 'cpp',
            '.cs': 'csharp',
            '.php': 'php',
            '.rb': 'ruby',
            '.swift': 'swift',
            '.kt': 'kotlin',
            '.scala': 'scala',
            '.clj': 'clojure',
            '.r': 'r',
            '.m': 'objective-c',
            '.sh': 'bash',
            '.sql': 'sql'
        }

        return language_map.get(extension, 'unknown')

    def _parse_review_result(
        self,
        agent_output: str,
        file_path: str,
        language: str,
        code_content: str
    ) -> CodeReviewResult:
        """Parse the agent's output into a structured result."""
        try:
            # Extract quality score (this would be more sophisticated in practice)
            quality_score = self._extract_quality_score(agent_output)

            return CodeReviewResult(
                file_path=file_path,
                language=language,
                quality_score=quality_score,
                issues=self._extract_issues(agent_output),
                security_vulnerabilities=self._extract_security_issues(agent_output),
                best_practices=self._extract_best_practices(agent_output),
                performance_suggestions=self._extract_performance_suggestions(agent_output),
                summary=agent_output[:500] + "..." if len(agent_output) > 500 else agent_output,
                overall_rating=self._get_overall_rating(quality_score)
            )

        except Exception as e:
            logger.error(f"Failed to parse review result: {e}")
            # Return a basic result in case of parsing failure
            return CodeReviewResult(
                file_path=file_path,
                language=language,
                quality_score=5,
                issues=[],
                security_vulnerabilities=[],
                best_practices=[],
                performance_suggestions=[],
                summary="Review completed with parsing errors",
                overall_rating="Fair"
            )

    def _extract_quality_score(self, output: str) -> int:
        """Extract quality score from agent output."""
        score_patterns = [
            r'(?:quality\s*)?score[:\s]*(\d+)(?:/10)?',
            r'rating[:\s]*(\d+)(?:/10)?',
            r'(\d+)(?:/10)\s*(?:quality|score|rating)',
            r'(?:gives?\s*(?:it\s*)?(?:a\s*)?score\s*of\s*)(\d+)'
        ]

        for pattern in score_patterns:
            match = re.search(pattern, output.lower())
            if match:
                score = int(match.group(1))
                return min(10, max(1, score))

        return 6  # Default score if not found

    def _extract_issues(self, output: str) -> List[Dict[str, Any]]:
        """Extract code issues from agent output."""
        issues = []

        # Look for common issue indicators
        issue_patterns = [
            r'(?:issue|problem|concern|bug)[:,\s]*(.*?)(?:\n|$)',
            r'(?:line\s*\d+)[:,\s]*(.*?)(?:\n|$)',
            r'(?:warning|error)[:,\s]*(.*?)(?:\n|$)'
        ]

        for pattern in issue_patterns:
            matches = re.finditer(pattern, output.lower(), re.MULTILINE)
            for match in matches:
                issue_text = match.group(1).strip()
                if len(issue_text) > 10:  # Only include substantial issues
                    issues.append({
                        'type': 'code_issue',
                        'description': issue_text,
                        'severity': 'medium'
                    })

        return issues[:10]  # Limit to top 10 issues

    def _extract_security_issues(self, output: str) -> List[Dict[str, Any]]:
        """Extract security issues from agent output."""
        security_issues = []

        security_keywords = [
            'security', 'vulnerability', 'injection', 'xss', 'csrf',
            'authentication', 'authorization', 'encryption', 'password'
        ]

        lines = output.lower().split('\n')
        for line in lines:
            if any(keyword in line for keyword in security_keywords):
                if len(line.strip()) > 20:
                    security_issues.append({
                        'type': 'security',
                        'description': line.strip(),
                        'severity': 'high'
                    })

        return security_issues[:5]  # Limit to top 5 security issues

    def _extract_best_practices(self, output: str) -> List[Dict[str, Any]]:
        """Extract best practices violations from agent output."""
        best_practices = []

        practice_keywords = [
            'best practice', 'convention', 'style', 'naming',
            'documentation', 'comment', 'structure'
        ]

        lines = output.lower().split('\n')
        for line in lines:
            if any(keyword in line for keyword in practice_keywords):
                if len(line.strip()) > 15:
                    best_practices.append({
                        'type': 'best_practice',
                        'description': line.strip(),
                        'severity': 'low'
                    })

        return best_practices[:5]  # Limit to top 5 practices

    def _extract_performance_suggestions(self, output: str) -> List[Dict[str, Any]]:
        """Extract performance suggestions from agent output."""
        performance_suggestions = []

        performance_keywords = [
            'performance', 'optimization', 'efficiency', 'speed',
            'memory', 'algorithm', 'complexity', 'slow'
        ]

        lines = output.lower().split('\n')
        for line in lines:
            if any(keyword in line for keyword in performance_keywords):
                if len(line.strip()) > 15:
                    performance_suggestions.append({
                        'type': 'performance',
                        'description': line.strip(),
                        'severity': 'medium'
                    })

        return performance_suggestions[:5]  # Limit to top 5 suggestions

    def _get_overall_rating(self, score: int) -> str:
        """Get overall rating based on score."""
        if score >= 9:
            return "Excellent"
        elif score >= 7:
            return "Good"
        elif score >= 5:
            return "Fair"
        elif score >= 3:
            return "Poor"
        else:
            return "Critical"

    def generate_report(self, results: List[CodeReviewResult]) -> str:
        """Generate a comprehensive report from review results."""
        try:
            from datetime import datetime

            report_lines = []
            report_lines.append("# Code Review Report")
            report_lines.append(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            report_lines.append(f"Total files reviewed: {len(results)}")
            report_lines.append("")

            if not results:
                report_lines.append("No files were reviewed.")
                return "\n".join(report_lines)

            # Summary statistics
            scores = [r.quality_score for r in results]
            avg_score = sum(scores) / len(scores)
            total_issues = sum(len(r.issues) for r in results)
            total_security = sum(len(r.security_vulnerabilities) for r in results)

            report_lines.append("## Summary")
            report_lines.append(f"- Average quality score: {avg_score:.1f}/10")
            report_lines.append(f"- Total issues found: {total_issues}")
            report_lines.append(f"- Security vulnerabilities: {total_security}")
            report_lines.append("")

            # Individual file reports
            report_lines.append("## File Reviews")
            for result in results:
                report_lines.append(f"### {result.file_path}")
                report_lines.append(f"- **Language**: {result.language}")
                report_lines.append(f"- **Quality Score**: {result.quality_score}/10")
                report_lines.append(f"- **Overall Rating**: {result.overall_rating}")
                report_lines.append(f"- **Issues**: {len(result.issues)}")
                report_lines.append(f"- **Security Issues**: {len(result.security_vulnerabilities)}")
                report_lines.append("")

                if result.summary:
                    report_lines.append("**Summary:**")
                    report_lines.append(result.summary)
                    report_lines.append("")

            return "\n".join(report_lines)

        except Exception as e:
            logger.error(f"Failed to generate report: {e}")
            return "Failed to generate report"

# Convenience functions for quick usage
def review_file(
    file_path: str,
    model_provider: str = "openai",
    model_name: Optional[str] = None,
    verbose: bool = False
) -> str:
    """
    Quick file review function.

    Args:
        file_path: Path to file to review
        model_provider: Either "openai" or "anthropic"
        model_name: Specific model name (optional)
        verbose: Enable detailed logging

    Returns:
        Review text
    """
    agent = {{AgentName}}(
        model_provider=model_provider,
        model_name=model_name,
        verbose=verbose
    )
    result = agent.review_file(file_path)
    return result.summary

def review_files(
    file_paths: List[str],
    model_provider: str = "openai",
    model_name: Optional[str] = None,
    verbose: bool = False
) -> List[CodeReviewResult]:
    """
    Quick multi-file review function.

    Args:
        file_paths: List of file paths to review
        model_provider: Either "openai" or "anthropic"
        model_name: Specific model name (optional)
        verbose: Enable detailed logging

    Returns:
        List of CodeReviewResult
    """
    agent = {{AgentName}}(
        model_provider=model_provider,
        model_name=model_name,
        verbose=verbose
    )
    return agent.review_files(file_paths)

# Example usage
if __name__ == "__main__":
    # Initialize the agent
    reviewer = {{AgentName}}(model_provider="openai", verbose=True)

    # Example code to review
    sample_code = '''
def calculate_total(items):
    """Calculate the total price of items."""
    total = 0
    for item in items:
        if item:  # Basic null check
            total += item.price
    return total

# This function has some issues:
# 1. No error handling for missing price attribute
# 2. No input validation
# 3. Could use more Pythonic approach
'''

    # Review the code
    try:
        result = reviewer.review_code(sample_code, "example.py", "python")
        print("\n" + "="*50)
        print("CODE REVIEW RESULTS")
        print("="*50)
        print(f"Quality Score: {result.quality_score}/10")
        print(f"Overall Rating: {result.overall_rating}")
        print(f"Language: {result.language}")
        print("\nSummary:")
        print(result.summary)

        if result.issues:
            print(f"\nIssues Found ({len(result.issues)}):")
            for i, issue in enumerate(result.issues[:3], 1):
                print(f"{i}. {issue['description']}")

    except Exception as e:
        print(f"Error during code review: {e}")