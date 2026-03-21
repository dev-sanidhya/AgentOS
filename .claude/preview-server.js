const http = require("http");
const fs = require("fs");
const path = require("path");

const MOCK_AGENTS = {
  builtIn: [
    { id: "research", slug: "research", name: "Research Agent", summary: "Deep research on any topic using web search and synthesis.", kind: "built_in", category: "Research", allowedTools: ["web_search", "web_scrape"], tags: ["research", "synthesis", "web"] },
    { id: "prd-writer", slug: "prd-writer", name: "PRD Writer", summary: "Generates structured product requirement documents from a brief description.", kind: "built_in", category: "Product", allowedTools: [], tags: ["product", "docs", "planning"] },
    { id: "code-review", slug: "code-review", name: "Code Reviewer", summary: "Reviews code for bugs, style issues, and improvement opportunities.", kind: "built_in", category: "Engineering", allowedTools: ["file_reader"], tags: ["code", "review", "quality"] },
    { id: "email-drafter", slug: "email-drafter", name: "Email Drafter", summary: "Drafts professional emails from a brief and tone description.", kind: "built_in", category: "Operations", allowedTools: [], tags: ["email", "writing", "communication"] },
    { id: "competitor-analyzer", slug: "competitor-analyzer", name: "Competitor Analyzer", summary: "Analyzes competitors and surfaces positioning opportunities.", kind: "built_in", category: "Business", allowedTools: ["web_search", "web_scrape"], tags: ["competitive", "strategy"] },
    { id: "data-analyst", slug: "data-analyst", name: "Data Analyst", summary: "Interprets datasets and surfaces key trends and anomalies.", kind: "built_in", category: "Research", allowedTools: ["file_reader"], tags: ["data", "analysis", "insights"] },
    { id: "sales-prospector", slug: "sales-prospector", name: "Sales Prospector", summary: "Identifies and qualifies high-fit leads for outbound sales.", kind: "built_in", category: "Business", allowedTools: ["web_search"], tags: ["sales", "leads", "outbound"] },
    { id: "content-writer", slug: "content-writer", name: "Content Writer", summary: "Creates polished blog posts, landing pages, and marketing copy.", kind: "built_in", category: "Marketing", allowedTools: [], tags: ["content", "writing", "marketing"] },
    { id: "meeting-summarizer", slug: "meeting-summarizer", name: "Meeting Summarizer", summary: "Condenses meeting transcripts into actions, decisions, and owners.", kind: "built_in", category: "Operations", allowedTools: [], tags: ["meetings", "summaries", "async"] },
    { id: "financial-analyst", slug: "financial-analyst", name: "Financial Analyst", summary: "Analyzes financials and produces structured commentary.", kind: "built_in", category: "Finance", allowedTools: ["file_reader"], tags: ["finance", "analysis", "reporting"] },
  ],
  custom: [
    { id: "interview-summarizer", slug: "interview-summarizer", name: "Interview Summarizer", summary: "Condenses customer interview transcripts into themes and action items.", kind: "custom", category: "Product", allowedTools: [], tags: ["interviews", "synthesis", "custom"] },
    { id: "onboarding-writer", slug: "onboarding-writer", name: "Onboarding Email Writer", summary: "Writes personalized onboarding email sequences for new users.", kind: "custom", category: "Marketing", allowedTools: [], tags: ["email", "onboarding", "custom"] },
  ],
};

const MOCK_RUNS = {
  items: [
    { id: "run-1", agent: { name: "Research Agent" }, timestamp: new Date(Date.now() - 3600000).toISOString(), success: true, cost: 0.0142, tokensUsed: { total: 4820 }, duration: 12400, authMode: "api_key", loops: 3, input: "Compare the top AI agent frameworks for 2025", output: "Here is a comprehensive comparison of leading AI agent frameworks in 2025:\n\n1. axiom — local-first, prebuilt agents, great DX\n2. LangChain — mature, large ecosystem, but verbose\n3. CrewAI — multi-agent orchestration focus\n4. AutoGen — Microsoft-backed, strong for complex chains", toolCalls: [{ tool: "web_search", input: "top AI agent frameworks 2025" }, { tool: "web_scrape", input: "https://example.com/agent-frameworks" }] },
    { id: "run-2", agent: { name: "PRD Writer" }, timestamp: new Date(Date.now() - 86400000).toISOString(), success: true, cost: 0.0089, tokensUsed: { total: 2930 }, duration: 8200, authMode: "oauth_token", loops: 2, input: "Dashboard for local agent run history", output: "# Product Requirements Document\n\n## Overview\nA local dashboard that lets developers browse agent catalogs, inspect run history, and trigger runs without leaving their project.\n\n## Goals\n- Fast local load, no backend required\n- Clear cost and token visibility per run", toolCalls: [] },
    { id: "run-3", agent: { name: "Code Reviewer" }, timestamp: new Date(Date.now() - 172800000).toISOString(), success: false, cost: 0.0021, tokensUsed: { total: 710 }, duration: 3100, authMode: "api_key", loops: 1, input: "Review my auth module", output: "", error: "Rate limit exceeded. Please retry in a moment.", toolCalls: [] },
    { id: "run-4", agent: { name: "Email Drafter" }, timestamp: new Date(Date.now() - 259200000).toISOString(), success: true, cost: 0.0055, tokensUsed: { total: 1840 }, duration: 5600, authMode: "oauth_token", loops: 1, input: "Cold outreach to a Series A SaaS founder interested in AI tooling", output: "Subject: Shipping agent capabilities in one line of code\n\nHi [Name],\n\nI noticed you've been thinking about adding AI agent capabilities to [Company]...", toolCalls: [] },
  ],
};

const htmlPath = "/tmp/axiom-dashboard-preview.html";

const server = http.createServer((req, res) => {
  const url = new URL(req.url, "http://localhost");

  if (url.pathname === "/api/agents") {
    res.writeHead(200, { "Content-Type": "application/json" });
    return res.end(JSON.stringify(MOCK_AGENTS));
  }

  if (url.pathname === "/api/runs") {
    res.writeHead(200, { "Content-Type": "application/json" });
    return res.end(JSON.stringify(MOCK_RUNS));
  }

  if (url.pathname.startsWith("/api/runs/")) {
    const id = url.pathname.split("/").pop();
    const item = MOCK_RUNS.items.find((r) => r.id === id);
    res.writeHead(item ? 200 : 404, { "Content-Type": "application/json" });
    return res.end(JSON.stringify(item ? { item } : { error: "Not found" }));
  }

  // Serve the dashboard HTML for all other routes
  res.writeHead(200, { "Content-Type": "text/html; charset=utf-8" });
  res.end(fs.readFileSync(htmlPath));
});

const port = process.env.PORT || 4444;
server.listen(port, "127.0.0.1", () => console.log(`axiom preview ready on port ${port}`));
