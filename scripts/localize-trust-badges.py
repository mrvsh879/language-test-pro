from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / 'index.html'
APP = ROOT / 'app.js'

html = INDEX.read_text(encoding='utf-8')
old = '<div class="trust-row"><span>8 языков</span><span>Адаптивный маршрут</span><span>HR-отчёт</span></div>'
new = '<div class="trust-row"><span data-i18n="languagesCount">8 мов</span><span data-i18n="adaptiveRouteBadge">Адаптивний маршрут</span><span data-i18n="hrReportBadge">HR-звіт</span></div>'
if old in html:
    html = html.replace(old, new, 1)
elif new not in html:
    raise RuntimeError('Trust row marker not found')
INDEX.write_text(html, encoding='utf-8')

js = APP.read_text(encoding='utf-8')
replacements = [
    (
        "headphonesHint:'Это поможет лучше слышать задания по аудированию и повысит точность результата.'}",
        "headphonesHint:'Это поможет лучше слышать задания по аудированию и повысит точность результата.',languagesCount:'8 языков',adaptiveRouteBadge:'Адаптивный маршрут',hrReportBadge:'HR-отчёт'}",
    ),
    (
        "headphonesHint:'Це допоможе краще чути завдання з аудіювання та підвищить точність результату.'}",
        "headphonesHint:'Це допоможе краще чути завдання з аудіювання та підвищить точність результату.',languagesCount:'8 мов',adaptiveRouteBadge:'Адаптивний маршрут',hrReportBadge:'HR-звіт'}",
    ),
    (
        "headphonesHint:'This will make listening tasks clearer and improve the accuracy of the result.'}",
        "headphonesHint:'This will make listening tasks clearer and improve the accuracy of the result.',languagesCount:'8 languages',adaptiveRouteBadge:'Adaptive route',hrReportBadge:'HR report'}",
    ),
]
for old_text, new_text in replacements:
    if new_text in js:
        continue
    if old_text not in js:
        raise RuntimeError(f'I18N marker not found: {old_text[:30]}')
    js = js.replace(old_text, new_text, 1)
APP.write_text(js, encoding='utf-8')
print('Trust badges localized')
