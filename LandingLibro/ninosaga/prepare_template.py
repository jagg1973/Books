import re

with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# 1. Remove I18N and language logic
# Regex match from `// ====== i18n dictionaries` up to the DOMContentLoaded `applyLang`
html = re.sub(
    r'// ====== i18n dictionaries.*?document\.addEventListener\("DOMContentLoaded", function \(\) \{[\s\n]*applyLang\(detectLang\(\)\);',
    'const CURRENT_LANG = \'{{LANG}}\';\n\n        document.addEventListener("DOMContentLoaded", function () {',
    html,
    flags=re.DOTALL
)

# 2. Update language select onchange
html = html.replace('onchange="setLang(this.value)"', 'onchange="window.location.href=this.value"')

# 3. Update comprarSaga window.__lang
html = html.replace('window.__lang', 'CURRENT_LANG')

with open('template.html', 'w', encoding='utf-8') as f:
    f.write(html)
