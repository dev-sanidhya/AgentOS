import chalk from "chalk";
import ora from "ora";
import inquirer from "inquirer";
import {
  ResearchAgent,
  CodeReviewAgent,
  ContentWriter,
  DataAnalyst,
  CompetitorAnalyzer,
  EmailDrafter,
  SEOAuditor,
  BugTriager,
  configure,
} from "@agentos/agents";

const AGENT_MAP: Record<string, { run: (input: string) => Promise<{ output: string; success: boolean; error?: string; toolCalls: { tool: string }[]; tokensUsed: { total: number }; cost: number; duration: number; loops: number }> }> = {
  researchagent: ResearchAgent,
  research: ResearchAgent,
  codereviewagent: CodeReviewAgent,
  codereview: CodeReviewAgent,
  contentwriter: ContentWriter,
  content: ContentWriter,
  dataanalyst: DataAnalyst,
  data: DataAnalyst,
  competitoranalyzer: CompetitorAnalyzer,
  competitor: CompetitorAnalyzer,
  emaildrafter: EmailDrafter,
  email: EmailDrafter,
  seoauditor: SEOAuditor,
  seo: SEOAuditor,
  bugtriager: BugTriager,
  bug: BugTriager,
};

export async function tryAgent(agentName?: string, input?: string): Promise<void> {
  // Resolve auth — support OAuth token, AGENTOS key, or ANTHROPIC key
  const oauthToken = process.env.CLAUDE_CODE_OAUTH_TOKEN;
  const apiKey = process.env.ANTHROPIC_API_KEY || process.env.AGENTOS_API_KEY;

  if (!oauthToken && !apiKey) {
    console.log();
    console.log(chalk.red("  No authentication found."));
    console.log();
    console.log(chalk.bold("  Option 1: Claude Max/Pro plan (recommended)"));
    console.log(chalk.gray("    Run:  claude setup-token"));
    console.log(chalk.gray("    Then: export CLAUDE_CODE_OAUTH_TOKEN=sk-ant-oat01-..."));
    console.log();
    console.log(chalk.bold("  Option 2: Anthropic API key"));
    console.log(chalk.gray("    export ANTHROPIC_API_KEY=sk-ant-..."));
    console.log();
    return;
  }

  if (oauthToken) {
    configure({ oauthToken });
  } else if (apiKey) {
    configure({ apiKey });
  }

  // Select agent
  if (!agentName) {
    const { selected } = await inquirer.prompt([
      {
        type: "list",
        name: "selected",
        message: "Which agent do you want to try?",
        choices: [
          { name: "Research Agent - Web research with structured reports", value: "research" },
          { name: "Code Review Agent - Security & quality analysis", value: "codereview" },
          { name: "Content Writer - Blog posts, docs, copy", value: "content" },
          { name: "Data Analyst - CSV/JSON analysis", value: "data" },
          { name: "Competitor Analyzer - Market analysis", value: "competitor" },
          { name: "Email Drafter - Professional email writing", value: "email" },
          { name: "SEO Auditor - Website SEO analysis", value: "seo" },
          { name: "Bug Triager - Bug report classification & diagnosis", value: "bug" },
        ],
      },
    ]);
    agentName = selected;
  }

  const agent = AGENT_MAP[agentName!.toLowerCase()];
  if (!agent) {
    console.log(chalk.red(`  Unknown agent: ${agentName}`));
    console.log(chalk.gray(`  Run ${chalk.white("agentos list")} to see available agents.`));
    return;
  }

  // Get input
  if (!input) {
    const { userInput } = await inquirer.prompt([
      {
        type: "input",
        name: "userInput",
        message: "What would you like the agent to do?",
      },
    ]);
    input = userInput;
  }

  if (!input || input.trim() === "") {
    console.log(chalk.red("  No input provided."));
    return;
  }

  // Run
  console.log();
  const spinner = ora({
    text: chalk.cyan("Agent is working..."),
    spinner: "dots",
  }).start();

  try {
    const result = await agent.run(input);
    spinner.stop();

    if (result.success) {
      console.log();
      console.log(result.output);
      console.log();
      console.log(chalk.gray("  ─────────────────────────────────────────────────────────"));
      console.log(
        chalk.gray(
          `  ${result.toolCalls.length} tool calls | ` +
          `${result.tokensUsed.total} tokens | ` +
          `$${result.cost.toFixed(4)} | ` +
          `${(result.duration / 1000).toFixed(1)}s | ` +
          `${result.loops} loops`
        )
      );
      console.log();
    } else {
      console.log();
      console.log(chalk.red(`  Error: ${result.error}`));
      console.log();
    }
  } catch (err) {
    spinner.stop();
    console.log();
    console.log(chalk.red(`  Error: ${err instanceof Error ? err.message : String(err)}`));
    console.log();
  }
}
