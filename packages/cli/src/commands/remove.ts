import { Command, Args, Flags } from '@oclif/core';
import chalk from 'chalk';
import * as path from 'path';
import * as inquirer from 'inquirer';
import { isAgentProject, listAgents } from '../utils/config-loader';
import {
  pathExists,
  readdir,
  removePath,
  stat,
} from '../utils/fs-utils';

export default class Remove extends Command {
  static description = 'Remove an agent from your project';

  static examples = [
    '<%= config.bin %> <%= command.id %> research-agent',
    '<%= config.bin %> <%= command.id %> research-agent --force',
  ];

  static args = {
    agent: Args.string({
      description: 'Agent name to remove',
      required: true,
    }),
  };

  static flags = {
    force: Flags.boolean({
      description: 'Skip confirmation prompts',
      default: false,
    }),
    'agents-dir': Flags.string({
      description: 'Agents directory path',
      default: './agents',
    }),
  };

  async run(): Promise<void> {
    const { args, flags } = await this.parse(Remove);

    try {
      // Check if we're in an agent project
      if (!await isAgentProject()) {
        this.log(chalk.yellow('⚠ Not in an agent project. Run "agent init" to create one.'));
        return;
      }

      const agentName = args.agent;
      const agentsDir = path.resolve(flags['agents-dir']);
      const agentPath = path.join(agentsDir, agentName);

      // Check if agent exists
      if (!await pathExists(agentPath)) {
        this.log(chalk.red(`❌ Agent "${agentName}" not found in ${agentsDir}`));

        const availableAgents = await listAgents();
        if (availableAgents.length > 0) {
          this.log(chalk.dim('\nAvailable agents:'));
          availableAgents.forEach(agent => {
            this.log(chalk.dim(`  - ${agent}`));
          });
        }
        return;
      }

      this.log(chalk.bold.yellow(`\n🗑️  Removing agent: ${agentName}\n`));

      // Show what will be removed
      const files = await this.getFilesToRemove(agentPath);
      this.log(chalk.red('📄 Files to be removed:'));
      files.forEach(file => {
        const relativePath = path.relative(process.cwd(), file);
        this.log(chalk.red(`  - ${relativePath}`));
      });

      // Confirmation
      if (!flags.force) {
        const { confirmed } = await inquirer.prompt([{
          type: 'confirm',
          name: 'confirmed',
          message: `Are you sure you want to remove the "${agentName}" agent?`,
          default: false,
        }]);

        if (!confirmed) {
          this.log(chalk.yellow('Operation cancelled.'));
          return;
        }

        // Double confirmation for safety
        const { doubleConfirmed } = await inquirer.prompt([{
          type: 'confirm',
          name: 'doubleConfirmed',
          message: 'This action cannot be undone. Are you absolutely sure?',
          default: false,
        }]);

        if (!doubleConfirmed) {
          this.log(chalk.yellow('Operation cancelled.'));
          return;
        }
      }

      // Remove the agent directory
      this.log(chalk.blue('\n🗑️  Removing files...'));
      await removePath(agentPath);

      this.log(chalk.green(`\n✅ Successfully removed agent "${agentName}"`));

      // Show remaining agents
      const remainingAgents = await listAgents();
      if (remainingAgents.length > 0) {
        this.log(chalk.dim(`\nRemaining agents (${remainingAgents.length}):`));
        remainingAgents.forEach(agent => {
          this.log(chalk.dim(`  - ${agent}`));
        });
      } else {
        this.log(chalk.dim('\nNo agents remaining. Use "agent add <template>" to add one.'));
      }

    } catch (error) {
      this.log(chalk.red(`❌ Failed to remove agent: ${error}`));
      if (process.env.DEBUG) {
        console.error(error);
      }
    }
  }

  private async getFilesToRemove(agentPath: string): Promise<string[]> {
    const files: string[] = [];

    const addFiles = async (dirPath: string) => {
      const items = await readdir(dirPath);

      for (const item of items) {
        const itemPath = path.join(dirPath, item);
        const itemStat = await stat(itemPath);

        if (itemStat.isDirectory()) {
          await addFiles(itemPath);
        } else {
          files.push(itemPath);
        }
      }
    };

    try {
      await addFiles(agentPath);
    } catch (error) {
      // Directory might not exist or be readable
    }

    return files;
  }
}
