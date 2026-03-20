require('dotenv').config();

async function debug() {
  const token = process.env.CLAUDE_CODE_OAUTH_TOKEN;
  console.log('Token prefix:', token?.slice(0, 25) + '...');

  // Test 1: Bearer auth with claude-sonnet-4-6
  console.log('\n--- Test 1: Bearer auth, claude-sonnet-4-6 ---');
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
        messages: [{ role: 'user', content: 'Say hello in exactly 5 words' }],
      }),
    });
    const data = await response.json();
    console.log('Status:', response.status);
    console.log('Response:', JSON.stringify(data).slice(0, 500));
  } catch (err) {
    console.log('Error:', err.message);
  }

  // Test 2: x-api-key header with claude-sonnet-4-6
  console.log('\n--- Test 2: x-api-key header, claude-sonnet-4-6 ---');
  try {
    const response = await fetch('https://api.anthropic.com/v1/messages', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'x-api-key': token,
        'anthropic-version': '2023-06-01',
      },
      body: JSON.stringify({
        model: 'claude-sonnet-4-6',
        max_tokens: 100,
        messages: [{ role: 'user', content: 'Say hello in exactly 5 words' }],
      }),
    });
    const data = await response.json();
    console.log('Status:', response.status);
    console.log('Response:', JSON.stringify(data).slice(0, 500));
  } catch (err) {
    console.log('Error:', err.message);
  }

  // Test 3: Bearer auth with claude-sonnet-4-5-20250514
  console.log('\n--- Test 3: Bearer auth, claude-sonnet-4-5-20250514 ---');
  try {
    const response = await fetch('https://api.anthropic.com/v1/messages', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`,
        'anthropic-version': '2023-06-01',
      },
      body: JSON.stringify({
        model: 'claude-sonnet-4-5-20250514',
        max_tokens: 100,
        messages: [{ role: 'user', content: 'Say hello in exactly 5 words' }],
      }),
    });
    const data = await response.json();
    console.log('Status:', response.status);
    console.log('Response:', JSON.stringify(data).slice(0, 500));
  } catch (err) {
    console.log('Error:', err.message);
  }
}

debug().catch(console.error);
