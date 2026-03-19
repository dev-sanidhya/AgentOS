"""
{{AgentName}} - CrewAI Research Agent

A comprehensive research agent built on CrewAI framework that coordinates multiple
specialized agents to conduct thorough research and analysis.

Features:
- Multi-agent research crew with specialized roles
- Support for OpenAI GPT and Anthropic Claude models
- Web search and scraping capabilities
- Structured research workflow
- Comprehensive error handling
- Configurable verbosity and model parameters

Example:
    Basic usage:
    >>> from {{agent_name}} import {{AgentName}}
    >>> agent = {{AgentName}}()
    >>> result = agent.research("What are the latest AI trends?")

    Quick research function:
    >>> from {{agent_name}} import research
    >>> result = research("What are the latest AI trends?")
"""

import os
import sys
from typing import Dict, Any, Optional, List, Union
from dotenv import load_dotenv
import logging
from datetime import datetime

# Import the crew implementation
try:
    from {{agent_name}}_crew import {{AgentName}} as CrewAI{{AgentName}}, research as crew_research
except ImportError:
    raise ImportError(
        "CrewAI implementation not found. Please ensure {{agent_name}}_crew.py is in the same directory."
    )

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class {{AgentName}}:
    """
    Main interface for the CrewAI research agent system.

    This class provides a comprehensive research agent that uses CrewAI framework
    to coordinate multiple specialized agents for conducting thorough research.

    The research crew consists of:
    - Search Specialist: Expert at finding and gathering information from various sources
    - Content Analyst: Specialized in analyzing and synthesizing research data
    - Research Synthesizer: Creates comprehensive, well-structured research reports

    Attributes:
        model (str): The language model to use (e.g., 'gpt-4', 'claude-3-sonnet-20240229')
        temperature (float): Creativity level for model responses (0.0 to 1.0)
        verbose (bool): Enable detailed logging and progress output
        max_iterations (int): Maximum iterations per agent task
        crew (CrewAI{{AgentName}}): The underlying CrewAI implementation
    """

    def __init__(
        self,
        model: str = "gpt-4",
        temperature: float = 0.7,
        verbose: bool = True,
        max_iterations: int = 5,
        api_keys: Optional[Dict[str, str]] = None
    ):
        """
        Initialize the research agent.

        Args:
            model: Language model to use. Supports OpenAI models (gpt-4, gpt-3.5-turbo)
                   and Anthropic models (claude-3-sonnet-20240229, claude-3-opus-20240229)
            temperature: Controls randomness in responses (0.0 = deterministic, 1.0 = very creative)
            verbose: Enable detailed progress logging and agent communications
            max_iterations: Maximum number of iterations each agent can perform per task
            api_keys: Optional dictionary of API keys. If not provided, uses environment variables

        Raises:
            ValueError: If required API keys are missing or invalid model is specified
            ImportError: If required dependencies are not installed
        """
        self.model = model
        self.temperature = temperature
        self.verbose = verbose
        self.max_iterations = max_iterations
        self.api_keys = api_keys or {}

        # Validate and set API keys
        self._validate_configuration()

        # Initialize the CrewAI implementation
        try:
            self.crew = CrewAI{{AgentName}}(
                model=model,
                temperature=temperature,
                verbose=verbose,
                max_iterations=max_iterations
            )
        except Exception as e:
            logger.error(f"Failed to initialize CrewAI implementation: {e}")
            raise

        if self.verbose:
            logger.info(f"{{AgentName}} initialized with model: {model}")

    def _validate_configuration(self) -> None:
        """
        Validate API keys and configuration.

        Raises:
            ValueError: If required API keys are missing
        """
        # Check for required API keys based on model
        if self.model.startswith("claude"):
            if not (os.getenv("ANTHROPIC_API_KEY") or self.api_keys.get("anthropic")):
                raise ValueError(
                    "ANTHROPIC_API_KEY is required for Claude models. "
                    "Set it in environment variables or pass it via api_keys parameter."
                )
        else:
            if not (os.getenv("OPENAI_API_KEY") or self.api_keys.get("openai")):
                raise ValueError(
                    "OPENAI_API_KEY is required for OpenAI models. "
                    "Set it in environment variables or pass it via api_keys parameter."
                )

        # Warn about optional but recommended API keys
        if not os.getenv("SERPER_API_KEY") and self.verbose:
            logger.warning(
                "SERPER_API_KEY not found. Web search capabilities will be limited. "
                "Get an API key at https://serper.dev/ for best results."
            )

    def research(
        self,
        query: str,
        context: Optional[str] = None,
        focus_areas: Optional[List[str]] = None,
        max_sources: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Conduct comprehensive research on the given query.

        This method orchestrates the multi-agent research process, where specialized
        agents collaborate to gather, analyze, and synthesize information.

        Args:
            query: The research question or topic to investigate
            context: Optional background context to guide the research
            focus_areas: Optional list of specific areas to focus on
            max_sources: Optional limit on number of sources to gather

        Returns:
            Dictionary containing:
                - query: The original research query
                - output: The final research report
                - metadata: Information about the research process
                - agents_used: List of agents that participated
                - tasks_completed: Number of tasks completed
                - success: Boolean indicating if research was successful
                - error: Error message if research failed
                - timestamp: When the research was conducted

        Raises:
            ValueError: If query is empty or invalid
            Exception: If research process fails
        """
        if not query or not query.strip():
            raise ValueError("Research query cannot be empty")

        # Enhance query with additional parameters if provided
        enhanced_query = query
        if context:
            enhanced_query += f"\n\nContext: {context}"

        if focus_areas:
            enhanced_query += f"\n\nFocus on these areas: {', '.join(focus_areas)}"

        if max_sources:
            enhanced_query += f"\n\nLimit search to approximately {max_sources} sources"

        if self.verbose:
            logger.info(f"Starting research for query: {query}")
            if context or focus_areas or max_sources:
                logger.info("Enhanced query with additional parameters")

        try:
            # Execute research using CrewAI implementation
            result = self.crew.research(enhanced_query)

            # Add metadata to result
            result.update({
                "timestamp": datetime.now().isoformat(),
                "model_used": self.model,
                "temperature": self.temperature,
                "original_query": query,
                "enhanced_query": enhanced_query if enhanced_query != query else None
            })

            if self.verbose:
                if result["success"]:
                    logger.info("Research completed successfully")
                    logger.info(f"Agents used: {', '.join(result.get('agents_used', []))}")
                else:
                    logger.error(f"Research failed: {result.get('error', 'Unknown error')}")

            return result

        except Exception as e:
            error_msg = f"Research failed: {str(e)}"
            logger.error(error_msg)

            return {
                "query": query,
                "output": f"Research failed due to an error: {str(e)}",
                "error": str(e),
                "success": False,
                "timestamp": datetime.now().isoformat(),
                "model_used": self.model
            }

    def quick_research(self, query: str) -> str:
        """
        Perform quick research and return just the report text.

        Args:
            query: Research question or topic

        Returns:
            Research report as string
        """
        result = self.research(query)
        return result.get("output", "Research failed")

    def batch_research(
        self,
        queries: List[str],
        combine_results: bool = False
    ) -> Union[List[Dict[str, Any]], Dict[str, Any]]:
        """
        Conduct research on multiple queries.

        Args:
            queries: List of research questions
            combine_results: If True, combine all results into a single report

        Returns:
            List of research results or combined result if combine_results=True
        """
        if not queries:
            raise ValueError("Query list cannot be empty")

        results = []

        for i, query in enumerate(queries, 1):
            if self.verbose:
                logger.info(f"Processing query {i}/{len(queries)}: {query}")

            result = self.research(query)
            results.append(result)

        if combine_results:
            # Combine all successful research results
            successful_results = [r for r in results if r.get("success", False)]

            if not successful_results:
                return {
                    "queries": queries,
                    "output": "All research queries failed",
                    "success": False,
                    "individual_results": results
                }

            combined_output = "# Combined Research Report\n\n"
            for i, result in enumerate(successful_results, 1):
                combined_output += f"## Research Query {i}: {result['query']}\n\n"
                combined_output += result['output'] + "\n\n" + "="*50 + "\n\n"

            return {
                "queries": queries,
                "output": combined_output,
                "success": True,
                "individual_results": results,
                "successful_queries": len(successful_results),
                "total_queries": len(queries)
            }

        return results

    def get_capabilities(self) -> Dict[str, Any]:
        """
        Get information about the agent's capabilities and configuration.

        Returns:
            Dictionary with capability information
        """
        capabilities = {
            "model": self.model,
            "temperature": self.temperature,
            "max_iterations": self.max_iterations,
            "agents": [
                {
                    "role": "Search Specialist",
                    "capabilities": [
                        "Web search using Serper API",
                        "Website content scraping",
                        "Information gathering from multiple sources",
                        "Source validation and reliability assessment"
                    ]
                },
                {
                    "role": "Content Analyst",
                    "capabilities": [
                        "Data analysis and pattern recognition",
                        "Information synthesis",
                        "Key insight extraction",
                        "Conflict resolution between sources"
                    ]
                },
                {
                    "role": "Research Synthesizer",
                    "capabilities": [
                        "Comprehensive report writing",
                        "Information structuring and organization",
                        "Citation management",
                        "Executive summary creation"
                    ]
                }
            ],
            "tools": [],
            "api_keys_configured": {
                "openai": bool(os.getenv("OPENAI_API_KEY")),
                "anthropic": bool(os.getenv("ANTHROPIC_API_KEY")),
                "serper": bool(os.getenv("SERPER_API_KEY"))
            }
        }

        # Add available tools
        if os.getenv("SERPER_API_KEY"):
            capabilities["tools"].append("SerperDev Web Search")
        capabilities["tools"].append("Website Scraping")

        return capabilities

    def update_configuration(
        self,
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        verbose: Optional[bool] = None,
        max_iterations: Optional[int] = None
    ) -> None:
        """
        Update agent configuration.

        Args:
            model: New model to use
            temperature: New temperature setting
            verbose: New verbosity setting
            max_iterations: New max iterations setting
        """
        needs_reinit = False

        if model and model != self.model:
            self.model = model
            needs_reinit = True

        if temperature is not None:
            self.temperature = temperature
            needs_reinit = True

        if verbose is not None:
            self.verbose = verbose
            needs_reinit = True

        if max_iterations is not None:
            self.max_iterations = max_iterations
            needs_reinit = True

        if needs_reinit:
            # Reinitialize the crew with new settings
            if self.verbose:
                logger.info("Reinitializing crew with new configuration")

            self._validate_configuration()
            self.crew = CrewAI{{AgentName}}(
                model=self.model,
                temperature=self.temperature,
                verbose=self.verbose,
                max_iterations=self.max_iterations
            )


def research(
    query: str,
    model: str = "gpt-4",
    temperature: float = 0.7,
    verbose: bool = True,
    context: Optional[str] = None,
    focus_areas: Optional[List[str]] = None
) -> str:
    """
    Quick research function that creates a temporary agent and returns the report.

    This is a convenience function for simple research tasks that don't require
    maintaining an agent instance.

    Args:
        query: Research question or topic
        model: Language model to use
        temperature: Creativity level (0.0 to 1.0)
        verbose: Enable detailed logging
        context: Optional background context
        focus_areas: Optional list of specific focus areas

    Returns:
        Research report as string

    Example:
        >>> result = research("What are the benefits of renewable energy?")
        >>> print(result)
    """
    try:
        agent = {{AgentName}}(
            model=model,
            temperature=temperature,
            verbose=verbose
        )

        result = agent.research(
            query=query,
            context=context,
            focus_areas=focus_areas
        )

        return result.get("output", "Research failed")

    except Exception as e:
        error_msg = f"Quick research failed: {str(e)}"
        if verbose:
            logger.error(error_msg)
        return error_msg


def batch_research(
    queries: List[str],
    model: str = "gpt-4",
    temperature: float = 0.7,
    verbose: bool = True,
    combine_results: bool = False
) -> Union[List[str], str]:
    """
    Conduct research on multiple queries using a temporary agent.

    Args:
        queries: List of research questions
        model: Language model to use
        temperature: Creativity level
        verbose: Enable detailed logging
        combine_results: If True, return combined report as single string

    Returns:
        List of research reports or combined report string
    """
    try:
        agent = {{AgentName}}(
            model=model,
            temperature=temperature,
            verbose=verbose
        )

        results = agent.batch_research(queries, combine_results=combine_results)

        if combine_results:
            return results.get("output", "Batch research failed")
        else:
            return [r.get("output", "Research failed") for r in results]

    except Exception as e:
        error_msg = f"Batch research failed: {str(e)}"
        if verbose:
            logger.error(error_msg)

        if combine_results:
            return error_msg
        else:
            return [error_msg] * len(queries)


def get_supported_models() -> Dict[str, List[str]]:
    """
    Get list of supported language models.

    Returns:
        Dictionary with model providers and their available models
    """
    return {
        "openai": [
            "gpt-4",
            "gpt-4-turbo",
            "gpt-3.5-turbo",
            "gpt-3.5-turbo-16k"
        ],
        "anthropic": [
            "claude-3-opus-20240229",
            "claude-3-sonnet-20240229",
            "claude-3-haiku-20240307"
        ]
    }


def validate_environment() -> Dict[str, Any]:
    """
    Validate the environment setup for the research agent.

    Returns:
        Dictionary with validation results and recommendations
    """
    validation = {
        "valid": True,
        "warnings": [],
        "errors": [],
        "api_keys": {},
        "recommendations": []
    }

    # Check API keys
    openai_key = bool(os.getenv("OPENAI_API_KEY"))
    anthropic_key = bool(os.getenv("ANTHROPIC_API_KEY"))
    serper_key = bool(os.getenv("SERPER_API_KEY"))

    validation["api_keys"] = {
        "openai": openai_key,
        "anthropic": anthropic_key,
        "serper": serper_key
    }

    # Validate at least one LLM API key is present
    if not openai_key and not anthropic_key:
        validation["valid"] = False
        validation["errors"].append(
            "No LLM API keys found. Set either OPENAI_API_KEY or ANTHROPIC_API_KEY"
        )

    # Check for Serper API key
    if not serper_key:
        validation["warnings"].append(
            "SERPER_API_KEY not found. Web search capabilities will be limited. "
            "Get an API key at https://serper.dev/"
        )
        validation["recommendations"].append("Set up Serper API for enhanced web search")

    # Check dependencies
    try:
        import crewai
        import langchain_openai
        import langchain_anthropic
        import crewai_tools
    except ImportError as e:
        validation["valid"] = False
        validation["errors"].append(f"Missing dependency: {e}")
        validation["recommendations"].append("Run: pip install -r requirements.txt")

    return validation


if __name__ == "__main__":
    """
    Example usage and testing when run directly.
    """
    print("{{AgentName}} - CrewAI Research Agent")
    print("=" * 50)

    # Validate environment
    env_check = validate_environment()

    if not env_check["valid"]:
        print("❌ Environment validation failed:")
        for error in env_check["errors"]:
            print(f"  • {error}")

        print("\n💡 Recommendations:")
        for rec in env_check["recommendations"]:
            print(f"  • {rec}")

        sys.exit(1)

    # Print warnings if any
    if env_check["warnings"]:
        print("⚠️  Warnings:")
        for warning in env_check["warnings"]:
            print(f"  • {warning}")
        print()

    # Example research
    try:
        print("🔍 Running example research...")
        result = research(
            "What are the main challenges facing renewable energy adoption in 2026?",
            model="gpt-4",
            verbose=True
        )

        print("\n📊 Research Results:")
        print("-" * 30)
        print(result[:500] + "..." if len(result) > 500 else result)

    except Exception as e:
        print(f"❌ Example failed: {e}")
        print("\n🔧 Troubleshooting:")
        print("1. Check your API keys in .env file")
        print("2. Install dependencies: pip install -r requirements.txt")
        print("3. Set up SERPER_API_KEY for best results")

    print("\n✨ Test completed!")