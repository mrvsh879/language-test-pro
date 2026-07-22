import fs from 'node:fs/promises';

const path = 'app.js';
let app = await fs.readFile(path, 'utf8');

app = app.replace(
  "preview:'Прослушать запись',analyze:'Отправить на проверку'",
  "preview:'Прослушать запись',textMatch:'Совпадение текста',completeness:'Полнота',recognitionConfidence:'Уверенность распознавания',pace:'Темп',wordsPerMinute:'Слов в минуту',analyze:'Отправить на проверку'"
);
app = app.replace(
  "preview:'Прослухати запис',analyze:'Надіслати на перевірку'",
  "preview:'Прослухати запис',textMatch:'Збіг тексту',completeness:'Повнота',recognitionConfidence:'Впевненість розпізнавання',pace:'Темп',wordsPerMinute:'Слів за хвилину',analyze:'Надіслати на перевірку'"
);
app = app.replace(
  "preview:'Play recording',analyze:'Send for analysis'",
  "preview:'Play recording',textMatch:'Text match',completeness:'Completeness',recognitionConfidence:'Recognition confidence',pace:'Pace',wordsPerMinute:'Words per minute',analyze:'Send for analysis'"
);

const oldRender = /function renderSpeaking\(q\)\{[\s\S]*?\nfunction stopRecording\(\)\{/;
const newRender = `function renderSpeaking(q){let box=$('#speakingBox');if(!box){box=document.createElement('div');box.id='speakingBox';box.className='speaking-box';$('#options').before(box)}if(q.skill!=='speaking'){box.classList.add('hidden');box.innerHTML='';return}box.classList.remove('hidden');const rec=state.recordings[q.id],ans=state.answers[q.id],isRecording=recorder?.state==='recording';const scoreRows=ans?.scores?\`<div class="score-grid"><div><span>\${esc(t('textMatch'))}</span><b>\${ans.scores.textMatch}%</b></div><div><span>\${esc(t('completeness'))}</span><b>\${ans.scores.completeness}%</b></div><div><span>\${esc(t('recognitionConfidence'))}</span><b>\${ans.scores.recognitionConfidence}%</b></div><div><span>\${esc(t('pace'))}</span><b>\${ans.scores.pace}%</b></div></div><p><b>\${esc(t('wordsPerMinute'))}:</b> \${ans.scores.wordsPerMinute}</p>\`:'';box.innerHTML=\`<div class="speaking-head"><div><strong>\${esc(t('readAloudHint'))}</strong><span id="recordStatus">\${ans?esc(t('analysisDone')):rec?.blob?esc(t('recordReady')):isRecording?esc(t('recording')):''}</span></div><b id="recordClock">\${rec?.durationSec?fmt(rec.durationSec):'00:00'}</b></div><div class="record-actions"><button id="recordBtn" class="record-button \${isRecording?'recording':''}" type="button">\${esc(isRecording?t('stop'):t('record'))}</button><button id="analyzeBtn" class="primary" type="button" \${rec?.blob&&!ans?'':'disabled'}>\${esc(t('analyze'))}</button></div>\${rec?.url?\`<audio id="recordPreview" class="record-preview" controls preload="metadata" src="\${rec.url}"></audio>\`:''}<div id="analysisResult" class="analysis-result \${ans?'':'hidden'}">\${ans?\`<strong>\${esc(t('readingAccuracy'))}: \${ans.score}%</strong>\${scoreRows}<p><b>\${esc(t('transcript'))}:</b> \${esc(ans.transcript)}</p>\`:''}</div>\`;
$('#recordBtn').addEventListener('click',()=>{if(recorder?.state==='recording'){stopRecording()}else{startRecording(q)}});$('#analyzeBtn').addEventListener('click',()=>analyzeRecording(q))}
function stopRecording(){`;
if (!oldRender.test(app)) throw new Error('renderSpeaking block not found');
app = app.replace(oldRender, newRender);

app = app.replace(/function previewRecording\(q\)\{[^\n]*\}\n/, '');

const oldAnalyze = /async function analyzeRecording\(q\)\{[\s\S]*?\nfunction renderQuestion/;
const newAnalyze = `async function analyzeRecording(q){const rec=state.recordings[q.id];if(!rec?.blob||rec.durationSec<3||rec.blob.size<1500){alert(ui==='uk'?'Запис порожній або занадто короткий.':ui==='en'?'The recording is empty or too short.':'Запись пустая или слишком короткая.');return}const btn=$('#analyzeBtn');btn.disabled=true;btn.textContent=t('analyzing');const fd=new FormData();fd.append('audio',rec.blob,\`reading.\${rec.blob.type.includes('mp4')?'mp4':rec.blob.type.includes('ogg')?'ogg':'webm'}\`);fd.append('candidateId',state.candidate.candidateId||state.candidate.email);fd.append('sessionId',state.sessionId);fd.append('questionId',q.id);fd.append('referenceText',q.passage);fd.append('level',q.level);fd.append('durationSec',String(rec.durationSec));try{const r=await fetch(WORKER_URL,{method:'POST',body:fd});const data=await r.json();if(!r.ok||!data.success)throw Error(data.details||data.error||'Analysis failed');const transcript=String(data.transcript||'').trim();if(!transcript)throw Error(ui==='uk'?'Мову не розпізнано. Запишіть ще раз.':ui==='en'?'No speech was recognized. Record again.':'Речь не распознана. Запишите ещё раз.');const scores=data.scores||{};const score=Number(scores.overall??scores.readingAccuracy??0);state.answers[q.id]={correct:score>=60,score,scores:{textMatch:Number(scores.textMatch??score),completeness:Number(scores.completeness??score),recognitionConfidence:Number(scores.recognitionConfidence??0),pace:Number(scores.pace??0),wordsPerMinute:Number(scores.wordsPerMinute??0)},transcript,recordingKey:data.recordingKey||'',answerText:\`\${score}%\`,answeredAt:new Date().toISOString()};renderSpeaking(q)}catch(e){delete state.answers[q.id];alert(\`\${t('analysisFailed')} \${e.message}\`);renderSpeaking(q)}}
function renderQuestion`;
if (!oldAnalyze.test(app)) throw new Error('analyzeRecording block not found');
app = app.replace(oldAnalyze, newAnalyze);

app = app.replace(
  "score:state.answers[q.id].score??null,timeSec:",
  "score:state.answers[q.id].score??null,scores:state.answers[q.id].scores||null,timeSec:"
);

app = app.replace(
  /a\.skill==='speaking'\?`<p><strong>\$\{esc\(t\('readingAccuracy'\)\)\}:<\/strong> \$\{a\.score\}%<\/p><p><strong>\$\{esc\(t\('transcript'\)\)\}:<\/strong> \$\{esc\(a\.transcript\)\}<\/p>`/,
  "a.skill==='speaking'?`<p><strong>${esc(t('readingAccuracy'))}:</strong> ${a.score}%</p>${a.scores?`<p>${esc(t('textMatch'))}: ${a.scores.textMatch}% · ${esc(t('completeness'))}: ${a.scores.completeness}% · ${esc(t('recognitionConfidence'))}: ${a.scores.recognitionConfidence}% · ${esc(t('pace'))}: ${a.scores.pace}%</p>`:''}<p><strong>${esc(t('transcript'))}:</strong> ${esc(a.transcript)}</p>`"
);

await fs.writeFile(path, app);
console.log('Speaking result UI improved');
