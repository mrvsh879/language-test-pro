from pathlib import Path

path=Path('app.js')
text=path.read_text(encoding='utf-8')
text=text.replace("['cs','de','it'].includes(lang)","['cs','de','it','pl'].includes(lang)")
text=text.replace("['cs','de','it'].includes(state.candidate?.language)","['cs','de','it','pl'].includes(state.candidate?.language)")
path.write_text(text,encoding='utf-8')
print('Polish listening and speaking modules enabled in app.js')
