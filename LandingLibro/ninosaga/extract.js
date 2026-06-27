const fs = require('fs');
const html = fs.readFileSync('index.html', 'utf8');
const match = html.match(/const I18N = (\{[\s\S]*?\n        \});/);
if (match) {
    const code = `const I18N = ${match[1]};
    require('fs').writeFileSync('translations.json', JSON.stringify(I18N, null, 2));`;
    fs.writeFileSync('temp_eval.js', code);
} else {
    console.log("No match found");
}
