import { Command } from "commander";
import chalk from "chalk";
import { listAgents } from "./commands/list";
import { tryAgent } from "./commands/try-agent";
import { createAgentCommand } from "./commands/create";
import { initProject } from "./commands/init";

const program = new Command();

program
  .name("agentos")
  .description("Pre-built AI agents you can import and use in one line")
  .version("0.1.0");

program
  .command("list")
  .description("List all available pre-built agents")
  .action(() => {
    listAgents();
  });

program
  .command("try [agent] [input]")
  .description("Try an agent interactively")
  .option("-i, --input <input>", "Input for the agent")
  .action(async (agent?: string, inputArg?: string, options?: { input?: string }) => {
    const input = options?.input ?? inputArg;
    await tryAgent(agent, input);
  });

program
  .command("create")
  .description("Create a custom agent from a description")
  .action(async () => {
    await createAgentCommand();
  });

program
  .command("init [name]")
  .description("Initialize a new AgentOS project")
  .action(async (name?: string) => {
    await initProject(name);
  });

// Default: show help with branding
if (process.argv.length <= 2) {
  console.log();
  console.log(chalk.bold.cyan("  AgentOS") + chalk.gray(" - Pre-built AI agents, one import away"));
  console.log();
  program.outputHelp();
  console.log();
} else {
  program.parse();
}
