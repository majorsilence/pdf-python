#!/usr/bin/env python3
"""
Example 06 — Custom Font

Embeds a TrueType/OpenType font from a file using pdf_style_set_font_file.

Usage:
    PDFNATIVE_LIB=/path/to/libpdfnative.so \
    CUSTOM_FONT_PATH=/path/to/MyFont.ttf \
    python example_06_custom_font.py

If CUSTOM_FONT_PATH is not set, the example falls back to the built-in Helvetica.
"""

import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
from majorsilence_pdf import load_library, PdfDocument, PdfStyle, A4

lib_path = os.environ.get('PDFNATIVE_LIB', '')
if not lib_path:
    sys.exit('Set PDFNATIVE_LIB to the path of the pdfnative shared library.')

font_path  = os.environ.get('CUSTOM_FONT_PATH', '')
output_dir = os.path.join(os.path.dirname(__file__), 'output')
os.makedirs(output_dir, exist_ok=True)
lib = load_library(lib_path)

W, H = A4

with PdfDocument(lib) as doc:
    doc.set_title('Custom Font')

    with doc.add_page(W, H) as canvas:
        with PdfStyle(lib) as heading:
            heading.set_size(18).set_bold()
            canvas.draw_text('Custom Font Embedding', 72, 50, heading)

        if font_path and os.path.exists(font_path):
            with PdfStyle(lib) as s:
                s.set_size(10).set_color(80, 80, 80)
                canvas.draw_text(f'Font file: {os.path.basename(font_path)}', 72, 78, s)

            y = 100.0
            for size in (10, 12, 14, 18, 24, 32):
                with PdfStyle(lib) as s:
                    s.set_font_file(font_path).set_size(size)
                    canvas.draw_text(f'{size} pt — The quick brown fox jumps over the lazy dog', 72, y, s)
                y += size + 8

            y += 10
            with PdfStyle(lib) as s:
                s.set_font_file(font_path).set_size(14).set_bold()
                canvas.draw_text('Bold variant (if supported by the font file):', 72, y, s)
            y += 22
            with PdfStyle(lib) as s:
                s.set_font_file(font_path).set_size(12).set_italic()
                canvas.draw_text('Italic variant (if supported by the font file):', 72, y, s)
        else:
            with PdfStyle(lib) as s:
                s.set_size(11).set_color(180, 0, 0)
                canvas.draw_text('CUSTOM_FONT_PATH not set or file not found.', 72, 100, s)
                canvas.draw_text('Set CUSTOM_FONT_PATH=/path/to/a/TrueType.ttf and re-run.', 72, 118, s)

            with PdfStyle(lib) as s:
                s.set_size(11).set_color(80, 80, 80)
                canvas.draw_text('Falling back to built-in Helvetica:', 72, 150, s)

            y = 172.0
            for size in (10, 12, 14, 18, 24):
                with PdfStyle(lib) as s:
                    s.set_size(size)
                    canvas.draw_text(f'{size} pt — The quick brown fox (Helvetica)', 72, y, s)
                y += size + 8

    doc.save(os.path.join(output_dir, 'example_06_custom_font.pdf'))

print('Written to', os.path.join(output_dir, 'example_06_custom_font.pdf'))
