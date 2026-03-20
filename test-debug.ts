import 'dotenv/config';
import Anthropic from '@anthropic-ai/sdk';

async function debug() {
  const token = process.env.CLAUDE_CODE_OAUTH_TOKEN;
  console.log('Token prefix:', token?.slice(0, 20));

  // Try 1: token as apiKey, default base URL, sonnet 4.6
  console.log('\n--- Test 1: claude-sonnet-4-6 ---');
  try {
    const client = new Anthropic({ apiKey: token });
    const res = await client.messages.create({
      model: 'claude-sonnet-4-6',
      max_tokens: 100,
      messages: [{ role: 'user', content: 'Say hello in 5 words' }],
    });
    console.log('Success:', res.content[0]);
  } catch (err: any) {
    console.log('Error:', err.status, err.message?.slice(0, 200));
  }

  // Try 2: claude-sonnet-4-5-20250514
  console.log('\n--- Test 2: claude-sonnet-4-5-20250514 ---');
  try {
    const client = new Anthropic({ apiKey: token });
    const res = await client.messages.create({
      model: 'claude-sonnet-4-5-20250514',
      max_tokens: 100,
      messages: [{ role: 'user', content: 'Say hello in 5 words' }],
    });
    console.log('Success:', res.content[0]);
  } catch (err: any) {
    console.log('Error:', err.status, err.message?.slice(0, 200));
  }

  // Try 3: claude-3-5-sonnet-20241022
  console.log('\n--- Test 3: claude-3-5-sonnet-20241022 ---');
  try {
    const client = new Anthropic({ apiKey: token });
    const res = await client.messages.create({
      model: 'claude-3-5-sonnet-20241022',
      max_tokens: 100,
      messages: [{ role: 'user', content: 'Say hello in 5 words' }],
    });
    console.log('Success:', res.content[0]);
  } catch (err: any) {
    console.log('Error:', err.status, err.message?.slice(0, 200));
  }

  // Try 4: Check if it needs bearer auth header instead
  console.log('\n--- Test 4: Bearer auth via fetch ---');
  try {
    const response = await fetch('https://api.anthropic.com/v1/messages', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`,
        'anthropic-version': '2023-06-01',
      },
      body: JSON.stringify({
        model: 'claude-sonnet-4-6',
        max_tokens: 100,
        messages: [{ role: 'user', content: 'Say hello in 5 words' }],
      }),
    });
    const data = await response.json();
    console.log('Status:', response.status);
    console.log('Response:', JSON.stringify(data).slice(0, 300));
  } catch (err: any) {
    console.log('Error:', err.message);
  }
}

debug().catch(console.error);
