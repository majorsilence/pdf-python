#!/usr/bin/env python3
"""
Example 04 — Lines and Strokes

Demonstrates lines with various widths, colours, and orientations.

Usage:
    PDFNATIVE_LIB=/path/to/libpdfnative.so python example_04_lines_and_strokes.py
"""

import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
from majorsilence_pdf import load_library, PdfDocument, PdfStyle, A4

lib_path = os.environ.get('PDFNATIVE_LIB', '')
if not lib_path:
    sys.exit('Set PDFNATIVE_LIB to the path of the pdfnative shared library.')

output_dir = os.path.join(os.path.dirname(__file__), 'output')
os.makedirs(output_dir, exist_ok=True)
lib = load_library(lib_path)

with PdfDocument(lib) as doc:
    doc.set_title('Lines and Strokes')
    with doc.add_page(*A4) as canvas:
        with PdfStyle(lib) as h:
            h.set_size(18).set_bold()
            canvas.draw_text('Lines and Strokes', 72, 40, h)

        label = PdfStyle(lib)
        label.set_size(10)

        y = 80.0

        canvas.draw_text('Line widths (0.5 -> 6 pt)', 72, y, label)
        y += 16
        for w in (0.5, 1.0, 1.5, 2.0, 3.0, 4.0, 6.0):
            canvas.draw_line(72, y, 420, y, width=w)
            canvas.draw_text(f'{w} pt', 430, y - 4, label)
            y += 18
        y += 12

        canvas.draw_text('Coloured lines (2 pt)', 72, y, label)
        y += 16
        for name, r, g, b in [
            ('Black',  0,   0,   0),
            ('Red',    220, 0,   0),
            ('Blue',   0,   0,   200),
            ('Green',  0,   160, 0),
            ('Orange', 220, 120, 0),
            ('Purple', 130, 0,   180),
        ]:
            canvas.draw_line(72, y, 300, y, r=r, g=g, b=b, width=2)
            canvas.draw_text(name, 310, y - 4, label)
            y += 18
        y += 12

        canvas.draw_text('Diagonal lines', 72, y, label)
        y += 16
        canvas.draw_line(72, y, 300, y + 80, width=1)
        canvas.draw_line(300, y, 72, y + 80, width=1)
        canvas.draw_line(72, y + 40, 300, y + 40, r=180, g=180, b=180, width=0.5)
        y += 100

        canvas.draw_text('Rectangle drawn from four lines', 72, y, label)
        y += 16
        x0, x1, y1 = 72, 300, y + 60
        for x1_, y1_, x2_, y2_ in [
            (x0, y, x1, y), (x1, y, x1, y1),
            (x1, y1, x0, y1), (x0, y1, x0, y),
        ]:
            canvas.draw_line(x1_, y1_, x2_, y2_, r=60, g=60, b=60, width=2)
        canvas.draw_text('Border composed of 4 draw_line calls', x0 + 10, y + 26, label)
        y += 80

        canvas.draw_text('Heavy rule separator', 72, y, label)
        y += 12
        canvas.draw_line(72, y, A4[0] - 72, y, r=26, g=86, b=160, width=3)
        y += 8
        canvas.draw_line(72, y, A4[0] - 72, y, r=26, g=86, b=160, width=0.5)

        label.close()

    doc.save(os.path.join(output_dir, 'example_04_lines_and_strokes.pdf'))

print('Written to', os.path.join(output_dir, 'example_04_lines_and_strokes.pdf'))
