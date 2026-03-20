import chalk from "chalk";
import ora from "ora";
import inquirer from "inquirer";
import { createAgent, configure } from "@agentos/agents";

export async function createAgentCommand(): Promise<void> {
  // Resolve auth
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

  console.log();
  console.log(chalk.bold("  Custom Agent Builder"));
  console.log(chalk.gray("  Describe what you want your agent to do and we'll build it for you."));
  console.log();

  const { mode } = await inquirer.prompt([
    {
      type: "list",
      name: "mode",
      message: "How would you like to describe your agent?",
      choices: [
        { name: "Free-text description", value: "text" },
        { name: "Guided questionnaire", value: "guided" },
      ],
    },
  ]);

  let description: string;

  if (mode === "text") {
    const { desc } = await inquirer.prompt([
      {
        type: "input",
        name: "desc",
        message: "Describe your agent:",
      },
    ]);
    description = desc;
  } else {
    const answers = await inquirer.prompt([
      {
        type: "input",
        name: "task",
        message: "What should this agent do?",
      },
      {
        type: "input",
        name: "inputs",
        message: "What inputs will it receive?",
      },
      {
        type: "input",
        name: "outputs",
        message: "What should the output look like?",
      },
      {
        type: "checkbox",
        name: "tools",
        message: "Which tools should it have access to?",
        choices: [
          { name: "Web Search - Search the internet", value: "web_search" },
          { name: "Web Scrape - Read web pages", value: "web_scrape" },
          { name: "File Reader - Read local files", value: "read_file" },
          { name: "File Lister - List directory contents", value: "list_files" },
        ],
      },
    ]);

    description = `Task: ${answers.task}\nInputs: ${answers.inputs}\nOutputs: ${answers.outputs}\nTools: ${answers.tools.join(", ")}`;
  }

  if (!description.trim()) {
    console.log(chalk.red("  No description provided."));
    return;
  }

  const spinner = ora({
    text: chalk.cyan("Building your agent..."),
    spinner: "dots",
  }).start();

  try {
    const agent = await createAgent(description);
    spinner.succeed(chalk.green("Agent created!"));

    console.log();
    console.log(chalk.gray("  Your agent is ready. Here's how to use it in code:"));
    console.log();
    console.log(chalk.white("    import { createAgent } from '@agentos/agents';"));
    console.log();
    console.log(chalk.white(`    const agent = await createAgent('${description.split("\n")[0]}');`));
    console.log(chalk.white("    const result = await agent.run('your input here');"));
    console.log();

    // Offer to try it
    const { tryIt } = await inquirer.prompt([
      {
        type: "confirm",
        name: "tryIt",
        message: "Want to try it now?",
        default: true,
      },
    ]);

    if (tryIt) {
      const { input } = await inquirer.prompt([
        {
          type: "input",
          name: "input",
          message: "Enter input for your agent:",
        },
      ]);

      if (input.trim()) {
        const runSpinner = ora({
          text: chalk.cyan("Agent is working..."),
          spinner: "dots",
        }).start();

        const result = await agent.run(input);
        runSpinner.stop();

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
              `${(result.duration / 1000).toFixed(1)}s`
            )
          );
          console.log();
        } else {
          console.log(chalk.red(`  Error: ${result.error}`));
        }
      }
    }
  } catch (err) {
    spinner.fail(chalk.red("Failed to create agent."));
    console.log(chalk.red(`  ${err instanceof Error ? err.message : String(err)}`));
  }
}
