# AgentOS

Pre-built AI agents you can import and use in one line. No AI knowledge required.

**Think shadcn, but for AI agents.**

## Install

```bash
npm install @agentos/agents
```

## Quick Start

```typescript
import { ResearchAgent } from '@agentos/agents';

const report = await ResearchAgent.run('Compare React vs Svelte in 2026');
console.log(report.output);
```

That's it. No frameworks to learn. No prompt engineering. No tool configuration.

## Authentication

### Option 1: Claude Max/Pro Plan (Recommended)

Use your existing Claude subscription — no API billing needed.

```bash
# Generate an OAuth token (valid for 1 year)
claude setup-token

# Set it in your environment
export CLAUDE_CODE_OAUTH_TOKEN=sk-ant-oat01-...
```

AgentOS auto-detects the token. No code changes needed.

### Option 2: Anthropic API Key

```bash
export ANTHROPIC_API_KEY=sk-ant-...
```

### Option 3: Explicit Configuration

```typescript
import { configure } from '@agentos/agents';

// With OAuth token (Max/Pro plan)
configure({ oauthToken: process.env.CLAUDE_CODE_OAUTH_TOKEN });

// Or with API key
configure({ apiKey: process.env.ANTHROPIC_API_KEY });
```

**Auth resolution order:** `CLAUDE_CODE_OAUTH_TOKEN` > `AGENTOS_API_KEY` > `ANTHROPIC_API_KEY` > config values.

## Available Agents

| Agent | What it does | Import |
|-------|-------------|--------|
| **Research Agent** | Web research with structured reports and citations | `ResearchAgent` |
| **Code Review Agent** | Security, quality, and best practices analysis | `CodeReviewAgent` |
| **Content Writer** | Blog posts, docs, marketing copy | `ContentWriter` |
| **Data Analyst** | CSV/JSON profiling and statistical analysis | `DataAnalyst` |
| **Competitor Analyzer** | Market landscape and competitive analysis | `CompetitorAnalyzer` |
| **Email Drafter** | Professional emails — cold outreach, follow-ups, internal comms | `EmailDrafter` |
| **SEO Auditor** | Website SEO audit with scoring and recommendations | `SEOAuditor` |
| **Bug Triager** | Bug report classification, root cause analysis, fix suggestions | `BugTriager` |

### Usage Examples

```typescript
import {
  ResearchAgent,
  CodeReviewAgent,
  EmailDrafter,
  SEOAuditor,
  BugTriager,
  DataAnalyst,
} from '@agentos/agents';

// Research a topic
const report = await ResearchAgent.run('AI agent frameworks comparison 2026');

// Review code
const review = await CodeReviewAgent.run('./src/auth.ts');

// Draft an email
const email = await EmailDrafter.run(
  'Follow-up email to an investor after a demo call, casual tone'
);

// Audit SEO
const seo = await SEOAuditor.run('https://mysite.com');

// Triage a bug
const triage = await BugTriager.run(
  'Login page crashes on Safari when clicking Forgot Password'
);

// Analyze data
const analysis = await DataAnalyst.run('./sales-data.csv');
```

### Result Shape

Every agent returns an `AgentResult`:

```typescript
const result = await ResearchAgent.run('...');

result.output       // string — the agent's final response
result.success      // boolean — whether it completed successfully
result.toolCalls    // array — tools used during execution
result.tokensUsed   // { input, output, total }
result.cost         // number — estimated cost in USD
result.duration     // number — execution time in ms
result.loops        // number — agentic loop iterations
```

## Build Your Own

```typescript
import { createAgent } from '@agentos/agents';

// From a plain English description
const agent = await createAgent(
  'An agent that monitors tech news and summarizes the top stories'
);
const summary = await agent.run('What happened in tech today?');

// From a structured spec
const agent = await createAgent({
  task: 'Analyze GitHub repositories',
  inputs: 'Repository URL or name',
  outputs: 'Report with stars, issues, activity metrics',
  tools: ['web_search', 'web_scrape'],
});
```

## Streaming

```typescript
import { Agent } from '@agentos/agents';

const agent = new Agent({
  instructions: 'You are a helpful assistant.',
  tools: [],
});

for await (const event of agent.stream('Tell me about TypeScript')) {
  if (event.type === 'text_delta') {
    process.stdout.write(event.delta ?? '');
  }
  if (event.type === 'tool_start') {
    console.log(`\nUsing tool: ${event.tool}`);
  }
  if (event.type === 'done') {
    console.log(`\nCost: $${event.finalResult?.cost}`);
  }
}
```

## CLI

```bash
npx agentos list              # See all 8 available agents
npx agentos try research      # Try an agent interactively
npx agentos try email         # Try the email drafter
npx agentos create            # Build a custom agent via prompts
npx agentos init my-project   # Scaffold a new project
```

## Configuration

```typescript
import { configure } from '@agentos/agents';

configure({
  oauthToken: '...',            // Claude Max/Pro plan OAuth token
  apiKey: '...',                // Or Anthropic API key
  baseUrl: '...',               // Custom API endpoint (proxy support)
  defaultModel: 'claude-sonnet-4-6',
  maxLoops: 10,                 // Global loop limit
  maxSpendPerRun: 1.00,         // Circuit breaker: max $ per agent run
  maxConcurrentRuns: 5,         // Limit concurrent agent executions
  verbose: true,                // Enable debug logging
});
```

Set `BRAVE_SEARCH_API_KEY` for better web search results (falls back to DuckDuckGo if not set).

## Safety Features

- **Spend limits** — Circuit breaker stops agents that exceed cost threshold (default: $1/run)
- **Loop limits** — Prevents runaway agent loops (configurable per agent)
- **Tool timeouts** — 30-second timeout on tool execution
- **Rate limit retry** — Automatic exponential backoff on 429/529 errors
- **Concurrency control** — Limit how many agents run simultaneously

## How It Works

AgentOS wraps the Anthropic Claude SDK internally. Each pre-built agent is a curated combination of:

- **System prompt** refined for reliable, high-quality outputs
- **Tool integrations** (web search, scraping, file reading) with error handling and content parsing
- **Safety controls** (loop limits, cost tracking, spend caps, timeouts)

You get the results. We handle the complexity.

## Architecture

```
@agentos/agents (the library)
├── 8 pre-built agents with curated prompts
├── Agent base class (agentic tool-use loop)
├── Tool implementations (web search, scrape, file ops)
├── Auth resolution (OAuth token / API key / proxy)
└── Safety layer (spend limits, retries, timeouts)

@agentos/cli (the CLI)
├── list — browse available agents
├── try  — run agents interactively
├── create — build custom agents via chat
└── init — scaffold new projects
```

Internally uses the Anthropic SDK. Not a framework — a library of ready-to-use agents.

## Development

```bash
pnpm install
pnpm build
pnpm test         # 70 tests across 7 suites
```

## License

MIT
