"""
{{AgentName}} - Raw Python Implementation

A simple, framework-agnostic research agent that directly uses LLM APIs
without external agent frameworks. Perfect for minimal dependencies
and maximum control.
"""

import os
import time
from typing import List, Optional
from dataclasses import dataclass
from dotenv import load_dotenv

# Import modular tools
from tools.web_search import WebSearchClient, SearchResult
from tools.web_scrape import WebScraperClient, ScrapedContent
from tools.llm_client import LLMClient, LLMResponse

# Load environment variables
load_dotenv()


@dataclass
class ResearchResult:
    """Represents the result of a research operation."""
    query: str
    output: str
    sources: List[str]
    duration: float
    tool_calls: int
    success: bool
    error: Optional[str] = None


class {{AgentName}}:
    """
    Simple research agent using direct API calls and modular tools.

    This agent conducts research by:
    1. Searching the web for information using WebSearchClient
    2. Extracting content from relevant sources using WebScraperClient
    3. Synthesizing findings into a comprehensive report using LLMClient
    """

    def __init__(
        self,
        model: str = "gpt-4",
        temperature: float = 0.7,
        max_sources: int = 5,
        verbose: bool = True
    ):
        """
        Initialize the research agent.

        Args:
            model: LLM model to use
            temperature: Creativity level (0-1)
            max_sources: Maximum sources to scrape
            verbose: Enable progress logging
        """
        self.model = model
        self.temperature = temperature
        self.max_sources = max_sources
        self.verbose = verbose

        # Initialize modular tools
        self.llm = LLMClient(model=model, temperature=temperature)
        self.search = WebSearchClient()
        self.scraper = WebScraperClient(max_content_length=5000)

    def research(self, query: str) -> ResearchResult:
        """
        Conduct research on the given query.

        Args:
            query: Research question or topic

        Returns:
            ResearchResult with findings and metadata
        """
        start_time = time.time()
        tool_calls = 0
        sources = []

        try:
            if self.verbose:
                print(f"🔍 Starting research on: {query}")

            # Step 1: Search for information
            if self.verbose:
                print("📡 Searching for information...")

            search_results = self.search.search(query, self.max_sources)
            tool_calls += 1

            if not search_results:
                raise Exception("No search results found")

            # Step 2: Extract content from top sources
            if self.verbose:
                print(f"📄 Extracting content from {len(search_results)} sources...")

            scraped_content = []
            for i, result in enumerate(search_results[:3]):  # Limit to top 3
                if self.verbose:
                    print(f"  Scraping {i+1}: {result.url}")

                content = self.scraper.scrape(result.url)
                tool_calls += 1

                if content.success and content.word_count > 50:
                    scraped_content.append({
                        "title": result.title,
                        "url": result.url,
                        "snippet": result.snippet,
                        "content": content.text[:3000]  # Limit content length
                    })
                    sources.append(result.url)

            # Step 3: Generate research report
            if self.verbose:
                print("🧠 Synthesizing findings...")

            report_response = self._generate_report(query, search_results, scraped_content)
            tool_calls += 1

            if not report_response.success:
                raise Exception(f"Report generation failed: {report_response.error}")

            duration = time.time() - start_time

            if self.verbose:
                print(f"✅ Research completed in {duration:.1f}s")

            return ResearchResult(
                query=query,
                output=report_response.content,
                sources=sources,
                duration=duration,
                tool_calls=tool_calls,
                success=True
            )

        except Exception as e:
            duration = time.time() - start_time
            error_msg = str(e)

            if self.verbose:
                print(f"❌ Research failed: {error_msg}")

            return ResearchResult(
                query=query,
                output=f"Research failed: {error_msg}",
                sources=[],
                duration=duration,
                tool_calls=tool_calls,
                success=False,
                error=error_msg
            )

    def _generate_report(
        self,
        query: str,
        search_results: List[SearchResult],
        scraped_content: List[dict]
    ) -> LLMResponse:
        """Generate a comprehensive research report."""

        # Prepare context for the LLM
        search_context = self._format_search_results(search_results)
        content_context = self._format_scraped_content(scraped_content)

        # System prompt for research analysis
        system_prompt = """You are a professional research analyst. Your task is to analyze provided information and create comprehensive, well-structured research reports.

Guidelines:
- Be factual and objective
- Distinguish between facts and opinions
- Cite sources when possible
- Note any limitations in available information
- Use clear, professional language
- Structure your response clearly"""

        # User prompt with research data
        user_prompt = f"""Based on the provided information, write a comprehensive research report on: "{query}"

SEARCH RESULTS SUMMARY:
{search_context}

DETAILED CONTENT FROM SOURCES:
{content_context}

Please provide a well-structured research report with:

1. **Executive Summary** (2-3 sentences)
2. **Key Findings** (organized by theme)
3. **Detailed Analysis** (supporting evidence and data)
4. **Sources** (list of URLs referenced)
5. **Conclusion** (synthesis and implications)

Research Report:"""

        return self.llm.generate(
            prompt=user_prompt,
            system_prompt=system_prompt
        )

    def _format_search_results(self, results: List[SearchResult]) -> str:
        """Format search results for the prompt."""
        if not results:
            return "No search results available."

        formatted = []
        for i, result in enumerate(results, 1):
            formatted.append(
                f"{i}. {result.title}\n"
                f"   URL: {result.url}\n"
                f"   Summary: {result.snippet}"
            )
        return "\n\n".join(formatted)

    def _format_scraped_content(self, content: List[dict]) -> str:
        """Format scraped content for the prompt."""
        if not content:
            return "No detailed content was successfully extracted."

        formatted = []
        for i, item in enumerate(content, 1):
            formatted.append(
                f"{i}. {item['title']}\n"
                f"   URL: {item['url']}\n"
                f"   Content: {item['content'][:2000]}..."
            )
        return "\n\n".join(formatted)

    def health_check(self) -> dict:
        """Perform health check on all components."""
        return {
            "llm": self.llm.health_check(),
            "search": self.search.get_available_apis(),
            "scraper": {"status": "ready"}
        }


def research(
    query: str,
    model: str = "gpt-4",
    temperature: float = 0.7,
    verbose: bool = True
) -> str:
    """
    Quick research function using the modular Raw Python implementation.

    Args:
        query: Research question
        model: LLM model to use
        temperature: Creativity level (0-1)
        verbose: Enable logging

    Returns:
        Research report as string
    """
    agent = {{AgentName}}(
        model=model,
        temperature=temperature,
        verbose=verbose
    )

    result = agent.research(query)
    return result.output


if __name__ == "__main__":
    # Example usage
    print("🤖 {{AgentName}} - Raw Python Implementation")
    print("=" * 60)

    # Check for API keys
    if not os.getenv("OPENAI_API_KEY") and not os.getenv("ANTHROPIC_API_KEY"):
        print("⚠️  Warning: No LLM API keys found!")
        print("Please set OPENAI_API_KEY or ANTHROPIC_API_KEY in your .env file")
        exit(1)

    # Run example research
    agent = {{AgentName}}(verbose=True)
    result = agent.research("What are the latest trends in renewable energy?")

    print("\n" + "="*50)
    print("RESEARCH RESULTS")
    print("="*50)
    print(result.output)

    if result.sources:
        print(f"\nSources consulted: {len(result.sources)}")
        for source in result.sources:
            print(f"- {source}")

    print(f"\nResearch completed in {result.duration:.1f}s with {result.tool_calls} tool calls")