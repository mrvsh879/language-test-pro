from pathlib import Path
import re

app_path = Path('app.js')
index_path = Path('index.html')

text = app_path.read_text(encoding='utf-8')
all_languages = "['cs','de','it','pl','sk','fr','ro','en']"

# Load listening/speaking banks for every supported language.
for old in [
    "['cs','de','it'].includes(lang)",
    "['cs','de','it','pl'].includes(lang)",
]:
    text = text.replace(old, f"{all_languages}.includes(lang)")

# Add one speaking task per tested level.
for old in [
    "['cs','de','it'].includes(state.candidate?.language)",
    "['cs','de','it','pl'].includes(state.candidate?.language)",
]:
    text = text.replace(old, f"{all_languages}.includes(state.candidate?.language)")

# Support both German-style `passage` and Polish-style `referenceText`.
text = text.replace(
    "$('#passage').textContent=q.passage||'';$('#passage').classList.toggle('hidden',!q.passage);",
    "const readingText=q.passage||q.referenceText||'';$('#passage').textContent=readingText;$('#passage').classList.toggle('hidden',!readingText);",
)
text = text.replace(
    "fd.append('referenceText',q.passage);",
    "fd.append('referenceText',q.passage||q.referenceText||'');",
)

# Add a CEFR-based fallback when maxDurationSec is absent.
text = text.replace(
    "if(sec>=q.maxDurationSec)stopRecording()",
    "const maxSec=q.maxDurationSec||({A1:40,A2:45,B1:55,B2:70,C1:80,C2:85}[q.level]||60);if(sec>=maxSec)stopRecording()",
)

# Apply the same strict high-level confirmation to all supported languages.
for old in [
    "if(['cs','de','it'].includes(state.candidate.language)&&idx(finalLevel)>=3)",
    "if(['cs','de','it','pl'].includes(state.candidate.language)&&idx(finalLevel)>=3)",
]:
    text = text.replace(
        old,
        f"if({all_languages}.includes(state.candidate.language)&&idx(finalLevel)>=3)",
    )

app_path.write_text(text, encoding='utf-8')

# Force GitHub Pages and browsers to load the new app.js.
html = index_path.read_text(encoding='utf-8')
html = re.sub(
    r'<script type="module" src="app\.js(?:\?v=[^"]*)?"></script>',
    '<script type="module" src="app.js?v=20260723-polish-oral-3"></script>',
    html,
)
index_path.write_text(html, encoding='utf-8')

print('Polish listening and speaking enabled; app.js cache version updated')
