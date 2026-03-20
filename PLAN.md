# AgentOS — Product & Architecture Plan

## What AgentOS Is

**One-liner:** Pre-built AI agents you can import and use in one line. No AI knowledge required.

AgentOS is a library of production-ready AI agents that anyone can import into their project. It targets the non-technical "vibe coder" audience — people who want to use AI agents but don't have the know-how to build them from scratch.

The original analogy: **shadcn, but for agents.**

## How This Differs From the Original Codebase

The original AgentOS repo had:

| Original Setup | Problem |
|---|---|
| Custom `AgentRuntime` execution engine | Reinventing the wheel — competing with LangChain, CrewAI, etc. |
| 5 template agents with simulated/fake outputs | Not real agents — just scaffolding |
| Multi-framework support (LangChain, CrewAI, 14 variants) | Too scattered — supporting everything means building nothing |
| CLI focused on scaffolding (`agent add`, `project init`) | Copy-paste workflow, not import-and-use |
| Event system for observability | Only worked for agents built on AgentOS's own runtime |
| No actual API calls or real LLM integration | Couldn't actually do anything useful |

### What Changed

| New Setup | Why |
|---|---|
| Built on **Claude Agent SDK** (`@anthropic-ai/claude-agent-sdk`) | No custom runtime. We use Anthropic's battle-tested agent infrastructure. |
| 8 real agents with real tool access | WebSearch, WebFetch, Read, Glob, Grep, Bash — all via Claude Code |
| **One framework only** — Claude Agent SDK | Focus beats breadth. |
| Import-based usage (`import { ResearchAgent } from '@agentos/agents'`) | npm install + import, not copy-paste templates |
| OAuth token support (Claude Max/Pro plan) | Users can run agents with their existing Claude subscription — no API billing needed |

## Architecture

### The Core Decision: We Are NOT Building an Agent Framework

We don't compete with LangChain, CrewAI, or the Anthropic SDK. We're a **curated library on top of the Claude Agent SDK.** The SDK does the hard work (agent loops, tool calling, streaming, auth). We add:

1. **Pre-built, tested agent prompts** that work out of the box
2. **Tool configuration** (which SDK tools each agent can access)
3. **Cost controls** (max budget per run, concurrency limits)
4. **Simple API surface** (`agent.run("query")` → result)

### How It Works Internally

```
User code:
  import { ResearchAgent } from '@agentos/agents'
  const result = await ResearchAgent.run("AI trends 2026")
            │
            ▼
  Agent class (packages/agents/src/agent.ts)
    - Builds system prompt from agent's instructions
    - Configures allowedTools (WebSearch, WebFetch, etc.)
    - Sets cost limits, max turns
    - Passes OAuth token via environment
            │
            ▼
  Claude Agent SDK (query() function)
    - Spawns Claude Code as a subprocess
    - Handles the full agentic loop
    - Executes tools (search, read files, etc.)
    - Returns streaming messages
            │
            ▼
  Agent class processes the stream
    - Collects text output, tool calls, costs
    - Returns structured AgentResult
```

### Authentication — Claude Max/Pro Plan via OAuth

From the [Divya Ranjan thread](https://x.com/divyaranjan_/status/2011468323742155069):

```bash
# Step 1: Generate a 1-year OAuth token from your Claude subscription
claude setup-token

# Step 2: Set it in your environment
export CLAUDE_CODE_OAUTH_TOKEN=sk-ant-oat01-...

# Step 3: Use AgentOS — no API key, no billing
```

The OAuth token is passed to the Claude Agent SDK subprocess via environment variables. The SDK handles authentication with Anthropic's servers using the user's existing Claude subscription.

**Priority order for auth resolution:**
1. `CLAUDE_CODE_OAUTH_TOKEN` (Max/Pro plan — recommended)
2. `oauthToken` in configure()
3. `AGENTOS_API_KEY` (future proxy)
4. `ANTHROPIC_API_KEY` (standard API billing)
5. `apiKey` in configure()

## Business Model

### The Proxy Play (Future — Path B)

Right now, users bring their own auth (OAuth token or API key). The future monetization path:

```typescript
// Future: One key for everything
configure({ agentosKey: process.env.AGENTOS_API_KEY });
```

**How it works:**
- User gets one API key from AgentOS
- We proxy to Anthropic (and future providers)
- We add a margin on usage
- User doesn't deal with multiple API providers

**Why vibe coders will pay:**
- One key instead of managing 5 different API accounts
- Built-in spend limits and usage dashboards
- No surprise bills — we handle rate limiting and cost controls

**Revenue model:** Usage-based with a markup (e.g., 20-30% on top of Anthropic's pricing), or tiered subscription with included credits.

### Why This Is Defensible

The agent code itself is simple (~30 lines per agent). The moat is in:

1. **Tool integrations that just work** — The Claude Agent SDK gives us WebSearch, WebFetch, file operations, code execution out of the box. Users don't configure anything.
2. **Curated, tested prompts** — Each agent's system prompt has been refined for quality output. A ResearchAgent that returns garbage isn't useful even if it's easy to import.
3. **The proxy/billing abstraction** — Once users are on our proxy, switching cost is real.
4. **The library effect** — More agents = more value. Network effects as community contributes agents.

## Product Scope

### What Ships Now (MVP)

| Component | Status |
|---|---|
| `@agentos/agents` npm package | Built — 8 pre-built agents |
| Claude Agent SDK integration | Built — uses `query()` from SDK |
| OAuth token auth | Built — Claude Max/Pro plan support |
| Cost controls | Built — max budget per run, concurrency limits |
| Agent builder (`createAgent()`) | Built — create custom agents from description |
| CLI (`agentos try`, `agentos list`, `agentos create`, `agentos init`) | Built |
| Unit tests | 76 tests passing |

### Pre-Built Agents

| Agent | Tools | Use Case |
|---|---|---|
| `ResearchAgent` | WebSearch, WebFetch, Read | Multi-source research reports with citations |
| `CodeReviewAgent` | Read, Glob, Grep | Actionable code reviews (security, quality, performance) |
| `ContentWriter` | WebSearch, WebFetch | Blog posts, docs, marketing copy, social media |
| `DataAnalyst` | Read, Glob, Bash | CSV/JSON analysis with insights and recommendations |
| `CompetitorAnalyzer` | WebSearch, WebFetch | Competitive landscape analysis |
| `EmailDrafter` | None (pure text) | Professional email drafting |
| `SEOAuditor` | WebSearch, WebFetch | Website SEO audits with prioritized fixes |
| `BugTriager` | Read, Glob, Grep | Bug report classification and root cause analysis |

### What Ships Next

| Feature | Priority |
|---|---|
| Streaming API (`agent.stream()`) | High — already implemented |
| AgentOS proxy service (one API key) | High — monetization |
| Dashboard (usage tracking, cost monitoring) | Medium |
| More agents (20+ library) | Medium |
| Community agent contributions | Medium |
| Agent marketplace | Low — future |

## Is This Actually Useful?

**Yes, for the right audience.** The target isn't senior engineers who can write their own agents in 30 lines. It's:

- **Vibe coders** who know enough JavaScript to import a package but not enough to understand tool-use protocols
- **Product managers / founders** who want to prototype agent-powered features quickly
- **Small teams** who don't want to spend a week learning LangChain

**The value prop is not the code — it's the curation.** A `ResearchAgent` that reliably produces good reports with citations saves hours of prompt engineering and tool configuration.

## Technical Decisions

### Why Claude Agent SDK (not raw API calls)

| Approach | Pros | Cons |
|---|---|---|
| Raw Anthropic API (`messages.create`) | Full control, lighter weight | Must implement tool execution, agent loop, error handling yourself |
| Claude Agent SDK (`query()`) | Built-in tool execution (WebSearch, file ops, code execution), battle-tested agent loop, OAuth support | Heavier (spawns subprocess), less control over individual steps |

We chose the SDK because:
1. **Tool execution is free** — WebSearch, WebFetch, file operations all work out of the box. With raw API, we'd need to implement each tool ourselves.
2. **OAuth support** — The SDK natively supports Claude Max/Pro plan tokens. Raw API doesn't.
3. **The agent loop is handled** — Tool-use cycling, error recovery, context management — all handled by the SDK.

### Why Not LangChain / CrewAI / etc.

The original codebase tried to support multiple frameworks (LangChain Python, CrewAI, etc.). This was wrong because:

1. **Maintenance nightmare** — 14 template variants, each with different bugs
2. **No depth** — Supporting everything means excelling at nothing
3. **Wrong abstraction** — Templates are copy-paste; imports are install-and-use
4. **Claude Agent SDK is better for our use case** — It gives us real tool execution (web search, file reading, code execution) for free, which is the hardest part of making agents actually useful

## Running the Project

```bash
# Install dependencies
pnpm install

# Build
pnpm build

# Run tests
pnpm --filter @agentos/agents test

# Set up auth (Claude Max/Pro plan)
claude setup-token
export CLAUDE_CODE_OAUTH_TOKEN=sk-ant-oat01-...

# Try an agent
npx agentos try research "AI trends in 2026"
```

## File Structure

```
packages/
  agents/
    src/
      agent.ts           # Base Agent class (wraps Claude Agent SDK)
      config.ts           # Global config + auth resolution
      types.ts            # TypeScript interfaces
      create-agent.ts     # Custom agent builder
      index.ts            # Public API exports
      agents/             # Pre-built agents (8 agents)
        research.ts
        code-review.ts
        content-writer.ts
        data-analyst.ts
        competitor-analyzer.ts
        email-drafter.ts
        seo-auditor.ts
        bug-triager.ts
      tools/              # Legacy tool implementations (kept for reference)
      __tests__/          # 76 unit tests
  cli/
    src/
      index.ts            # CLI entry point
      commands/            # try-agent, create, init, list
```
