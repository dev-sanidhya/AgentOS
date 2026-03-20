import chalk from "chalk";

interface AgentInfo {
  name: string;
  importName: string;
  description: string;
  tools: string[];
}

const AGENTS: AgentInfo[] = [
  {
    name: "Research Agent",
    importName: "ResearchAgent",
    description: "Multi-source web research with structured reports and citations",
    tools: ["web_search", "web_scrape"],
  },
  {
    name: "Code Review Agent",
    importName: "CodeReviewAgent",
    description: "Security analysis, code quality scoring, and best practices review",
    tools: ["read_file", "list_files"],
  },
  {
    name: "Content Writer",
    importName: "ContentWriter",
    description: "Blog posts, docs, marketing copy, emails, and more",
    tools: ["web_search"],
  },
  {
    name: "Data Analyst",
    importName: "DataAnalyst",
    description: "CSV/JSON profiling, statistical summaries, and data quality analysis",
    tools: ["read_file", "list_files"],
  },
  {
    name: "Competitor Analyzer",
    importName: "CompetitorAnalyzer",
    description: "Market landscape analysis with feature comparison and positioning",
    tools: ["web_search", "web_scrape"],
  },
  {
    name: "Email Drafter",
    importName: "EmailDrafter",
    description: "Professional email drafting — cold outreach, follow-ups, internal comms",
    tools: [],
  },
  {
    name: "SEO Auditor",
    importName: "SEOAuditor",
    description: "Website SEO audit with actionable recommendations and scoring",
    tools: ["web_search", "web_scrape"],
  },
  {
    name: "Bug Triager",
    importName: "BugTriager",
    description: "Bug report triage — severity classification, root cause analysis, fix suggestions",
    tools: ["read_file", "list_files"],
  },
];

export function listAgents(): void {
  console.log();
  console.log(chalk.bold("  Available Agents"));
  console.log(chalk.gray("  ─────────────────────────────────────────────────────────"));
  console.log();

  for (const agent of AGENTS) {
    console.log(`  ${chalk.cyan.bold(agent.name)}`);
    console.log(`  ${chalk.gray(agent.description)}`);
    if (agent.tools.length > 0) {
      console.log(`  ${chalk.gray("Tools:")} ${agent.tools.map((t) => chalk.yellow(t)).join(", ")}`);
    } else {
      console.log(`  ${chalk.gray("Tools:")} ${chalk.gray("none (pure LLM)")}`);
    }
    console.log();
    console.log(
      `  ${chalk.gray("Import:")} ${chalk.white(`import { ${agent.importName} } from '@agentos/agents';`)}`
    );
    console.log(
      `  ${chalk.gray("Try:   ")} ${chalk.white(`npx agentos try ${agent.importName.toLowerCase()}`)}`
    );
    console.log();
    console.log(chalk.gray("  ─────────────────────────────────────────────────────────"));
    console.log();
  }

  console.log(
    `  ${chalk.gray("Or create your own:")} ${chalk.white("npx agentos create")}`
  );
  console.log();
}

export { AGENTS };
