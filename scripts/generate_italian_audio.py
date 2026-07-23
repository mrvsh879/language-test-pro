import json
import os
import pathlib
import sys
import requests

API_KEY = os.getenv('OPENAI_API_KEY')
if not API_KEY:
    raise SystemExit('OPENAI_API_KEY is missing')

bank = json.load(open('data/it-listening.json', encoding='utf-8'))
out_dir = pathlib.Path('audio/it')
out_dir.mkdir(parents=True, exist_ok=True)

expected_files = set()
for item in bank['questions']:
    path = out_dir / f"{item['id']}.mp3"
    expected_files.add(path.name)
    level = item.get('level', '')
    pace = (
        'mantieni un ritmo calmo e molto chiaro' if level in {'A1', 'A2'}
        else 'usa un ritmo naturale da conversazione professionale' if level in {'B1', 'B2'}
        else 'leggi con ritmo naturale, intonazione sfumata e pause logiche'
    )
    payload = {
        'model': 'gpt-4o-mini-tts',
        'voice': 'marin',
        'input': item['transcript'],
        'instructions': (
            'Parla in italiano standard naturale e chiaramente articolato. '
            f'{pace}. Rispetta accenti, doppie consonanti, elisioni e punteggiatura. '
            'Non aggiungere, omettere o parafrasare alcuna parola.'
        ),
        'response_format': 'mp3',
    }
    response = requests.post(
        'https://api.openai.com/v1/audio/speech',
        headers={
            'Authorization': f'Bearer {API_KEY}',
            'Content-Type': 'application/json',
        },
        json=payload,
        timeout=180,
    )
    if not response.ok:
        print(response.status_code, response.text, file=sys.stderr)
        raise SystemExit(f'Audio generation failed for {item["id"]}')
    path.write_bytes(response.content)
    if path.stat().st_size <= 1000:
        raise SystemExit(f'Generated audio is too small: {path}')
    print('regenerated', path, len(response.content))

for stale in out_dir.glob('*.mp3'):
    if stale.name not in expected_files:
        stale.unlink()
        print('removed stale', stale)

actual = list(out_dir.glob('*.mp3'))
if len(actual) != bank['questionCount']:
    raise SystemExit(
        f'Expected {bank["questionCount"]} MP3 files, found {len(actual)}'
    )
print('Italian audio complete:', len(actual))
