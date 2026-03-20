import * as fs from "fs";
import * as path from "path";
import chalk from "chalk";
import inquirer from "inquirer";

export async function initProject(name?: string): Promise<void> {
  if (!name) {
    const { projectName } = await inquirer.prompt([
      {
        type: "input",
        name: "projectName",
        message: "Project name:",
        default: "my-agent-project",
      },
    ]);
    name = projectName;
  }

  const projectDir = path.resolve(name!);

  if (fs.existsSync(projectDir)) {
    console.log(chalk.red(`  Directory ${name} already exists.`));
    return;
  }

  console.log();
  console.log(chalk.cyan(`  Creating ${name}...`));

  fs.mkdirSync(projectDir, { recursive: true });

  // package.json
  const pkg = {
    name,
    version: "0.1.0",
    private: true,
    scripts: {
      start: "ts-node index.ts",
    },
    dependencies: {
      "@agentos/agents": "^0.1.0",
    },
    devDependencies: {
      "@types/node": "^20.11.0",
      "ts-node": "^10.9.2",
      "typescript": "^5.3.3",
    },
  };

  fs.writeFileSync(
    path.join(projectDir, "package.json"),
    JSON.stringify(pkg, null, 2)
  );

  // tsconfig.json
  const tsconfig = {
    compilerOptions: {
      target: "ES2022",
      module: "commonjs",
      esModuleInterop: true,
      strict: true,
      skipLibCheck: true,
    },
  };

  fs.writeFileSync(
    path.join(projectDir, "tsconfig.json"),
    JSON.stringify(tsconfig, null, 2)
  );

  // .env
  fs.writeFileSync(
    path.join(projectDir, ".env"),
    [
      "# Authentication (pick one)",
      "",
      "# Option 1: Claude Max/Pro plan (recommended — no API billing)",
      "# Run: claude setup-token",
      "# CLAUDE_CODE_OAUTH_TOKEN=sk-ant-oat01-...",
      "",
      "# Option 2: Anthropic API key",
      "# ANTHROPIC_API_KEY=sk-ant-...",
      "",
      "# Optional: For web search (Brave Search API)",
      "# BRAVE_SEARCH_API_KEY=",
      "",
    ].join("\n")
  );

  // .gitignore
  fs.writeFileSync(
    path.join(projectDir, ".gitignore"),
    "node_modules/\ndist/\n.env\n"
  );

  // index.ts - example usage
  const example = `import {
  ResearchAgent,
  CodeReviewAgent,
  ContentWriter,
  EmailDrafter,
  SEOAuditor,
  BugTriager,
  configure,
} from '@agentos/agents';
import 'dotenv/config';

// Authentication is auto-detected from environment variables:
// - CLAUDE_CODE_OAUTH_TOKEN (Max/Pro plan — recommended)
// - ANTHROPIC_API_KEY (standard API key)
//
// Or configure explicitly:
// configure({ oauthToken: process.env.CLAUDE_CODE_OAUTH_TOKEN });

async function main() {
  // Example 1: Research a topic
  console.log('Researching...');
  const research = await ResearchAgent.run('Latest trends in AI agents 2026');
  console.log(research.output);

  // Example 2: Draft an email
  // const email = await EmailDrafter.run('Follow-up email to a potential investor after a demo call');
  // console.log(email.output);

  // Example 3: Audit SEO
  // const seo = await SEOAuditor.run('https://example.com');
  // console.log(seo.output);

  // Example 4: Review code
  // const review = await CodeReviewAgent.run('./index.ts');
  // console.log(review.output);

  // Example 5: Triage a bug
  // const triage = await BugTriager.run('Login page crashes on Safari when clicking "Forgot Password"');
  // console.log(triage.output);
}

main().catch(console.error);
`;

  fs.writeFileSync(path.join(projectDir, "index.ts"), example);

  console.log(chalk.green("  Done!"));
  console.log();
  console.log("  Next steps:");
  console.log();
  console.log(chalk.gray(`    cd ${name}`));
  console.log(chalk.gray("    npm install"));
  console.log(chalk.gray("    # Set up auth (pick one):"));
  console.log(chalk.gray("    #   claude setup-token && export CLAUDE_CODE_OAUTH_TOKEN=..."));
  console.log(chalk.gray("    #   export ANTHROPIC_API_KEY=sk-ant-..."));
  console.log(chalk.gray("    npx ts-node index.ts"));
  console.log();
}
