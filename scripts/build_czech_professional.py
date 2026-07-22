from __future__ import annotations
import json
from collections import Counter
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/'data'
APP=ROOT/'app.js'
LEVELS=['A1','A2','B1','B2','C1','C2']

def read(name):
    return json.loads((DATA/name).read_text(encoding='utf-8'))

def validate(items,skill=None):
    ids=[q['id'] for q in items]
    if len(ids)!=len(set(ids)): raise ValueError('Duplicate IDs')
    for q in items:
        if q['level'] not in LEVELS: raise ValueError(f"Bad level {q['id']}")
        if skill and q['skill']!=skill: raise ValueError(f"Bad skill {q['id']}")
        if q['skill']!='speaking':
            if len(q.get('options',[]))!=4 or not isinstance(q.get('answer'),int): raise ValueError(f"Bad options {q['id']}")

def write(name,items,count):
    (DATA/name).write_text(json.dumps({'language':'cs','version':'3.0.0-professional','questionCount':count,'questions':items},ensure_ascii=False,separators=(',',':')),encoding='utf-8')

def main():
    ordinary=read('cs.json')['questions']
    for q in ordinary:
        if q['id']=='cs-a2-g-05':
            q.update({'prompt':'Zítra ___ babičku.','options':['navštívím','budu navštívit','navštěvoval jsem','navštívil bych'],'answer':0,'explanation':'Pro jednorázový budoucí děj se používá dokonavý tvar „navštívím“.'})
    validate(ordinary)
    counts=Counter(q['level'] for q in ordinary)
    if any(counts[x]!=20 for x in LEVELS): raise ValueError(f'Expected 20 per level: {counts}')

    listening=read('cs-listening.json')['questions']+read('cs-professional-listening-b1-c2.json')['questions']
    speaking=read('cs-speaking.json')['questions']+read('cs-professional-speaking-b1-c2.json')['questions']
    validate(listening,'listening'); validate(speaking,'speaking')
    lc=Counter(q['level'] for q in listening); sc=Counter(q['level'] for q in speaking)
    if any(lc[x]<4 for x in LEVELS): raise ValueError(f'Listening incomplete: {lc}')
    if any(sc[x]<2 for x in LEVELS): raise ValueError(f'Speaking incomplete: {sc}')

    write('cs.json',ordinary,len(ordinary)); write('cs-listening.json',listening,len(listening)); write('cs-speaking.json',speaking,len(speaking))

    text=APP.read_text(encoding='utf-8')
    old="if(state.candidate.language==='cs'){state.queue.push(...shuffle(state.bank.filter(q=>q.skill==='listening'&&['A1','A2'].includes(q.level))).slice(0,4));state.queue.push(...shuffle(state.bank.filter(q=>q.skill==='speaking'&&['A1','A2'].includes(q.level))).slice(0,2))}else if(state.candidate.language==='de')"
    new="if(state.candidate.language==='cs'){const targetIndex=idx(state.candidate.target),oralLevels=[LEVELS[targetIndex],LEVELS[clamp(targetIndex-1,0,5)]],listenPool=state.bank.filter(q=>q.skill==='listening'&&oralLevels.includes(q.level)),speakPool=state.bank.filter(q=>q.skill==='speaking'&&oralLevels.includes(q.level));state.queue.push(...shuffle(listenPool).slice(0,6));state.queue.push(...shuffle(speakPool).slice(0,3))}else if(state.candidate.language==='de')"
    if old not in text and new not in text: raise ValueError('Czech route signature not found')
    text=text.replace(old,new)
    text=text.replace("if(state.candidate.language==='de'&&idx(finalLevel)>=3)","if(['cs','de'].includes(state.candidate.language)&&idx(finalLevel)>=3)")
    APP.write_text(text,encoding='utf-8')
    print('Czech professional build complete',len(ordinary),len(listening),len(speaking),dict(lc),dict(sc))

if __name__=='__main__': main()
