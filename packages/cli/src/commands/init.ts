import { Command, Args, Flags } from '@oclif/core';
import { promises as fs } from 'fs';
import path from 'path';
import chalk from 'chalk';
import inquirer from 'inquirer';
import ora from 'ora';

export default class Init extends Command {
  static description = 'Initialize a new agent project';

  static examples = [
    '<%= config.bin %> <%= command.id %>',
    '<%= config.bin %> <%= command.id %> my-agent-project',
    '<%= config.bin %> <%= command.id %> --name my-agent',
  ];

  static flags = {
    name: Flags.string({
      char: 'n',
      description: 'Project name',
    }),
    typescript: Flags.boolean({
      char: 't',
      description: 'Use TypeScript',
      default: true,
      allowNo: true,
    }),
  };

  static args = {
    projectName: Args.string({
      description: 'Name of the project to create',
      required: false,
    }),
  };

  async run(): Promise<void> {
    const { args, flags } = await this.parse(Init);

    // Get project name
    let projectName = args.projectName || flags.name;

    if (!projectName) {
      const answers = await inquirer.prompt([
        {
          type: 'input',
          name: 'projectName',
          message: 'What is your project name?',
          default: 'my-agent-project',
          validate: (input: string) => {
            if (!input || input.trim().length === 0) {
              return 'Project name is required';
            }
            if (!/^[a-z0-9-]+$/.test(input)) {
              return 'Project name can only contain lowercase letters, numbers, and hyphens';
            }
            return true;
          },
        },
      ]);
      projectName = answers.projectName;
    }

    if (!projectName) {
      this.error(chalk.red('Project name is required.'));
    }

    const projectPath = path.join(process.cwd(), projectName);

    // Check if directory already exists
    try {
      await fs.access(projectPath);
      this.error(
        chalk.red(`Directory ${chalk.bold(projectName)} already exists!`)
      );
    } catch {
      // Directory doesn't exist, which is good
    }

    const spinner = ora('Creating project structure...').start();

    try {
      // Create project directory
      await fs.mkdir(projectPath, { recursive: true });

      // Create subdirectories
      await fs.mkdir(path.join(projectPath, 'agents'), { recursive: true });
      await fs.mkdir(path.join(projectPath, 'tools'), { recursive: true });

      // Create package.json
      const packageJson = {
        name: projectName,
        version: '0.1.0',
        description: 'AI Agent Project',
        main: 'index.js',
        scripts: {
          dev: 'agent dev',
          build: 'tsc',
          test: 'agent test',
        },
        dependencies: {
          '@agent-platform/core': 'latest',
        },
        devDependencies: flags.typescript
          ? {
              typescript: '^5.3.3',
              '@types/node': '^20.11.0',
            }
          : {},
      };

      await fs.writeFile(
        path.join(projectPath, 'package.json'),
        JSON.stringify(packageJson, null, 2)
      );

      // Create agent.config.js
      const configContent = flags.typescript
        ? this.getTypeScriptConfig()
        : this.getJavaScriptConfig();

      await fs.writeFile(
        path.join(
          projectPath,
          flags.typescript ? 'agent.config.ts' : 'agent.config.js'
        ),
        configContent
      );

      // Create example agent
      const exampleAgentContent = flags.typescript
        ? this.getTypeScriptExampleAgent()
        : this.getJavaScriptExampleAgent();

      await fs.writeFile(
        path.join(
          projectPath,
          'agents',
          flags.typescript ? 'example.agent.ts' : 'example.agent.js'
        ),
        exampleAgentContent
      );

      // Create .env file
      const envContent = `# API Keys
OPENAI_API_KEY=your_openai_api_key_here
ANTHROPIC_API_KEY=your_anthropic_api_key_here

# Agent Configuration
DEFAULT_MODEL=claude-sonnet-4
ENABLE_LOGGING=true
`;

      await fs.writeFile(path.join(projectPath, '.env'), envContent);

      // Create .gitignore
      const gitignoreContent = `node_modules/
.env
.env.local
dist/
build/
*.log
.agent-platform/
`;

      await fs.writeFile(path.join(projectPath, '.gitignore'), gitignoreContent);

      // Create README.md
      const readmeContent = this.getReadmeContent(projectName, flags.typescript);
      await fs.writeFile(path.join(projectPath, 'README.md'), readmeContent);

      // Create TypeScript config if needed
      if (flags.typescript) {
        const tsconfigContent = {
          compilerOptions: {
            target: 'ES2022',
            module: 'commonjs',
            lib: ['ES2022'],
            outDir: './dist',
            rootDir: './src',
            strict: true,
            esModuleInterop: true,
            skipLibCheck: true,
            forceConsistentCasingInFileNames: true,
            resolveJsonModule: true,
          },
          include: ['agents/**/*', 'tools/**/*', '*.ts'],
          exclude: ['node_modules', 'dist'],
        };

        await fs.writeFile(
          path.join(projectPath, 'tsconfig.json'),
          JSON.stringify(tsconfigContent, null, 2)
        );
      }

      spinner.succeed(chalk.green('Project created successfully!'));

      // Display next steps
      this.log('\n' + chalk.bold.green('✓ Project initialized!'));
      this.log('\n' + chalk.bold('Next steps:'));
      this.log('  ' + chalk.cyan(`cd ${projectName}`));
      this.log('  ' + chalk.cyan('npm install'));
      this.log('  ' + chalk.cyan('agent dev') + ' - Start dev server');
      this.log('  ' + chalk.cyan('agent run example') + ' - Run example agent');
      this.log('\n' + chalk.dim('Happy coding! 🚀'));
    } catch (error) {
      spinner.fail(chalk.red('Failed to create project'));
      this.error(error as Error);
    }
  }

  private getTypeScriptConfig(): string {
    return `import { AgentConfig } from '@agent-platform/core';

export const config: AgentConfig = {
  provider: 'anthropic',
  model: 'claude-sonnet-4',
  temperature: 0.7,
  maxTokens: 4000,
};

export default config;
`;
  }

  private getJavaScriptConfig(): string {
    return `module.exports = {
  provider: 'anthropic',
  model: 'claude-sonnet-4',
  temperature: 0.7,
  maxTokens: 4000,
};
`;
  }

  private getTypeScriptExampleAgent(): string {
    return `import { AgentDefinition, AgentContext } from '@agent-platform/core';

const exampleAgent: AgentDefinition = {
  name: 'example-agent',
  version: '0.1.0',
  description: 'An example agent to get you started',

  systemPrompt: \`You are a helpful AI assistant.
You help users with their tasks in a clear and concise manner.\`,

  tools: [],

  config: {
    model: 'claude-sonnet-4',
    provider: 'anthropic',
    temperature: 0.7,
    maxTokens: 4000,
  },

  async execute(input: string, context: AgentContext): Promise<string> {
    // This is where your agent logic goes
    // For now, it just echoes back the input

    context.emit?.('agent:thinking', { message: 'Processing input...' });

    return \`You said: \${input}\`;
  },
};

export default exampleAgent;
`;
  }

  private getJavaScriptExampleAgent(): string {
    return `module.exports = {
  name: 'example-agent',
  version: '0.1.0',
  description: 'An example agent to get you started',

  systemPrompt: \`You are a helpful AI assistant.
You help users with their tasks in a clear and concise manner.\`,

  tools: [],

  config: {
    model: 'claude-sonnet-4',
    provider: 'anthropic',
    temperature: 0.7,
    maxTokens: 4000,
  },

  async execute(input, context) {
    // This is where your agent logic goes
    // For now, it just echoes back the input

    if (context.emit) {
      context.emit('agent:thinking', { message: 'Processing input...' });
    }

    return \`You said: \${input}\`;
  },
};
`;
  }

  private getReadmeContent(projectName: string, useTypeScript: boolean): string {
    return `# ${projectName}

An AI Agent project built with Agent Platform.

## Getting Started

1. Install dependencies:
\`\`\`bash
npm install
\`\`\`

2. Set up your API keys in \`.env\`:
\`\`\`bash
ANTHROPIC_API_KEY=your_key_here
OPENAI_API_KEY=your_key_here
\`\`\`

3. Run the dev server:
\`\`\`bash
agent dev
\`\`\`

4. Run your agent:
\`\`\`bash
agent run example
\`\`\`

## Project Structure

\`\`\`
${projectName}/
├── agents/          # Your agent definitions
├── tools/           # Custom tools for agents
├── agent.config.${useTypeScript ? 'ts' : 'js'}  # Agent configuration
└── .env            # Environment variables
\`\`\`

## Available Commands

- \`agent dev\` - Start development server with UI
- \`agent run <agent-name>\` - Run an agent
- \`agent test\` - Run agent tests
- \`agent add <template>\` - Add agent from template

## Learn More

- [Documentation](https://agent-platform.dev/docs)
- [Examples](https://agent-platform.dev/examples)
- [Community](https://agent-platform.dev/community)
`;
  }
}
