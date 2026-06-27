import os
import re
from bs4 import BeautifulSoup
import ebooklib
from ebooklib import epub
from deep_translator import GoogleTranslator

# Suppress ebooklib warnings
import warnings
warnings.filterwarnings('ignore', category=UserWarning, module='ebooklib')

source_epub = r"C:\Users\User\OneDrive\Documentos\Books\LandingLibro\ninosaga\assets\EN Book\Nino-Hell-EN-revised.epub"
output_dir = r"C:\Users\User\OneDrive\Documentos\Books\LandingLibro\ninosaga\assets"

targets = {
    'PT': 'portuguese',
    'CN': 'zh-CN',
    'IT': 'italian',
    'DE': 'german'
}

def translate_html(html_bytes, translator):
    soup = BeautifulSoup(html_bytes, 'lxml')
    # find all text nodes
    for text_node in soup.find_all(string=True):
        parent = text_node.parent
        # ignore scripts, styles, etc
        if parent.name in ['style', 'script', 'head', 'title', 'meta', '[document]']:
            continue
        text = text_node.strip()
        if not text:
            continue
        # Avoid translating short structural strings
        if len(text) < 2 and not text.isalpha():
            continue
            
        try:
            # deep-translator has a 5000 character limit, but epub text nodes are usually small
            translated = translator.translate(text)
            if translated:
                text_node.replace_with(translated)
        except Exception as e:
            print(f"Error translating chunk: {e}")
            pass
            
    return str(soup).encode('utf-8')

for lang_code, lang_name in targets.items():
    print(f"--- Starting translation to {lang_name} ({lang_code}) ---")
    
    output_filename = os.path.join(output_dir, f"Nino-Hell-{lang_code}-revised.epub")
    if os.path.exists(output_filename):
        print(f"{output_filename} already exists, skipping.")
        continue
        
    try:
        book = epub.read_epub(source_epub)
        translator = GoogleTranslator(source='en', target=lang_name)
        
        # update metadata
        book.set_language(lang_code.lower())

        # fix ebooklib NoneType uid bug
        def fix_toc(toc_list):
            for t in toc_list:
                if isinstance(t, (tuple, list)) and len(t) == 2:
                    sec, links = t
                    if hasattr(sec, 'uid') and getattr(sec, 'uid', None) is None:
                        sec.uid = f"uid_{id(sec)}"
                    fix_toc(links)
                else:
                    if hasattr(t, 'uid') and getattr(t, 'uid', None) is None:
                        t.uid = f"uid_{id(t)}"
        fix_toc(book.toc)
        
        for item in book.get_items():
            if hasattr(item, 'uid') and getattr(item, 'uid', None) is None:
                item.uid = f"uid_{id(item)}"
            if item.get_type() == ebooklib.ITEM_DOCUMENT:
                print(f" Translating {item.get_name()}...")
                original_content = item.get_content()
                new_content = translate_html(original_content, translator)
                item.set_content(new_content)
                
        # save book
        print(f"Saving to {output_filename}...")
        epub.write_epub(output_filename, book, {} )
        print(f"Successfully generated {lang_code} epub.")
        
    except Exception as e:
        print(f"Failed to process {lang_code}: {e}")

print("All translations finished.")
