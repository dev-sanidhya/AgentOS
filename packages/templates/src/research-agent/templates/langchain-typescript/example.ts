/**
 * Example usage of {{AgentName}}
 * 
 * This script demonstrates how to use the research agent to gather
 * and synthesize information from the web.
 */

import { {{AgentName}}, research } from './{{agent_name}}';
import { config } from 'dotenv';

// Load environment variables
config();

async function basicExample(): Promise<void> {
  console.log('🔍 Basic Research Example');
  console.log('='.repeat(50));

  const query = 'What are the latest trends in artificial intelligence for 2026?';
  const result = await research(query, { model: 'gpt-4', verbose: true });

  console.log('\n📊 Results:');
  console.log(result);
}

async function advancedExample(): Promise<void> {
  console.log('\n🔍 Advanced Research Example');
  console.log('='.repeat(50));

  // Initialize agent with custom configuration
  const agent = new {{AgentName}}({
    model: 'gpt-4', // or 'claude-3-opus-20240229'
    temperature: 0.7,
    maxIterations: 10,
    verbose: true,
  });

  // Conduct research
  const query = 'Compare the performance of different LLM models on reasoning tasks';
  const result = await agent.research(query);

  console.log('\n📊 Results:');
  console.log(result.output);

  console.log('\n🔧 Intermediate Steps:');
  for (let i = 0; i < result.intermediateSteps.length; i++) {
    const step = result.intermediateSteps[i];
    console.log(`\nStep ${i + 1}: ${step.action.tool}`);
    console.log(`Input: ${JSON.stringify(step.action.toolInput)}`);
    console.log(`Output: ${step.observation.substring(0, 200)}...`); // Truncate for readability
  }
}

async function multiQueryExample(): Promise<void> {
  console.log('\n🔍 Multi-Query Research Example');
  console.log('='.repeat(50));

  const agent = new {{AgentName}}({ model: 'gpt-4', verbose: true });

  const queries = [
    'What is retrieval-augmented generation (RAG)?',
    'What are the main components of a RAG system?',
    'What are the best practices for implementing RAG?',
  ];

  const results: Array<{ query: string; result: any }> = [];
  
  for (const query of queries) {
    console.log(`\n📝 Query: ${query}`);
    const result = await agent.research(query);
    results.push({ query, result });
    console.log('✅ Completed\n');
  }

  console.log('\n📊 All Results:');
  for (let i = 0; i < results.length; i++) {
    const { query, result } = results[i];
    console.log(`\n--- Query ${i + 1} ---`);
    console.log(`Q: ${query}`);
    console.log(`A: ${result.output.substring(0, 300)}...`); // Truncate for readability
  }
}

async function main(): Promise<void> {
  // Check for API keys
  if (!process.env.OPENAI_API_KEY && !process.env.ANTHROPIC_API_KEY) {
    console.log('⚠️  Warning: No API keys found!');
    console.log('Please set OPENAI_API_KEY or ANTHROPIC_API_KEY in your .env file');
    console.log('\nExample .env file:');
    console.log('OPENAI_API_KEY=sk-...');
    console.log('ANTHROPIC_API_KEY=sk-ant-...');
    process.exit(1);
  }

  try {
    await basicExample();
    await advancedExample();

    // Uncomment to run multi-query example
    // await multiQueryExample();

  } catch (error) {
    console.log(`\n❌ Error: ${error}`);
    console.log('\nMake sure you have:');
    console.log('1. Set up your API keys in .env');
    console.log('2. Installed all dependencies: npm install');
    console.log('3. (Optional) Set up a search API (Brave, SerpAPI, or Tavily)');
  }
}

// Run the examples
if (require.main === module) {
  main().catch(console.error);
}

export { basicExample, advancedExample, multiQueryExample };
