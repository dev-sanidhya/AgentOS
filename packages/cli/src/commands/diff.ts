import { Command, Args, Flags } from '@oclif/core';
import chalk from 'chalk';
import * as path from 'path';
import { isAgentProject } from '../utils/config-loader';
import {
  detectProjectFramework,
  detectProjectLanguage,
  getAvailableTemplates,
  createTemplateVariables,
  type TemplateVariant,
  type FrameworkType,
  type LanguageType
} from '../utils/template-manager';

export default class Diff extends Command {
  static description = 'Preview files that would be created by agent add';

  static examples = [
    '<%= config.bin %> <%= command.id %> research-agent',
    '<%= config.bin %> <%= command.id %> research-agent --framework=crewai',
    '<%= config.bin %> <%= command.id %> research-agent --path=./src/agents',
  ];

  static args = {
    template: Args.string({
      description: 'Agent template name to preview',
      required: true,
    }),
  };

  static flags = {
    framework: Flags.string({
      description: 'Framework to use (langchain, crewai, raw)',
      options: ['langchain', 'crewai', 'raw'],
    }),
    lang: Flags.string({
      description: 'Language to use (python, typescript)',
      options: ['python', 'typescript'],
    }),
    path: Flags.string({
      description: 'Path where files would be added',
      default: './agents',
    }),
    'agent-name': Flags.string({
      description: 'Custom agent name (defaults to template name)',
    }),
  };

  async run(): Promise<void> {
    const { args, flags } = await this.parse(Diff);

    try {
      // Check if we're in an agent project
      if (!await isAgentProject()) {
        this.log(chalk.yellow('⚠ Not in an agent project. Run "agent init" to create one.'));
        return;
      }

      const templateName = args.template;
      const agentName = flags['agent-name'] || templateName.replace('-agent', '');

      this.log(chalk.bold.cyan(`\n🔍 Preview: Adding ${templateName} template\n`));

      // Get available templates
      const availableTemplates = await getAvailableTemplates();
      const template = availableTemplates.find(t => t.name === templateName);

      if (!template) {
        this.log(chalk.red(`❌ Template "${templateName}" not found`));
        this.log(chalk.dim('Available templates:'));
        availableTemplates.forEach(t => {
          this.log(chalk.dim(`  - ${t.name}`));
        });
        return;
      }

      // Detect or get framework and language preferences
      const framework = (flags.framework as FrameworkType) || await detectProjectFramework();
      const language = (flags.lang as LanguageType) || await detectProjectLanguage();

      // Find matching variant
      const variant = Object.values(template.variants).find(v =>
        v.framework === framework && v.language === language
      ) as TemplateVariant;

      if (!variant) {
        this.log(chalk.red(`❌ No ${language} + ${framework} variant available for ${templateName}`));
        this.log(chalk.dim('Available variants:'));
        Object.values(template.variants).forEach(v => {
          this.log(chalk.dim(`  - ${v.language} + ${v.framework}: ${v.description}`));
        });
        return;
      }

      // Show configuration
      this.log(chalk.blue('📋 Configuration:'));
      this.log(`  Template:  ${chalk.white(templateName)}`);
      this.log(`  Agent:     ${chalk.white(agentName)}`);
      this.log(`  Language:  ${chalk.white(language)}`);
      this.log(`  Framework: ${chalk.white(framework)}`);
      this.log(`  Path:      ${chalk.white(flags.path)}/${chalk.white(agentName)}`);

      // Show template variables
      const context = {
        targetPath: path.resolve(flags.path, agentName),
        agentName,
        templateName,
        framework,
        language,
        author: 'Your Name',
        description: template.description,
      };

      const variables = createTemplateVariables(context);

      this.log(chalk.blue('\n🔧 Template Variables:'));
      Object.entries(variables).forEach(([key, value]) => {
        if (key !== 'date' && key !== 'year') {
          this.log(`  ${chalk.dim(key + ':').padEnd(15)} ${chalk.white(value)}`);
        }
      });

      // Show files that would be created
      this.log(chalk.blue('\n📄 Files to be created:'));

      const targetPath = path.resolve(flags.path, agentName);
      if (variant.files) {
        Object.entries(variant.files).forEach(([type, fileName]) => {
          const processedName = this.processFileName(fileName, variables);
          const fullPath = path.join(targetPath, processedName);
          const relativePath = path.relative(process.cwd(), fullPath);

          this.log(`  ${chalk.green('+')} ${chalk.white(relativePath)} ${chalk.dim(`(${type})`)}`);
        });
      } else {
        // Fallback - show common files
        const commonFiles = [
          { name: `{{agent_name}}.${language === 'python' ? 'py' : 'ts'}`, type: 'main agent' },
          { name: 'README.md', type: 'documentation' },
          { name: `example.${language === 'python' ? 'py' : 'ts'}`, type: 'example usage' },
          { name: language === 'python' ? 'requirements.txt' : 'package.json', type: 'dependencies' },
          { name: '.env.example', type: 'environment template' },
        ];

        if (framework === 'langchain') {
          commonFiles.push({ name: 'tools/', type: 'tool modules' });
          commonFiles.push({ name: `prompts.${language === 'python' ? 'py' : 'ts'}`, type: 'prompts' });
        }

        commonFiles.forEach(({ name, type }) => {
          const processedName = this.processFileName(name, variables);
          const fullPath = path.join(targetPath, processedName);
          const relativePath = path.relative(process.cwd(), fullPath);

          this.log(`  ${chalk.green('+')} ${chalk.white(relativePath)} ${chalk.dim(`(${type})`)}`);
        });
      }

      // Show dependencies
      if (variant.dependencies) {
        this.log(chalk.blue('\n📦 Dependencies to install:'));

        if (language === 'python' && variant.dependencies.packages) {
          const packages = Array.isArray(variant.dependencies.packages)
            ? variant.dependencies.packages
            : Object.keys(variant.dependencies.packages);

          packages.forEach(pkg => {
            this.log(`  ${chalk.green('+')} ${chalk.white(pkg)}`);
          });

          this.log(chalk.dim('\n  Install with: pip install -r requirements.txt'));
        } else if (language === 'typescript' && variant.dependencies.packages) {
          const packages = variant.dependencies.packages as Record<string, string>;
          Object.entries(packages).forEach(([pkg, version]) => {
            this.log(`  ${chalk.green('+')} ${chalk.white(pkg)} ${chalk.dim(version)}`);
          });

          this.log(chalk.dim('\n  Install with: npm install'));
        }
      }

      // Show next steps
      this.log(chalk.bold.green('\n✨ Next Steps:'));
      this.log(chalk.cyan(`  agent add ${templateName}${flags.framework ? ` --framework=${flags.framework}` : ''}${flags.lang ? ` --lang=${flags.lang}` : ''}`));

      if (variant.framework !== 'raw') {
        this.log(chalk.dim(`\n💡 This template uses ${variant.framework} framework - perfect for ${variant.description.toLowerCase()}`));
      } else {
        this.log(chalk.dim('\n💡 This template uses raw Python/TypeScript - great for maximum control and minimal dependencies'));
      }

    } catch (error) {
      this.log(chalk.red(`❌ Failed to preview template: ${error}`));
      if (process.env.DEBUG) {
        console.error(error);
      }
    }
  }

  private processFileName(fileName: string, variables: Record<string, string>): string {
    let processed = fileName;
    Object.entries(variables).forEach(([key, value]) => {
      processed = processed.replace(new RegExp(`{{${key}}}`, 'g'), value);
    });
    return processed;
  }
}
