import { Command, Args, Flags } from '@oclif/core';
import path from 'path';
import chalk from 'chalk';
import ora from 'ora';
import { AgentRuntime, AgentDefinition, formatDuration } from '@agent-platform/core';
import { loadAgent, loadConfig } from '../utils/config-loader';

export default class Run extends Command {
  static description = 'Run an agent';

  static examples = [
    '<%= config.bin %> <%= command.id %> example',
    '<%= config.bin %> <%= command.id %> research-agent --input "Search for AI trends"',
    '<%= config.bin %> <%= command.id %> my-agent -i "Hello" --verbose',
  ];

  static flags = {
    input: Flags.string({
      char: 'i',
      description: 'Input for the agent',
    }),
    verbose: Flags.boolean({
      char: 'v',
      description: 'Show detailed execution logs',
      default: false,
    }),
    json: Flags.boolean({
      description: 'Output result as JSON',
      default: false,
    }),
  };

  static args = {
    agentName: Args.string({
      description: 'Name of the agent to run',
      required: true,
    }),
  };

  async run(): Promise<void> {
    const { args, flags } = await this.parse(Run);
    const { agentName } = args;

    // Get input
    let input = flags.input;
    if (!input) {
      this.log(
        chalk.red('Input is required. Use --input or -i flag to provide input.')
      );
      return;
    }

    let spinner: ora.Ora | undefined;

    try {
      // Load agent configuration
      if (flags.verbose) {
        this.log(chalk.dim(`Loading agent: ${agentName}`));
      }

      const agent = await loadAgent(agentName);

      if (!agent) {
        this.log(
          chalk.red(`Agent "${agentName}" not found. Check your agents/ directory.`)
        );
        return;
      }

      // Create runtime
      const runtime = new AgentRuntime([]);

      // Set up event listeners for verbose output
      if (flags.verbose) {
        runtime.on('agent:start', (data: any) => {
          this.log(chalk.blue(`▶ Starting agent: ${data.agentName}`));
        });

        runtime.on('agent:executing', () => {
          this.log(chalk.yellow('⚙ Executing agent...'));
        });

        runtime.on('tool:start', (data: any) => {
          this.log(chalk.cyan(`  🔧 Calling tool: ${data.toolName}`));
        });

        runtime.on('tool:complete', (data: any) => {
          this.log(
            chalk.green(
              `  ✓ Tool completed in ${formatDuration(data.duration)}`
            )
          );
        });

        runtime.on('tool:error', (data: any) => {
          this.log(chalk.red(`  ✗ Tool error: ${data.error}`));
        });
      } else {
        spinner = ora(`Running ${agentName}...`).start();
      }

      // Execute agent
      const startTime = Date.now();
      const result = await runtime.execute(agent, input);
      const duration = Date.now() - startTime;

      if (spinner) {
        if (result.status === 'success') {
          spinner.succeed(chalk.green('Agent completed successfully'));
        } else {
          spinner.fail(chalk.red('Agent failed'));
        }
      }

      // Output results
      if (flags.json) {
        this.log(JSON.stringify(result, null, 2));
      } else {
        this.log('\n' + chalk.bold('─'.repeat(50)));
        this.log(chalk.bold.cyan('Agent Output:'));
        this.log(chalk.bold('─'.repeat(50)));

        if (result.status === 'success') {
          this.log(chalk.white(result.output || ''));
        } else {
          this.log(chalk.red('Error: ' + result.error));
        }

        this.log(chalk.bold('─'.repeat(50)));
        this.log(chalk.dim(`Duration: ${formatDuration(duration)}`));

        if (result.toolCalls.length > 0) {
          this.log(
            chalk.dim(`Tools used: ${result.toolCalls.map(tc => tc.toolName).join(', ')}`)
          );
        }

        if (result.tokensUsed) {
          this.log(chalk.dim(`Tokens: ${result.tokensUsed}`));
        }

        if (result.cost) {
          this.log(chalk.dim(`Cost: $${result.cost.toFixed(4)}`));
        }
      }
    } catch (error) {
      if (spinner) {
        spinner.fail(chalk.red('Failed to run agent'));
      }
      this.error(error as Error);
    }
  }
}
