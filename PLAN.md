# 🎯 Agent Library & Runtime Platform - Master Plan

## **Project Vision**

Build the **ultimate AI agent toolkit** that combines:

1. **Code Library** (like shadcn) - Copy production-ready agent code into your workspace
2. **Runtime & Dev Tools** - Run, test, and debug agents with beautiful tooling

**Core Philosophy:**

- 🎨 **Copy & Customize** - Get agent code you can modify (`agent add`)
- ⚡ **Run & Test** - Execute agents instantly (`agent run`)
- 🔧 **Framework Flexible** - Works standalone OR with LangChain/CrewAI
- 💎 **Production Ready** - High-quality templates with best practices
- 🌐 **Beautiful Tools** - Dev server with observability

**The Best of Both Worlds:**

1. Want to integrate with your existing system? → **Copy the code**
2. Want to prototype quickly? → **Run it directly**
3. Want to debug agent behavior? → **Use the dev server**

---

## 📋 **PHASE 0: Foundation & Setup** (Week 1) ✅

### Goals:

- Project architecture decision
- Core tech stack setup
- Initial project structure

### Deliverables:

```
✓ Monorepo structure with pnpm workspaces
✓ CLI package setup with oclif
✓ Core runtime package with types
✓ Templates package structure
✓ TypeScript configuration
```

### Tech Stack:

**CLI:**

- Language: TypeScript/Node.js
- Framework: oclif
- File operations: fs-extra, glob
- Templating: Handlebars for customization

**Runtime:**

- Agent execution engine
- Event system for observability
- Tool registration system
- Multi-provider support (OpenAI, Anthropic)

**Templates:**

- Multiple languages: Python, TypeScript, JavaScript
- Multiple frameworks: LangChain, CrewAI, Raw
- Standalone executable versions

**Dev Server:**

- Backend: Node.js + Fastify + WebSockets
- Frontend: Next.js + React + Tailwind
- Real-time execution viewer

**Showcase Website:**

- Next.js + React + Tailwind
- Syntax highlighting with Shiki
- Live code preview
- Framework selector

### File Structure:

```
agent-platform/
├── packages/
│   ├── cli/                    # CLI tool
│   ├── core/                   # Agent runtime
│   ├── templates/              # Agent templates
│   │   ├── research-agent/
│   │   │   ├── runtime/        # For 'agent run'
│   │   │   │   └── agent.ts
│   │   │   ├── templates/      # For 'agent add'
│   │   │   │   ├── langchain-python/
│   │   │   │   ├── langchain-typescript/
│   │   │   │   ├── crewai/
│   │   │   │   └── raw-python/
│   │   │   ├── manifest.json
│   │   │   └── README.md
│   │   └── code-review-agent/
│   ├── dev-server/             # Development server
│   └── ui/                     # Shared UI components
├── website/                    # Showcase website
└── docs/                       # Documentation
```

**Status:** ✅ Complete

---

## 📋 **PHASE 1: MVP - Dual-Mode CLI** (Week 2-4) 🚧

### Goals:

Create CLI that can both RUN agents AND COPY templates

### Core Commands:

#### **1. Template Commands (Copy Code)**

**`agent init [project-name]`** ✅ (needs enhancement)

- Creates new agent project
- Detects language preference (Python/TypeScript)
- Sets up configuration
- Includes example agents

**`agent add <template-name>`** ❌ (needs building)

```bash
# Interactive mode
agent add research-agent
? Choose framework: (LangChain Python, LangChain TypeScript, CrewAI, Raw Python)
? Where to add files: ./agents/research

# Non-interactive
agent add research-agent --framework=langchain --lang=python --path=./agents

# What happens:
✓ Detecting project type: Python
✓ Copying template files to ./agents/research/

  Added files:
  ✓ agents/research/research_agent.py
  ✓ agents/research/tools/web_search.py
  ✓ agents/research/tools/web_scrape.py
  ✓ agents/research/prompts.py
  ✓ agents/research/example_usage.py
  ✓ agents/research/README.md

  Dependencies to install:
  - langchain>=0.1.0
  - requests>=2.31.0
  - beautifulsoup4>=4.12.0

  Run: pip install -r agents/research/requirements.txt

  Quick start:
  python agents/research/example_usage.py
```

**`agent list [--mode=templates|installed]`** ✅ (needs enhancement)

- Lists available templates for `add`
- Lists installed agents (copied to workspace)
- Shows agent compatibility and requirements

**`agent diff <template-name>`** ❌ (new)

- Preview files before adding
- Show what will be created/modified

**`agent remove <agent-name>`** ❌ (new)

- Remove agent files from workspace
- Interactive confirmation

**`agent update <agent-name>`** ❌ (new)

- Update agent to latest version
- Show diff of changes
- Preserve user modifications

#### **2. Runtime Commands (Execute Agents)**

**`agent run <agent-name>`** ✅ (already built)

```bash
# Run agent from workspace
agent run research-agent --input "AI trends 2026"

# Run with verbose logging
agent run research-agent -i "query" --verbose

# Run with JSON output
agent run research-agent -i "query" --json
```

**`agent dev`** ❌ (Phase 2)

```bash
# Starts development server
agent dev

# Features:
# - Real-time execution viewer
# - Tool call inspector
# - Token usage tracking
# - Execution history
```

**`agent test [agent-name]`** ❌ (Phase 3)

```bash
# Run agent tests
agent test research-agent
```

### Template Structure:

Each agent has **TWO versions**:

```
research-agent/
├── manifest.json              # Metadata for discovery
├── README.md                  # Agent documentation
│
├── runtime/                   # For 'agent run' (immediate execution)
│   ├── agent.ts              # Runtime-ready TypeScript
│   ├── tools.ts
│   └── prompts.ts
│
├── templates/                 # For 'agent add' (copy to workspace)
│   ├── langchain-python/      # LangChain Python version
│   │   ├── {{agent_name}}.py
│   │   ├── tools/
│   │   │   ├── web_search.py
│   │   │   └── web_scrape.py
│   │   ├── prompts.py
│   │   ├── requirements.txt
│   │   ├── example_usage.py
│   │   └── README.md
│   │
│   ├── langchain-typescript/  # LangChain TypeScript version
│   │   ├── {{agentName}}.ts
│   │   ├── tools/
│   │   ├── prompts.ts
│   │   ├── package.json
│   │   ├── example.ts
│   │   └── README.md
│   │
│   ├── crewai/                # CrewAI version
│   │   ├── {{agent_name}}_agent.py
│   │   ├── tools.py
│   │   ├── crew_config.yaml
│   │   └── README.md
│   │
│   └── raw-python/            # Framework-agnostic Python
│       ├── {{agent_name}}.py
│       ├── requirements.txt
│       ├── example.py
│       └── README.md
│
└── examples/
    ├── use-case-1.md
    └── use-case-2.md
```

### manifest.json Format:

```json
{
  "name": "research-agent",
  "version": "1.0.0",
  "description": "AI-powered research agent with web search and content analysis",
  "author": "Agent Platform",
  "license": "MIT",
  "tags": ["research", "web-search", "analysis", "scraping"],

  "capabilities": {
    "tools": ["web-search", "web-scrape", "http-request"],
    "useCases": ["market-research", "competitor-analysis", "fact-checking"]
  },

  "runtime": {
    "entry": "runtime/agent.ts",
    "executable": true
  },

  "templates": {
    "frameworks": ["langchain", "crewai", "raw"],
    "languages": ["python", "typescript"],

    "variants": {
      "langchain-python": {
        "path": "templates/langchain-python",
        "language": "python",
        "framework": "langchain",
        "dependencies": {
          "python": ">=3.9",
          "packages": ["langchain>=0.1.0", "requests", "beautifulsoup4"]
        },
        "files": {
          "agent": "{{agent_name}}.py",
          "tools": "tools/",
          "example": "example_usage.py"
        }
      },

      "langchain-typescript": {
        "path": "templates/langchain-typescript",
        "language": "typescript",
        "framework": "langchain",
        "dependencies": {
          "node": ">=18",
          "packages": {
            "langchain": "^0.1.0",
            "axios": "^1.6.0",
            "cheerio": "^1.0.0"
          }
        }
      }
    }
  },

  "examples": [
    {
      "title": "Market Research",
      "description": "Research competitors in a specific market",
      "input": "Research top 5 AI coding assistants",
      "expectedOutput": "Comprehensive research report with sources"
    },
    {
      "title": "Fact Checking",
      "description": "Verify claims with web sources",
      "input": "Verify: 'Python is the most popular programming language'",
      "expectedOutput": "Analysis with supporting evidence"
    }
  ]
}
```

### Agent Templates to Build:

**1. Research Agent** 🔍

- Runtime version for `agent run`
- Templates for: LangChain (Py/TS), CrewAI, Raw
- Tools: web search, scraping, summarization
- Status: ✅ Runtime built, ❌ Templates needed

**2. Code Review Agent** 🔧

- Runtime version for `agent run`
- Templates for: LangChain (Py/TS), Raw
- Tools: file reading, static analysis
- Status: ✅ Runtime built, ❌ Templates needed

**3. Data Analysis Agent** 📊

- Runtime version for `agent run`
- Templates for: LangChain (Py), Raw
- Tools: CSV/JSON parsing, pandas, plotting
- Status: ❌ Not started

### Deliverables:

- ✅ CLI with `init`, `run`, `list` commands
- 🚧 Add `agent add` command with template copying
- ❌ Add `agent diff`, `agent remove`, `agent update`
- ✅ Runtime execution engine
- ✅ 2 runtime agents (research, code-review)
- ❌ Multi-framework templates for each agent
- ❌ Template variable substitution
- ❌ Dependency installation helpers

**Current Status:** 40% Complete

---

## 📋 **PHASE 2: Dev Server with Observability** (Week 5-6)

### Goals:

Local development server for running and debugging agents

### Features:

**1. Launch Dev Server:**

```bash
agent dev
# Starts on localhost:3000
# Opens browser with agent dashboard
```

**2. Dashboard Features:**

- **Agent Library** - All available agents (runtime + workspace)
- **Execution Playground** - Run agents with inputs
- **Live Execution Viewer** - Real-time step-by-step view
- **Tool Call Inspector** - See every tool call with I/O
- **Token Usage Tracker** - Cost per run
- **Execution History** - Past runs with replay
- **Agent Editor** - Edit agent code inline (optional)

**3. Real-time Execution View:**

```
┌─────────────────────────────────────────────┐
│ Research Agent - RUNNING                    │
├─────────────────────────────────────────────┤
│ Input: "Latest AI agent frameworks 2026"    │
│                                             │
│ Step 1: Planning                            │
│ ✓ Analyzing query...                        │
│ ✓ Generated 3 search queries                │
│                                             │
│ Step 2: Web Search [Tool Call]              │
│ → web_search("AI agent frameworks 2026")    │
│ ← Found 10 results (250ms)                  │
│                                             │
│ Step 3: Content Extraction                  │
│ → web_scrape("https://...")                 │
│ ← Extracted 5000 chars (1.2s)               │
│                                             │
│ Step 4: Analysis                            │
│ • Processing articles...                    │
│ • Extracting key insights...                │
│ • Generating report...                      │
│                                             │
│ Status: ✓ Complete                          │
│ Tokens: 1,234 | Cost: $0.02 | Time: 8.5s   │
└─────────────────────────────────────────────┘
```

**4. Tool Call Inspector:**

```typescript
{
  toolName: "web_search",
  timestamp: "2026-03-19T10:30:45",
  input: {
    query: "AI agent frameworks 2026",
    maxResults: 10
  },
  output: {
    results: [
      { title: "...", url: "...", snippet: "..." }
    ],
    totalResults: 10
  },
  duration: 250,
  success: true
}
```

### Technical Architecture:

**Backend:**

```typescript
dev-server/
├── server.ts              # Fastify + WebSocket server
├── agent-runner.ts        # Execute agents with event hooks
├── storage.ts             # SQLite for history
└── api/
    ├── agents.ts          # List/run agents
    ├── executions.ts      # Execution history
    ├── templates.ts       # Available templates
    └── workspace.ts       # User's workspace agents
```

**Frontend:**

```typescript
ui/
├── app/
│   ├── page.tsx                  # Dashboard
│   ├── playground/page.tsx       # Run agents
│   ├── history/page.tsx          # Execution history
│   └── execution/[id]/page.tsx   # Execution detail
├── components/
│   ├── AgentList.tsx
│   ├── ExecutionViewer.tsx
│   ├── ToolCallInspector.tsx
│   ├── TokenTracker.tsx
│   └── CodeEditor.tsx            # Monaco editor
└── hooks/
    └── useAgentExecution.ts      # WebSocket connection
```

**WebSocket Events:**

```typescript
ws.on('agent:start')
ws.on('agent:thinking')
ws.on('agent:tool_call')
ws.on('agent:tool_result')
ws.on('agent:step_complete')
ws.on('agent:response')
ws.on('agent:complete')
ws.on('agent:error')
```

### Deliverables:

- ❌ Dev server with WebSocket support
- ❌ Real-time execution viewer UI
- ❌ Tool call inspector
- ❌ Execution history with SQLite
- ❌ Token/cost tracking
- ❌ Beautiful Tailwind dashboard
- ❌ Agent playground interface

**Status:** 0% Complete

---

## 📋 **PHASE 3: Showcase Website** (Week 7-9)

### Goals:

Beautiful website to showcase agents and templates

### Features:

**Homepage:**

- Hero: "Copy agent code OR run them instantly"
- Dual showcase: Template library + Runtime platform
- Live code preview
- Quick start for both modes
- GitHub stars, downloads counter

**Agent Gallery:**

```
/agents

Grid of agent cards showing:
- Visual icon
- Name & description
- Tags (research, code, data)
- Framework badges
- "Add to Project" button
- "Try in Playground" button
```

**Agent Detail Page:**

```
/agents/research-agent

Tabs:
1. Overview
   - Description
   - Use cases
   - Demo video/gif

2. Add to Project (Code Library)
   - Framework selector (LangChain/CrewAI/Raw)
   - Language selector (Python/TypeScript)
   - Code preview with syntax highlighting
   - Copy button
   - Installation instructions

3. Try It (Runtime)
   - Input field
   - Run button
   - Live results
   - "Install CLI to run locally"

4. Documentation
   - API reference
   - Configuration options
   - Tool descriptions
   - Examples

5. Community
   - Ratings & reviews
   - Download stats
   - Related agents
```

**Interactive Code Preview:**

```tsx
<FrameworkSelector>
  <Tab value="langchain-python">
    <CodeBlock language="python">
      {researchAgentLangChainPython}
    </CodeBlock>
  </Tab>

  <Tab value="crewai">
    <CodeBlock language="python">
      {researchAgentCrewAI}
    </CodeBlock>
  </Tab>
</FrameworkSelector>

<CopyButton text={code} />
<DownloadButton filename="research_agent.py" content={code} />
```

**Live Playground:**

- Try agents in browser (integrates with dev server)
- Fork and modify code
- Share custom configurations

### Technical Stack:

- Next.js 14 with App Router
- Tailwind CSS + Framer Motion
- Shiki for syntax highlighting
- React Flow for visualizations
- RunKit for live code (optional)

### Deliverables:

- ❌ Beautiful homepage
- ❌ Agent gallery with filters
- ❌ Agent detail pages
- ❌ Interactive code preview
- ❌ Framework/language selector
- ❌ Copy-to-clipboard
- ❌ Live playground integration
- ❌ Documentation pages
- ❌ Mobile responsive design

**Status:** 0% Complete

---

## 📋 **PHASE 4: Agent Testing Framework** (Week 10-11)

### Goals:

Make agents testable and reliable

### Features:

**1. Test Command:**

```bash
agent test                    # Run all tests
agent test research-agent     # Test specific agent
agent test --watch           # Watch mode
```

**2. Test Templates:**
When you run `agent add research-agent`, also get test files:

```
agents/research/
├── research_agent.py
├── tools/
├── __tests__/
│   ├── test_research_agent.py
│   ├── test_tools.py
│   └── fixtures/
│       └── mock_search_results.json
└── README.md
```

**3. Test Syntax:**

```python
# __tests__/test_research_agent.py
from agent_platform.testing import test_agent, mock_tool, expect

@test_agent("research_agent")
def test_web_search_integration():
    result = run_agent(
        "research_agent",
        input="AI trends 2026",
        mocks={
            "web_search": mock_tool(
                return_value=load_fixture("mock_search_results.json")
            )
        }
    )

    expect(result.used_tools).to_contain("web_search")
    expect(result.status).to_equal("success")
    expect(result.output).to_contain("AI")
    expect(result.token_count).to_be_less_than(5000)
```

**4. Evaluation Framework:**

```python
from agent_platform.testing import evaluate

dataset = [
    {"input": "Research X", "expected_tools": ["web_search"]},
    {"input": "Research Y", "expected_tools": ["web_search", "web_scrape"]}
]

results = evaluate("research_agent", dataset)
print(f"Pass rate: {results.pass_rate}%")
```

### Deliverables:

- ❌ Testing framework package
- ❌ `agent test` command
- ❌ Mock system for tools
- ❌ Assertion library
- ❌ Test templates included with agents
- ❌ Dataset evaluation
- ❌ CI/CD examples

**Status:** 0% Complete

---

## 📋 **PHASE 5: Community & Marketplace** (Week 12-14)

### Goals:

Enable community contributions and discovery

### Features:

**1. Publishing:**

```bash
agent login
agent publish ./my-custom-agent
```

**2. Discovery:**

```bash
agent search "customer support"
agent info @username/support-agent
agent add @username/support-agent
```

**3. Marketplace Website:**

- Browse community agents
- User profiles
- Ratings & reviews
- Download stats
- Featured agents

### Deliverables:

- ❌ Publishing system
- ❌ Marketplace API
- ❌ Community discovery
- ❌ Quality validation
- ❌ Versioning system

**Status:** 0% Complete

---

## 📋 **PHASE 6: Visual Agent Builder** (Week 15-17)

### Goals:

Visual tool to design agents, export code or run directly

### Features:

```bash
agent builder
# Opens visual designer
```

- Drag-and-drop flow designer
- Export to LangChain/CrewAI/Raw
- OR save as runtime agent
- Share flows as JSON

### Deliverables:

- ❌ Visual flow designer
- ❌ Code generation
- ❌ Runtime export
- ❌ Flow sharing

**Status:** 0% Complete

---

## 📋 **PHASE 7: Advanced Features** (Week 18-20)

### Features:

- Multi-agent system templates
- Integration templates (Slack, Discord, API)
- Custom tool marketplace
- Agent deployment helpers
- Managed cloud service

**Status:** 0% Complete

---

## 🎯 **Success Metrics**

### MVP Success (Phase 1-2):

- [ ] 500 CLI installations
- [ ] 100 templates copied via `agent add`
- [ ] 50 agents run via `agent run`
- [ ] 5 community agents

### Growth Success (Phase 3-5):

- [ ] 5,000 active developers
- [ ] 100+ community agents
- [ ] 50,000+ template installs
- [ ] Featured on HackerNews

### Long-term Success:

- [ ] 50,000+ developers
- [ ] 1,000+ community agents
- [ ] "shadcn for agents" reputation

---

## 💻 **Tech Stack Summary**

| Component      | Technology                      |
| -------------- | ------------------------------- |
| CLI            | TypeScript + oclif + fs-extra   |
| Runtime        | TypeScript + Event System       |
| Templates      | Multi-language (Python, TS, JS) |
| Dev Server     | Fastify + WebSockets + SQLite   |
| Dashboard      | Next.js + React + Tailwind      |
| Website        | Next.js + Tailwind + Shiki      |
| Visual Builder | React Flow + Monaco             |
| Marketplace    | Next.js + Postgres + S3         |

---

## 📅 **Timeline Overview**

- **Phase 0:** ✅ 1 week - Foundation (Complete)
- **Phase 1:** 🚧 3 weeks - Dual-mode CLI (40% complete)
- **Phase 2:** ❌ 2 weeks - Dev Server
- **Phase 3:** ❌ 3 weeks - Showcase Website
- **Phase 4:** ❌ 2 weeks - Testing
- **Phase 5:** ❌ 3 weeks - Community
- **Phase 6:** ❌ 3 weeks - Visual Builder
- **Phase 7:** ❌ 3 weeks - Advanced
- **Total:** ~20 weeks (5 months)

---

## 📊 **Current Progress Summary**

### ✅ **Completed (Phase 0 + Partial Phase 1)**

**Phase 0: Foundation - 100%**

- ✅ Monorepo structure with pnpm/turbo
- ✅ CLI package with oclif
- ✅ Core runtime package
- ✅ Type system and interfaces
- ✅ Templates package structure

**Phase 1: Dual-Mode CLI - 40%**

**Runtime Mode (Execute Agents):**

- ✅ `agent init` - Create projects
- ✅ `agent run` - Execute agents
- ✅ `agent list` - List agents
- ✅ AgentRuntime execution engine
- ✅ Event system for observability
- ✅ Tool registration system
- ✅ 2 runtime agents:
  - ✅ Research Agent (web search, scraping)
  - ✅ Code Review Agent (file analysis, security)
- ✅ Built-in tools:
  - ✅ Web tools (search, scrape, HTTP)
  - ✅ File tools (read, write, list, stats)

**Template Mode (Copy Code):**

- ❌ `agent add` command
- ❌ Template copying system
- ❌ Framework detection
- ❌ Multi-framework templates
- ❌ Variable substitution
- ❌ Dependency helpers

### ❌ **Not Started**

- Phase 2: Dev Server (0%)
- Phase 3: Showcase Website (0%)
- Phase 4: Testing Framework (0%)
- Phase 5: Community/Marketplace (0%)
- Phase 6: Visual Builder (0%)
- Phase 7: Advanced Features (0%)

---

## 🚀 **Immediate Next Steps**

**To Complete Phase 1:**

1. Build `agent add` command
2. Create multi-framework templates for:
   - Research Agent (LangChain Py/TS, CrewAI, Raw)
   - Code Review Agent (LangChain Py/TS, Raw)
3. Implement template variable substitution
4. Add framework/language detection
5. Build `agent diff` and `agent update`

**Then Move to Phase 2:**

- Build dev server
- Real-time execution viewer
- Beautiful dashboard

---

## 🔑 **Key Differentiators**

1. **Dual Mode** - Copy code OR run instantly
2. **Framework Flexible** - Works with any AI framework
3. **High Quality** - Production-ready templates
4. **Developer Tools** - Observability and debugging
5. **Beautiful UX** - Great CLI and web experiences
6. **Community Driven** - Easy contributions

---

## 📝 **Notes**

- **Both Runtime AND Library** - Best of both worlds
- **Users Choose** - Copy code for full control, run for speed
- **Quality First** - Better to have 10 great agents than 100 mediocre
- **Framework Neutral** - Don't force users into our ecosystem
- **Community First** - Make contributions easy
