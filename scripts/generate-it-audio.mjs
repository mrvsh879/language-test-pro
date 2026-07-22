import fs from 'node:fs/promises';
import path from 'node:path';

const apiKey = process.env.OPENAI_API_KEY;
if (!apiKey) throw new Error('OPENAI_API_KEY is missing');

const bank = JSON.parse(await fs.readFile('data/it-listening.json', 'utf8'));
await fs.mkdir('audio/it', { recursive: true });

for (const q of bank.questions) {
  const out = path.join('audio', 'it', `${q.id}.mp3`);
  try {
    await fs.access(out);
    console.log('skip', out);
    continue;
  } catch {}

  const response = await fetch('https://api.openai.com/v1/audio/speech', {
    method: 'POST',
    headers: {
      Authorization: `Bearer ${apiKey}`,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      model: 'gpt-4o-mini-tts',
      voice: 'coral',
      input: q.transcript,
      instructions: 'Speak in clear, natural Standard Italian at a pace appropriate for a professional language listening test. Do not add or omit any words.',
      response_format: 'mp3',
    }),
  });

  if (!response.ok) throw new Error(`${q.id}: ${response.status} ${await response.text()}`);
  await fs.writeFile(out, Buffer.from(await response.arrayBuffer()));
  console.log('created', out);
}

// Trigger marker: 2026-07-22
