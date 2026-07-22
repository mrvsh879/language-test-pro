const LEVELS=['A1','A2','B1','B2','C1','C2'];
const SKILL_LABELS={grammar:'Грамматика',vocabulary:'Лексика',reading:'Чтение'};
const $=s=>document.querySelector(s);
const state={candidate:null,bank:[],queue:[],current:0,answers:{},times:{},questionStartedAt:0,startedAt:0,tabSwitches:0,hiddenMs:0,hiddenAt:null,branches:0,report:null};

const screens={intro:$('#introScreen'),test:$('#testScreen'),result:$('#resultScreen')};
const shuffle=a=>{const x=[...a];for(let i=x.length-1;i>0;i--){const j=Math.floor(Math.random()*(i+1));[x[i],x[j]]=[x[j],x[i]]}return x};
const fmt=s=>`${String(Math.floor(s/60)).padStart(2,'0')}:${String(s%60).padStart(2,'0')}`;
const clamp=(n,a,b)=>Math.max(a,Math.min(b,n));
const levelIndex=l=>LEVELS.indexOf(l);

async function loadBank(){
  const response=await fetch('./data/de.json',{cache:'no-store'});
  if(!response.ok) throw new Error(`Не удалось загрузить банк вопросов: ${response.status}`);
  const data=await response.json();
  state.bank=data.questions.map(q=>({...q,options:shuffle(q.options.map((text,index)=>({text,correct:index===q.answer}))).map((item,index,arr)=>({text:item.text,correct:item.correct,index}))}));
}

function levelQuestions(level){return shuffle(state.bank.filter(q=>q.level===level));}
function addLevel(level){
  const existing=new Set(state.queue.map(q=>q.id));
  state.queue.push(...levelQuestions(level).filter(q=>!existing.has(q.id)));
}
function startRoute(){state.queue=[];addLevel('B1');}

function saveQuestionTime(){
  const q=state.queue[state.current];
  if(!q||!state.questionStartedAt)return;
  state.times[q.id]=(state.times[q.id]||0)+Math.max(0,Math.round((Date.now()-state.questionStartedAt)/1000));
  state.questionStartedAt=Date.now();
}
function blockStats(level){
  const qs=state.queue.filter(q=>q.level===level);
  const answered=qs.filter(q=>state.answers[q.id]);
  const correct=answered.filter(q=>state.answers[q.id].correct).length;
  return {total:qs.length,answered:answered.length,correct,rate:answered.length?correct/answered.length:0};
}
function maybeExtendRoute(){
  if(state.current!==state.queue.length-1||state.branches>=2)return false;
  const currentLevel=state.queue[state.current].level;
  const stats=blockStats(currentLevel);
  let next;
  if(stats.rate>=.8) next=LEVELS[clamp(levelIndex(currentLevel)+1,0,LEVELS.length-1)];
  else if(stats.rate<=.4) next=LEVELS[clamp(levelIndex(currentLevel)-1,0,LEVELS.length-1)];
  else return false;
  if(next===currentLevel||state.queue.some(q=>q.level===next))return false;
  addLevel(next);state.branches++;return true;
}

function showScreen(name){Object.values(screens).forEach(x=>x.classList.add('hidden'));screens[name].classList.remove('hidden')}
function renderQuestion(){
  const q=state.queue[state.current];
  if(!q)return finishTest();
  $('#questionCounter').textContent=`Вопрос ${state.current+1} из ${state.queue.length}`;
  $('#sectionLabel').textContent=state.current<5?'Диагностический блок':'Адаптивный блок';
  $('#skillTag').textContent=SKILL_LABELS[q.skill]||q.skill;
  $('#prompt').textContent=q.prompt;
  const passage=$('#passage');
  passage.textContent=q.passage||'';passage.classList.toggle('hidden',!q.passage);
  const host=$('#options');host.innerHTML='';
  q.options.forEach((opt,index)=>{
    const label=document.createElement('label');label.className='option';
    const checked=state.answers[q.id]?.optionIndex===index;
    if(checked)label.classList.add('selected');
    label.innerHTML=`<input type="radio" name="answer" value="${index}" ${checked?'checked':''}><span>${escapeHtml(opt.text)}</span>`;
    label.addEventListener('click',()=>{document.querySelectorAll('.option').forEach(x=>x.classList.remove('selected'));label.classList.add('selected');state.answers[q.id]={optionIndex:index,correct:opt.correct,answeredAt:new Date().toISOString()}});
    host.appendChild(label);
  });
  $('#progressBar').style.width=`${((state.current+1)/state.queue.length)*100}%`;
  $('#prevBtn').disabled=state.current===0;
  $('#nextBtn').textContent=state.current===state.queue.length-1?'Завершить блок':'Далее';
  state.questionStartedAt=Date.now();
}
function escapeHtml(value){return String(value).replace(/[&<>'"]/g,ch=>({'&':'&amp;','<':'&lt;','>':'&gt;',"'":'&#39;','"':'&quot;'}[ch]))}

$('#candidateForm').addEventListener('submit',async event=>{
  event.preventDefault();
  const data=Object.fromEntries(new FormData(event.currentTarget));
  state.candidate={name:data.name.trim(),email:data.email.trim(),position:data.position.trim(),candidateId:data.candidateId.trim(),language:data.language,target:data.target};
  try{await loadBank()}catch(error){alert(error.message);return}
  startRoute();state.startedAt=Date.now();state.questionStartedAt=Date.now();
  $('#sessionStatus').textContent=`Кандидат: ${state.candidate.name}`;
  showScreen('test');renderQuestion();startTimer();
});

$('#prevBtn').addEventListener('click',()=>{saveQuestionTime();if(state.current>0){state.current--;renderQuestion()}});
$('#nextBtn').addEventListener('click',()=>{
  const q=state.queue[state.current];
  if(!state.answers[q.id]){alert('Выберите ответ перед продолжением.');return}
  saveQuestionTime();
  if(state.current===state.queue.length-1){
    if(maybeExtendRoute()){state.current++;renderQuestion()}else finishTest();
  }else{state.current++;renderQuestion()}
});

document.addEventListener('visibilitychange',()=>{
  if(document.visibilityState==='hidden'){state.tabSwitches++;state.hiddenAt=Date.now()}
  else if(state.hiddenAt){state.hiddenMs+=Date.now()-state.hiddenAt;state.hiddenAt=null}
});
let timerHandle;
function startTimer(){clearInterval(timerHandle);timerHandle=setInterval(()=>{$('#timer').textContent=fmt(Math.floor((Date.now()-state.startedAt)/1000))},1000)}

function calculateReport(){
  const answeredQuestions=state.queue.filter(q=>state.answers[q.id]);
  const byLevel={};const bySkill={grammar:[],vocabulary:[],reading:[]};
  for(const q of answeredQuestions){
    (byLevel[q.level]??=[]).push(state.answers[q.id].correct);
    (bySkill[q.skill]??=[]).push(state.answers[q.id].correct);
  }
  const levelScores=Object.fromEntries(Object.entries(byLevel).map(([level,arr])=>[level,{correct:arr.filter(Boolean).length,total:arr.length,rate:arr.filter(Boolean).length/arr.length}]));
  const skillScores=Object.fromEntries(Object.entries(bySkill).map(([skill,arr])=>[skill,{correct:arr.filter(Boolean).length,total:arr.length,rate:arr.length?arr.filter(Boolean).length/arr.length:0}]));
  const testedLevels=Object.keys(levelScores).sort((a,b)=>levelIndex(a)-levelIndex(b));
  let finalLevel='A1';
  for(const level of testedLevels){if(levelScores[level].rate>=.6)finalLevel=level}
  const finalRate=levelScores[finalLevel]?.rate||0;
  const lower=LEVELS[clamp(levelIndex(finalLevel)-(finalRate<.7?1:0),0,5)];
  const upper=LEVELS[clamp(levelIndex(finalLevel)+(finalRate>=.8?1:0),0,5)];
  const totalSec=Math.floor((Date.now()-state.startedAt)/1000);
  const fastAnswers=answeredQuestions.filter(q=>(state.times[q.id]||0)<3).length;
  const accuracy=answeredQuestions.length?answeredQuestions.filter(q=>state.answers[q.id].correct).length/answeredQuestions.length:0;
  let reliability=100-state.tabSwitches*8-fastAnswers*5-Math.floor(state.hiddenMs/60000)*3;
  reliability=clamp(reliability,35,100);
  const targetIdx=levelIndex(state.candidate.target),finalIdx=levelIndex(finalLevel);
  let recommendation;
  if(reliability<65)recommendation='Результат требует повторного прохождения под наблюдением или подтверждения на разговорном интервью.';
  else if(finalIdx>=targetIdx)recommendation=`Кандидат достиг целевого уровня ${state.candidate.target}. Рекомендуется допустить к разговорному интервью и проверить устную речь.`;
  else if(finalIdx===targetIdx-1)recommendation=`Кандидат находится рядом с целевым уровнем ${state.candidate.target}. Рекомендуется короткое интервью с рабочими сценариями.`;
  else recommendation=`Текущий результат заметно ниже целевого уровня ${state.candidate.target}. Для этой вакансии потребуется дополнительное обучение.`;
  return {generatedAt:new Date().toISOString(),candidate:state.candidate,assessment:{level:finalLevel,range:lower===upper?finalLevel:`${lower}–${upper}`,accuracy,levelScores,skillScores,reliability,recommendation},session:{totalSec,questions:answeredQuestions.length,tabSwitches:state.tabSwitches,hiddenSec:Math.round(state.hiddenMs/1000),fastAnswers,route:[...new Set(state.queue.map(q=>q.level))]},answers:answeredQuestions.map(q=>({id:q.id,level:q.level,skill:q.skill,correct:state.answers[q.id].correct,timeSec:state.times[q.id]||0}))};
}

function finishTest(){saveQuestionTime();clearInterval(timerHandle);state.report=calculateReport();renderResult();showScreen('result')}
function renderResult(){
  const r=state.report;$('#resultName').textContent=r.candidate.name;$('#resultMeta').textContent=`${r.candidate.position} · ${r.candidate.email} · цель ${r.candidate.target}`;
  $('#finalLevel').textContent=r.assessment.level;$('#confidenceRange').textContent=`Диапазон: ${r.assessment.range}`;
  const metrics=[['Общая точность',`${Math.round(r.assessment.accuracy*100)}%`],['Надёжность',`${r.assessment.reliability}%`],['Время',fmt(r.session.totalSec)],['Вопросов',r.session.questions]];
  $('#metricGrid').innerHTML=metrics.map(([label,value])=>`<div class="metric"><span>${label}</span><strong>${value}</strong></div>`).join('');
  $('#skillProfile').innerHTML=Object.entries(r.assessment.skillScores).map(([skill,data])=>`<div class="bar-row"><div class="bar-label"><span>${SKILL_LABELS[skill]}</span><strong>${Math.round(data.rate*100)}%</strong></div><div class="mini-bar"><div style="width:${Math.round(data.rate*100)}%"></div></div></div>`).join('');
  const risks=[['Уходы со вкладки',r.session.tabSwitches],['Вне вкладки',`${r.session.hiddenSec} сек.`],['Ответы быстрее 3 сек.',r.session.fastAnswers],['Маршрут уровней',r.session.route.join(' → ')]];
  $('#riskProfile').innerHTML=risks.map(([label,value])=>`<div class="risk-item"><span>${label}</span><strong>${value}</strong></div>`).join('');
  $('#recommendation').textContent=r.assessment.recommendation;
}

$('#printBtn').addEventListener('click',()=>window.print());
$('#downloadBtn').addEventListener('click',()=>{
  const blob=new Blob([JSON.stringify(state.report,null,2)],{type:'application/json'});const url=URL.createObjectURL(blob);const a=document.createElement('a');a.href=url;a.download=`language-test-${state.candidate.name.replace(/\s+/g,'-').toLowerCase()}.json`;a.click();setTimeout(()=>URL.revokeObjectURL(url),1000)
});
$('#restartBtn').addEventListener('click',()=>location.reload());
