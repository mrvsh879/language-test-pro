import fs from 'node:fs/promises';

const path = 'app.js';
let app = await fs.readFile(path, 'utf8');

const oldRender = /function renderSpeaking\(q\)\{[\s\S]*?\nasync function startRecording\(q\)\{/;
const newRender = `function renderSpeaking(q){let box=$('#speakingBox');if(!box){box=document.createElement('div');box.id='speakingBox';box.className='speaking-box';$('#options').before(box)}if(q.skill!=='speaking'){box.classList.add('hidden');box.innerHTML='';return}box.classList.remove('hidden');const rec=state.recordings[q.id],ans=state.answers[q.id],isRecording=recorder?.state==='recording';box.innerHTML=\`<div class="speaking-head"><div><strong>\${esc(t('readAloudHint'))}</strong><span id="recordStatus">\${ans?esc(t('analysisDone')):rec?.blob?esc(t('recordReady')):isRecording?esc(t('recording')):''}</span></div><b id="recordClock">\${rec?.durationSec?fmt(rec.durationSec):'00:00'}</b></div><div class="record-actions"><button id="recordBtn" class="record-button \${isRecording?'recording':''}" type="button">\${esc(isRecording?t('stop'):t('record'))}</button><button id="previewBtn" class="secondary" type="button" \${rec?.blob?'':'disabled'}>\${esc(t('preview'))}</button><button id="analyzeBtn" class="primary" type="button" \${rec?.blob&&!ans?'':'disabled'}>\${esc(t('analyze'))}</button></div><div id="analysisResult" class="analysis-result \${ans?'':'hidden'}">\${ans?\`<strong>\${esc(t('readingAccuracy'))}: \${ans.score}%</strong><p><b>\${esc(t('transcript'))}:</b> \${esc(ans.transcript)}</p>\`:''}</div>\`;
$('#recordBtn').addEventListener('click',()=>{if(recorder?.state==='recording'){stopRecording()}else{startRecording(q)}});$('#previewBtn').addEventListener('click',()=>previewRecording(q));$('#analyzeBtn').addEventListener('click',()=>analyzeRecording(q))}
function stopRecording(){if(recorder?.state==='recording'){try{recorder.requestData()}catch{}setTimeout(()=>{if(recorder?.state==='recording')recorder.stop()},120)}}
async function startRecording(q){`;

if (!oldRender.test(app)) throw new Error('Recorder block was not found');
app = app.replace(oldRender, newRender);

const oldStart = /async function startRecording\(q\)\{[\s\S]*?\nfunction previewRecording\(q\)\{/;
const newStart = `async function startRecording(q){if(!navigator.mediaDevices?.getUserMedia||!window.MediaRecorder){alert(t('micDenied'));return}try{cancelMedia();const previous=state.recordings[q.id];if(previous?.url)URL.revokeObjectURL(previous.url);delete state.recordings[q.id];delete state.answers[q.id];recordStream=await navigator.mediaDevices.getUserMedia({audio:{echoCancellation:true,noiseSuppression:true,autoGainControl:true}});const chunks=[],mime=preferredMime();const activeRecorder=new MediaRecorder(recordStream,mime?{mimeType:mime}:undefined);recorder=activeRecorder;activeRecorder.ondataavailable=e=>{if(e.data&&e.data.size>0)chunks.push(e.data)};activeRecorder.onerror=()=>{recordStream?.getTracks().forEach(x=>x.stop());recordStream=null;clearInterval(recordTimer);alert(t('analysisFailed'))};activeRecorder.onstop=()=>{const durationSec=Math.max(0,Math.round((Date.now()-recordStarted)/1000));const actualType=activeRecorder.mimeType||chunks.find(x=>x.type)?.type||'audio/webm';const blob=new Blob(chunks,{type:actualType});recordStream?.getTracks().forEach(x=>x.stop());recordStream=null;clearInterval(recordTimer);recorder=null;if(durationSec<3||blob.size<1500){alert(ui==='uk'?'Запис занадто короткий або порожній. Запишіть щонайменше 3 секунди.':ui==='en'?'The recording is too short or empty. Record at least 3 seconds.':'Запись слишком короткая или пустая. Запишите минимум 3 секунды.');renderSpeaking(q);return}const url=URL.createObjectURL(blob);state.recordings[q.id]={blob,url,durationSec,mimeType:actualType,size:blob.size};renderSpeaking(q)};activeRecorder.start(500);recordStarted=Date.now();renderSpeaking(q);recordTimer=setInterval(()=>{const sec=Math.floor((Date.now()-recordStarted)/1000);const clock=$('#recordClock');if(clock)clock.textContent=fmt(sec);if(sec>=q.maxDurationSec)stopRecording()},250)}catch(e){recordStream?.getTracks().forEach(x=>x.stop());recordStream=null;recorder=null;alert(t('micDenied'))}}
function previewRecording(q){`;

if (!oldStart.test(app)) throw new Error('startRecording block was not found');
app = app.replace(oldStart, newStart);

app = app.replace(
  /function previewRecording\(q\)\{[^\n]*\}/,
  `function previewRecording(q){const rec=state.recordings[q.id];if(!rec?.blob||rec.blob.size<1500)return;cancelMedia();const a=new Audio();window.__ltpAudio=a;a.preload='auto';a.src=rec.url;a.onended=()=>{window.__ltpAudio=null};a.onerror=()=>alert(ui==='uk'?'Браузер не зміг відтворити запис. Запишіть ще раз.':ui==='en'?'The browser could not play this recording. Record it again.':'Браузер не смог воспроизвести запись. Запишите её ещё раз.');a.play().catch(()=>alert(ui==='uk'?'Не вдалося запустити відтворення.':ui==='en'?'Playback could not start.':'Не удалось запустить воспроизведение.'))}`
);

app = app.replace(
  `async function analyzeRecording(q){const rec=state.recordings[q.id];if(!rec)return;`,
  `async function analyzeRecording(q){const rec=state.recordings[q.id];if(!rec?.blob||rec.durationSec<3||rec.blob.size<1500){alert(ui==='uk'?'Запис порожній або занадто короткий.':ui==='en'?'The recording is empty or too short.':'Запись пустая или слишком короткая.');return;}`
);

await fs.writeFile(path, app);
console.log('Recorder fixed');
