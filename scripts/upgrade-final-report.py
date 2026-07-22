from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / 'index.html'
APP = ROOT / 'app.js'
CSS = ROOT / 'styles.css'


def patch_once(text: str, marker: str, replacement: str, label: str) -> str:
    if replacement in text:
        return text
    if marker not in text:
        raise RuntimeError(f'Marker not found: {label}')
    return text.replace(marker, replacement, 1)


def main():
    html = INDEX.read_text(encoding='utf-8')
    marker = '      <div id="metricGrid" class="metric-grid"></div>'
    replacement = '''      <div id="metricGrid" class="metric-grid"></div>
      <section class="panel final-summary-panel">
        <div class="final-summary-head">
          <div><span class="overline">LANGUAGE LEVEL</span><h2 id="confirmedLevelTitle">Ваш подтверждённый уровень</h2></div>
          <span id="assessmentConfidence" class="confidence-chip">—</span>
        </div>
        <p id="levelPlainExplanation" class="level-plain-explanation">—</p>
        <div class="final-columns">
          <div>
            <h3>Как сформирован результат</h3>
            <div id="levelBreakdown" class="level-breakdown"></div>
          </div>
          <div>
            <h3>Что это означает на практике</h3>
            <p id="practicalLevelDescription">—</p>
            <p id="nextLevelStatus" class="next-level-status">—</p>
          </div>
        </div>
      </section>
      <section class="panel ai-conclusion-panel">
        <div class="section-head"><div><span class="overline">AI ANALYSIS</span><h2>Итоговое заключение</h2></div><span id="aiConclusionStatus" class="confidence-chip">Анализ</span></div>
        <p id="aiConclusionText">Формируется итоговый разбор…</p>
        <div class="final-columns compact">
          <div><h3>Сильные стороны</h3><ul id="resultStrengths"></ul></div>
          <div><h3>Зоны роста</h3><ul id="resultWeaknesses"></ul></div>
        </div>
        <div class="next-step-box"><strong>Следующий шаг</strong><p id="personalNextStep">—</p></div>
        <small class="ai-note">Основной уровень рассчитывается по ответам и проходным порогам. AI только объясняет результат и не может самостоятельно повысить уровень.</small>
      </section>'''
    html = patch_once(html, marker, replacement, 'result metric grid')
    INDEX.write_text(html, encoding='utf-8')

    js = APP.read_text(encoding='utf-8')
    js_append = r'''

// Enhanced transparent final report v1
const LEVEL_DESCRIPTIONS={
A1:'Вы понимаете и используете самые простые фразы: представиться, сообщить основные данные, задать короткий вопрос и понять очень простую инструкцию.',
A2:'Вы справляетесь с привычными бытовыми ситуациями, понимаете короткие сообщения и можете поддержать простой разговор на знакомую тему.',
B1:'Вы можете общаться в большинстве повседневных и стандартных рабочих ситуаций, понимать основную мысль обычной речи и объяснять своё мнение простыми связными фразами.',
B2:'Вы можете достаточно уверенно работать и общаться на языке, понимать подробные тексты и разговоры, аргументировать позицию и участвовать в обсуждениях.',
C1:'Вы свободно понимаете сложную речь и тексты, гибко используете язык в работе и можете точно выражать сложные мысли.',
C2:'Вы почти без усилий понимаете сложную речь и тексты, точно передаёте оттенки смысла и уверенно используете язык в самых требовательных ситуациях.'
};
const SKILL_LABELS={grammar:'Грамматика',vocabulary:'Лексика',reading:'Чтение',listening:'Аудирование',speaking:'Чтение вслух'};
function pct(v){return Math.round((Number(v)||0)*100)}
function assessmentConfidence(report){const a=report.assessment||{},levels=Object.values(a.levelScores||{}),skills=Object.keys(a.skillScores||{}).length,q=report.session?.questions||0,r=a.reliability||0;let score=0;score+=Math.min(35,q*1.5);score+=Math.min(25,levels.length*8);score+=Math.min(20,skills*4);score+=Math.min(20,r*.2);if(score>=82)return{label:'Высокая уверенность',className:'high',score:Math.round(score)};if(score>=62)return{label:'Средняя уверенность',className:'medium',score:Math.round(score)};return{label:'Предварительный результат',className:'low',score:Math.round(score)}}
function inferredSkillBand(rate,finalLevel){const p=pct(rate),i=idx(finalLevel);if(p>=84)return LEVELS[Math.min(5,i+1)];if(p>=62)return finalLevel;return LEVELS[Math.max(0,i-1)]}
function buildLocalConclusion(report){const a=report.assessment||{},level=a.level||'A1',skills=a.skillScores||{},entries=Object.entries(skills).sort((x,y)=>(y[1].rate||0)-(x[1].rate||0)),strong=entries.slice(0,2),weak=[...entries].reverse().slice(0,2),next=LEVELS[Math.min(5,idx(level)+1)],top=strong.map(([s])=>SKILL_LABELS[s]).join(' и ').toLowerCase()||'основные задания',bottom=weak.map(([s])=>SKILL_LABELS[s]).join(' и ').toLowerCase()||'сложные задания';return{
summary:`Подтверждённый результат соответствует уровню ${level}. Сильнее всего проявились ${top}. Для устойчивого перехода к ${next} необходимо улучшить ${bottom}.`,
strengths:strong.map(([s,v])=>`${SKILL_LABELS[s]}: ${pct(v.rate)}%, ориентир ${inferredSkillBand(v.rate,level)}`),
weaknesses:weak.map(([s,v])=>`${SKILL_LABELS[s]}: ${pct(v.rate)}% — основная зона для практики`),
nextStep:level==='C2'?'Поддерживайте уровень регулярной практикой сложной профессиональной и разговорной речи.':`Сосредоточьтесь на заданиях ${next}, прежде всего на двух самых слабых навыках, и повторите проверку после периода практики.`,
source:'Расчётный анализ'
}}
async function requestAiConclusion(report){const fallback=buildLocalConclusion(report);try{const url=WORKER_URL.replace('/analyze-reading','/analyze-result');const controller=new AbortController(),timer=setTimeout(()=>controller.abort(),18000);const payload={language:report.candidate?.language,confirmedLevel:report.assessment?.level,targetLevel:report.candidate?.target,levelScores:report.assessment?.levelScores,skillScores:report.assessment?.skillScores,reliability:report.assessment?.reliability,route:report.session?.route,answers:(report.answers||[]).map(x=>({level:x.level,skill:x.skill,correct:x.correct,score:x.score,timeSec:x.timeSec}))};const r=await fetch(url,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(payload),signal:controller.signal});clearTimeout(timer);if(!r.ok)throw Error('AI endpoint unavailable');const data=await r.json();if(!data?.summary)throw Error('Invalid AI response');return{summary:String(data.summary),strengths:Array.isArray(data.strengths)?data.strengths:fallback.strengths,weaknesses:Array.isArray(data.weaknesses)?data.weaknesses:fallback.weaknesses,nextStep:String(data.nextStep||fallback.nextStep),source:'AI-заключение'}}catch{return fallback}}
function renderList(id,items){const el=$(id);if(el)el.innerHTML=(items||[]).map(x=>`<li>${esc(x)}</li>`).join('')||'<li>Недостаточно данных</li>'}
async function renderEnhancedFinalReport(){const report=state.report;if(!report?.assessment||!$('#levelBreakdown'))return;const a=report.assessment,level=a.level||'A1',next=LEVELS[Math.min(5,idx(level)+1)],conf=assessmentConfidence(report);$('#confirmedLevelTitle').textContent=`Ваш подтверждённый уровень: ${level}`;const chip=$('#assessmentConfidence');chip.textContent=`${conf.label} · ${conf.score}%`;chip.className=`confidence-chip ${conf.className}`;const levels=Object.entries(a.levelScores||{}).sort((x,y)=>idx(x[0])-idx(y[0]));$('#levelBreakdown').innerHTML=levels.map(([l,s])=>{const threshold=idx(l)>=3?72:65,passed=l===level||idx(l)<idx(level),status=passed&&pct(s.rate)>=threshold?'Подтверждён':pct(s.rate)>=threshold?'Пройден в маршруте':'Не подтверждён';return `<div class="level-row"><strong>${esc(l)}</strong><span>${pct(s.rate)}% · ${s.correct}/${s.total}</span><b class="${status==='Подтверждён'?'ok':'not-ok'}">${status}</b></div>`}).join('');const failed=levels.find(([l,s])=>idx(l)>idx(level)&&pct(s.rate)<(idx(l)>=3?72:65));$('#levelPlainExplanation').textContent=failed?`Уровень ${level} подтверждён. На следующей проверенной ступени ${failed[0]} получено ${pct(failed[1].rate)}%, поэтому она пока не подтверждена.`:`Самый высокий устойчиво пройденный уровень — ${level}. Результат основан на заданиях тех уровней, которые были открыты адаптивным маршрутом.`;$('#practicalLevelDescription').textContent=LEVEL_DESCRIPTIONS[level];$('#nextLevelStatus').textContent=level==='C2'?'Вы достигли верхней ступени шкалы CEFR в рамках этого теста.':`Следующий уровень в развитии: ${next}. Он не считается полученным, пока не пройден необходимый порог.`;const conclusion=await requestAiConclusion(report);$('#aiConclusionText').textContent=conclusion.summary;$('#aiConclusionStatus').textContent=conclusion.source;renderList('#resultStrengths',conclusion.strengths);renderList('#resultWeaknesses',conclusion.weaknesses);$('#personalNextStep').textContent=conclusion.nextStep}
const finalLevelObserver=new MutationObserver(()=>{if(!$('#resultScreen')?.classList.contains('hidden')&&state.report)renderEnhancedFinalReport()});const finalLevelNode=$('#finalLevel');if(finalLevelNode)finalLevelObserver.observe(finalLevelNode,{childList:true,characterData:true,subtree:true});
'''
    if '// Enhanced transparent final report v1' not in js:
        js += js_append
    APP.write_text(js, encoding='utf-8')

    css = CSS.read_text(encoding='utf-8')
    css_append = '''

/* Enhanced transparent final report */
.final-summary-panel,.ai-conclusion-panel{margin-top:20px}
.final-summary-head{display:flex;align-items:flex-start;justify-content:space-between;gap:20px;margin-bottom:12px}
.final-summary-head h2{margin:5px 0 0}
.confidence-chip{display:inline-flex;padding:8px 12px;border-radius:999px;background:#eef2ff;font-weight:700;font-size:13px;white-space:nowrap}
.confidence-chip.high{background:#e8f7ee;color:#17643a}.confidence-chip.medium{background:#fff5d9;color:#765400}.confidence-chip.low{background:#fff0f0;color:#8a2b2b}
.level-plain-explanation{font-size:17px;line-height:1.6;margin:0 0 20px}
.final-columns{display:grid;grid-template-columns:1fr 1fr;gap:24px}.final-columns.compact{margin-top:18px}
.final-columns h3{margin:0 0 10px;font-size:16px}.final-columns p{line-height:1.6}
.level-breakdown{display:grid;gap:9px}.level-row{display:grid;grid-template-columns:48px 1fr auto;align-items:center;gap:10px;padding:11px 12px;border:1px solid var(--border,#e4e7ec);border-radius:12px}.level-row span{color:var(--muted,#667085)}.level-row b{font-size:12px}.level-row .ok{color:#177245}.level-row .not-ok{color:#9b3a3a}
.next-level-status{padding:12px 14px;border-radius:12px;background:#f5f7fb;font-weight:600}
.ai-conclusion-panel>p{font-size:17px;line-height:1.65}.ai-conclusion-panel ul{margin:0;padding-left:20px;line-height:1.7}
.next-step-box{margin-top:18px;padding:15px 17px;border-radius:14px;background:#f5f7fb}.next-step-box p{margin:6px 0 0;line-height:1.6}.ai-note{display:block;margin-top:14px;color:var(--muted,#667085);line-height:1.5}
@media(max-width:760px){.final-columns{grid-template-columns:1fr}.final-summary-head{flex-direction:column}.level-row{grid-template-columns:42px 1fr}.level-row b{grid-column:2}}
'''
    if '/* Enhanced transparent final report */' not in css:
        css += css_append
    CSS.write_text(css, encoding='utf-8')
    print('Final report upgrade applied')


if __name__ == '__main__':
    main()
