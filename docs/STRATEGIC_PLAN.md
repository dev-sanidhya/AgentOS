# AgentOS Strategic Build Plan

> "Pre-built AI agents you can import and use in one line. No AI knowledge required."

---

## 1. What Is AgentOS?

AgentOS is **shadcn but for AI agents** — a library of pre-built, production-ready AI agents that anyone can import and use in one line of code. It targets the growing "vibe coder" market: developers and non-technical builders who want AI agent capabilities without understanding the underlying infrastructure.

### The Core User Experience

```typescript
import { ResearchAgent } from '@agentos/agents';

const report = await ResearchAgent.run("Compare React vs Svelte in 2026");
console.log(report.output);
// → Beautiful structured report with sources, analysis, comparison tables
```

No API key management headaches. No understanding of agentic loops, tool-use protocols, or prompt engineering. Import, call `.run()`, get results.

---

## 2. How This Differs From Our Current Setup

### What We Had Before (Old Architecture)

The original AgentOS was a **template scaffolding tool** — essentially a project generator:

- `packages/core/` — Custom `AgentRuntime` execution engine with event emitters
- `packages/templates/` — 14 template variants across 5 agent types (LangChain Python, CrewAI, raw Python, LangChain TypeScript, raw TypeScript)
- CLI commands like `agent add`, `agent remove`, `agent diff` for managing templates
- Agents were **copied into user's project** as source files
- No real API calls — agents were template skeletons

**Problems with this approach:**
1. Templates became stale the moment they were copied
2. 14 framework variants = massive maintenance burden
3. Users had to understand the template code to customize it
4. No actual agent execution — just scaffolding

### What We Built (Current Architecture)

The codebase was refactored into an **agent library** approach:

- `packages/agents/` — Real, working agents with an agentic loop
- 5 pre-built agents (Research, CodeReview, ContentWriter, DataAnalyst, CompetitorAnalyzer)
- Base `Agent` class with proper tool-use loop via Anthropic SDK
- Real tool implementations (web search, web scrape, file reader)
- CLI for trying agents interactively and building custom ones

**What's still missing:**
- No OAuth/Max plan support (requires API key)
- No streaming
- No error safety (rate limits, spend caps, circuit breakers)
- No tests
- Only 5 agents (target: 8 for MVP)
- No CI/CD or npm publish setup

### Where We're Going (This Plan)

Complete the library into a **shippable v0.1 product** with:
- OAuth token support (use Claude Max plan, no API key needed)
- 8 pre-built agents
- Streaming support
- Production error handling
- Full test coverage
- CI/CD pipeline
- npm-publishable packages

---

## 3. Technical Architecture

### The "Agentic" Base

**We are NOT building our own agent framework.** We are a wrapper around the Anthropic SDK that:

1. Manages the tool-use loop (send message → model requests tool → execute tool → send result → repeat)
2. Packages curated, tested system prompts for common tasks
3. Ships hardened tool implementations (web search, scraping, file ops)
4. Adds safety (spend limits, circuit breakers, rate limit handling)
5. Provides a dead-simple interface (`agent.run("do the thing")`)

Internally, every agent call flows through:

```
User calls agent.run("query")
    ↓
Agent class builds messages array
    ↓
Calls Anthropic SDK: client.messages.create({ model, tools, messages })
    ↓
If response has tool_use blocks → execute tools → add results → loop
    ↓
If response is end_turn → return final text
```

The Anthropic SDK does all the hard work: authentication, streaming, retry, rate limiting at the HTTP level. We just manage the conversation loop on top.

### Authentication: OAuth Token (Claude Max Plan)

Based on the approach from [Divya Ranjan's thread](https://x.com/divyaranjan_/status/2011468323742155069):

Instead of requiring users to get an Anthropic API key and manage billing:

```bash
# Step 1: Generate a long-lived OAuth token from your Claude Max subscription
claude setup-token

# Step 2: Set it in your environment
export CLAUDE_CODE_OAUTH_TOKEN=sk-ant-oat01-xxxxx

# That's it. No API key needed.
```

Our auth resolution order:
1. `CLAUDE_CODE_OAUTH_TOKEN` (Max plan — free with subscription)
2. `AGENTOS_API_KEY` (future proxy service)
3. `ANTHROPIC_API_KEY` (standard API key)
4. Auto-detect from Claude Code login (if already logged in locally)

This dramatically lowers the barrier. Anyone with a Claude Pro/Max subscription can use AgentOS without managing API billing.

### Package Structure

```
packages/
├── agents/          # The library (npm: @agentos/agents)
│   ├── src/
│   │   ├── agent.ts           # Base Agent class (agentic loop)
│   │   ├── config.ts          # Global config + auth resolution
│   │   ├── types.ts           # TypeScript interfaces
│   │   ├── create-agent.ts    # Custom agent builder
│   │   ├── agents/            # Pre-built agents (8 total)
│   │   │   ├── research.ts
│   │   │   ├── code-review.ts
│   │   │   ├── content-writer.ts
│   │   │   ├── data-analyst.ts
│   │   │   ├── competitor-analyzer.ts
│   │   │   ├── email-drafter.ts     # NEW
│   │   │   ├── seo-auditor.ts       # NEW
│   │   │   └── bug-triager.ts       # NEW
│   │   └── tools/             # Tool implementations
│   │       ├── web-search.ts
│   │       ├── web-scrape.ts
│   │       └── file-reader.ts
│   └── __tests__/             # Unit + integration tests
│       ├── agent.test.ts
│       ├── config.test.ts
│       ├── tools/
│       └── agents/
│
└── cli/             # The CLI (npm: @agentos/cli)
    ├── bin/run.js
    └── src/
        ├── index.ts
        └── commands/
            ├── list.ts
            ├── try-agent.ts
            ├── create.ts
            └── init.ts
```

---

## 4. Business Model & Monetization

### Phase 1: Open Source Library (Now → 3 months)

Free, open-source npm package. Users bring their own auth (Max plan OAuth or API key).

**Goal:** Get adoption, build community, establish brand.

### Phase 2: AgentOS Proxy (3-6 months)

One API key for everything: LLM calls + web search + scraping + all tool APIs.

```typescript
configure({ agentosKey: process.env.AGENTOS_API_KEY });
// One key. All tools work. We handle billing.
```

**How it works:**
- User signs up at agentos.dev, gets one API key
- We proxy Anthropic API calls (add margin)
- We provide Brave Search, scraping infrastructure, etc.
- User pays one bill instead of managing 5 API providers

**Revenue model:** Usage-based pricing with margin on API calls.

### Phase 3: Premium Agents & Marketplace (6-12 months)

- Premium agents (more complex, more tools, higher quality)
- Community marketplace where developers publish agents
- Enterprise features (team management, usage controls, audit logs)

### The Proxy Advantage

The proxy isn't just about convenience — it's about data:

1. **Usage analytics**: You know which agents are popular, which fail
2. **Cost optimization**: Cache common requests, batch API calls
3. **Quality improvement**: Analyze failures to improve prompts
4. **Spend controls**: Per-user/per-agent cost limits
5. **Rate limiting**: Protect users from runaway loops

---

## 5. Competitive Positioning

### Who We're NOT Competing With

- **LangChain/CrewAI/Autogen** — These are frameworks for building agents. We're a library of pre-built agents. Users of those frameworks aren't our audience.
- **LangSmith/Langfuse** — Observability tools. Different category entirely.
- **OpenAI Agents SDK** — Framework for developers. We target non-developers.

### Who We ARE Competing With

- **Custom GPTs (ChatGPT)** — Similar "non-technical agent" market, but locked to OpenAI's UI. We offer programmatic access.
- **Zapier AI** — Automation for non-technical users, but web-only and expensive.
- **Direct API usage** — Our agents are just prompt + loop, but the value is in the curation, testing, and tool integrations.

### Our Moat

1. **Tool integrations** — The agent code is simple. The tools (web search, scraping, file ops) with all their edge cases are 5,000+ lines of hardened code.
2. **Curated prompts** — Tested against hundreds of inputs, handling edge cases that naive prompting misses.
3. **One-line UX** — Import, call `.run()`, done. No framework to learn.
4. **OAuth support** — Use your existing Claude subscription. No billing setup.

---

## 6. What "Useful" Looks Like

### Target Users

1. **Vibe coders** — People who can write basic JS/TS but don't understand AI infrastructure. They want to add AI capabilities to their apps.
2. **Indie hackers / solo founders** — Building MVPs fast, need agent capabilities without building agent infrastructure.
3. **Non-technical PMs / analysts** — Want to automate research, data analysis, content generation via simple scripts.

### Use Cases That Drive Adoption

| Use Case | Agent | Why It Works |
|----------|-------|-------------|
| "Research my competitors" | CompetitorAnalyzer | Every startup needs this, nobody wants to do it manually |
| "Review my code before PR" | CodeReviewAgent | Junior devs and solo devs need a second pair of eyes |
| "Write my blog post" | ContentWriter | Content marketing is a universal need |
| "Analyze this CSV" | DataAnalyst | Data analysis without learning pandas or SQL |
| "Draft this email" | EmailDrafter | Professional communication assistance |
| "Audit my site's SEO" | SEOAuditor | Every website owner cares about SEO |
| "Triage these bug reports" | BugTriager | Dev teams drowning in issues |

---

## 7. Implementation Scope (This Build)

### Must-Have for v0.1

- [x] Base Agent class with agentic loop
- [x] 5 pre-built agents (Research, CodeReview, ContentWriter, DataAnalyst, CompetitorAnalyzer)
- [x] 4 tool implementations (web search, web scrape, file read, file list)
- [x] CLI (list, try, create, init)
- [ ] OAuth/Max plan authentication support
- [ ] 3 new agents (EmailDrafter, SEOAuditor, BugTriager)
- [ ] Streaming support
- [ ] Error handling (rate limits, spend caps, circuit breakers)
- [ ] Unit tests (Agent class, config, tools)
- [ ] Integration tests (agent execution flow)
- [ ] CI/CD (GitHub Actions)
- [ ] npm publish configuration
- [ ] Updated README with OAuth setup

### Nice-to-Have (Post v0.1)

- Dashboard web UI
- Agent marketplace
- Proxy service
- Session recording/replay
- Multi-model support (OpenAI, Gemini)

---

## 8. Success Metrics

| Metric | Target (3 months) |
|--------|-------------------|
| npm weekly downloads | 500+ |
| GitHub stars | 200+ |
| Pre-built agents | 15+ |
| Community-contributed agents | 5+ |
| Active users (proxy) | 50+ |

---

*Last updated: 2026-03-20*
