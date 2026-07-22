import fs from 'node:fs/promises';

const path = 'app.js';
let app = await fs.readFile(path, 'utf8');

const oldAnalyze = /async function analyzeRecording\(q\)\{[\s\S]*?\nfunction renderQuestion/;
const newAnalyze = `async function analyzeRecording(q){const rec=state.recordings[q.id];if(!rec?.blob||rec.durationSec<3||rec.blob.size<1500){alert('Запись пустая или слишком короткая.');return}const btn=$('#analyzeBtn');btn.disabled=true;btn.textContent=t('analyzing');let status=$('#submitStatus');if(!status){status=document.createElement('div');status.id='submitStatus';status.className='submit-status';btn.parentElement?.after(status)}status.textContent='Загрузка записи…';const fd=new FormData();const ext=rec.blob.type.includes('mp4')?'mp4':rec.blob.type.includes('ogg')?'ogg':'webm';fd.append('audio',rec.blob,\`reading.\${ext}\`);fd.append('candidateId',state.candidate.candidateId||state.candidate.email);fd.append('sessionId',state.sessionId);fd.append('questionId',q.id);fd.append('referenceText',q.passage);fd.append('durationSec',String(rec.durationSec));fd.append('level',q.level);const controller=new AbortController();const timeout=setTimeout(()=>controller.abort(),90000);try{status.textContent='AI распознаёт и оценивает чтение…';const r=await fetch(WORKER_URL,{method:'POST',body:fd,signal:controller.signal});const raw=await r.text();let data;try{data=JSON.parse(raw)}catch{throw Error(raw||\`HTTP \${r.status}\`)}if(!r.ok||!data.success)throw Error(data.details||data.error||\`HTTP \${r.status}\`);const score=Number(data.scores?.overall??data.scores?.readingAccuracy??0);if(!data.transcript?.trim())throw Error('Речь не распознана. Запишите чтение ещё раз.');state.answers[q.id]={correct:score>=60,score,scoreDetails:data.scores||{},transcript:data.transcript,recordingKey:data.recordingKey||'',answerText:\`\${score}%\`,answeredAt:new Date().toISOString()};status.textContent='Проверка завершена.';renderSpeaking(q)}catch(e){const message=e.name==='AbortError'?'Сервер не ответил за 90 секунд. Повторите отправку.':e.message;status.textContent=\`Ошибка: \${message}\`;alert(\`\${t('analysisFailed')} \${message}\`);btn.disabled=false;btn.textContent=t('analyze')}finally{clearTimeout(timeout)}}
function renderQuestion`;

if (!oldAnalyze.test(app)) {
  throw new Error('analyzeRecording block not found');
}

app = app.replace(oldAnalyze, newAnalyze);
await fs.writeFile(path, app);
console.log('Speaking submit fixed');
