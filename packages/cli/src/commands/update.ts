import { Command, Args, Flags } from '@oclif/core';
import chalk from 'chalk';
import * as path from 'path';
import * as inquirer from 'inquirer';
import { isAgentProject, listAgents } from '../utils/config-loader';
import {
  getAvailableTemplates,
  copyTemplate,
  type FrameworkType,
  type LanguageType,
} from '../utils/template-manager';
import {
  copyPath,
  pathExists,
  readFile,
  readdir,
} from '../utils/fs-utils';

export default class Update extends Command {
  static description = 'Update an agent to the latest template version';

  static examples = [
    '<%= config.bin %> <%= command.id %> research-agent',
    '<%= config.bin %> <%= command.id %> research-agent --backup',
  ];

  static args = {
    agent: Args.string({
      description: 'Agent name to update',
      required: true,
    }),
  };

  static flags = {
    backup: Flags.boolean({
      description: 'Create backup before updating',
      default: true,
    }),
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
    const { args, flags } = await this.parse(Update);

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

      this.log(chalk.bold.cyan(`\n🔄 Updating agent: ${agentName}\n`));

      // Try to detect what template this agent was created from
      const templateName = await this.detectAgentTemplate(agentPath);

      if (!templateName) {
        this.log(chalk.red('❌ Could not detect agent template. Manual update required.'));
        this.log(chalk.dim('This agent may have been heavily customized or created manually.'));
        return;
      }

      // Get the template
      const availableTemplates = await getAvailableTemplates();
      const template = availableTemplates.find(t => t.name === templateName);

      if (!template) {
        this.log(chalk.red(`❌ Template "${templateName}" no longer available`));
        return;
      }

      // Detect framework and language
      const { framework, language } = await this.detectAgentVariant(agentPath);

      const variant = Object.values(template.variants).find(v =>
        v.framework === framework && v.language === language
      );

      if (!variant) {
        this.log(chalk.red(`❌ No ${language} + ${framework} variant available`));
        return;
      }

      this.log(chalk.blue('📋 Update Configuration:'));
      this.log(`  Agent:     ${chalk.white(agentName)}`);
      this.log(`  Template:  ${chalk.white(templateName)}`);
      this.log(`  Language:  ${chalk.white(language)}`);
      this.log(`  Framework: ${chalk.white(framework)}`);

      // Warning about customizations
      this.log(chalk.yellow('\n⚠️  Warning: This will overwrite template files!'));
      this.log(chalk.dim('Your customizations will be lost unless you have backups.'));

      // Confirmation
      if (!flags.force) {
        const { confirmed } = await inquirer.prompt([{
          type: 'confirm',
          name: 'confirmed',
          message: 'Continue with the update?',
          default: false,
        }]);

        if (!confirmed) {
          this.log(chalk.yellow('Update cancelled.'));
          return;
        }
      }

      // Create backup if requested
      let backupPath: string | null = null;
      if (flags.backup) {
        backupPath = await this.createBackup(agentPath, agentName);
        if (backupPath) {
          this.log(chalk.green(`📦 Backup created: ${path.relative(process.cwd(), backupPath)}`));
        }
      }

      // Update the agent
      this.log(chalk.blue('\n🔄 Updating agent files...'));

      const context = {
        targetPath: agentPath,
        agentName,
        templateName,
        framework,
        language,
        author: await this.getAuthorName(),
        description: template.description,
      };

      const updatedFiles = await copyTemplate(template, variant, context);

      this.log(chalk.green(`\n✅ Successfully updated ${agentName}!`));

      // Show what was updated
      this.log(chalk.bold('\n📄 Updated files:'));
      updatedFiles.forEach(file => {
        this.log(chalk.green(`  ✓ ${path.relative(process.cwd(), file)}`));
      });

      if (backupPath) {
        this.log(chalk.dim(`\n💾 Backup available at: ${path.relative(process.cwd(), backupPath)}`));
        this.log(chalk.dim('Delete the backup when you\'re confident the update is working correctly.'));
      }

      // Show next steps
      this.log(chalk.bold.green('\n🚀 Next Steps:'));
      this.log(chalk.cyan('1. Review changes and test the updated agent'));
      this.log(chalk.cyan('2. Update your API keys if needed in .env'));
      this.log(chalk.cyan(`3. Open agents\\${agentName}\\README.md for usage examples`));

    } catch (error) {
      this.log(chalk.red(`❌ Failed to update agent: ${error}`));
      if (process.env.DEBUG) {
        console.error(error);
      }
    }
  }

  private async detectAgentTemplate(agentPath: string): Promise<string | null> {
    // Look for template indicators in files
    const indicators = [
      { file: 'README.md', patterns: ['research-agent', 'code-review-agent'] },
      { file: 'package.json', patterns: ['"name":', 'research', 'code-review'] },
      { file: 'requirements.txt', patterns: ['langchain', 'crewai'] },
    ];

    for (const indicator of indicators) {
      const filePath = path.join(agentPath, indicator.file);

      if (await pathExists(filePath)) {
        try {
          const content = await readFile(filePath, 'utf-8');

          for (const pattern of indicator.patterns) {
            if (content.toLowerCase().includes(pattern)) {
              if (pattern.includes('research')) return 'research-agent';
              if (pattern.includes('code-review')) return 'code-review-agent';
            }
          }
        } catch {
          // Ignore file read errors
        }
      }
    }

    // Try to guess from directory contents
    const files = await readdir(agentPath);

    if (files.some(f => f.includes('research'))) return 'research-agent';
    if (files.some(f => f.includes('review'))) return 'code-review-agent';

    return null;
  }

  private async detectAgentVariant(
    agentPath: string
  ): Promise<{ framework: FrameworkType; language: LanguageType }> {
    const packageJsonPath = path.join(agentPath, 'package.json');
    const requirementsPath = path.join(agentPath, 'requirements.txt');
    const readmePath = path.join(agentPath, 'README.md');
    const fileNames = await readdir(agentPath);

    let language: LanguageType = 'python';
    let framework: FrameworkType = 'raw';

    if (await pathExists(packageJsonPath)) {
      language = 'typescript';
      const packageJson = await readFile(packageJsonPath, 'utf-8');
      const normalized = packageJson.toLowerCase();
      if (normalized.includes('langchain')) {
        framework = 'langchain';
      }
    }

    if (await pathExists(requirementsPath)) {
      language = 'python';
      const requirements = (await readFile(requirementsPath, 'utf-8')).toLowerCase();
      if (requirements.includes('crewai')) {
        framework = 'crewai';
      } else if (requirements.includes('langchain')) {
        framework = 'langchain';
      }
    }

    if (await pathExists(readmePath)) {
      const readme = (await readFile(readmePath, 'utf-8')).toLowerCase();
      if (readme.includes('crewai')) {
        framework = 'crewai';
      } else if (readme.includes('langchain')) {
        framework = 'langchain';
      } else if (readme.includes('raw python') || readme.includes('framework-agnostic')) {
        framework = 'raw';
      }
    }

    if (fileNames.some(file => file.endsWith('.ts'))) {
      language = 'typescript';
    }

    return { framework, language };
  }

  private async createBackup(agentPath: string, agentName: string): Promise<string | null> {
    try {
      const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
      const backupPath = `${agentPath}.backup.${timestamp}`;

      await copyPath(agentPath, backupPath);
      return backupPath;
    } catch (error) {
      this.log(chalk.yellow(`⚠️  Could not create backup: ${error}`));
      return null;
    }
  }

  private async getAuthorName(): Promise<string> {
    return (
      process.env.GIT_AUTHOR_NAME ||
      process.env.USERNAME ||
      process.env.USER ||
      'Agent Developer'
    );
  }
}
