from pathlib import Path

path = Path('app.js')
text = path.read_text(encoding='utf-8')

all_languages = "['cs','de','it','pl','sk','fr','ro','en']"

text = text.replace(
    "['cs','de','it'].includes(lang)",
    f"{all_languages}.includes(lang)",
)
text = text.replace(
    "['cs','de','it','pl'].includes(lang)",
    f"{all_languages}.includes(lang)",
)
text = text.replace(
    "['cs','de','it'].includes(state.candidate?.language)",
    f"{all_languages}.includes(state.candidate?.language)",
)
text = text.replace(
    "['cs','de','it','pl'].includes(state.candidate?.language)",
    f"{all_languages}.includes(state.candidate?.language)",
)

path.write_text(text, encoding='utf-8')
print('Listening and speaking modules enabled for cs, de, it, pl, sk, fr, ro and en')
