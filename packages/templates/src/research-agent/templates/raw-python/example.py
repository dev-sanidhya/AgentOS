"""
{{AgentName}} Raw Python Examples

This script demonstrates how to use the research agent without
external frameworks - just direct API calls and simple Python.
"""

from {{agent_name}} import {{AgentName}}, research, ResearchResult
import os
import time
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


def basic_example():
    """Basic usage - quick research function."""
    print("🔍 Basic Raw Python Research Example")
    print("=" * 50)

    query = "What are the environmental benefits of electric vehicles?"

    try:
        result = research(
            query,
            model="gpt-4",
            verbose=True
        )

        print("\n📊 Research Results:")
        print(result)

    except Exception as e:
        print(f"❌ Error: {e}")


def advanced_example():
    """Advanced usage - using the agent class with full configuration."""
    print("\n🔍 Advanced Research Agent Example")
    print("=" * 50)

    try:
        # Initialize research agent
        agent = {{AgentName}}(
            model="gpt-4",           # or "claude-3-opus-20240229"
            temperature=0.6,         # slightly factual
            max_sources=3,           # limit sources for faster execution
            verbose=True
        )

        # Conduct research
        query = "How is blockchain technology being used in supply chain management?"
        result = agent.research(query)

        print("\n📊 Detailed Results:")
        print(f"Query: {result.query}")
        print(f"Success: {result.success}")
        print(f"Duration: {result.duration:.2f}s")
        print(f"Tool Calls: {result.tool_calls}")
        print(f"Sources: {len(result.sources)}")

        if result.success:
            print(f"\n📝 Report:\n{result.output}")

            print(f"\n🔗 Sources Consulted:")
            for i, source in enumerate(result.sources, 1):
                print(f"{i}. {source}")
        else:
            print(f"\n❌ Error: {result.error}")

    except Exception as e:
        print(f"❌ Error: {e}")


def model_comparison_example():
    """Compare different models side by side."""
    print("\n🔍 Model Comparison Example")
    print("=" * 50)

    query = "What are the key challenges in space exploration?"

    # Available models
    models = ["gpt-3.5-turbo", "gpt-4"]

    # Add Claude if API key is available
    if os.getenv("ANTHROPIC_API_KEY"):
        models.append("claude-3-sonnet-20240229")

    results = {}

    for model in models:
        print(f"\n🤖 Testing {model}...")

        try:
            start_time = time.time()

            agent = {{AgentName}}(
                model=model,
                temperature=0.5,
                max_sources=2,  # Fewer sources for speed
                verbose=False   # Quiet for comparison
            )

            result = agent.research(query)
            duration = time.time() - start_time

            results[model] = {
                "success": result.success,
                "duration": duration,
                "tool_calls": result.tool_calls,
                "output_length": len(result.output),
                "sources": len(result.sources),
                "preview": result.output[:200] + "..." if result.success else "Failed"
            }

            print(f"✅ {model}: {duration:.1f}s, {len(result.output)} chars")

        except Exception as e:
            print(f"❌ {model}: Failed - {e}")
            results[model] = {"success": False, "error": str(e)}

    # Summary
    print("\n📊 Comparison Summary:")
    for model, data in results.items():
        if data["success"]:
            print(f"\n{model}:")
            print(f"  Duration: {data['duration']:.1f}s")
            print(f"  Tool calls: {data['tool_calls']}")
            print(f"  Output: {data['output_length']} chars")
            print(f"  Sources: {data['sources']}")
            print(f"  Preview: {data['preview']}")
        else:
            print(f"\n{model}: ❌ {data.get('error', 'Failed')}")


def batch_research_example():
    """Research multiple related queries."""
    print("\n🔍 Batch Research Example")
    print("=" * 50)

    queries = [
        "What is artificial intelligence?",
        "How does machine learning work?",
        "What are neural networks?",
        "What is deep learning?"
    ]

    agent = {{AgentName}}(
        model="gpt-3.5-turbo",  # Faster model for batch processing
        temperature=0.4,
        max_sources=2,
        verbose=False
    )

    results = []
    total_start = time.time()

    for i, query in enumerate(queries, 1):
        print(f"\n📝 Query {i}/{len(queries)}: {query}")

        try:
            result = agent.research(query)
            results.append(result)

            if result.success:
                print(f"✅ Completed in {result.duration:.1f}s")
                print(f"📄 Preview: {result.output[:100]}...")
            else:
                print(f"❌ Failed: {result.error}")

        except Exception as e:
            print(f"❌ Error: {e}")

    total_duration = time.time() - total_start

    # Summary
    successful = [r for r in results if r.success]
    print(f"\n📊 Batch Results:")
    print(f"Total time: {total_duration:.1f}s")
    print(f"Successful: {len(successful)}/{len(queries)}")
    print(f"Total tool calls: {sum(r.tool_calls for r in results)}")
    print(f"Total sources: {sum(len(r.sources) for r in results)}")

    if successful:
        avg_duration = sum(r.duration for r in successful) / len(successful)
        avg_length = sum(len(r.output) for r in successful) / len(successful)
        print(f"Average duration: {avg_duration:.1f}s")
        print(f"Average report length: {avg_length:.0f} chars")


def custom_configuration_example():
    """Example with different configurations for different use cases."""
    print("\n🔍 Custom Configuration Example")
    print("=" * 50)

    configurations = [
        {
            "name": "Quick Research",
            "config": {
                "model": "gpt-3.5-turbo",
                "temperature": 0.3,
                "max_sources": 2,
                "verbose": False
            },
            "query": "What is quantum computing?"
        },
        {
            "name": "Detailed Analysis",
            "config": {
                "model": "gpt-4",
                "temperature": 0.7,
                "max_sources": 5,
                "verbose": False
            },
            "query": "Analyze the future of renewable energy"
        },
        {
            "name": "Creative Research",
            "config": {
                "model": "gpt-4",
                "temperature": 0.9,
                "max_sources": 3,
                "verbose": False
            },
            "query": "Innovative solutions for climate change"
        }
    ]

    for config_info in configurations:
        print(f"\n🎯 {config_info['name']}:")
        print(f"Query: {config_info['query']}")

        try:
            agent = {{AgentName}}(**config_info['config'])
            result = agent.research(config_info['query'])

            if result.success:
                print(f"✅ Success: {result.duration:.1f}s, {len(result.output)} chars")
                print(f"📄 Preview: {result.output[:150]}...")
            else:
                print(f"❌ Failed: {result.error}")

        except Exception as e:
            print(f"❌ Error: {e}")


def main():
    """Main function to run examples."""
    # Check for API keys
    if not os.getenv("OPENAI_API_KEY") and not os.getenv("ANTHROPIC_API_KEY"):
        print("⚠️  Warning: No API keys found!")
        print("Please set OPENAI_API_KEY or ANTHROPIC_API_KEY in your .env file")
        print("\nExample .env file:")
        print("OPENAI_API_KEY=sk-...")
        print("ANTHROPIC_API_KEY=sk-ant-...")
        return

    if not any([
        os.getenv("BRAVE_API_KEY"),
        os.getenv("SERPER_API_KEY"),
        os.getenv("SERPAPI_KEY")
    ]):
        print("⚠️  Warning: No search API keys found!")
        print("The agent will use mock search results.")
        print("For better results, add one of these to your .env file:")
        print("- BRAVE_API_KEY (recommended)")
        print("- SERPER_API_KEY")
        print("- SERPAPI_KEY")
        print()

    print("🤖 {{AgentName}} Raw Python Examples")
    print("=" * 60)

    try:
        # Run examples (uncomment the ones you want to test)
        basic_example()
        # advanced_example()
        # model_comparison_example()
        # batch_research_example()
        # custom_configuration_example()

    except Exception as e:
        print(f"\n💥 Fatal error: {e}")
        print("\n🔧 Troubleshooting:")
        print("1. Check your API keys in .env file")
        print("2. Ensure dependencies are installed: pip install -r requirements.txt")
        print("3. Check your internet connection")
        print("4. Verify API key permissions and credits")

    print("\n✨ Examples completed!")


if __name__ == "__main__":
    main()