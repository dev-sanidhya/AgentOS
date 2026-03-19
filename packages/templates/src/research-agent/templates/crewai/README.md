# {{AgentName}} - CrewAI Multi-Agent Research Implementation

A powerful multi-agent research system built with CrewAI that coordinates specialized agents to conduct comprehensive research and analysis.

## 🚀 Overview

This implementation uses **CrewAI** to orchestrate multiple AI agents working together:

- 🔍 **Researcher Agent**: Finds and gathers information from multiple sources
- 📊 **Analyst Agent**: Analyzes data and extracts key insights
- ✍️ **Writer Agent**: Creates comprehensive, well-structured reports

The agents work sequentially to deliver thorough research with proper analysis and professional reporting.

## 🎯 Features

- **Multi-Agent Coordination**: Specialized agents for different research phases
- **Sequential Processing**: Each agent builds on the previous agent's work
- **Web Search Integration**: Built-in search tools via Serper API
- **Content Extraction**: Web scraping capabilities for detailed analysis
- **Multiple LLM Support**: Works with OpenAI GPT and Anthropic Claude models
- **Flexible Configuration**: Customizable temperature, iterations, and verbosity

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

# Add search API key (highly recommended)
echo "SERPER_API_KEY=your-serper-key" >> .env
```

### 3. Get API Keys

**LLM Provider (Required):**
- [OpenAI API](https://platform.openai.com/api-keys) - For GPT models
- [Anthropic API](https://console.anthropic.com/) - For Claude models

**Search API (Recommended):**
- [Serper](https://serper.dev/) - Google search API optimized for AI (recommended for CrewAI)

## 🎯 Quick Start

### Simple Research

```python
from {{agent_name}}_crew import research

# Quick research with default settings
result = research("What are the latest advances in quantum computing?")
print(result)
```

### Advanced Usage

```python
from {{agent_name}}_crew import {{AgentName}}

# Create research crew with custom configuration
crew = {{AgentName}}(
    model="gpt-4",           # or "claude-3-opus-20240229"
    temperature=0.7,         # creativity level (0-1)
    verbose=True,            # show agent interactions
    max_iterations=3         # max iterations per agent
)

# Conduct research
result = crew.research("Analyze the impact of AI on modern healthcare")

# Access results
print(f"Success: {result['success']}")
print(f"Agents Used: {result['agents_used']}")
print(f"Report: {result['output']}")
```

### Run Examples

```bash
python example.py
```

## 🏗️ How It Works

### The Research Process

1. **🔍 Research Phase**
   - The Researcher agent searches for information
   - Gathers data from multiple sources and perspectives
   - Identifies authoritative sources and recent developments

2. **📊 Analysis Phase**
   - The Analyst agent processes all gathered information
   - Identifies patterns, trends, and key insights
   - Prioritizes information by importance and reliability

3. **✍️ Writing Phase**
   - The Writer agent synthesizes everything into a report
   - Creates structured, professional documentation
   - Includes proper citations and clear organization

### Agent Roles

```python
# Researcher Agent
role='Senior Research Specialist'
goal='Find the most relevant and up-to-date information'

# Analyst Agent
role='Data Analysis Expert'
goal='Analyze and synthesize information to extract key insights'

# Writer Agent
role='Research Report Writer'
goal='Create comprehensive, well-structured research reports'
```

## 📖 API Reference

### {{AgentName}} Class

```python
class {{AgentName}}:
    def __init__(
        self,
        model: str = "gpt-4",
        temperature: float = 0.7,
        verbose: bool = True,
        max_iterations: int = 5
    )

    def research(self, query: str) -> Dict[str, Any]
```

### Configuration Options

- `model`: LLM model ("gpt-4", "gpt-3.5-turbo", "claude-3-opus-20240229")
- `temperature`: Creativity level (0.0 = factual, 1.0 = creative)
- `verbose`: Show detailed agent interactions
- `max_iterations`: Maximum iterations per agent

### Return Format

```python
{
    "query": "Your research question",
    "output": "Complete research report",
    "agents_used": ["Researcher", "Analyst", "Writer"],
    "tasks_completed": 3,
    "success": True
}
```

## 🎯 Supported Models

### OpenAI Models
- `gpt-4` - Most capable (recommended)
- `gpt-4-turbo` - Faster and more cost-effective
- `gpt-3.5-turbo` - Budget-friendly option

### Anthropic Models
- `claude-3-opus-20240229` - Most capable Claude model
- `claude-3-sonnet-20240229` - Balanced performance and cost
- `claude-3-haiku-20240307` - Fastest and most economical

## 🛠️ Customization

### Different Research Types

```python
# Factual research (low temperature)
crew = {{AgentName}}(temperature=0.2, max_iterations=3)

# Creative research (high temperature)
crew = {{AgentName}}(temperature=0.8, max_iterations=5)

# Quick research (fewer iterations)
crew = {{AgentName}}(max_iterations=2, model="gpt-3.5-turbo")
```

### Custom Agent Configuration

You can modify the agents in the `_create_crew()` method:

```python
# Modify agent backstories, goals, or tools
# Add custom tools to the tools list
# Adjust agent interaction patterns
```

## 📁 Project Structure

```
{{agent_name}}/
├── {{agent_name}}_crew.py    # Main crew implementation
├── requirements.txt          # Python dependencies
├── example.py               # Usage examples
├── .env.example            # Environment template
└── README.md              # This file
```

## 🔧 Troubleshooting

### Common Issues

**"No API key found"**
- Ensure your `.env` file has `OPENAI_API_KEY` or `ANTHROPIC_API_KEY`
- Check that the key is valid and has sufficient credits

**"Search failed" or limited results**
- Set up `SERPER_API_KEY` for web search functionality
- CrewAI tools work best with Serper integration

**Slow performance**
- Use `gpt-3.5-turbo` for faster responses
- Reduce `max_iterations` for quicker results
- Set `verbose=False` to reduce output processing

**Agent delegation errors**
- Ensure sufficient context window for your model
- Try reducing the complexity of your research query

### Debug Mode

Enable verbose logging to see agent interactions:

```python
crew = {{AgentName}}(verbose=True)
```

## 🏆 Best Practices

1. **Clear Research Questions**
   ```python
   # ❌ Vague
   result = crew.research("Tell me about AI")

   # ✅ Specific
   result = crew.research("How is AI being used in drug discovery in 2026?")
   ```

2. **Choose Appropriate Temperature**
   ```python
   # For factual research
   crew = {{AgentName}}(temperature=0.2)

   # For creative analysis
   crew = {{AgentName}}(temperature=0.8)
   ```

3. **Error Handling**
   ```python
   try:
       result = crew.research(query)
       if result['success']:
           print(result['output'])
       else:
           print(f"Research failed: {result.get('error')}")
   except Exception as e:
       print(f"Error: {e}")
   ```

4. **Resource Management**
   - Monitor API usage for cost control
   - Use appropriate models for your needs
   - Consider caching for repeated queries

## 🌟 Advantages of CrewAI

- **Specialized Agents**: Each agent focuses on their expertise
- **Quality Control**: Multiple agents review and improve the work
- **Structured Process**: Systematic approach to research
- **Scalable**: Easy to add more agents or modify the process
- **Collaborative**: Agents can delegate tasks to each other

## 📄 License

MIT

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📚 Learn More

- [CrewAI Documentation](https://docs.crewai.com/)
- [CrewAI Tools](https://github.com/joaomdmoura/crewai-tools)
- [Serper API](https://serper.dev/)