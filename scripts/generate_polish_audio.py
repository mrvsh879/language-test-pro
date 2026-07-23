import json, os, pathlib, sys, requests

API_KEY=os.getenv('OPENAI_API_KEY')
if not API_KEY:
    raise SystemExit('OPENAI_API_KEY is missing')

bank=json.load(open('data/pl-listening.json',encoding='utf-8'))
out_dir=pathlib.Path('audio/pl')
out_dir.mkdir(parents=True,exist_ok=True)

expected_files=set()
for item in bank['questions']:
    path=out_dir/f"{item['id']}.mp3"
    expected_files.add(path.name)
    payload={
        'model':'gpt-4o-mini-tts',
        'voice':'marin',
        'input':item['transcript'],
        'instructions':'Mów naturalnym, wyraźnym standardowym językiem polskim. Dla poziomów A1–A2 zachowaj spokojne tempo. Dla B1–B2 użyj naturalnego tempa rozmowy zawodowej. Dla C1–C2 czytaj płynnie, z naturalną intonacją i logicznymi pauzami. Nie dodawaj żadnych słów.',
        'response_format':'mp3'
    }
    response=requests.post(
        'https://api.openai.com/v1/audio/speech',
        headers={'Authorization':f'Bearer {API_KEY}','Content-Type':'application/json'},
        json=payload,
        timeout=180,
    )
    if not response.ok:
        print(response.status_code,response.text,file=sys.stderr)
        raise SystemExit(f'Audio generation failed for {item["id"]}')
    path.write_bytes(response.content)
    if path.stat().st_size <= 1000:
        raise SystemExit(f'Generated audio is too small: {path}')
    print('regenerated',path,len(response.content))

for stale in out_dir.glob('*.mp3'):
    if stale.name not in expected_files:
        stale.unlink()
        print('removed stale',stale)

actual=list(out_dir.glob('*.mp3'))
if len(actual)!=bank['questionCount']:
    raise SystemExit(f'Expected {bank["questionCount"]} MP3 files, found {len(actual)}')
print('Polish audio complete:',len(actual))
