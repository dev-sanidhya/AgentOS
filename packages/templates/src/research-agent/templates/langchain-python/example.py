"""
Example usage of {{AgentName}}

This script demonstrates how to use the research agent to gather
and synthesize information from the web.
"""

from {{agent_name}} import {{AgentName}}, research
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


def basic_example():
    """Basic usage - quick research function."""
    print("🔍 Basic Research Example")
    print("=" * 50)

    query = "What are the latest trends in artificial intelligence for 2026?"
    result = research(query, model="gpt-4", verbose=True)

    print("\n📊 Results:")
    print(result)


def advanced_example():
    """Advanced usage - using the agent class with configuration."""
    print("\n🔍 Advanced Research Example")
    print("=" * 50)

    # Initialize agent with custom configuration
    agent = {{AgentName}}(
        model="gpt-4",  # or "claude-3-opus-20240229"
        temperature=0.7,
        max_iterations=10,
        verbose=True
    )

    # Conduct research
    query = "Compare the performance of different LLM models on reasoning tasks"
    result = agent.research(query)

    print("\n📊 Results:")
    print(result["output"])

    print("\n🔧 Intermediate Steps:")
    for i, step in enumerate(result["intermediate_steps"], 1):
        action, observation = step
        print(f"\nStep {i}: {action.tool}")
        print(f"Input: {action.tool_input}")
        print(f"Output: {observation[:200]}...")  # Truncate for readability


async def async_example():
    """Async usage example."""
    print("\n🔍 Async Research Example")
    print("=" * 50)

    agent = {{AgentName}}(
        model="gpt-4",
        verbose=True
    )

    query = "What are the key differences between quantum and classical computing?"
    result = await agent.aresearch(query)

    print("\n📊 Results:")
    print(result["output"])


def multi_query_example():
    """Example with multiple related queries."""
    print("\n🔍 Multi-Query Research Example")
    print("=" * 50)

    agent = {{AgentName}}(model="gpt-4", verbose=True)

    queries = [
        "What is retrieval-augmented generation (RAG)?",
        "What are the main components of a RAG system?",
        "What are the best practices for implementing RAG?"
    ]

    results = []
    for query in queries:
        print(f"\n📝 Query: {query}")
        result = agent.research(query)
        results.append(result)
        print(f"✅ Completed\n")

    print("\n📊 All Results:")
    for i, result in enumerate(results, 1):
        print(f"\n--- Query {i} ---")
        print(result["output"][:300] + "...")  # Truncate for readability


if __name__ == "__main__":
    # Check for API keys
    if not os.getenv("OPENAI_API_KEY") and not os.getenv("ANTHROPIC_API_KEY"):
        print("⚠️  Warning: No API keys found!")
        print("Please set OPENAI_API_KEY or ANTHROPIC_API_KEY in your .env file")
        print("\nExample .env file:")
        print("OPENAI_API_KEY=sk-...")
        print("ANTHROPIC_API_KEY=sk-ant-...")
        exit(1)

    # Run examples
    try:
        basic_example()
        advanced_example()

        # Uncomment to run async example
        # import asyncio
        # asyncio.run(async_example())

        # Uncomment to run multi-query example
        # multi_query_example()

    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\nMake sure you have:")
        print("1. Set up your API keys in .env")
        print("2. Installed all dependencies: pip install -r requirements.txt")
        print("3. (Optional) Set up a search API (Brave, SerpAPI, or Tavily)")
