# {{AgentName}} - Raw Python Implementation

A simple, framework-agnostic research agent built with pure Python and direct API calls. Perfect for minimal dependencies, maximum control, and easy customization.

## 🚀 Overview

This implementation provides a clean, straightforward approach to AI research without external agent frameworks:

- **Direct API Integration**: Uses OpenAI and Anthropic APIs directly
- **Minimal Dependencies**: Only requires `requests` and `python-dotenv`
- **Full Control**: Every component is transparent and customizable
- **No Magic**: Clear, readable code with explicit behavior
- **Easy to Modify**: Simple structure makes customization straightforward

## 🎯 Features

- 🔍 **Web Search**: Multiple search API integrations (Brave, Serper, SerpAPI)
- 📄 **Content Extraction**: Simple web scraping with basic HTML parsing
- 🧠 **LLM Integration**: Direct support for OpenAI and Anthropic models
- 📊 **Structured Results**: Clear data structures with metadata
- 🛠️ **Highly Customizable**: Modify any component easily
- ⚡ **Lightweight**: Minimal dependencies and overhead

## 📦 Installation

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
# Copy the environment template
cp .env.example .env

# Add your LLM API key (choose one)
echo "OPENAI_API_KEY=sk-your-openai-key" >> .env
# OR
echo "ANTHROPIC_API_KEY=sk-ant-your-anthropic-key" >> .env

# Optional: Add search API key for better results
echo "BRAVE_API_KEY=your-brave-key" >> .env
# OR
echo "SERPER_API_KEY=your-serper-key" >> .env
# OR
echo "SERPAPI_KEY=your-serpapi-key" >> .env
```

### 3. Get API Keys

**LLM Provider (Required):**
- [OpenAI API](https://platform.openai.com/api-keys)
- [Anthropic API](https://console.anthropic.com/)

**Search API (Optional but Recommended):**
- [Brave Search](https://brave.com/search/api/) - Clean results, recommended
- [Serper](https://serper.dev/) - Google search proxy
- [SerpAPI](https://serpapi.com/) - Google search with rich data

## 🎯 Quick Start

### Simple Research

```python
from {{agent_name}} import research

# One-line research
result = research("What are the latest developments in quantum computing?")
print(result)
```

### Advanced Usage

```python
from {{agent_name}} import {{AgentName}}

# Create agent with custom configuration
agent = {{AgentName}}(
    model="gpt-4",           # or "claude-3-opus-20240229"
    temperature=0.7,         # creativity level (0-1)
    max_sources=5,           # max sources to scrape
    verbose=True             # show progress
)

# Conduct research
result = agent.research("Impact of AI on renewable energy")

# Access detailed results
print(f"Success: {result.success}")
print(f"Duration: {result.duration:.2f}s")
print(f"Sources: {len(result.sources)}")
print(f"Report: {result.output}")
```

### Run Examples

```python
python example.py
```

## 📖 API Reference

### {{AgentName}} Class

```python
class {{AgentName}}:
    def __init__(
        self,
        model: str = "gpt-4",
        temperature: float = 0.7,
        max_sources: int = 5,
        verbose: bool = True
    )

    def research(self, query: str) -> ResearchResult
```

### ResearchResult

```python
@dataclass
class ResearchResult:
    query: str              # Original query
    output: str            # Research report
    sources: List[str]     # URLs consulted
    duration: float        # Time taken (seconds)
    tool_calls: int       # Number of API calls made
    success: bool         # Whether research succeeded
    error: Optional[str]  # Error message if failed
```

### Configuration Options

- `model`: LLM model to use ("gpt-4", "gpt-3.5-turbo", "claude-3-opus-20240229")
- `temperature`: Creativity level (0.0 = factual, 1.0 = creative)
- `max_sources`: Maximum sources to scrape for content
- `verbose`: Show progress and debugging information

## 🎯 Supported Models

### OpenAI Models
- `gpt-4` - Most capable (recommended)
- `gpt-4-turbo` - Faster and cheaper than GPT-4
- `gpt-3.5-turbo` - Fastest and most economical

### Anthropic Models
- `claude-3-opus-20240229` - Most capable Claude
- `claude-3-sonnet-20240229` - Balanced performance
- `claude-3-haiku-20240307` - Fastest Claude

## 🛠️ How It Works

### Research Process

1. **🔍 Web Search**
   - Query multiple search APIs for relevant information
   - Collect titles, URLs, and snippets
   - Prioritize authoritative sources

2. **📄 Content Extraction**
   - Scrape full content from top sources
   - Basic HTML parsing and text extraction
   - Limit content length for processing

3. **🧠 Report Generation**
   - Send all information to LLM for synthesis
   - Generate structured, comprehensive report
   - Include citations and source references

### Components

```python
# Import modular tools
from tools.web_search import WebSearchClient
from tools.web_scrape import WebScraperClient
from tools.llm_client import LLMClient

# Use individual components
search = WebSearchClient()
results = search.search(query, max_results=5)

scraper = WebScraperClient()
content = scraper.scrape(url)

llm = LLMClient(model="gpt-4", temperature=0.7)
response = llm.generate(prompt)
```

## 🔧 Customization

### Custom Search Integration

Add your own search API by modifying `SimpleWebSearch`:

```python
class SimpleWebSearch:
    def _my_custom_search(self, query: str, max_results: int):
        # Your search implementation
        return [SearchResult(...)]
```

### Custom Content Processing

Enhance scraping by modifying `SimpleWebScraper`:

```python
class SimpleWebScraper:
    def scrape(self, url: str) -> str:
        # Add BeautifulSoup, readability, etc.
        return processed_text
```

### Custom LLM Integration

Add new LLM providers by extending `SimpleLLM`:

```python
class SimpleLLM:
    def _my_llm_generate(self, prompt: str) -> str:
        # Your LLM API integration
        return response
```

### Custom Report Templates

Modify the report generation in `_generate_report()`:

```python
def _generate_report(self, query, search_results, content):
    prompt = f"""Custom prompt template for {query}..."""
    return self.llm.generate(prompt)
```

## 📁 Project Structure

```
{{agent_name}}/
├── {{agent_name}}.py        # Main agent implementation
├── tools/                   # Modular tool components
│   ├── __init__.py         # Tools package initialization
│   ├── web_search.py       # Direct search API integration
│   ├── web_scrape.py       # BeautifulSoup web scraping
│   └── llm_client.py       # Direct LLM API client
├── requirements.txt         # Python dependencies
├── example.py              # Usage examples
├── .env.example           # Environment template
└── README.md             # This file
```

## 🏆 Advantages

### 1. **Simplicity**
- No complex agent frameworks
- Clear, readable code
- Easy to understand and debug

### 2. **Control**
- Direct API access
- Customize every component
- No hidden behavior

### 3. **Lightweight**
- Minimal dependencies
- Fast startup and execution
- Low memory footprint

### 4. **Flexibility**
- Easy to modify for specific use cases
- Add new APIs or features quickly
- Integrate with existing systems

## 💡 Use Cases

### Research Assistant
```python
agent = {{AgentName}}(temperature=0.3, max_sources=5)
report = agent.research("Climate change impact on agriculture")
```

### Market Analysis
```python
agent = {{AgentName}}(temperature=0.6, max_sources=3)
report = agent.research("Electric vehicle market trends 2026")
```

### Technical Documentation
```python
agent = {{AgentName}}(temperature=0.2, max_sources=3)
report = agent.research("Best practices for API security")
```

### Quick Facts
```python
result = research("Current population of Tokyo", model="gpt-3.5-turbo")
```

## 🔧 Troubleshooting

### Common Issues

**"No API key found"**
- Check your `.env` file has the correct variable names
- Verify API key is valid and has credits

**Mock search results only**
- No search API keys configured
- Add BRAVE_API_KEY, SERPER_API_KEY, or SERPAPI_KEY

**Scraping failures**
- Some sites block automated requests
- Network connectivity issues
- Rate limiting from target sites

**LLM API errors**
- Check API key permissions
- Verify account has sufficient credits
- Check for rate limiting

### Debug Mode

Enable verbose logging:

```python
agent = {{AgentName}}(verbose=True)
```

This shows:
- Search queries and results
- URLs being scraped
- Content extraction progress
- API call timing

## 🏆 Best Practices

### 1. **Choose Right Configuration**

```python
# For factual research
agent = {{AgentName}}(temperature=0.2, model="gpt-4")

# For creative analysis
agent = {{AgentName}}(temperature=0.8, model="gpt-4")

# For quick/cheap research
agent = {{AgentName}}(model="gpt-3.5-turbo", max_sources=2)
```

### 2. **Handle Errors Gracefully**

```python
result = agent.research(query)
if result.success:
    process_report(result.output)
else:
    handle_error(result.error)
```

### 3. **Optimize for Your Use Case**

```python
# Batch processing
agent = {{AgentName}}(verbose=False, max_sources=2)

# Detailed analysis
agent = {{AgentName}}(max_sources=7, temperature=0.4)

# Real-time queries
agent = {{AgentName}}(model="gpt-3.5-turbo", max_sources=3)
```

### 4. **Monitor Usage**

```python
result = agent.research(query)
print(f"Duration: {result.duration:.1f}s")
print(f"API calls: {result.tool_calls}")
print(f"Sources: {len(result.sources)}")
```

## 📄 License

MIT

## 🤝 Contributing

This is a simple, standalone implementation designed for easy modification. Fork it and make it your own!

1. Copy the code
2. Modify for your needs
3. Add features you want
4. Share improvements

## 💪 Extending the Agent

### Add New Search APIs
```python
def _my_search_api(self, query, max_results):
    # Implementation
    return search_results
```

### Add Content Processing
```python
def _process_content(self, raw_content):
    # Clean, extract, summarize
    return processed_content
```

### Add Result Caching
```python
import sqlite3

class CachedResearchAgent({{AgentName}}):
    def research(self, query):
        # Check cache first
        # Fall back to super().research()
```

### Add Async Support
```python
import asyncio
import aiohttp

class AsyncResearchAgent({{AgentName}}):
    async def research(self, query):
        # Async implementation
```

---

**Why Raw Python?**

Sometimes you need full control, minimal dependencies, and maximum transparency. This implementation gives you exactly that - a simple, powerful research agent you can understand, modify, and extend exactly how you need it.