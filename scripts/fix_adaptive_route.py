from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / 'app.js'
DATA = ROOT / 'data'


def replace_once(text: str, pattern: str, replacement: str, label: str) -> str:
    updated, count = re.subn(pattern, replacement, text, count=1)
    if count != 1:
        raise ValueError(f'{label}: expected one match, got {count}')
    return updated


def fix_route() -> None:
    text = APP.read_text(encoding='utf-8')

    text = replace_once(
        text,
        r"function addLevel\(level\)\{if\(!state\.visitedLevels\.includes\(level\)\)state\.visitedLevels\.push\(level\);state\.queue\.push\(\.\.\.sampleLevel\(level\)\);renderRoute\(\)\}",
        "function addLevel(level){if(!state.visitedLevels.includes(level))state.visitedLevels.push(level);state.queue.push(...sampleLevel(level));if(['cs','de'].includes(state.candidate?.language)){const speakingPool=state.bank.filter(q=>q.skill==='speaking'&&q.level===level&&!state.queue.some(x=>x.id===q.id));if(speakingPool.length)state.queue.push(shuffle(speakingPool)[0])}renderRoute()}",
        'addLevel',
    )

    text = replace_once(
        text,
        r"function startRoute\(\)\{state\.queue=\[\];state\.visitedLevels=\[\];addLevel\('B1'\);if\(state\.candidate\.language==='cs'\)\{.*?\}\}",
        "function startRoute(){state.queue=[];state.visitedLevels=[];const targetIndex=idx(state.candidate.target);const startIndex=targetIndex<=1?0:targetIndex===2?1:2;addLevel(LEVELS[startIndex])}",
        'startRoute',
    )

    APP.write_text(text, encoding='utf-8')


def simplify_json(path: Path, replacements: dict[str, str]) -> None:
    if not path.exists():
        return
    data = json.loads(path.read_text(encoding='utf-8'))
    raw = json.dumps(data, ensure_ascii=False)
    for old, new in replacements.items():
        raw = raw.replace(old, new)
    path.write_text(raw, encoding='utf-8')


def simplify_language() -> None:
    cs = {
        'nezpochybnitelně': 'zcela přesvědčivě',
        'pouhou inscenaci': 'pouhou ukázku',
        'ztotožňovat se spravedlností': 'automaticky považovat za spravedlnost',
        'neslučitelné cíle': 'cíle, které nejdou spojit',
        'vyžadují přesnější vymezení': 'vyžadují přesnější vysvětlení',
        'základní problém motivace': 'hlavní problém motivace',
        'Formálně stejné pravidlo': 'Stejné pravidlo',
        'výchozí podmínky': 'počáteční podmínky',
    }
    de = {
        'unanfechtbar': 'völlig überzeugend',
        'zur Inszenierung': 'zu einer bloßen Darstellung',
        'zugrunde liegende Anreizproblem': 'eigentliche Motivationsproblem',
        'ohne Weiteres mit Gerechtigkeit gleichzusetzen': 'nicht automatisch als gerecht anzusehen',
        'unvereinbare Ziele': 'Ziele, die nicht zusammenpassen',
        'zentrale Konflikte vertagt werden': 'wichtige Konflikte auf später verschoben werden',
        'dessen Reichweite': 'seine Gültigkeit',
        'differenziertere Bewertung': 'genauere Bewertung',
    }

    for name in [
        'cs.json', 'cs-listening.json', 'cs-speaking.json',
        'cs-professional-listening-b1-c2.json', 'cs-professional-speaking-b1-c2.json',
    ]:
        simplify_json(DATA / name, cs)

    for name in [
        'de.json', 'de-listening.json', 'de-speaking.json',
        'de-professional-listening-b1-c2.json', 'de-professional-speaking-b1-c2.json',
    ]:
        simplify_json(DATA / name, de)


if __name__ == '__main__':
    fix_route()
    simplify_language()
    print('Adaptive route fixed and overly academic wording simplified.')
