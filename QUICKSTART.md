# 🚀 Quick Start Guide

## What We've Built

✅ **Complete Phase 0 & 1 (MVP CLI)**

We've created a fully functional AI Agent Development Platform with:

### Packages Created:
1. **@agent-platform/core** - Agent runtime engine with types and utilities
2. **@agent-platform/cli** - Command-line tool with `init`, `run`, and `list` commands
3. **@agent-platform/templates** - Production-ready agent templates

### High-Quality Agents:
1. **Research Agent** - Web search, content extraction, and comprehensive reporting
2. **Code Review Agent** - Security analysis, quality checks, and detailed reviews

### Built-in Tools:
- Web search, scraping, and HTTP requests
- File reading, writing, and listing
- Fully extensible tool system

---

## 🏃 Next Steps to Run the Platform

### 1. Install Dependencies

```bash
# Make sure you have pnpm installed
npm install -g pnpm

# Install all dependencies
pnpm install
```

### 2. Build the Packages

```bash
# Build all packages in the monorepo
pnpm build
```

### 3. Link the CLI Locally (for development)

```bash
# Go to the CLI package
cd packages/cli

# Link it globally for testing
npm link

# Now you can use the 'agent' command anywhere
agent --help
```

### 4. Test the CLI

```bash
# Create a new project
agent init my-test-project

# Go into the project
cd my-test-project

# Install dependencies
npm install

# Run the example agent
agent run example --input "Hello Agent Platform!"

# List all agents
agent list
```

---

## 🔧 Development Workflow

### Running in Dev Mode

```bash
# In the root of agent-platform, start watch mode for all packages
pnpm dev
```

This will:
- Watch for changes in all packages
- Auto-rebuild on file changes
- Hot reload your agents

### Testing Your Changes

```bash
# After making changes, rebuild
pnpm build

# Test the CLI
cd ../my-test-project
agent run example --input "Test my changes"
```

---

## 📝 Creating Your First Custom Agent

1. In your agent project (`my-test-project`), create a new agent file:

```typescript
// agents/greeter.agent.ts
import { AgentDefinition, AgentContext } from '@agent-platform/core';

const greeterAgent: AgentDefinition = {
  name: 'greeter',
  version: '1.0.0',
  description: 'A friendly greeting agent',

  systemPrompt: 'You are a friendly greeter who creates personalized greetings.',

  tools: [],

  config: {
    model: 'claude-sonnet-4',
    provider: 'anthropic',
    temperature: 0.9,
    maxTokens: 500,
  },

  async execute(input: string, context: AgentContext): Promise<string> {
    const name = input.trim();
    const hour = new Date().getHours();

    const timeGreeting = hour < 12 ? 'Good morning'
                       : hour < 18 ? 'Good afternoon'
                       : 'Good evening';

    return `${timeGreeting}, ${name}! 👋\n\nWelcome to Agent Platform! Ready to build something amazing?`;
  },
};

export default greeterAgent;
```

2. Run your custom agent:

```bash
agent run greeter --input "Alice"
```

---

## 🎯 What's Next?

### Immediate Tasks (Optional Enhancements):

1. **Add Real Web Search Integration**
   - Sign up for Brave Search API or SerpAPI
   - Replace placeholder in `packages/templates/src/tools/web-tools.ts`
   - Add API key to `.env`

2. **Add More Agent Templates**
   - Data Analysis Agent
   - Writing Assistant Agent
   - Task Planning Agent

3. **Improve Error Handling**
   - Add better error messages
   - Add validation for agent configs
   - Add retry logic for API calls

### Phase 2: Dev Server (Next Major Milestone)

Once you're happy with the CLI, we'll build:
- Real-time execution viewer
- WebSocket-based live updates
- Beautiful Tailwind UI dashboard
- Tool call inspector
- Cost tracking

---

## 🐛 Troubleshooting

### "Command not found: agent"

```bash
# Make sure you linked the CLI
cd packages/cli
npm link
```

### "Module not found" errors

```bash
# Rebuild all packages
pnpm build
```

### TypeScript errors

```bash
# Make sure you've built the core package first
cd packages/core
pnpm build
```

---

## 📚 Learn More

- Check out `plan.md` for the full roadmap
- Read `README.md` for detailed documentation
- Explore `packages/templates/src/agents/` for agent examples

---

**You're all set! Start building your AI agents! 🚀**

Questions? Just ask!
