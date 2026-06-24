#!/usr/bin/env python3
"""
Example 02 — Text Styles

Demonstrates font sizes, bold, italic, colours, alignment, and decorations.

Usage:
    PDFNATIVE_LIB=/path/to/libpdfnative.so python example_02_text_styles.py
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
from majorsilence_pdf import (
    load_library, PdfDocument, PdfStyle, A4,
    ALIGN_LEFT, ALIGN_CENTER, ALIGN_RIGHT,
    DECOR_UNDERLINE, DECOR_STRIKETHROUGH, DECOR_OVERLINE,
)

lib_path = os.environ.get('PDFNATIVE_LIB', '')
if not lib_path:
    sys.exit('Set PDFNATIVE_LIB to the path of the pdfnative shared library.')

output_dir = os.path.join(os.path.dirname(__file__), 'output')
os.makedirs(output_dir, exist_ok=True)

lib = load_library(lib_path)

with PdfDocument(lib) as doc:
    doc.set_title('Text Styles')

    with doc.add_page(*A4) as canvas:
        y = 50.0

        with PdfStyle(lib) as s:
            s.set_size(24).set_bold()
            canvas.draw_text('Text Styles', 72, y, s)
        y += 36

        with PdfStyle(lib) as s:
            s.set_size(18).set_bold()
            canvas.draw_text('Font sizes', 72, y, s)
        y += 26

        for size in (8, 10, 12, 14, 18, 24):
            with PdfStyle(lib) as s:
                s.set_size(size)
                canvas.draw_text(f'{size} pt — The quick brown fox', 72, y, s)
            y += size + 6
        y += 12

        with PdfStyle(lib) as s:
            s.set_size(18).set_bold()
            canvas.draw_text('Bold and italic', 72, y, s)
        y += 26

        with PdfStyle(lib) as s:
            s.set_size(12).set_bold()
            canvas.draw_text('Bold text', 72, y, s)
        y += 18
        with PdfStyle(lib) as s:
            s.set_size(12).set_italic()
            canvas.draw_text('Italic text', 72, y, s)
        y += 18
        with PdfStyle(lib) as s:
            s.set_size(12).set_bold().set_italic()
            canvas.draw_text('Bold italic text', 72, y, s)
        y += 28

        with PdfStyle(lib) as s:
            s.set_size(18).set_bold()
            canvas.draw_text('Colour', 72, y, s)
        y += 26

        for label, r, g, b in [
            ('Red',   220, 0,   0),
            ('Green', 0,   160, 0),
            ('Blue',  0,   0,   200),
            ('Gray',  128, 128, 128),
        ]:
            with PdfStyle(lib) as s:
                s.set_size(12).set_color(r, g, b)
                canvas.draw_text(f'{label} text  (r={r}, g={g}, b={b})', 72, y, s)
            y += 18
        y += 10

        with PdfStyle(lib) as s:
            s.set_size(18).set_bold()
            canvas.draw_text('Alignment', 72, y, s)
        y += 26

        page_width = A4[0]
        box_width  = page_width - 144  # 72 pt margin each side

        with PdfStyle(lib) as s:
            s.set_size(12).set_alignment(ALIGN_LEFT)
            canvas.draw_text('Left-aligned text', 72, y, s)
        y += 18
        with PdfStyle(lib) as s:
            s.set_size(12).set_alignment(ALIGN_CENTER)
            canvas.draw_textbox('Centre-aligned text', 72, y, box_width, 20, s)
        y += 22
        with PdfStyle(lib) as s:
            s.set_size(12).set_alignment(ALIGN_RIGHT)
            canvas.draw_textbox('Right-aligned text', 72, y, box_width, 20, s)
        y += 28

        with PdfStyle(lib) as s:
            s.set_size(18).set_bold()
            canvas.draw_text('Decoration', 72, y, s)
        y += 26

        with PdfStyle(lib) as s:
            s.set_size(12).set_decoration(DECOR_UNDERLINE)
            canvas.draw_text('Underlined text', 72, y, s)
        y += 18
        with PdfStyle(lib) as s:
            s.set_size(12).set_decoration(DECOR_STRIKETHROUGH)
            canvas.draw_text('Strikethrough text', 72, y, s)
        y += 18
        with PdfStyle(lib) as s:
            s.set_size(12).set_decoration(DECOR_OVERLINE)
            canvas.draw_text('Overline text', 72, y, s)

    doc.save(os.path.join(output_dir, 'example_02_text_styles.pdf'))

print('Written to', os.path.join(output_dir, 'example_02_text_styles.pdf'))
