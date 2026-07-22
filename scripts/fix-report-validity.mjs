import fs from 'node:fs/promises';

const path = 'app.js';
let app = await fs.readFile(path, 'utf8');

function mustReplace(search, replacement, label) {
  if (!app.includes(search)) throw new Error(`${label} not found`);
  app = app.replace(search, replacement);
}

mustReplace(
  "for(const q of answered){(byLevel[q.level]??=[]).push(state.answers[q.id].correct);(bySkill[q.skill]??=[]).push(q.skill==='speaking'?(state.answers[q.id].score||0)/100:(state.answers[q.id].correct?1:0))}",
  "for(const q of answered){if(q.skill!=='speaking')(byLevel[q.level]??=[]).push(state.answers[q.id].correct);(bySkill[q.skill]??=[]).push(q.skill==='speaking'?(state.answers[q.id].score||0)/100:(state.answers[q.id].correct?1:0))}",
  'level scoring loop',
);

mustReplace(
  "accuracy=answered.length?answered.filter(q=>state.answers[q.id].correct).length/answered.length:0,reliability=clamp(100-state.tabSwitches*8-fast*5-Math.floor(state.hiddenMs/60000)*3,35,100);",
  "scoredAnswers=answered.filter(q=>q.skill!=='speaking'),accuracy=scoredAnswers.length?scoredAnswers.filter(q=>state.answers[q.id].correct).length/scoredAnswers.length:0,reliability=clamp(100-state.tabSwitches*8-fast*5-Math.floor(state.hiddenMs/60000)*3,35,100),validResult=reliability>=65&&fast<=Math.max(3,Math.floor(scoredAnswers.length*.3));",
  'accuracy calculation',
);

mustReplace(
  "assessment:{level:finalLevel,range:lower===upper?finalLevel:`${lower}–${upper}`,accuracy,levelScores,skillScores,reliability,recommendation}",
  "assessment:{level:finalLevel,range:lower===upper?finalLevel:`${lower}–${upper}`,accuracy,levelScores,skillScores,reliability,recommendation,validResult}",
  'assessment object',
);

mustReplace(
  "$('#finalLevel').textContent=r.assessment.level;$('#confidenceRange').textContent=`${t('range')}: ${r.assessment.range}`;",
  "$('#finalLevel').textContent=r.assessment.validResult?r.assessment.level:'—';$('#confidenceRange').textContent=r.assessment.validResult?`${t('range')}: ${r.assessment.range}`:'Результат недостоверен';",
  'result level display',
);

mustReplace(
  "<p><strong>${esc(t('readingAccuracy'))}:</strong> ${a.score}%</p><p><strong>${esc(t('transcript'))}:</strong> ${esc(a.transcript)}</p>",
  "<p><strong>Распознаваемость чтения:</strong> ${a.score}%</p><p><strong>${esc(t('transcript'))}:</strong> ${esc(a.transcript)}</p>${a.scoreDetails?`<p><strong>Совпадение текста:</strong> ${a.scoreDetails.textMatch??'—'}% · <strong>Полнота:</strong> ${a.scoreDetails.completeness??'—'}% · <strong>Понятность для распознавателя:</strong> ${a.scoreDetails.recognitionConfidence??'—'}% · <strong>Темп:</strong> ${a.scoreDetails.pace??'—'}%</p><p><small>Этот показатель не является оценкой акцента, ударения или фонетики.</small></p>`:''}",
  'speaking review block',
);

mustReplace(
  "score:state.answers[q.id].score??null,timeSec:",
  "score:state.answers[q.id].score??null,scoreDetails:state.answers[q.id].scoreDetails||null,timeSec:",
  'report score details',
);

await fs.writeFile(path, app);
console.log('Report validity corrected');
