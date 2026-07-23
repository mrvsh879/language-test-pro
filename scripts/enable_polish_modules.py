from pathlib import Path

path = Path('app.js')
text = path.read_text(encoding='utf-8')

all_languages = "['cs','de','it','pl','sk','fr','ro','en']"

# 1. Load listening/speaking banks for every supported language.
for old in [
    "['cs','de','it'].includes(lang)",
    "['cs','de','it','pl'].includes(lang)",
]:
    text = text.replace(old, f"{all_languages}.includes(lang)")

# 2. Add one speaking task per tested level for every supported language.
for old in [
    "['cs','de','it'].includes(state.candidate?.language)",
    "['cs','de','it','pl'].includes(state.candidate?.language)",
]:
    text = text.replace(old, f"{all_languages}.includes(state.candidate?.language)")

# 3. Polish speaking files use referenceText; German uses passage.
# Support both schemas everywhere in the UI and Worker request.
text = text.replace(
    "$('#passage').textContent=q.passage||'';$('#passage').classList.toggle('hidden',!q.passage);",
    "const readingText=q.passage||q.referenceText||'';$('#passage').textContent=readingText;$('#passage').classList.toggle('hidden',!readingText);",
)
text = text.replace(
    "fd.append('referenceText',q.passage);",
    "fd.append('referenceText',q.passage||q.referenceText||'');",
)

# 4. Polish speaking tasks currently have no maxDurationSec.
# Use a safe CEFR-based fallback instead of an unlimited recording.
text = text.replace(
    "if(sec>=q.maxDurationSec)stopRecording()",
    "const maxSec=q.maxDurationSec||({A1:40,A2:45,B1:55,B2:70,C1:80,C2:85}[q.level]||60);if(sec>=maxSec)stopRecording()",
)

# 5. Apply the same strict high-level confirmation to Polish and future languages.
text = text.replace(
    "if(['cs','de','it'].includes(state.candidate.language)&&idx(finalLevel)>=3)",
    f"if({all_languages}.includes(state.candidate.language)&&idx(finalLevel)>=3)",
)
text = text.replace(
    "if(['cs','de','it','pl'].includes(state.candidate.language)&&idx(finalLevel)>=3)",
    f"if({all_languages}.includes(state.candidate.language)&&idx(finalLevel)>=3)",
)

path.write_text(text, encoding='utf-8')
print('All oral modules aligned; Polish schema compatibility enabled')
