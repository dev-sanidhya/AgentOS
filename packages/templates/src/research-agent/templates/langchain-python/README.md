# {{AgentName}} - AI Research Assistant

An intelligent research agent that searches the web, extracts content, and synthesizes comprehensive reports from multiple sources.

## Features

- 🔍 **Web Search**: Search the web for information on any topic
- 📄 **Content Extraction**: Scrape and read web pages in detail
- 🧠 **Information Synthesis**: Combine insights from multiple sources
- 📊 **Structured Reports**: Generate well-organized research outputs
- 🔄 **Multiple LLM Support**: Works with OpenAI GPT models and Anthropic Claude

## Installation

1. Install Python dependencies:
```bash
pip install -r requirements.txt
```

2. Set up environment variables:
```bash
# Copy the example .env file
cp .env.example .env

# Add your API keys
echo "OPENAI_API_KEY=sk-..." >> .env
# OR
echo "ANTHROPIC_API_KEY=sk-ant-..." >> .env
```

3. (Optional) Set up a search API for real web search:

Choose one of these options:

**Option 1: Brave Search (Recommended)**
- Sign up at https://brave.com/search/api/
- Add to .env: `BRAVE_API_KEY=your_key`
- Uncomment Brave Search code in `tools/web_search.py`

**Option 2: SerpAPI (Google Search)**
- Sign up at https://serpapi.com/
- Add to .env: `SERPAPI_KEY=your_key`
- Uncomment SerpAPI code in `tools/web_search.py`

**Option 3: Tavily (AI-optimized)**
- Sign up at https://tavily.com/
- Add to .env: `TAVILY_API_KEY=your_key`
- Uncomment Tavily code in `tools/web_search.py`

## Usage

### Quick Start

```python
from {{agent_name}} import research

# Simple research query
result = research("What are the latest trends in AI?")
print(result)
```

### Advanced Usage

```python
from {{agent_name}} import {{AgentName}}

# Initialize with configuration
agent = {{AgentName}}(
    model="gpt-4",          # or "claude-3-opus-20240229"
    temperature=0.7,        # creativity level (0-1)
    max_iterations=10,      # max research steps
    verbose=True            # enable logging
)

# Conduct research
result = agent.research("Compare quantum computing and classical computing")

# Access results
print(result["output"])                    # Final research report
print(result["intermediate_steps"])        # Tool calls and results
```

### Async Usage

```python
import asyncio
from {{agent_name}} import {{AgentName}}

async def main():
    agent = {{AgentName}}(model="gpt-4")
    result = await agent.aresearch("What is RAG in AI?")
    print(result["output"])

asyncio.run(main())
```

### Run the Examples

```bash
python example.py
```

## How It Works

The research agent follows a systematic methodology:

1. **Understand the Query**
   - Identifies core questions and information needs
   - Considers multiple perspectives

2. **Plan the Search**
   - Breaks complex queries into searchable components
   - Identifies key terms and authoritative sources

3. **Gather Information**
   - Conducts web searches from multiple angles
   - Extracts detailed content from promising sources
   - Cross-references information

4. **Verify and Synthesize**
   - Corroborates information across sources
   - Prioritizes authoritative and recent sources
   - Notes disagreements and uncertainties

5. **Generate Report**
   - Organizes findings logically
   - Provides executive summary
   - Cites sources
   - Distinguishes facts from opinions

## Output Format

Research reports are structured as:

```
**Executive Summary**
Brief overview of key findings (2-3 sentences)

**Main Findings**
- Organized by theme or subtopic
- Specific data and facts
- Multiple perspectives

**Sources**
- Key sources consulted
- URLs and references

**Conclusion**
- Synthesis of findings
- Answer to original question
- Limitations or areas for further research
```

## Configuration

### Supported Models

**OpenAI:**
- `gpt-4` (recommended for quality)
- `gpt-4-turbo`
- `gpt-3.5-turbo` (faster, cheaper)

**Anthropic:**
- `claude-3-opus-20240229` (most capable)
- `claude-3-sonnet-20240229` (balanced)
- `claude-3-haiku-20240307` (fastest)

### Parameters

```python
agent = {{AgentName}}(
    model="gpt-4",              # LLM model to use
    temperature=0.7,            # 0 = focused, 1 = creative
    max_iterations=10,          # Maximum research steps
    verbose=False               # Enable detailed logging
)
```

## Customization

### Custom Prompts

You can use alternative prompts for specific use cases:

```python
from {{agent_name}} import {{AgentName}}
from prompts import FACT_CHECKING_PROMPT, MARKET_RESEARCH_PROMPT

# Use for fact-checking
agent = {{AgentName}}(model="gpt-4")
# Modify the system prompt in the agent's initialization
```

Available prompt variants:
- `RESEARCH_AGENT_PROMPT` (default): General-purpose research
- `FACT_CHECKING_PROMPT`: Verify claims with sources
- `MARKET_RESEARCH_PROMPT`: Business and market analysis
- `ACADEMIC_RESEARCH_PROMPT`: Scholarly research

### Add Custom Tools

```python
from langchain.tools import Tool
from {{agent_name}} import {{AgentName}}

# Define custom tool
def my_tool(query: str) -> str:
    # Your tool logic
    return "Result"

custom_tool = Tool(
    name="my_tool",
    description="What this tool does",
    func=my_tool
)

# Add to agent
agent = {{AgentName}}(model="gpt-4")
agent.tools.append(custom_tool)
```

## Project Structure

```
{{agent_name}}/
├── {{agent_name}}.py          # Main agent class
├── prompts.py                 # System prompts
├── tools/
│   ├── __init__.py
│   ├── web_search.py         # Web search tool
│   └── web_scrape.py         # Web scraping tool
├── requirements.txt          # Dependencies
├── example.py               # Usage examples
├── .env.example            # Environment template
└── README.md              # This file
```

## Troubleshooting

**No API key found:**
- Make sure you have a `.env` file with `OPENAI_API_KEY` or `ANTHROPIC_API_KEY`

**Mock search results:**
- The web search uses a placeholder by default
- Set up a real search API (Brave, SerpAPI, or Tavily) for actual web search

**Agent not finding information:**
- Try rephrasing your query more specifically
- Enable verbose mode to see what the agent is doing
- Check your search API rate limits

**Import errors:**
- Make sure all dependencies are installed: `pip install -r requirements.txt`

## Best Practices

1. **Be Specific**: Clear, specific queries yield better results
2. **Iterate**: Use follow-up queries to drill into details
3. **Verify**: Always cross-check critical information
4. **Monitor Usage**: Track API calls for cost management
5. **Enable Logging**: Use `verbose=True` for debugging

## License

MIT

## Contributing

Contributions welcome! Feel free to submit issues or pull requests.
