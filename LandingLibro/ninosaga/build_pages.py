import json
import os
import shutil
from bs4 import BeautifulSoup

def build():
    # Load translations
    with open('translations.json', 'r', encoding='utf-8') as f:
        i18n = json.load(f)

    with open('template.html', 'r', encoding='utf-8') as f:
        template_html = f.read()

    langs = ['es', 'en', 'pt', 'zh', 'it', 'de']
    base_url = "https://ninosaga.com"

    # Create dist directory
    os.makedirs('dist', exist_ok=True)

    for lang in langs:
        print(f"Building {lang}...")
        # 1. Inject language into JS
        html = template_html.replace('{{LANG}}', lang)
        
        # 2. Parse with BeautifulSoup
        soup = BeautifulSoup(html, 'html.parser')
        
        # 3. Set html lang attribute
        if soup.html:
            soup.html['lang'] = lang
        
        # 4. Replace data-i18n
        t = i18n.get(lang, i18n.get('es', {}))
        for el in soup.find_all(attrs={"data-i18n": True}):
            key = el['data-i18n']
            if key in t:
                el.clear()
                # Parse translation as HTML in case it contains <br> or <strong>
                parsed_t = BeautifulSoup(t[key], 'html.parser')
                el.append(parsed_t)
                
        # 5. Replace title
        if 'meta.title' in t and soup.title:
            soup.title.string = t['meta.title']
            
        # 6. Update language selector paths
        select = soup.find(id='langSelect')
        if select:
            for option in select.find_all('option'):
                opt_lang = option.get('value', '')
                if opt_lang:
                    option['value'] = f"/{opt_lang}/" if opt_lang != 'es' else "/"
                    if opt_lang == lang:
                        option['selected'] = 'selected'
                    else:
                        if 'selected' in option.attrs:
                            del option['selected']
                    
        # 7. Update hreflang links
        for link in soup.find_all('link', rel='alternate', hreflang=True):
            hl = link['hreflang']
            if hl == 'x-default' or hl == 'es':
                link['href'] = f"{base_url}/"
            else:
                link['href'] = f"{base_url}/{hl}/"
                
        # Write to dist
        out_dir = 'dist' if lang == 'es' else f'dist/{lang}'
        os.makedirs(out_dir, exist_ok=True)
        with open(f'{out_dir}/index.html', 'w', encoding='utf-8') as f:
            f.write(str(soup))
            
    # Copy assets to dist
    if not os.path.exists('dist/assets'):
        print("Copying assets...")
        shutil.copytree('assets', 'dist/assets')
        
    print("Build complete!")

if __name__ == "__main__":
    build()
