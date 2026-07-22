import fs from 'node:fs/promises';
import path from 'node:path';

const apiKey = process.env.OPENAI_API_KEY;
if (!apiKey) throw new Error('OPENAI_API_KEY is not configured');

const bankPath = 'data/cs-listening.json';
const bank = JSON.parse(await fs.readFile(bankPath, 'utf8'));
const outputDir = 'audio/cs';
await fs.mkdir(outputDir, { recursive: true });

for (const question of bank.questions) {
  const outputPath = path.join(outputDir, `${question.id}.mp3`);
  try {
    await fs.access(outputPath);
    console.log(`Skip existing: ${outputPath}`);
    continue;
  } catch {}

  console.log(`Generating ${question.id}...`);
  const response = await fetch('https://api.openai.com/v1/audio/speech', {
    method: 'POST',
    headers: {
      Authorization: `Bearer ${apiKey}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      model: 'gpt-4o-mini-tts',
      voice: 'marin',
      input: question.transcript,
      response_format: 'mp3',
      instructions: question.level === 'A1'
        ? 'Speak in natural, clear Czech. Use a calm friendly female voice, slow A1 learner pace, precise Czech pronunciation, and natural pauses. Do not translate or add any words.'
        : 'Speak in natural, clear Czech. Use a calm friendly female voice, moderate A2 learner pace, precise Czech pronunciation, and natural pauses. Do not translate or add any words.'
    })
  });

  if (!response.ok) {
    throw new Error(`${question.id}: ${response.status} ${await response.text()}`);
  }

  await fs.writeFile(outputPath, Buffer.from(await response.arrayBuffer()));
}

// Switch the web app from browser speech synthesis to generated MP3 files.
const appPath = 'app.js';
let app = await fs.readFile(appPath, 'utf8');
app = app.replace(
  /function cancelSpeech\(\) \{[^\n]*\}/,
  "function cancelSpeech() { if ('speechSynthesis' in window) window.speechSynthesis.cancel(); speaking = false; if (window.__ltpAudio) { window.__ltpAudio.pause(); window.__ltpAudio.currentTime = 0; window.__ltpAudio = null; } }"
);

const mp3RenderAudio = `function renderAudio(q) {
  let box = $('#audioBox');
  if (!box) { box = document.createElement('div'); box.id = 'audioBox'; box.className = 'audio-box'; $('#prompt').before(box); }
  if (q.skill !== 'listening') { box.classList.add('hidden'); box.innerHTML = ''; return; }
  box.classList.remove('hidden');
  const used = state.plays[q.id] || 0;
  const max = q.maxPlays || 2;
  const left = Math.max(0, max - used);
  box.innerHTML = \`<div class="audio-icon">▶</div><div class="audio-copy"><strong>\${esc(t('listenHint'))}</strong><span>\${esc(t('playsLeft'))}: <b>\${left}</b> · AI Czech MP3</span></div><button id="playAudioBtn" class="audio-button" type="button" \${left === 0 ? 'disabled' : ''}>\${esc(t('play'))}</button>\`;
  $('#playAudioBtn')?.addEventListener('click', async () => {
    if ((state.plays[q.id] || 0) >= max || speaking) return;
    cancelSpeech();
    const audio = new Audio(\`./audio/cs/\${q.id}.mp3\`);
    window.__ltpAudio = audio;
    speaking = true;
    audio.onended = () => { speaking = false; window.__ltpAudio = null; renderAudio(q); };
    audio.onerror = () => { speaking = false; window.__ltpAudio = null; alert('AI audio file is unavailable. Run the Generate Czech AI audio workflow.'); renderAudio(q); };
    try {
      await audio.play();
      state.plays[q.id] = (state.plays[q.id] || 0) + 1;
      renderAudio(q);
    } catch (error) {
      speaking = false;
      window.__ltpAudio = null;
      alert('Audio playback could not start.');
    }
  });
}`;

app = app.replace(/function renderAudio\(q\) \{[\s\S]*?\n\}\n\nfunction renderQuestion/, `${mp3RenderAudio}\n\nfunction renderQuestion`);
await fs.writeFile(appPath, app);
console.log('Generated Czech MP3 files and enabled AI audio playback.');
