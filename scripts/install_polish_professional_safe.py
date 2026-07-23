import ast
import base64
import gzip
import json
from pathlib import Path

SOURCE = Path('scripts/install_polish_professional.py')
text = SOURCE.read_text(encoding='utf-8')
module = ast.parse(text)

payload = None
for node in module.body:
    if isinstance(node, ast.Assign):
        for target in node.targets:
            if isinstance(target, ast.Name) and target.id == 'PAYLOAD':
                payload = ast.literal_eval(node.value)
                break
    if payload is not None:
        break

if not isinstance(payload, str) or not payload:
    raise SystemExit('PAYLOAD was not found in install_polish_professional.py')

# Base64 strings can legally omit trailing = characters. Restore them safely.
payload += '=' * (-len(payload) % 4)

try:
    packed = base64.b64decode(payload, validate=True)
except Exception as exc:
    raise SystemExit(f'Invalid Base64 payload: {exc}') from exc

try:
    raw = gzip.decompress(packed)
except Exception as exc:
    raise SystemExit(f'Invalid or incomplete gzip payload: {exc}') from exc

try:
    data = json.loads(raw.decode('utf-8'))
except Exception as exc:
    raise SystemExit(f'Invalid JSON payload: {exc}') from exc

expected = {
    'pl.json': 120,
    'pl-listening.json': 40,
    'pl-speaking.json': 28,
}
levels = {'A1', 'A2', 'B1', 'B2', 'C1', 'C2'}
out = Path('data')
out.mkdir(exist_ok=True)

for name, count in expected.items():
    obj = data.get(name)
    if not isinstance(obj, dict):
        raise SystemExit(f'Missing bank: {name}')
    questions = obj.get('questions')
    if obj.get('questionCount') != count or not isinstance(questions, list) or len(questions) != count:
        raise SystemExit(f'Invalid question count in {name}')
    if {q.get('level') for q in questions} != levels:
        raise SystemExit(f'Incomplete CEFR levels in {name}')
    if len({q.get('id') for q in questions}) != count:
        raise SystemExit(f'Duplicate question IDs in {name}')
    (out / name).write_text(
        json.dumps(obj, ensure_ascii=False, separators=(',', ':')),
        encoding='utf-8',
    )
    print(name, obj.get('version'), count, 'OK')
