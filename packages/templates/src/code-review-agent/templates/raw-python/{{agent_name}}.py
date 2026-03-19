"""
{{AgentName}} - Raw Python Implementation

A comprehensive, framework-agnostic code review agent that uses direct LLM API calls
and modular tools for file analysis, security scanning, and quality assessment.
Perfect for minimal dependencies and maximum control over the review process.
"""

import os
import time
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass
from pathlib import Path
from dotenv import load_dotenv

# Import our modular tools
from tools import (
    FileAnalyzer, FileMetrics, CodeIssue,
    SecurityScanner, SecurityIssue, SecurityReport,
    LLMClient, LLMConfig, LLMResponse, Models
)

# Load environment variables
load_dotenv()


@dataclass
class ReviewResult:
    """Comprehensive code review result."""
    file_or_files: str
    language: str
    review: str
    quality_score: Optional[int]
    security_score: Optional[int]
    issues_found: int
    security_issues: int
    duration: float
    success: bool
    error: Optional[str] = None

    # Detailed analysis data
    file_metrics: Optional[FileMetrics] = None
    security_report: Optional[SecurityReport] = None
    code_issues: Optional[List[CodeIssue]] = None


class {{AgentName}}:
    """
    Comprehensive code review agent using direct API calls and modular tools.

    This agent provides multi-layered code review by:
    1. File analysis and metrics calculation
    2. Security vulnerability detection
    3. LLM-powered quality assessment
    4. Best practices validation
    5. Performance and maintainability analysis
    """

    def __init__(
        self,
        model: str = "gpt-4",
        temperature: float = 0.3,
        verbose: bool = True,
        max_tokens: int = 4000
    ):
        self.verbose = verbose

        # Initialize modular components
        self.file_analyzer = FileAnalyzer()
        self.security_scanner = SecurityScanner()
        self.llm_client = LLMClient(LLMConfig(
            model=model,
            temperature=temperature,
            max_tokens=max_tokens
        ))

        # Validate API keys
        self._validate_setup()

    def review_file(self, file_path: str) -> ReviewResult:
        """
        Perform comprehensive review of a single file.

        Args:
            file_path: Path to the file to review

        Returns:
            ReviewResult with comprehensive analysis
        """
        start_time = time.time()

        try:
            if self.verbose:
                print(f"🔍 Starting comprehensive review of: {file_path}")

            # Step 1: File analysis
            if self.verbose:
                print("  📊 Analyzing file structure and metrics...")

            file_analysis = self.file_analyzer.analyze_file(file_path)
            if not file_analysis['success']:
                raise Exception(f"File analysis failed: {file_analysis['error']}")

            language = file_analysis['language']
            metrics = file_analysis['metrics']
            code_issues = file_analysis['issues']
            content = file_analysis.get('content', '')

            # Step 2: Security scanning
            if self.verbose:
                print("  🔒 Scanning for security vulnerabilities...")

            security_report = self.security_scanner.scan_file(
                file_path, content, language
            )

            # Step 3: LLM-powered review
            if self.verbose:
                print("  🤖 Generating AI-powered code review...")

            llm_response = self.llm_client.generate_structured_review(
                content, language, file_path
            )

            if not llm_response.success:
                raise Exception(f"LLM review failed: {llm_response.error}")

            # Step 4: Generate enhanced review
            enhanced_review = self._enhance_review_with_analysis(
                llm_response.content,
                file_analysis,
                security_report
            )

            # Step 5: Extract scores and metrics
            quality_score = self._extract_quality_score(enhanced_review)
            security_score = self._calculate_security_score(security_report)

            duration = time.time() - start_time

            if self.verbose:
                print(f"✅ Review completed in {duration:.1f}s")
                print(f"   Quality Score: {quality_score}/10")
                print(f"   Security Score: {security_score}/10")
                print(f"   Issues Found: {len(code_issues)}")
                print(f"   Security Issues: {security_report.total_issues}")

            return ReviewResult(
                file_or_files=file_path,
                language=language,
                review=enhanced_review,
                quality_score=quality_score,
                security_score=security_score,
                issues_found=len(code_issues),
                security_issues=security_report.total_issues,
                duration=duration,
                success=True,
                file_metrics=metrics,
                security_report=security_report,
                code_issues=code_issues
            )

        except Exception as e:
            duration = time.time() - start_time
            error_msg = str(e)

            if self.verbose:
                print(f"❌ Review failed: {error_msg}")

            return ReviewResult(
                file_or_files=file_path,
                language="Unknown",
                review=f"Review failed: {error_msg}",
                quality_score=None,
                security_score=None,
                issues_found=0,
                security_issues=0,
                duration=duration,
                success=False,
                error=error_msg
            )

    def review_files(self, file_paths: List[str]) -> ReviewResult:
        """
        Review multiple files together with cross-file analysis.

        Args:
            file_paths: List of file paths to review

        Returns:
            ReviewResult with combined analysis
        """
        start_time = time.time()

        try:
            if self.verbose:
                print(f"🔍 Starting multi-file review of {len(file_paths)} files")

            # Analyze each file individually
            file_analyses = []
            security_reports = []
            all_issues = []
            total_security_issues = 0

            for i, file_path in enumerate(file_paths, 1):
                if self.verbose:
                    print(f"  📂 Analyzing file {i}/{len(file_paths)}: {Path(file_path).name}")

                # File analysis
                analysis = self.file_analyzer.analyze_file(file_path)
                if analysis['success']:
                    file_analyses.append(analysis)
                    all_issues.extend(analysis.get('issues', []))

                    # Security analysis
                    content = analysis.get('content', '')
                    language = analysis.get('language', 'Unknown')
                    security_report = self.security_scanner.scan_file(
                        file_path, content, language
                    )
                    security_reports.append(security_report)
                    total_security_issues += security_report.total_issues

                elif self.verbose:
                    print(f"    ⚠️ Skipping {file_path}: {analysis.get('error', 'Unknown error')}")

            if not file_analyses:
                raise Exception("No valid files to review")

            # Generate multi-file review
            if self.verbose:
                print("  🤖 Generating comprehensive multi-file review...")

            context = f"Multi-file review of {len(file_analyses)} files"
            llm_response = self.llm_client.generate_multi_file_review(
                file_analyses, context
            )

            if not llm_response.success:
                raise Exception(f"Multi-file review failed: {llm_response.error}")

            # Enhanced review with cross-file analysis
            enhanced_review = self._enhance_multi_file_review(
                llm_response.content,
                file_analyses,
                security_reports
            )

            # Calculate scores
            quality_score = self._extract_quality_score(enhanced_review)
            security_score = self._calculate_multi_file_security_score(security_reports)

            duration = time.time() - start_time

            if self.verbose:
                print(f"✅ Multi-file review completed in {duration:.1f}s")
                print(f"   Overall Quality Score: {quality_score}/10")
                print(f"   Overall Security Score: {security_score}/10")

            return ReviewResult(
                file_or_files=f"{len(file_paths)} files",
                language="Mixed",
                review=enhanced_review,
                quality_score=quality_score,
                security_score=security_score,
                issues_found=len(all_issues),
                security_issues=total_security_issues,
                duration=duration,
                success=True
            )

        except Exception as e:
            duration = time.time() - start_time
            error_msg = str(e)

            if self.verbose:
                print(f"❌ Multi-file review failed: {error_msg}")

            return ReviewResult(
                file_or_files=f"{len(file_paths)} files",
                language="Mixed",
                review=f"Multi-file review failed: {error_msg}",
                quality_score=None,
                security_score=None,
                issues_found=0,
                security_issues=0,
                duration=duration,
                success=False,
                error=error_msg
            )

    def review_directory(
        self,
        directory: str,
        file_patterns: Optional[List[str]] = None,
        max_files: int = 50
    ) -> ReviewResult:
        """
        Review all files in a directory.

        Args:
            directory: Directory to review
            file_patterns: File patterns to match (e.g., ["*.py"])
            max_files: Maximum number of files to review

        Returns:
            ReviewResult with directory analysis
        """
        try:
            if self.verbose:
                print(f"🔍 Finding code files in directory: {directory}")

            # Find files
            files = self.file_analyzer.list_files(directory, file_patterns, max_files)

            if not files:
                raise Exception(f"No code files found in {directory}")

            if self.verbose:
                print(f"   Found {len(files)} files to review")

            # Review the found files
            return self.review_files(files)

        except Exception as e:
            return ReviewResult(
                file_or_files=directory,
                language="Mixed",
                review=f"Directory review failed: {str(e)}",
                quality_score=None,
                security_score=None,
                issues_found=0,
                security_issues=0,
                duration=0.0,
                success=False,
                error=str(e)
            )

    def quick_security_scan(self, file_path: str) -> SecurityReport:
        """
        Perform a quick security-only scan of a file.

        Args:
            file_path: Path to the file to scan

        Returns:
            SecurityReport with vulnerability details
        """
        try:
            # Read file
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()

            # Detect language
            language = self.file_analyzer.detect_language(file_path)

            # Scan for security issues
            return self.security_scanner.scan_file(file_path, content, language)

        except Exception as e:
            return SecurityReport(
                file_path=file_path,
                language="Unknown",
                total_issues=0,
                critical_issues=0,
                high_issues=0,
                medium_issues=0,
                low_issues=0,
                issues=[],
                risk_score=0
            )

    def _enhance_review_with_analysis(
        self,
        llm_review: str,
        file_analysis: Dict[str, Any],
        security_report: SecurityReport
    ) -> str:
        """Enhance LLM review with detailed analysis data."""

        metrics = file_analysis.get('metrics')
        issues = file_analysis.get('issues', [])

        enhanced_review = f"""{llm_review}

## Detailed Analysis

### File Metrics
- Lines of Code: {metrics.lines_of_code}
- Comments: {metrics.lines_of_comments} ({metrics.lines_of_comments / max(1, metrics.lines_of_code) * 100:.1f}% comment ratio)
- Blank Lines: {metrics.blank_lines}
- Functions: {metrics.function_count}
- Classes: {metrics.class_count}
- Cyclomatic Complexity: {metrics.cyclomatic_complexity}
- Max Line Length: {metrics.max_line_length}
- Average Line Length: {metrics.average_line_length:.1f}

### Security Analysis
- Total Security Issues: {security_report.total_issues}
- Critical: {security_report.critical_issues}
- High: {security_report.high_issues}
- Medium: {security_report.medium_issues}
- Low: {security_report.low_issues}
- Risk Score: {security_report.risk_score}/100

### Code Issues Found
{self._format_issues(issues)}

### Security Issues Found
{self._format_security_issues(security_report.issues)}
"""

        return enhanced_review

    def _enhance_multi_file_review(
        self,
        llm_review: str,
        file_analyses: List[Dict],
        security_reports: List[SecurityReport]
    ) -> str:
        """Enhance multi-file review with aggregated analysis."""

        total_loc = sum(analysis['metrics'].lines_of_code for analysis in file_analyses)
        total_functions = sum(analysis['metrics'].function_count for analysis in file_analyses)
        total_classes = sum(analysis['metrics'].class_count for analysis in file_analyses)

        total_security_issues = sum(report.total_issues for report in security_reports)
        total_risk_score = sum(report.risk_score for report in security_reports)
        avg_risk_score = total_risk_score / max(1, len(security_reports))

        enhanced_review = f"""{llm_review}

## Aggregate Analysis

### Combined Metrics
- Total Lines of Code: {total_loc}
- Total Functions: {total_functions}
- Total Classes: {total_classes}
- Files Analyzed: {len(file_analyses)}

### Security Overview
- Total Security Issues: {total_security_issues}
- Average Risk Score: {avg_risk_score:.1f}/100

### Per-File Summary
{self._format_file_summary(file_analyses, security_reports)}
"""

        return enhanced_review

    def _format_issues(self, issues: List[CodeIssue]) -> str:
        """Format code issues for display."""
        if not issues:
            return "No issues found."

        formatted = []
        for issue in issues[:10]:  # Limit to top 10 issues
            formatted.append(f"- Line {issue.line_number}: {issue.message} ({issue.severity})")

        if len(issues) > 10:
            formatted.append(f"... and {len(issues) - 10} more issues")

        return "\n".join(formatted)

    def _format_security_issues(self, issues: List[SecurityIssue]) -> str:
        """Format security issues for display."""
        if not issues:
            return "No security issues found."

        formatted = []
        for issue in issues[:5]:  # Limit to top 5 security issues
            formatted.append(
                f"- Line {issue.line_number}: {issue.message} "
                f"({issue.severity}) - {issue.recommendation}"
            )

        if len(issues) > 5:
            formatted.append(f"... and {len(issues) - 5} more security issues")

        return "\n".join(formatted)

    def _format_file_summary(
        self,
        file_analyses: List[Dict],
        security_reports: List[SecurityReport]
    ) -> str:
        """Format per-file summary."""
        summary_lines = []

        for analysis, security in zip(file_analyses, security_reports):
            file_path = analysis['file_path']
            metrics = analysis['metrics']
            summary_lines.append(
                f"**{Path(file_path).name}** ({analysis['language']}): "
                f"{metrics.lines_of_code} LOC, "
                f"{len(analysis.get('issues', []))} issues, "
                f"{security.total_issues} security issues"
            )

        return "\n".join(summary_lines)

    def _extract_quality_score(self, review: str) -> Optional[int]:
        """Extract quality score from review text."""
        import re

        patterns = [
            r'quality score[:\s]*(\d+)',
            r'score[:\s]*(\d+)',
            r'(\d+)/10',
            r'rating[:\s]*(\d+)'
        ]

        for pattern in patterns:
            match = re.search(pattern, review.lower())
            if match:
                score = int(match.group(1))
                if 1 <= score <= 10:
                    return score

        return None

    def _calculate_security_score(self, security_report: SecurityReport) -> int:
        """Calculate security score based on issues found."""
        if security_report.total_issues == 0:
            return 10

        # Score calculation based on severity of issues
        score = 10
        score -= security_report.critical_issues * 3
        score -= security_report.high_issues * 2
        score -= security_report.medium_issues * 1
        score -= security_report.low_issues * 0.5

        return max(1, int(score))

    def _calculate_multi_file_security_score(self, security_reports: List[SecurityReport]) -> int:
        """Calculate overall security score for multiple files."""
        if not security_reports:
            return 10

        avg_risk = sum(report.risk_score for report in security_reports) / len(security_reports)
        # Convert risk score (0-100) to security score (1-10, inverted)
        return max(1, int(10 - (avg_risk / 10)))

    def _validate_setup(self):
        """Validate that the agent is properly configured."""
        api_keys = self.llm_client.validate_api_keys()

        if not any(api_keys.values()):
            print("⚠️ Warning: No LLM API keys found. Please set OPENAI_API_KEY or ANTHROPIC_API_KEY")
        elif self.verbose:
            available_providers = [provider for provider, available in api_keys.items() if available]
            print(f"✅ API keys configured for: {', '.join(available_providers)}")

    def get_supported_languages(self) -> List[str]:
        """Get list of supported programming languages."""
        return list(self.file_analyzer.supported_extensions.values())

    def test_connection(self, model: Optional[str] = None) -> Dict[str, Any]:
        """Test connection to the LLM API."""
        return self.llm_client.test_connection(model)


# Convenience functions for quick usage
def review_file(
    file_path: str,
    model: str = "gpt-4",
    verbose: bool = False
) -> str:
    """
    Quick file review function.

    Args:
        file_path: Path to file to review
        model: LLM model to use
        verbose: Enable detailed logging

    Returns:
        Review text
    """
    agent = {{AgentName}}(model=model, verbose=verbose)
    result = agent.review_file(file_path)
    return result.review


def review_files(
    file_paths: List[str],
    model: str = "gpt-4",
    verbose: bool = False
) -> str:
    """
    Quick multi-file review function.

    Args:
        file_paths: List of file paths to review
        model: LLM model to use
        verbose: Enable detailed logging

    Returns:
        Review text
    """
    agent = {{AgentName}}(model=model, verbose=verbose)
    result = agent.review_files(file_paths)
    return result.review


def security_scan(file_path: str) -> SecurityReport:
    """
    Quick security scan function.

    Args:
        file_path: Path to file to scan

    Returns:
        SecurityReport with vulnerability details
    """
    agent = {{AgentName}}(verbose=False)
    return agent.quick_security_scan(file_path)


if __name__ == "__main__":
    # Example usage
    print("🚀 {{AgentName}} - Comprehensive Code Review Agent")
    print("=" * 60)

    # Create reviewer
    reviewer = {{AgentName}}(verbose=True)

    # Test API connection
    print("\n🔗 Testing API connection...")
    connection_test = reviewer.test_connection()
    if connection_test['success']:
        print(f"✅ Connected to {connection_test['model']} (response time: {connection_test.get('response_time', 0):.1f}s)")
    else:
        print(f"❌ Connection failed: {connection_test.get('error')}")
        print("Please check your API keys in the .env file")
        exit(1)

    # Review this file as example
    print(f"\n🔍 Reviewing current file as demonstration...")
    result = reviewer.review_file(__file__)

    print("\n" + "="*60)
    print("📋 COMPREHENSIVE CODE REVIEW RESULTS")
    print("="*60)
    print(f"File: {result.file_or_files}")
    print(f"Language: {result.language}")
    print(f"Quality Score: {result.quality_score}/10")
    print(f"Security Score: {result.security_score}/10")
    print(f"Issues Found: {result.issues_found}")
    print(f"Security Issues: {result.security_issues}")
    print(f"Duration: {result.duration:.1f}s")
    print(f"Success: {result.success}")

    if result.file_metrics:
        print(f"\nFile Metrics:")
        print(f"  Lines of Code: {result.file_metrics.lines_of_code}")
        print(f"  Functions: {result.file_metrics.function_count}")
        print(f"  Classes: {result.file_metrics.class_count}")
        print(f"  Complexity: {result.file_metrics.cyclomatic_complexity}")

    print(f"\n📝 Detailed Review:")
    print("-" * 60)
    print(result.review)