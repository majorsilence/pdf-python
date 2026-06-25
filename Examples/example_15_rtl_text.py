#!/usr/bin/env python3
"""
Example 15 — RTL Text

Embeds right-to-left text (Arabic, Hebrew).
Proper RTL shaping requires an embedded font with RTL glyph tables.
Set RTL_FONT_PATH to an Arabic/Hebrew-capable font (e.g. Noto Sans Arabic),
or set ARABIC_FONT_PATH and HEBREW_FONT_PATH separately.

Usage:
    PDFNATIVE_LIB=/path/to/pdfnative.so python example_15_rtl_text.py
    PDFNATIVE_LIB=... RTL_FONT_PATH=/path/to/NotoSansArabic.ttf python example_15_rtl_text.py
"""

import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
from majorsilence_pdf import load_library, PdfDocument, PdfStyle, A4, ALIGN_RIGHT

lib_path = os.environ.get('PDFNATIVE_LIB', '')
if not lib_path:
    sys.exit('Set PDFNATIVE_LIB to the path of the pdfnative shared library.')

output_dir = os.path.join(os.path.dirname(__file__), 'output')
os.makedirs(output_dir, exist_ok=True)
lib = load_library(lib_path)

W, H = A4

def _find_font(*candidates):
    for path in candidates:
        if os.path.exists(path):
            return path
    return ''

_override = os.environ.get('RTL_FONT_PATH', '')
arabic_font = os.environ.get('ARABIC_FONT_PATH', _override) or _find_font(
    '/usr/share/fonts/truetype/noto/NotoSansArabic-Regular.ttf',
)
hebrew_font = os.environ.get('HEBREW_FONT_PATH', _override) or _find_font(
    '/usr/share/fonts/truetype/noto/NotoSansHebrew-Regular.ttf',
    '/usr/share/fonts/truetype/noto/NotoSerifHebrew-Regular.ttf',
)

# (label, text, font_path)  — label must be ASCII so it renders with Helvetica
RTL_SAMPLES = [
    ('Arabic',              'مرحبا بالعالم! هذا مثال على النص العربي في ملف PDF.', arabic_font),
    ('Arabic numerals',     '١ ٢ ٣ ٤ ٥ ٦ ٧ ٨ ٩ ٠',                              arabic_font),
    ('Hebrew',              'שלום! זהו טקסט עברי בתוך קובץ PDF.',                  hebrew_font),
    ('Bidirectional (EN/AR)', 'Price: 250 USD — السعر: 250 dollar',                arabic_font),
]

with PdfDocument(lib) as doc:
    doc.set_title('RTL Text')

    with doc.add_page(W, H) as canvas:
        with PdfStyle(lib) as h:
            h.set_size(18).set_bold()
            canvas.draw_text('Right-to-Left Text', 72, 50, h)

        with PdfStyle(lib) as info:
            info.set_size(9).set_color(80, 80, 80)
            fonts_found = [f for f in (arabic_font, hebrew_font) if f]
            if fonts_found:
                canvas.draw_text('Fonts: ' + ', '.join(os.path.basename(f) for f in fonts_found), 72, 72, info)
            else:
                info.set_color(160, 80, 0)
                canvas.draw_text('No RTL fonts found — set RTL_FONT_PATH to a font supporting Arabic/Hebrew.', 72, 72, info)

        y = 95.0
        lbl_s = PdfStyle(lib).set_size(9).set_color(100, 100, 100)

        for label_text, text, font_path in RTL_SAMPLES:
            canvas.draw_text(label_text, 72, y, lbl_s)
            y += 14
            with PdfStyle(lib) as rtl_s:
                rtl_s.set_size(14).set_alignment(ALIGN_RIGHT)
                if font_path:
                    rtl_s.set_font_file(font_path)
                canvas.draw_text(text, 72, y, rtl_s)
            y += 24
            canvas.draw_line(72, y, W - 72, y, r=220, g=220, b=220, width=0.3)
            y += 8

        lbl_s.close()

        with PdfStyle(lib) as note:
            note.set_size(9).set_color(130, 130, 130)
            canvas.draw_textbox(
                'Note: PDF supports Unicode RTL text via right-alignment and Unicode '
                'code points. Full glyph shaping (ligatures, contextual forms) requires '
                'an OpenType font with Arabic/Hebrew GSUB/GPOS tables and an engine '
                'that performs shaping (e.g. HarfBuzz) before rendering.',
                72, y + 10, W - 144, 80, note,
            )

    doc.save(os.path.join(output_dir, 'example_15_rtl_text.pdf'))

print('Written to', os.path.join(output_dir, 'example_15_rtl_text.pdf'))
