import ebooklib
from ebooklib import epub

book = epub.read_epub(r"C:\Users\User\OneDrive\Documentos\Books\LandingLibro\ninosaga\assets\EN Book\Nino-Hell-EN-revised.epub")
epub.write_epub('test.epub', book)

