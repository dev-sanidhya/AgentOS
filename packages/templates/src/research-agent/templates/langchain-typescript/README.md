# {{AgentName}} - AI Research Assistant (TypeScript)

An intelligent research agent built with LangChain and TypeScript that searches the web, extracts content, and synthesizes comprehensive reports from multiple sources.

## Features

- 🔍 **Web Search**: Search the web for information on any topic
- 📄 **Content Extraction**: Scrape and read web pages in detail
- 🧠 **Information Synthesis**: Combine insights from multiple sources
- 📊 **Structured Reports**: Generate well-organized research outputs
- 🔄 **Multiple LLM Support**: Works with OpenAI GPT models and Anthropic Claude
- 🛡️ **Type Safety**: Full TypeScript support with strict typing

## Installation

### 1. Install Dependencies

```bash
npm install
```

### 2. Configure Environment

Copy `.env.example` to `.env` and add your API keys:

```bash
# Copy the example .env file
cp .env.example .env

# Add your API keys (choose one)
echo "OPENAI_API_KEY=sk-..." >> .env
# OR
echo "ANTHROPIC_API_KEY=sk-ant-..." >> .env
```

### 3. (Optional) Set up a search API for real web search:

Choose one of these options:

**Option 1: Brave Search (Recommended)**
- Sign up at https://brave.com/search/api/
- Add to .env: `BRAVE_API_KEY=your_key`

**Option 2: SerpAPI (Google Search)**
- Sign up at https://serpapi.com/
- Add to .env: `SERPAPI_KEY=your_key`

**Option 3: Tavily (AI-optimized)**
- Sign up at https://tavily.com/
- Add to .env: `TAVILY_API_KEY=your_key`

## Usage

### Quick Start

```typescript
import { research } from './{{agent_name}}';

// Simple research query
const result = await research('What are the latest trends in AI?');
console.log(result);
```

### Advanced Usage

```typescript
import { {{AgentName}} } from './{{agent_name}}';

// Initialize with configuration
const agent = new {{AgentName}}({
  model: 'gpt-4',          // or 'claude-3-opus-20240229'
  temperature: 0.7,        // creativity level (0-1)
  maxIterations: 10,       // max research steps
  verbose: true            // enable logging
});

// Conduct research
const result = await agent.research('Compare quantum computing and classical computing');

// Access results
console.log(result.output);                    // Final research report
console.log(result.intermediateSteps);        // Tool calls and results
```

### Build and Run

```bash
# Build the project
npm run build

# Run the example
npm run example

# Development mode
npm run dev
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

```typescript
interface {{AgentName}}Config {
  model?: string;              // LLM model to use
  temperature?: number;        // 0 = focused, 1 = creative
  maxIterations?: number;      // Maximum research steps
  verbose?: boolean;           // Enable detailed logging
}
```

## Project Structure

```
{{agent_name}}/
├── {{agent_name}}.ts         # Main agent class
├── prompts.ts                # System prompts
├── tools/
│   ├── index.ts
│   ├── webSearch.ts         # Web search tool  
│   └── webScrape.ts         # Web scraping tool
├── package.json             # Dependencies
├── tsconfig.json            # TypeScript config
├── example.ts              # Usage examples
├── .env.example           # Environment template
└── README.md             # This file
```

## Customization

### Custom Prompts

You can use alternative prompts for specific use cases:

```typescript
import { {{AgentName}} } from './{{agent_name}}';
import { 
  FACT_CHECKING_PROMPT,
  MARKET_RESEARCH_PROMPT,
  ACADEMIC_RESEARCH_PROMPT 
} from './prompts';

// Create agent with custom prompt
const agent = new {{AgentName}}({ model: 'gpt-4' });
// Note: Prompt customization requires modifying the agent initialization
```

Available prompt variants:
- `RESEARCH_AGENT_PROMPT` (default): General-purpose research
- `FACT_CHECKING_PROMPT`: Verify claims with sources
- `MARKET_RESEARCH_PROMPT`: Business and market analysis
- `ACADEMIC_RESEARCH_PROMPT`: Scholarly research

### Add Custom Tools

```typescript
import { Tool } from '@langchain/core/tools';
import { {{AgentName}} } from './{{agent_name}}';

// Define custom tool
class MyCustomTool extends Tool {
  name = 'my_tool';
  description = 'What this tool does';

  async _call(input: string): Promise<string> {
    // Your tool logic
    return 'Result';
  }
}

// Add to agent (requires modification of the agent class)
const customTool = new MyCustomTool();
```

## API Reference

### {{AgentName}}

```typescript
class {{AgentName}} {
  constructor(config?: {{AgentName}}Config)
  research(query: string): Promise<ResearchResult>
  aresearch(query: string): Promise<ResearchResult> // Alias for research
}
```

### ResearchResult

```typescript
interface ResearchResult {
  output: string;                    // Final research report
  intermediateSteps: Array<{         // Tool calls and results
    action: {
      tool: string;
      toolInput: any;
    };
    observation: string;
  }>;
  logs?: string[];                   // Execution logs
}
```

## Troubleshooting

**No API key found:**
- Make sure you have a `.env` file with `OPENAI_API_KEY` or `ANTHROPIC_API_KEY`

**Mock search results:**
- The web search uses a placeholder by default
- Set up a real search API (Brave, SerpAPI, or Tavily) for actual web search

**TypeScript compilation errors:**
- Run `npm run build` to check for type errors
- Ensure all dependencies are installed

**Agent not finding information:**
- Try rephrasing your query more specifically
- Enable verbose mode to see what the agent is doing
- Check your search API rate limits

## Best Practices

1. **Be Specific**: Clear, specific queries yield better results
2. **Iterate**: Use follow-up queries to drill into details
3. **Verify**: Always cross-check critical information
4. **Monitor Usage**: Track API calls for cost management
5. **Enable Logging**: Use `verbose: true` for debugging
6. **Type Safety**: Leverage TypeScript types for better development experience

## Development

```bash
# Install dependencies
npm install

# Build the project
npm run build

# Run in development mode
npm run dev

# Clean build artifacts
npm run clean
```

## License

MIT

## Contributing

Contributions welcome! Feel free to submit issues or pull requests.
