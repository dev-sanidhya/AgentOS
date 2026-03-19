# 🤖 Agent Platform

> The first comprehensive Developer Experience Platform for AI Agents

Build, test, and deploy AI agents with a powerful CLI, real-time dev server, and production-ready templates.

## ✨ Features

- 🚀 **CLI-First**: Simple commands to scaffold, run, and manage AI agents
- 🔍 **Real-time Observability**: Dev server with live agent execution viewer
- 🧪 **Testing Framework**: Unit test your agents with mock tools and assertions
- 📦 **High-Quality Templates**: Production-ready agents (research, code review, and more)
- 🛠️ **Extensible Tools**: Built-in tools for web, files, and custom integrations
- 🎨 **Beautiful UI**: Tailwind-powered dashboard for debugging agents
- 🌐 **Multi-Provider**: Support for OpenAI, Anthropic, and custom models

## 🚀 Quick Start

### Installation

```bash
npm install -g @agent-platform/cli
```

### Create Your First Project

```bash
# Initialize a new agent project
agent init my-agent-project

# Navigate to your project
cd my-agent-project

# Install dependencies
npm install

# Run the example agent
agent run example --input "Hello, world!"
```

### Start Dev Server

```bash
# Launch the dev server with real-time UI
agent dev
```

The dev server will open at `http://localhost:3000` with:
- 📊 Real-time execution viewer
- 🔧 Tool call inspector
- 💰 Token usage tracking
- 📝 Execution history

## 📚 Documentation

### CLI Commands

| Command | Description |
|---------|-------------|
| `agent init <name>` | Create a new agent project |
| `agent run <agent> -i <input>` | Execute an agent |
| `agent list` | List all available agents |
| `agent dev` | Start development server |
| `agent test` | Run agent tests |
| `agent add <template>` | Add agent from template |

### Project Structure

```
my-agent-project/
├── agents/              # Your agent definitions
│   └── example.agent.ts
├── tools/               # Custom tools
├── agent.config.ts      # Configuration
├── .env                 # API keys
└── package.json
```

### Creating an Agent

```typescript
import { AgentDefinition, AgentContext } from '@agent-platform/core';

const myAgent: AgentDefinition = {
  name: 'my-agent',
  version: '1.0.0',
  description: 'My custom agent',

  systemPrompt: `You are a helpful AI assistant.`,

  tools: ['web-search'], // Tools this agent uses

  config: {
    model: 'claude-sonnet-4',
    provider: 'anthropic',
    temperature: 0.7,
    maxTokens: 4000,
  },

  async execute(input: string, context: AgentContext): Promise<string> {
    // Your agent logic here
    return `Processed: ${input}`;
  },
};

export default myAgent;
```

## 🎯 Built-in Agent Templates

### Research Agent
**Best for**: Market research, competitive analysis, information gathering

```bash
agent add research-agent
agent run research-agent --input "Latest AI trends in 2026"
```

Features:
- Multi-source web search
- Content extraction and analysis
- Source citation and verification
- Comprehensive report generation

### Code Review Agent
**Best for**: Pull request reviews, code quality audits, mentoring

```bash
agent add code-review-agent
agent run code-review-agent --input "./src/app.ts"
```

Features:
- Code quality analysis
- Security vulnerability detection
- Best practices validation
- Performance optimization suggestions
- Detailed review reports

## 🛠️ Built-in Tools

### Web Tools
- **web-search**: Search the web for information
- **web-scrape**: Extract content from web pages
- **http-request**: Make HTTP API requests

### File Tools
- **read-file**: Read file contents
- **write-file**: Write to files
- **list-files**: List directory contents
- **file-stats**: Get file metadata

### Creating Custom Tools

```typescript
import { Tool } from '@agent-platform/core';
import { z } from 'zod';

export const myTool: Tool = {
  name: 'my-tool',
  description: 'Description of what this tool does',

  parameters: z.object({
    input: z.string().describe('Input parameter'),
  }),

  async execute(params, context) {
    // Tool implementation
    return { result: 'Tool output' };
  },
};
```

## 🔧 Configuration

### Environment Variables

Create a `.env` file in your project root:

```env
# API Keys
OPENAI_API_KEY=your_openai_key
ANTHROPIC_API_KEY=your_anthropic_key

# Agent Configuration
DEFAULT_MODEL=claude-sonnet-4
ENABLE_LOGGING=true
```

### Agent Config

Customize agent behavior in `agent.config.ts`:

```typescript
export const config = {
  provider: 'anthropic',
  model: 'claude-sonnet-4',
  temperature: 0.7,
  maxTokens: 4000,
};
```

## 📊 Dev Server Features

The dev server provides real-time insights into agent execution:

### Execution Viewer
Watch agents think and act in real-time:
- See tool calls as they happen
- View reasoning steps
- Track token usage and costs
- Monitor performance

### Tool Inspector
Debug tool calls with detailed views:
- Input parameters
- Output results
- Execution time
- Error messages

### History
Browse past executions:
- Filter by agent or status
- Compare different runs
- Export execution data

## 🧪 Testing (Coming in Phase 3)

```typescript
import { test, expect } from '@agent-platform/testing';

test('research agent finds information', async () => {
  const result = await runAgent('research-agent', {
    input: 'AI trends',
    mock: {
      'web-search': {
        return: [/* mock results */]
      }
    }
  });

  expect(result.usedTools).toContain('web-search');
  expect(result.status).toBe('success');
});
```

## 🏗️ Architecture

Agent Platform is built as a monorepo with the following packages:

- **@agent-platform/core**: Agent runtime and types
- **@agent-platform/cli**: Command-line interface
- **@agent-platform/dev-server**: Development server
- **@agent-platform/templates**: Production agent templates
- **@agent-platform/ui**: Shared UI components

## 🎯 Roadmap

### ✅ Phase 0-1: Foundation (Current)
- [x] Monorepo setup
- [x] Core runtime
- [x] CLI with init, run, list commands
- [x] High-quality agent templates

### 🚧 Phase 2: Dev Server (Next)
- [ ] Real-time execution viewer
- [ ] Tool call inspector
- [ ] WebSocket events
- [ ] Beautiful Tailwind UI

### 📋 Phase 3: Testing
- [ ] Agent testing framework
- [ ] Mock system for tools
- [ ] Assertion library
- [ ] CI/CD integration

### 🌐 Phase 4: Marketplace
- [ ] Agent publishing
- [ ] Community templates
- [ ] Version control
- [ ] Discovery and search

### 🎨 Phase 5: Visual Builder
- [ ] Drag-and-drop flow designer
- [ ] Code generation
- [ ] Two-way sync

### 🚀 Phase 6: Production
- [ ] One-command deployment
- [ ] Multi-platform support
- [ ] Monitoring and analytics
- [ ] Managed cloud service

## 💻 Development

### Prerequisites
- Node.js >= 18
- pnpm >= 8

### Setup

```bash
# Clone the repository
git clone https://github.com/yourusername/agent-platform.git
cd agent-platform

# Install dependencies
pnpm install

# Build all packages
pnpm build

# Run in development mode
pnpm dev
```

### Project Structure

```
agent-platform/
├── packages/
│   ├── core/           # Agent runtime
│   ├── cli/            # CLI tool
│   ├── dev-server/     # Dev server (Phase 2)
│   ├── templates/      # Agent templates
│   └── ui/             # UI components (Phase 2)
├── docs/               # Documentation
└── examples/           # Example projects
```

## 🤝 Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## 📄 License

MIT License - see [LICENSE](LICENSE) for details.

## 🙏 Acknowledgments

Built with:
- [oclif](https://oclif.io/) - CLI framework
- [TypeScript](https://www.typescriptlang.org/)
- [Anthropic Claude](https://www.anthropic.com/)
- [OpenAI](https://openai.com/)

## 📞 Support

- 📖 [Documentation](https://agent-platform.dev/docs)
- 💬 [Discord Community](https://discord.gg/agent-platform)
- 🐛 [Issue Tracker](https://github.com/yourusername/agent-platform/issues)
- 🐦 [Twitter](https://twitter.com/agent_platform)

---

**Ready to build something amazing? Start with `agent init` and let's go! 🚀**
