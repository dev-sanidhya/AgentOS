"""
Example usage of {{AgentName}} - CrewAI Implementation

This script demonstrates the multi-agent research capabilities
of the CrewAI-based research system.
"""

import os
from dotenv import load_dotenv
from {{agent_name}} import {{AgentName}}, research

# Load environment variables
load_dotenv()


def basic_example():
    """Basic usage - quick research function."""
    print("🔬 Basic CrewAI Research Example")
    print("=" * 50)

    query = "What are the latest developments in renewable energy technology?"
    result = research(query, model="gpt-4", verbose=True)

    print("\n📊 Research Results:")
    print(result)


def advanced_example():
    """Advanced usage - using the multi-agent crew directly."""
    print("\n🔬 Advanced CrewAI Research Example")
    print("=" * 50)

    # Initialize the research crew
    crew = {{AgentName}}(
        model="gpt-4",  # or "claude-3-opus-20240229"
        temperature=0.7,
        verbose=True
    )

    # Conduct comprehensive research
    query = "Compare different approaches to artificial general intelligence (AGI)"
    result = crew.research(query)

    print("\n📊 Full Results:")
    print(f"Query: {result['query']}")
    print(f"Model Used: {result['model']}")
    print(f"Agents Involved: {result['agents_used']}")
    print(f"Tasks Completed: {result['tasks_completed']}")
    print("\n" + "=" * 50)
    print("RESEARCH REPORT:")
    print("=" * 50)
    print(result['output'])


def multi_topic_example():
    """Example researching multiple related topics."""
    print("\n🔬 Multi-Topic Research Example")
    print("=" * 50)

    crew = {{AgentName}}(model="gpt-4", verbose=True)

    topics = [
        "What is quantum computing and how does it work?",
        "What are the current applications of quantum computing?", 
        "What are the main challenges facing quantum computing adoption?"
    ]

    results = []
    for topic in topics:
        print(f"\n📝 Researching: {topic}")
        result = crew.research(topic)
        results.append(result)
        print("✅ Research completed\n")

    # Combine results for comprehensive understanding
    print("\n📊 Combined Research Summary:")
    print("=" * 60)
    for i, result in enumerate(results, 1):
        print(f"\n--- Topic {i}: {result['query'][:60]}... ---")
        # Show first paragraph of each result
        first_paragraph = result['output'].split('\n\n')[0]
        print(first_paragraph)


def error_handling_example():
    """Example showing error handling and fallback behavior."""
    print("\n🔬 Error Handling Example")
    print("=" * 50)

    crew = {{AgentName}}(model="gpt-4", verbose=True)

    # This should work normally
    print("Testing normal operation...")
    result = crew.research("What is machine learning?")
    
    if "Error:" in result['output']:
        print("❌ Unexpected error in normal operation")
        print(result['output'])
    else:
        print("✅ Normal operation successful")
        print(f"Report length: {len(result['output'])} characters")


def check_environment():
    """Check if the environment is properly configured."""
    print("\n🔧 Environment Check")
    print("=" * 30)

    # Check for LLM API keys
    has_openai = bool(os.getenv("OPENAI_API_KEY"))
    has_anthropic = bool(os.getenv("ANTHROPIC_API_KEY"))
    
    print(f"OpenAI API Key: {'✅ Configured' if has_openai else '❌ Missing'}")
    print(f"Anthropic API Key: {'✅ Configured' if has_anthropic else '❌ Missing'}")

    if not (has_openai or has_anthropic):
        print("\n⚠️  Warning: No LLM API keys found!")
        print("Set OPENAI_API_KEY or ANTHROPIC_API_KEY in your .env file")
        return False

    # Check for search API keys (optional but recommended)
    search_apis = {
        "SerperDev": os.getenv("SERPER_API_KEY"),
        "Brave Search": os.getenv("BRAVE_API_KEY"),
        "SerpAPI": os.getenv("SERPAPI_KEY"),
        "Tavily": os.getenv("TAVILY_API_KEY")
    }

    has_search = any(search_apis.values())
    print(f"\nSearch API Status: {'✅ Configured' if has_search else '⚠️  Using mock search'}")
    
    for api_name, api_key in search_apis.items():
        status = "✅ Available" if api_key else "❌ Not configured"
        print(f"  {api_name}: {status}")

    if not has_search:
        print("\n💡 Recommendation: Configure a search API for better results")
        print("   SerperDev is recommended for CrewAI integration")

    return True


if __name__ == "__main__":
    print("🚀 {{AgentName}} - CrewAI Multi-Agent Research System")
    print("=" * 65)

    # Check environment setup
    if not check_environment():
        print("\nPlease configure your environment and try again.")
        exit(1)

    try:
        # Run examples
        basic_example()
        advanced_example()

        # Uncomment to run additional examples
        # multi_topic_example()
        # error_handling_example()

        print("\n🎉 All examples completed successfully!")
        print("\nNext steps:")
        print("1. Try your own research queries")
        print("2. Experiment with different models and settings")
        print("3. Configure additional search APIs for better results")

    except Exception as e:
        print(f"\n❌ Error running examples: {e}")
        print("\nTroubleshooting checklist:")
        print("1. Ensure all dependencies are installed: pip install -r requirements.txt")
        print("2. Check your .env file has valid API keys")
        print("3. Verify internet connection for web search capabilities")
        print("4. Try with verbose=True to see detailed execution logs")
