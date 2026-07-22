from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / 'index.html'
APP = ROOT / 'app.js'
CSS = ROOT / 'styles.css'


def replace_once(text: str, old: str, new: str, label: str) -> str:
    if new and new in text:
        return text
    if old not in text:
        if not new:
            return text
        raise RuntimeError(f'Marker not found: {label}')
    return text.replace(old, new, 1)


def main():
    html = INDEX.read_text(encoding='utf-8')
    html = replace_once(
        html,
        '<div class="trust-row"><span>8 языков</span><span>Адаптивный маршрут</span><span>HR-отчёт</span><span>Listening A1–A2 CZ</span></div>',
        '<div class="trust-row"><span>8 языков</span><span>Адаптивный маршрут</span><span>HR-отчёт</span></div>',
        'pilot trust badge',
    )
    html = replace_once(
        html,
        '<div><i>L</i><span><b data-i18n="listening">Аудирование</b><small>A1–A2 Czech pilot module</small></span></div>',
        '<div><i>L</i><span><b data-i18n="listening">Аудирование</b></span></div>',
        'pilot listening description',
    )
    html = replace_once(
        html,
        '          <label><span>Email</span><input name="email" type="email" required autocomplete="email"></label>\n',
        '',
        'email field',
    )
    html = replace_once(
        html,
        '          <label><span data-i18n="candidateId">ID кандидата</span><input name="candidateId" maxlength="50" placeholder="optional"></label>\n',
        '',
        'candidate id field',
    )
    html = replace_once(
        html,
        '        </div>\n        <label class="consent">',
        '        </div>\n        <div class="headphones-hint"><span class="headphones-icon">🎧</span><div><strong data-i18n="headphonesTitle">Рекомендуємо проходити тест у навушниках</strong><p data-i18n="headphonesHint">Це допоможе краще чути завдання з аудіювання та підвищить точність результату.</p></div></div>\n        <label class="consent">',
        'headphones recommendation',
    )
    html = replace_once(
        html,
        '        <div class="form-actions"><p data-i18n="disclaimer">Предварительная HR-оценка, не официальный сертификат CEFR.</p><button class="primary" type="submit" data-i18n="start">Начать тест</button></div>',
        '        <div class="form-actions form-actions-end"><button class="primary" type="submit" data-i18n="start">Начать тест</button></div>',
        'disclaimer',
    )
    INDEX.write_text(html, encoding='utf-8')

    js = APP.read_text(encoding='utf-8')
    js = js.replace("let ui=localStorage.getItem('ltp_ui')||'ru'", "let ui=localStorage.getItem('ltp_ui')||'uk'", 1)
    js = js.replace(
        "mustAnalyze:'Сначала запишите и отправьте чтение на проверку.'}",
        "mustAnalyze:'Сначала запишите и отправьте чтение на проверку.',headphonesTitle:'Рекомендуем проходить тест в наушниках',headphonesHint:'Это поможет лучше слышать задания по аудированию и повысит точность результата.'}",
        1,
    )
    js = js.replace(
        "mustAnalyze:'Спочатку запишіть і надішліть читання на перевірку.'}",
        "mustAnalyze:'Спочатку запишіть і надішліть читання на перевірку.',headphonesTitle:'Рекомендуємо проходити тест у навушниках',headphonesHint:'Це допоможе краще чути завдання з аудіювання та підвищить точність результату.'}",
        1,
    )
    js = js.replace(
        "mustAnalyze:'Record and submit the reading before continuing.'}",
        "mustAnalyze:'Record and submit the reading before continuing.',headphonesTitle:'We recommend taking the test with headphones',headphonesHint:'This will make listening tasks clearer and improve the accuracy of the result.'}",
        1,
    )
    old_candidate = "state.candidate={name:d.name.trim(),email:d.email.trim(),position:d.position.trim(),candidateId:d.candidateId.trim(),language:d.language,target:d.target}"
    new_candidate = "state.candidate={name:d.name.trim(),email:'',position:d.position.trim(),candidateId:state.sessionId,language:d.language,target:d.target}"
    if old_candidate in js:
        js = js.replace(old_candidate, new_candidate, 1)
    elif new_candidate not in js:
        raise RuntimeError('Candidate form handler marker not found')
    APP.write_text(js, encoding='utf-8')

    css = CSS.read_text(encoding='utf-8')
    addition = '''\n\n/* Start page cleanup */\n.headphones-hint{display:flex;align-items:flex-start;gap:12px;margin:16px 0;padding:14px 16px;border:1px solid #d9e2ff;border-radius:14px;background:#f4f7ff;color:#1d315f}.headphones-icon{font-size:24px;line-height:1}.headphones-hint strong{display:block;margin-bottom:4px}.headphones-hint p{margin:0;color:#5b6b8f;line-height:1.45}.form-actions-end{justify-content:flex-end}.form-grid{grid-template-columns:repeat(2,minmax(0,1fr))}@media(max-width:760px){.form-grid{grid-template-columns:1fr}.headphones-hint{padding:13px}}\n'''
    if '/* Start page cleanup */' not in css:
        css += addition
    CSS.write_text(css, encoding='utf-8')
    print('Start page updated')


if __name__ == '__main__':
    main()
