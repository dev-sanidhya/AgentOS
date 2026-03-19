module.exports = { 
  name: 'example', 
  version: '0.1.0', 
  description: 'Example agent for e2e', 
  systemPrompt: 'You are a test agent.', 
  tools: [], 
  config: { model: 'test-model', provider: 'test', temperature: 0.0, maxTokens: 256 }, 
  async execute(input) { return 'Echo: ' && ' + input; } 
}; 
