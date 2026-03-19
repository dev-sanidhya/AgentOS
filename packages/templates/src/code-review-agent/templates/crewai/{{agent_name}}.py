"""
{{AgentName}} - Multi-Agent Code Review System using CrewAI

A comprehensive code review system powered by multiple specialized agents
working together to analyze code quality, security, and best practices.

Author: {{author_name}}
Created: {{creation_date}}
"""

import os
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any, Union

from crewai import Agent, Task, Crew, Process
from crewai.tools import BaseTool
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic

from .tools.file_analyzer import FileAnalyzer
from .tools.security_scanner import SecurityScanner


class {{AgentName}}:
    """
    Multi-Agent Code Review System using CrewAI framework.

    This system coordinates multiple specialized agents to perform comprehensive
    code reviews including syntax analysis, security scanning, and quality assessment.
    """

    def __init__(
        self,
        model_provider: str = "openai",
        model_name: str = "gpt-4o",
        api_key: Optional[str] = None,
        temperature: float = 0.1,
        max_tokens: int = 4000
    ):
        """
        Initialize the {{AgentName}} with specified configuration.

        Args:
            model_provider: The LLM provider ("openai" or "anthropic")
            model_name: Name of the model to use
            api_key: API key for the model provider
            temperature: Temperature for model responses
            max_tokens: Maximum tokens for responses
        """
        self.model_provider = model_provider
        self.model_name = model_name
        self.api_key = api_key or self._get_api_key()
        self.temperature = temperature
        self.max_tokens = max_tokens

        # Initialize LLM
        self.llm = self._initialize_llm()

        # Initialize tools
        self.file_analyzer = FileAnalyzer()
        self.security_scanner = SecurityScanner()

        # Initialize agents
        self.code_analyzer_agent = self._create_code_analyzer_agent()
        self.security_auditor_agent = self._create_security_auditor_agent()
        self.quality_reviewer_agent = self._create_quality_reviewer_agent()

        # Review results storage
        self.review_results = {}

    def _get_api_key(self) -> str:
        """Get API key from environment variables."""
        if self.model_provider == "openai":
            return os.getenv("OPENAI_API_KEY", "")
        elif self.model_provider == "anthropic":
            return os.getenv("ANTHROPIC_API_KEY", "")
        else:
            raise ValueError(f"Unsupported model provider: {self.model_provider}")

    def _initialize_llm(self):
        """Initialize the language model based on provider."""
        if self.model_provider == "openai":
            return ChatOpenAI(
                model=self.model_name,
                temperature=self.temperature,
                max_tokens=self.max_tokens,
                openai_api_key=self.api_key
            )
        elif self.model_provider == "anthropic":
            return ChatAnthropic(
                model=self.model_name,
                temperature=self.temperature,
                max_tokens_to_sample=self.max_tokens,
                anthropic_api_key=self.api_key
            )
        else:
            raise ValueError(f"Unsupported model provider: {self.model_provider}")

    def _create_code_analyzer_agent(self) -> Agent:
        """Create the Code Analyzer Agent."""
        return Agent(
            role="Senior Code Analyzer",
            goal="Analyze code syntax, structure, complexity, and maintainability",
            backstory="""You are a senior software engineer with 15+ years of experience
            in code analysis and architecture review. You excel at identifying code smells,
            complexity issues, and maintainability problems. Your expertise spans multiple
            programming languages and you can quickly spot anti-patterns and suggest
            improvements.""",
            verbose=True,
            allow_delegation=False,
            tools=[self.file_analyzer],
            llm=self.llm
        )

    def _create_security_auditor_agent(self) -> Agent:
        """Create the Security Auditor Agent."""
        return Agent(
            role="Cybersecurity Auditor",
            goal="Identify security vulnerabilities and potential threats in code",
            backstory="""You are a cybersecurity expert with deep knowledge of common
            vulnerabilities, security best practices, and threat modeling. You specialize
            in static code analysis for security issues including OWASP Top 10 vulnerabilities,
            injection attacks, authentication flaws, and data exposure risks.""",
            verbose=True,
            allow_delegation=False,
            tools=[self.security_scanner, self.file_analyzer],
            llm=self.llm
        )

    def _create_quality_reviewer_agent(self) -> Agent:
        """Create the Quality Reviewer Agent."""
        return Agent(
            role="Code Quality Reviewer",
            goal="Review code for best practices, documentation, and overall quality",
            backstory="""You are a senior technical lead who specializes in code quality,
            documentation standards, and development best practices. You have extensive
            experience in code reviews, team mentoring, and establishing coding standards.
            You focus on readability, documentation quality, naming conventions, and
            adherence to established patterns.""",
            verbose=True,
            allow_delegation=False,
            tools=[self.file_analyzer],
            llm=self.llm
        )

    def create_analysis_task(self, file_path: str, code_content: str) -> Task:
        """Create code analysis task."""
        return Task(
            description=f"""
            Analyze the code file at {file_path} for:
            1. Syntax correctness and language-specific best practices
            2. Code complexity and maintainability metrics
            3. Design patterns and architectural concerns
            4. Performance implications
            5. Error handling and edge cases

            Code content:
            ```
            {code_content}
            ```

            Provide a detailed analysis with specific recommendations and a complexity score (1-10).
            """,
            agent=self.code_analyzer_agent,
            expected_output="Detailed code analysis report with complexity score and recommendations"
        )

    def create_security_task(self, file_path: str, code_content: str) -> Task:
        """Create security analysis task."""
        return Task(
            description=f"""
            Perform a comprehensive security audit of the code file at {file_path}:
            1. Scan for common vulnerabilities (OWASP Top 10)
            2. Check for injection attack vectors
            3. Analyze authentication and authorization
            4. Review data handling and privacy concerns
            5. Identify potential security misconfigurations

            Code content:
            ```
            {code_content}
            ```

            Provide a security assessment with severity ratings and remediation steps.
            """,
            agent=self.security_auditor_agent,
            expected_output="Security audit report with vulnerability assessment and remediation recommendations"
        )

    def create_quality_task(self, file_path: str, code_content: str) -> Task:
        """Create quality review task."""
        return Task(
            description=f"""
            Review the code file at {file_path} for quality and best practices:
            1. Code readability and clarity
            2. Documentation quality and completeness
            3. Naming conventions and consistency
            4. Adherence to language-specific style guides
            5. Test coverage and testability
            6. Code organization and structure

            Code content:
            ```
            {code_content}
            ```

            Provide a quality assessment with improvement suggestions and a quality score (1-10).
            """,
            agent=self.quality_reviewer_agent,
            expected_output="Code quality review with quality score and improvement recommendations"
        )

    def review_code(
        self,
        file_path: str,
        code_content: Optional[str] = None,
        include_security: bool = True,
        include_quality: bool = True
    ) -> Dict[str, Any]:
        """
        Perform comprehensive code review using multiple agents.

        Args:
            file_path: Path to the code file to review
            code_content: Code content (if None, will read from file_path)
            include_security: Whether to include security analysis
            include_quality: Whether to include quality review

        Returns:
            Dictionary containing comprehensive review results
        """
        # Read code content if not provided
        if code_content is None:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    code_content = f.read()
            except Exception as e:
                return {"error": f"Failed to read file {file_path}: {str(e)}"}

        # Create tasks
        tasks = []

        # Always include code analysis
        analysis_task = self.create_analysis_task(file_path, code_content)
        tasks.append(analysis_task)

        # Add security analysis if requested
        if include_security:
            security_task = self.create_security_task(file_path, code_content)
            tasks.append(security_task)

        # Add quality review if requested
        if include_quality:
            quality_task = self.create_quality_task(file_path, code_content)
            tasks.append(quality_task)

        # Create crew with all agents
        agents = [self.code_analyzer_agent]
        if include_security:
            agents.append(self.security_auditor_agent)
        if include_quality:
            agents.append(self.quality_reviewer_agent)

        crew = Crew(
            agents=agents,
            tasks=tasks,
            process=Process.sequential,
            verbose=True
        )

        # Execute review
        try:
            results = crew.kickoff()

            # Parse and structure results
            review_result = {
                "file_path": file_path,
                "timestamp": datetime.now().isoformat(),
                "analysis": self._extract_analysis_results(results, tasks),
                "summary": self._generate_summary(results, tasks),
                "raw_results": str(results)
            }

            self.review_results[file_path] = review_result
            return review_result

        except Exception as e:
            return {"error": f"Review failed: {str(e)}"}

    def review_directory(
        self,
        directory_path: str,
        file_patterns: List[str] = None,
        recursive: bool = True
    ) -> Dict[str, Any]:
        """
        Review all code files in a directory.

        Args:
            directory_path: Path to directory to review
            file_patterns: List of file patterns to include (e.g., ['*.py', '*.js'])
            recursive: Whether to search subdirectories

        Returns:
            Dictionary containing results for all reviewed files
        """
        if file_patterns is None:
            file_patterns = ['*.py', '*.js', '*.ts', '*.java', '*.cpp', '*.c', '*.go', '*.rs']

        directory = Path(directory_path)
        files_to_review = []

        # Find files to review
        for pattern in file_patterns:
            if recursive:
                files_to_review.extend(directory.rglob(pattern))
            else:
                files_to_review.extend(directory.glob(pattern))

        # Review each file
        directory_results = {
            "directory": directory_path,
            "timestamp": datetime.now().isoformat(),
            "files_reviewed": len(files_to_review),
            "results": {},
            "summary": {}
        }

        for file_path in files_to_review:
            file_result = self.review_code(str(file_path))
            directory_results["results"][str(file_path)] = file_result

        # Generate directory summary
        directory_results["summary"] = self._generate_directory_summary(directory_results["results"])

        return directory_results

    def _extract_analysis_results(self, results: Any, tasks: List[Task]) -> Dict[str, Any]:
        """Extract and structure analysis results from crew output."""
        analysis = {}

        # Parse results based on task types
        result_parts = str(results).split('\n\n')

        for i, task in enumerate(tasks):
            if task.agent == self.code_analyzer_agent:
                analysis['code_analysis'] = result_parts[i] if i < len(result_parts) else ""
            elif task.agent == self.security_auditor_agent:
                analysis['security_audit'] = result_parts[i] if i < len(result_parts) else ""
            elif task.agent == self.quality_reviewer_agent:
                analysis['quality_review'] = result_parts[i] if i < len(result_parts) else ""

        return analysis

    def _generate_summary(self, results: Any, tasks: List[Task]) -> Dict[str, Any]:
        """Generate a summary of the review results."""
        summary = {
            "overall_score": 0,
            "key_issues": [],
            "recommendations": [],
            "agents_used": len(tasks)
        }

        # Extract key insights from results
        # This is a simplified implementation - in practice, you might use
        # more sophisticated parsing or additional LLM calls to generate summaries

        return summary

    def _generate_directory_summary(self, file_results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate summary for directory review."""
        summary = {
            "total_files": len(file_results),
            "successful_reviews": 0,
            "failed_reviews": 0,
            "common_issues": [],
            "overall_health": "Unknown"
        }

        for file_path, result in file_results.items():
            if "error" in result:
                summary["failed_reviews"] += 1
            else:
                summary["successful_reviews"] += 1

        return summary

    def generate_report(self, output_format: str = "json") -> str:
        """
        Generate a comprehensive report of all reviews.

        Args:
            output_format: Format for the report ("json", "html", "markdown")

        Returns:
            Formatted report string
        """
        if output_format == "json":
            return json.dumps(self.review_results, indent=2)
        elif output_format == "markdown":
            return self._generate_markdown_report()
        elif output_format == "html":
            return self._generate_html_report()
        else:
            raise ValueError(f"Unsupported output format: {output_format}")

    def _generate_markdown_report(self) -> str:
        """Generate a markdown report."""
        report = "# {{AgentName}} Code Review Report\n\n"
        report += f"Generated on: {datetime.now().isoformat()}\n\n"

        for file_path, result in self.review_results.items():
            report += f"## {file_path}\n\n"

            if "error" in result:
                report += f"**Error:** {result['error']}\n\n"
                continue

            # Add analysis sections
            analysis = result.get("analysis", {})

            if "code_analysis" in analysis:
                report += "### Code Analysis\n"
                report += f"{analysis['code_analysis']}\n\n"

            if "security_audit" in analysis:
                report += "### Security Audit\n"
                report += f"{analysis['security_audit']}\n\n"

            if "quality_review" in analysis:
                report += "### Quality Review\n"
                report += f"{analysis['quality_review']}\n\n"

        return report

    def _generate_html_report(self) -> str:
        """Generate an HTML report."""
        html = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>{{AgentName}} Code Review Report</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 20px; }
                .file-section { margin-bottom: 30px; border: 1px solid #ddd; padding: 15px; }
                .error { color: red; }
                .analysis-section { margin-bottom: 15px; }
                pre { background-color: #f4f4f4; padding: 10px; overflow-x: auto; }
            </style>
        </head>
        <body>
            <h1>{{AgentName}} Code Review Report</h1>
            <p>Generated on: """ + datetime.now().isoformat() + """</p>
        """

        for file_path, result in self.review_results.items():
            html += f'<div class="file-section">'
            html += f'<h2>{file_path}</h2>'

            if "error" in result:
                html += f'<p class="error">Error: {result["error"]}</p>'
                html += '</div>'
                continue

            analysis = result.get("analysis", {})

            for section_name, section_content in analysis.items():
                html += f'<div class="analysis-section">'
                html += f'<h3>{section_name.replace("_", " ").title()}</h3>'
                html += f'<pre>{section_content}</pre>'
                html += '</div>'

            html += '</div>'

        html += "</body></html>"
        return html

    def save_report(self, file_path: str, output_format: str = "json"):
        """Save the review report to a file."""
        report = self.generate_report(output_format)

        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(report)

    def clear_results(self):
        """Clear all stored review results."""
        self.review_results.clear()


# Example usage and CLI support
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="{{AgentName}} - Multi-Agent Code Review System")
    parser.add_argument("path", help="File or directory path to review")
    parser.add_argument("--provider", choices=["openai", "anthropic"], default="openai",
                       help="LLM provider to use")
    parser.add_argument("--model", default="gpt-4o", help="Model name to use")
    parser.add_argument("--output", help="Output file for report")
    parser.add_argument("--format", choices=["json", "html", "markdown"], default="json",
                       help="Output format for report")
    parser.add_argument("--recursive", action="store_true", help="Review directories recursively")

    args = parser.parse_args()

    # Initialize agent
    agent = {{AgentName}}(
        model_provider=args.provider,
        model_name=args.model
    )

    # Perform review
    path = Path(args.path)
    if path.is_file():
        result = agent.review_code(str(path))
        print(f"Reviewed file: {path}")
    elif path.is_dir():
        result = agent.review_directory(str(path), recursive=args.recursive)
        print(f"Reviewed directory: {path}")
    else:
        print(f"Error: Path {path} does not exist")
        exit(1)

    # Generate and save report
    if args.output:
        agent.save_report(args.output, args.format)
        print(f"Report saved to: {args.output}")
    else:
        print("\n" + "="*50)
        print("REVIEW REPORT")
        print("="*50)
        print(agent.generate_report(args.format))