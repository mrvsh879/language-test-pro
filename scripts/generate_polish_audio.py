import json, os, pathlib, sys, requests

API_KEY=os.getenv('OPENAI_API_KEY')
if not API_KEY:
    raise SystemExit('OPENAI_API_KEY is missing')

bank=json.load(open('data/pl-listening.json',encoding='utf-8'))
out_dir=pathlib.Path('audio/pl')
out_dir.mkdir(parents=True,exist_ok=True)

for item in bank['questions']:
    path=out_dir/f"{item['id']}.mp3"
    if path.exists() and path.stat().st_size>1000:
        print('skip',path)
        continue
    payload={
        'model':'gpt-4o-mini-tts',
        'voice':'marin',
        'input':item['transcript'],
        'instructions':'Mów naturalnym, wyraźnym standardowym językiem polskim. Zachowaj spokojne tempo odpowiednie dla testu językowego.',
        'response_format':'mp3'
    }
    response=requests.post(
        'https://api.openai.com/v1/audio/speech',
        headers={'Authorization':f'Bearer {API_KEY}','Content-Type':'application/json'},
        json=payload,
        timeout=120,
    )
    if not response.ok:
        print(response.status_code,response.text,file=sys.stderr)
        raise SystemExit(f'Audio generation failed for {item["id"]}')
    path.write_bytes(response.content)
    print('created',path,len(response.content))
