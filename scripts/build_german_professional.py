# Professional German assessment build and validation
from __future__ import annotations

import glob
import json
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
APP = ROOT / "app.js"
LEVELS = ["A1", "A2", "B1", "B2", "C1", "C2"]


def read_json(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as fh:
        return json.load(fh)


def validate_questions(questions: list[dict], *, expected_skill: str | None = None) -> None:
    ids = [q.get("id") for q in questions]
    duplicates = [x for x, n in Counter(ids).items() if n > 1]
    if duplicates:
        raise ValueError(f"Duplicate IDs: {duplicates}")

    for q in questions:
        missing = [k for k in ("id", "level", "skill", "prompt") if not q.get(k)]
        if missing:
            raise ValueError(f"{q.get('id', '<unknown>')}: missing {missing}")
        if q["level"] not in LEVELS:
            raise ValueError(f"{q['id']}: invalid level {q['level']}")
        if expected_skill and q["skill"] != expected_skill:
            raise ValueError(f"{q['id']}: expected skill {expected_skill}")
        if q["skill"] != "speaking":
            options = q.get("options")
            answer = q.get("answer")
            if not isinstance(options, list) or len(options) != 4:
                raise ValueError(f"{q['id']}: exactly four options required")
            if not isinstance(answer, int) or not 0 <= answer < 4:
                raise ValueError(f"{q['id']}: invalid answer index")
        if q["skill"] == "reading" and not q.get("passage"):
            raise ValueError(f"{q['id']}: reading passage required")
        if q["skill"] == "listening" and not q.get("transcript"):
            raise ValueError(f"{q['id']}: listening transcript required")
        if q["skill"] == "speaking" and not q.get("passage"):
            raise ValueError(f"{q['id']}: speaking passage required")


def merge_files(patterns: list[str], *, expected_skill: str | None = None) -> list[dict]:
    paths: list[Path] = []
    for pattern in patterns:
        paths.extend(Path(p) for p in glob.glob(str(DATA / pattern)))
    unique_paths = sorted(set(paths))
    questions: list[dict] = []
    seen: set[str] = set()
    for path in unique_paths:
        payload = read_json(path)
        for q in payload.get("questions", []):
            if q.get("id") in seen:
                continue
            seen.add(q.get("id"))
            questions.append(q)
    validate_questions(questions, expected_skill=expected_skill)
    return sorted(questions, key=lambda q: (LEVELS.index(q["level"]), q["skill"], q["id"]))


def write_bank(path: Path, questions: list[dict], version: str) -> None:
    payload = {
        "language": "de",
        "version": version,
        "questionCount": len(questions),
        "questions": questions,
    }
    path.write_text(json.dumps(payload, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")


def patch_app() -> None:
    text = APP.read_text(encoding="utf-8")

    old_route = "function startRoute(){state.queue=[];state.visitedLevels=[];addLevel('B1');if(['cs','de'].includes(state.candidate.language)){state.queue.push(...shuffle(state.bank.filter(q=>q.skill==='listening'&&['A1','A2'].includes(q.level))).slice(0,4));state.queue.push(...shuffle(state.bank.filter(q=>q.skill==='speaking'&&['A1','A2'].includes(q.level))).slice(0,2))}}"
    new_route = "function startRoute(){state.queue=[];state.visitedLevels=[];addLevel('B1');if(state.candidate.language==='cs'){state.queue.push(...shuffle(state.bank.filter(q=>q.skill==='listening'&&['A1','A2'].includes(q.level))).slice(0,4));state.queue.push(...shuffle(state.bank.filter(q=>q.skill==='speaking'&&['A1','A2'].includes(q.level))).slice(0,2))}else if(state.candidate.language==='de'){const targetIndex=idx(state.candidate.target),oralLevels=[LEVELS[targetIndex],LEVELS[clamp(targetIndex-1,0,5)]],listenPool=state.bank.filter(q=>q.skill==='listening'&&oralLevels.includes(q.level)),speakPool=state.bank.filter(q=>q.skill==='speaking'&&oralLevels.includes(q.level));state.queue.push(...shuffle(listenPool).slice(0,6));state.queue.push(...shuffle(speakPool).slice(0,3))}}"
    if old_route not in text and new_route not in text:
        raise ValueError("startRoute signature not found")
    text = text.replace(old_route, new_route)

    old_final = "let finalLevel='A1';for(const l of tested)if(levelScores[l].rate>=.6)finalLevel=l;"
    new_final = "let finalLevel='A1';for(const l of tested){const s=levelScores[l],threshold=idx(l)>=3?.72:.65,minItems=idx(l)>=3?6:5;if(s.total>=minItems&&s.rate>=threshold)finalLevel=l}if(state.candidate.language==='de'&&idx(finalLevel)>=3){const required=LEVELS.slice(2,idx(finalLevel)+1);for(const l of required){const s=levelScores[l];if(!s||s.total<6||s.rate<(idx(l)>=3?.72:.65)){finalLevel=LEVELS[Math.max(0,idx(l)-1)];break}}}"
    if old_final not in text and new_final not in text:
        raise ValueError("final-level calculation signature not found")
    text = text.replace(old_final, new_final)

    APP.write_text(text, encoding="utf-8")


def main() -> None:
    professional = merge_files([f"de-professional-{level.lower()}.json" for level in LEVELS])
    by_level = defaultdict(list)
    for q in professional:
        by_level[q["level"]].append(q)
    counts = {level: len(by_level[level]) for level in LEVELS}
    if any(counts[level] != 20 for level in LEVELS):
        raise ValueError(f"Expected 20 professional questions per level, got {counts}")
    skill_counts = Counter(q["skill"] for q in professional)
    if skill_counts != Counter({"grammar": 42, "vocabulary": 42, "reading": 36}):
        raise ValueError(f"Unexpected skill distribution: {skill_counts}")

    listening = merge_files(["de-listening.json", "de-listening-*.json"], expected_skill="listening")
    speaking = merge_files(["de-speaking.json", "de-speaking-*.json"], expected_skill="speaking")

    listening_levels = Counter(q["level"] for q in listening)
    speaking_levels = Counter(q["level"] for q in speaking)
    for level in LEVELS:
        if listening_levels[level] < 4:
            raise ValueError(f"At least four listening items required for {level}: {listening_levels}")
        if speaking_levels[level] < 2:
            raise ValueError(f"At least two speaking items required for {level}: {speaking_levels}")

    write_bank(DATA / "de.json", professional, "3.0.0-professional")
    write_bank(DATA / "de-listening.json", listening, "3.0.0-professional")
    write_bank(DATA / "de-speaking.json", speaking, "3.0.0-professional")
    patch_app()

    print("German professional build complete")
    print("ordinary:", len(professional), counts)
    print("listening:", len(listening), dict(listening_levels))
    print("speaking:", len(speaking), dict(speaking_levels))


if __name__ == "__main__":
    main()
