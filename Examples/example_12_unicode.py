#!/usr/bin/env python3
"""
Example 12 — Unicode Text

Renders text in Latin extended, Greek, Cyrillic, and other Unicode scripts.
Note: full multi-script coverage requires an embedded font with broad glyph
coverage (e.g. Noto Sans). The built-in Helvetica covers Latin + some symbols.

Usage:
    PDFNATIVE_LIB=/path/to/libpdfnative.so python example_12_unicode.py
    PDFNATIVE_LIB=... UNICODE_FONT_PATH=/path/to/NotoSans-Regular.ttf python example_12_unicode.py
"""

import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
from majorsilence_pdf import load_library, PdfDocument, PdfStyle, A4

lib_path = os.environ.get('PDFNATIVE_LIB', '')
if not lib_path:
    sys.exit('Set PDFNATIVE_LIB to the path of the pdfnative shared library.')

uni_font   = os.environ.get('UNICODE_FONT_PATH', '')
output_dir = os.path.join(os.path.dirname(__file__), 'output')
os.makedirs(output_dir, exist_ok=True)
lib = load_library(lib_path)

W, H = A4

SAMPLES = [
    ('Latin (basic)',         'Hello, World! 0 1 2 3 4 5 6 7 8 9'),
    ('Latin extended',        'Héllo Wörld — café, naïve, résumé, façade'),
    ('Latin extended-B',      'Ɓƙƿ Ǆǌǅ ǋǆ ȡȠ Ʒǯ'),
    ('Greek',                 'Ελληνικά — Αλφάβητο Αβγδεζηθ'),
    ('Cyrillic',              'Привет мир — кириллица'),
    ('Symbols',               '© ® ™ € £ ¥ § ¶ † ‡ • … ‰ ′ ″'),
    ('Arrows & math',         '← → ↑ ↓ ↔ ⇐ ⇒ ∑ ∏ √ ∞ ≠ ≤ ≥ ∈ ∉'),
    ('Box drawing',           '┌─┬─┐  │ │ │  ├─┼─┤  └─┴─┘'),
    ('Emojis (if supported)', '😀 📄 🖨️ 🔒 🗒️'),
]

with PdfDocument(lib) as doc:
    doc.set_title('Unicode Text')

    with doc.add_page(W, H) as canvas:
        with PdfStyle(lib) as h:
            h.set_size(18).set_bold()
            canvas.draw_text('Unicode Text Rendering', 72, 50, h)

        if uni_font and os.path.exists(uni_font):
            with PdfStyle(lib) as info:
                info.set_size(9).set_color(80, 80, 80)
                canvas.draw_text(f'Using font: {os.path.basename(uni_font)}', 72, 72, info)

        y = 90.0
        script_s  = PdfStyle(lib).set_size(8).set_color(100, 100, 100)
        sample_s  = PdfStyle(lib).set_size(12)
        if uni_font and os.path.exists(uni_font):
            sample_s.set_font_file(uni_font)

        for script, text in SAMPLES:
            canvas.draw_text(script, 72, y, script_s)
            y += 12
            canvas.draw_text(text, 72, y, sample_s)
            y += 20
            canvas.draw_line(72, y, W - 72, y, r=220, g=220, b=220, width=0.3)
            y += 6

        script_s.close()
        sample_s.close()

        with PdfStyle(lib) as note:
            note.set_size(8).set_color(130, 130, 130)
            canvas.draw_text(
                'Tip: set UNICODE_FONT_PATH to a wide-coverage font (e.g. Noto Sans) for full glyph rendering.',
                72, y + 10, note,
            )

    doc.save(os.path.join(output_dir, 'example_12_unicode.pdf'))

print('Written to', os.path.join(output_dir, 'example_12_unicode.pdf'))
