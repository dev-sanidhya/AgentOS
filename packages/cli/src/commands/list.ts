import { Command, Flags } from '@oclif/core';
import chalk from 'chalk';
import path from 'path';
import { listAgents, isAgentProject } from '../utils/config-loader';
import { getAvailableTemplates } from '../utils/template-manager';
import { pathExists, readdir, stat } from '../utils/fs-utils';

export default class List extends Command {
  static description = 'List available runtime agents, templates, or installed copies';

  static examples = [
    '<%= config.bin %> <%= command.id %>',
    '<%= config.bin %> <%= command.id %> --mode=templates',
    '<%= config.bin %> <%= command.id %> --mode=installed',
  ];

  static flags = {
    mode: Flags.string({
      description: 'What to list',
      options: ['agents', 'templates', 'installed'],
      default: 'agents',
    }),
  };

  async run(): Promise<void> {
    const { flags } = await this.parse(List);

    if (flags.mode === 'templates') {
      await this.listTemplates();
      return;
    }

    const inProject = await isAgentProject();
    if (!inProject) {
      this.log(
        chalk.yellow('⚠ Not in an agent project. Run "agent init" to create one.')
      );
      return;
    }

    if (flags.mode === 'installed') {
      await this.listInstalledAgents();
      return;
    }

    await this.listRunnableAgents();
  }

  private async listRunnableAgents(): Promise<void> {
    const agents = await listAgents();

    if (agents.length === 0) {
      this.log(chalk.dim('No runnable agents found in agents/.'));
      this.log(chalk.dim('Create one with "agent init" or copy a template with "agent add".'));
      return;
    }

    this.log(chalk.bold.cyan(`\nRunnable Agents (${agents.length}):\n`));
    for (const agentName of agents) {
      this.log(`  ${chalk.green('●')} ${chalk.white(agentName)}`);
    }

    this.log(chalk.dim(`\nRun an agent with: ${chalk.cyan('agent run <name>')}`));
  }

  private async listTemplates(): Promise<void> {
    const templates = await getAvailableTemplates();

    if (templates.length === 0) {
      this.log(chalk.dim('No templates available.'));
      return;
    }

    this.log(chalk.bold.cyan(`\nAvailable Templates (${templates.length}):\n`));
    for (const template of templates) {
      const variants = Object.keys(template.variants).join(', ');
      this.log(`  ${chalk.green('●')} ${chalk.white(template.name)} ${chalk.dim(`(${variants})`)}`);
      this.log(chalk.dim(`    ${template.description}`));
    }

    this.log(chalk.dim(`\nCopy one into your project with: ${chalk.cyan('agent add <template>')}`));
  }

  private async listInstalledAgents(): Promise<void> {
    const agentsDir = path.join(process.cwd(), 'agents');
    if (!await pathExists(agentsDir)) {
      this.log(chalk.dim('No agents directory found.'));
      return;
    }

    const entries = await readdir(agentsDir);
    const installed: string[] = [];

    for (const entry of entries) {
      const entryPath = path.join(agentsDir, entry);
      const entryStat = await stat(entryPath);
      if (entryStat.isDirectory() && !entry.includes('.backup.')) {
        installed.push(`${entry}/`);
      }
    }

    const runnable = await listAgents();
    const combined = [...runnable, ...installed].sort((left, right) => left.localeCompare(right));

    if (combined.length === 0) {
      this.log(chalk.dim('No installed agents found.'));
      return;
    }

    this.log(chalk.bold.cyan(`\nInstalled Agents (${combined.length}):\n`));
    for (const item of combined) {
      const kind = item.endsWith('/') ? 'template copy' : 'runtime agent';
      this.log(`  ${chalk.green('●')} ${chalk.white(item)} ${chalk.dim(`(${kind})`)}`);
    }
  }
}
