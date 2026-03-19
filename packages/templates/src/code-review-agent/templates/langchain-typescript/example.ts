import { config } from 'dotenv';
import { {{AgentName}} } from './{{agent_name}}.js';
import type { ModelConfig, ReviewConfig, CodeReviewResult } from './{{agent_name}}.js';

// Load environment variables
config();

/**
 * Example usage of the {{AgentName}}
 */
async function main() {
  try {
    // Example 1: Basic setup with OpenAI
    console.log('🔍 Setting up Code Review Agent with OpenAI...\n');

    const openaiConfig: ModelConfig = {
      provider: 'openai',
      model: process.env.OPENAI_MODEL || 'gpt-4',
      temperature: 0.1,
      maxTokens: 4000,
    };

    const reviewConfig: ReviewConfig = {
      includeSecurityScan: true,
      includePerformanceAnalysis: true,
      strictMode: false,
      languageSpecific: true,
    };

    const agent = new {{AgentName}}(openaiConfig, reviewConfig);

    // Example 2: Review TypeScript code
    console.log('📝 Reviewing TypeScript code...\n');

    const typescriptCode = `
interface User {
  id: string;
  email: string;
  password: string; // This should be hashed
}

class UserService {
  private users: User[] = [];

  async createUser(userData: Partial<User>): Promise<User> {
    // Security issue: No input validation
    const user = {
      id: Math.random().toString(36), // Weak ID generation
      email: userData.email,
      password: userData.password, // Plain text password!
    } as User;

    this.users.push(user);
    console.log('User created:', user); // Information disclosure
    return user;
  }

  findUserByEmail(email: string): User | undefined {
    // Performance issue: Linear search
    for (let i = 0; i < this.users.length; i++) {
      if (this.users[i].email === email) {
        return this.users[i];
      }
    }
    return undefined;
  }
}`;

    const tsResult = await agent.reviewCode(typescriptCode, 'UserService.ts', 'typescript');
    console.log('TypeScript Review Result:');
    console.log('Overall Score:', tsResult.overallScore);
    console.log('Security Issues:', tsResult.analysis.security.vulnerabilities.length);
    console.log('Quality Issues:', tsResult.analysis.codeQuality.issues.length);
    console.log('Performance Issues:', tsResult.analysis.performance.bottlenecks.length);
    console.log('Summary:', tsResult.summary);
    console.log('\n' + '='.repeat(80) + '\n');

    // Example 3: Review Python code with security issues
    console.log('🐍 Reviewing Python code with security vulnerabilities...\n');

    const pythonCode = `
import os
import sqlite3
from flask import Flask, request

app = Flask(__name__)

@app.route('/user')
def get_user():
    user_id = request.args.get('id')

    # SQL Injection vulnerability
    query = f"SELECT * FROM users WHERE id = '{user_id}'"

    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute(query)
    user = cursor.fetchone()

    if not user:
        return "User not found", 404

    return {"user": user}

@app.route('/execute')
def execute_command():
    cmd = request.args.get('cmd')

    # Command injection vulnerability
    result = os.system(cmd)
    return f"Command executed with result: {result}"

# Exposed secret
API_KEY = "sk-1234567890abcdef"
`;

    const pythonResult = await agent.reviewCode(pythonCode, 'app.py', 'python');
    console.log('Python Review Result:');
    console.log('Overall Score:', pythonResult.overallScore);
    console.log('Critical Security Issues:',
      pythonResult.analysis.security.vulnerabilities.filter(v => v.severity === 'critical').length
    );
    console.log('\n' + '='.repeat(80) + '\n');

    // Example 4: Quick security scan only
    console.log('🔒 Running quick security scan...\n');

    const vulnerabilities = await agent.quickSecurityScan(pythonCode, 'python');
    console.log(`Found ${vulnerabilities.length} security vulnerabilities:`);
    vulnerabilities.forEach((vuln, index) => {
      console.log(`${index + 1}. ${vuln.type} (${vuln.severity}) - Line ${vuln.line}`);
      console.log(`   ${vuln.description}`);
    });
    console.log('\n' + '='.repeat(80) + '\n');

    // Example 5: Validate best practices for JavaScript
    console.log('✅ Validating JavaScript best practices...\n');

    const jsCode = `
var userName = "john_doe"; // Should use const
var userAge = 25;

function getUserInfo() {
  if (userName == "admin") { // Should use strict equality
    return {
      name: userName,
      age: userAge,
      isAdmin: true
    }
  } else {
    return {
      name: userName,
      age: userAge,
      isAdmin: false
    }
  }
}

// Missing error handling
function parseUserData(jsonString) {
  return JSON.parse(jsonString);
}
`;

    const bestPracticesIssues = await agent.validateBestPractices(jsCode, 'javascript');
    console.log(`Found ${bestPracticesIssues.length} best practice violations:`);
    bestPracticesIssues.forEach((issue, index) => {
      console.log(`${index + 1}. ${issue.message} (Line ${issue.line})`);
      console.log(`   Suggestion: ${issue.suggestion}`);
    });
    console.log('\n' + '='.repeat(80) + '\n');

    // Example 6: Review multiple files
    console.log('📁 Reviewing multiple files...\n');

    const files = [
      {
        code: typescriptCode,
        fileName: 'UserService.ts',
        language: 'typescript'
      },
      {
        code: pythonCode,
        fileName: 'app.py',
        language: 'python'
      },
      {
        code: jsCode,
        fileName: 'utils.js',
        language: 'javascript'
      }
    ];

    const multipleResults = await agent.reviewMultipleFiles(files);
    console.log(`Reviewed ${multipleResults.size} files:`);

    multipleResults.forEach((result, fileName) => {
      console.log(`- ${fileName}: Score ${result.overallScore}/10`);
    });
    console.log('\n' + '='.repeat(80) + '\n');

    // Example 7: Using Anthropic Claude
    console.log('🤖 Testing with Anthropic Claude...\n');

    const claudeConfig: ModelConfig = {
      provider: 'anthropic',
      model: process.env.ANTHROPIC_MODEL || 'claude-3-sonnet-20240229',
      temperature: 0.1,
      maxTokens: 4000,
    };

    const claudeAgent = new {{AgentName}}(claudeConfig, reviewConfig);

    const simpleCode = `
function add(a, b) {
  return a + b;
}

const result = add(5, 3);
console.log(result);
`;

    const claudeResult = await claudeAgent.reviewCode(simpleCode, 'simple.js', 'javascript');
    console.log('Claude Review Result:');
    console.log('Score:', claudeResult.overallScore);
    console.log('Summary:', claudeResult.summary);
    console.log('\n' + '='.repeat(80) + '\n');

    // Example 8: Configuration updates
    console.log('⚙️  Testing configuration updates...\n');

    console.log('Current config:', agent.getConfig());

    agent.updateConfig({
      strictMode: true,
      includePerformanceAnalysis: false,
      customRules: ['no-console', 'prefer-const']
    });

    console.log('Updated config:', agent.getConfig());
    console.log('\n' + '='.repeat(80) + '\n');

    // Example 9: Error handling demonstration
    console.log('❌ Testing error handling...\n');

    try {
      await agent.reviewCode('invalid code that will cause issues', 'test.js', 'javascript');
    } catch (error) {
      console.log('Caught error:', error instanceof Error ? error.message : String(error));
    }

    console.log('\n✅ All examples completed successfully!');

  } catch (error) {
    console.error('❌ Example failed:', error);
    process.exit(1);
  }
}

// Helper function to demonstrate custom analysis
async function demonstrateCustomAnalysis() {
  console.log('\n🔬 Advanced Analysis Examples\n');

  const config: ModelConfig = {
    provider: (process.env.DEFAULT_MODEL_PROVIDER as 'openai' | 'anthropic') || 'openai',
    model: process.env.OPENAI_MODEL || 'gpt-4',
  };

  const agent = new {{AgentName}}(config);

  // Complex code with multiple issues
  const complexCode = `
class DatabaseManager {
  constructor() {
    this.connection = null;
    this.password = "admin123"; // Hardcoded password
  }

  async connect() {
    try {
      this.connection = await mysql.createConnection({
        host: 'localhost',
        user: 'root',
        password: this.password,
        database: 'myapp'
      });
    } catch (err) {
      console.log('Connection error:', err); // Exposing sensitive error info
    }
  }

  async getUser(id) {
    if (!this.connection) {
      throw new Error('Not connected');
    }

    // SQL injection vulnerability
    const query = \`SELECT * FROM users WHERE id = \${id}\`;

    try {
      const [rows] = await this.connection.execute(query);
      return rows[0];
    } catch (error) {
      throw error; // Re-throwing without handling
    }
  }

  async getAllUsers() {
    const users = [];
    const query = 'SELECT * FROM users';
    const [rows] = await this.connection.execute(query);

    // Performance issue: N+1 query pattern
    for (let i = 0; i < rows.length; i++) {
      const userDetails = await this.getUserDetails(rows[i].id);
      users.push({ ...rows[i], ...userDetails });
    }

    return users;
  }

  async getUserDetails(id) {
    const query = \`SELECT * FROM user_details WHERE user_id = \${id}\`;
    const [rows] = await this.connection.execute(query);
    return rows[0];
  }
}`;

  const result = await agent.reviewCode(complexCode, 'DatabaseManager.js', 'javascript');

  console.log('🔍 Detailed Analysis Results:');
  console.log('Overall Score:', result.overallScore);
  console.log('\n📊 Breakdown:');
  console.log(`- Code Quality: ${result.analysis.codeQuality.score}/10`);
  console.log(`- Security: ${result.analysis.security.score}/10`);
  console.log(`- Performance: ${result.analysis.performance.score}/10`);
  console.log(`- Maintainability: ${result.analysis.maintainability.score}/10`);

  console.log('\n🚨 Critical Issues:');
  const criticalIssues = [
    ...result.analysis.codeQuality.issues.filter(i => i.severity === 'critical'),
    ...result.analysis.security.vulnerabilities.filter(v => v.severity === 'critical')
  ];

  criticalIssues.forEach((issue, index) => {
    console.log(`${index + 1}. ${'type' in issue ? issue.message : issue.description} (Line ${'line' in issue ? issue.line : 'unknown'})`);
  });
}

// Run examples
if (require.main === module) {
  main()
    .then(() => demonstrateCustomAnalysis())
    .catch(console.error);
}

export { main, demonstrateCustomAnalysis };