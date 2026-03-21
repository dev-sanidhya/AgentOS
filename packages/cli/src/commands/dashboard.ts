import path from "path";
import chalk from "chalk";
import { configure } from "@axiomcm/agents";
import { startDashboardServer } from "@axiomcm/dashboard";

export async function openDashboard(port = 3210): Promise<void> {
  const oauthToken = process.env.CLAUDE_CODE_OAUTH_TOKEN;
  const apiKey = process.env.ANTHROPIC_API_KEY ?? process.env.AXIOM_API_KEY;

  configure({
    storageDir: path.join(process.cwd(), ".axiom"),
    projectName: path.basename(process.cwd()),
    persistRuns: true,
    ...(oauthToken ? { oauthToken } : {}),
    ...(!oauthToken && apiKey ? { apiKey } : {}),
  });

  if (!oauthToken && !apiKey) {
    console.log();
    console.log(chalk.yellow("  No auth found — catalog and run history available, but running agents will fail."));
    console.log(chalk.gray("  Set CLAUDE_CODE_OAUTH_TOKEN or ANTHROPIC_API_KEY to enable agent runs."));
    console.log();
  }

  const handle = await startDashboardServer({ projectDir: process.cwd(), port, open: true });
  console.log();
  console.log(chalk.green(`  axiom dashboard → ${handle.url}`));
  console.log(chalk.gray("  Ctrl+C to stop"));
  console.log();
}
