#!/usr/bin/env python3
"""
Example 03 — Shapes

Draws lines, rectangles (filled/stroked/both), and ellipses.

Usage:
    PDFNATIVE_LIB=/path/to/libpdfnative.so python example_03_shapes.py
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
from majorsilence_pdf import load_library, PdfDocument, PdfStyle, A4

lib_path = os.environ.get('PDFNATIVE_LIB', '')
if not lib_path:
    sys.exit('Set PDFNATIVE_LIB to the path of the pdfnative shared library.')

output_dir = os.path.join(os.path.dirname(__file__), 'output')
os.makedirs(output_dir, exist_ok=True)

lib = load_library(lib_path)

with PdfDocument(lib) as doc:
    doc.set_title('Shapes')

    with doc.add_page(*A4) as canvas:
        with PdfStyle(lib) as heading:
            heading.set_size(18).set_bold()

        with PdfStyle(lib) as label:
            label.set_size(10)

        y = 50.0

        canvas.draw_text('Lines', 72, y, None)
        y += 20

        for i, (r, g, b, w) in enumerate([
            (0,   0,   0,   0.5),
            (200, 0,   0,   1.0),
            (0,   0,   200, 2.0),
            (0,   150, 0,   3.0),
        ]):
            canvas.draw_line(72, y + i * 14, 400, y + i * 14, r=r, g=g, b=b, width=w)
        y += 80

        canvas.draw_text('Filled rectangles', 72, y, None)
        y += 16

        colors = [(220, 50, 50), (50, 150, 50), (50, 50, 220), (200, 150, 0)]
        for i, (r, g, b) in enumerate(colors):
            canvas.draw_rect(72 + i * 110, y, 100, 60, fill_rgb=(r, g, b))
        y += 80

        canvas.draw_text('Stroked rectangles', 72, y, None)
        y += 16

        for i, (r, g, b) in enumerate(colors):
            canvas.draw_rect(72 + i * 110, y, 100, 60, stroke_rgb=(r, g, b), stroke_width=2.0)
        y += 80

        canvas.draw_text('Filled + stroked rectangles', 72, y, None)
        y += 16

        canvas.draw_rect(72,  y, 100, 60, fill_rgb=(240, 200, 200), stroke_rgb=(180, 0, 0), stroke_width=2.0)
        canvas.draw_rect(182, y, 100, 60, fill_rgb=(200, 240, 200), stroke_rgb=(0, 160, 0), stroke_width=2.0)
        canvas.draw_rect(292, y, 100, 60, fill_rgb=(200, 220, 255), stroke_rgb=(0, 0, 180), stroke_width=2.0)
        y += 90

        canvas.draw_text('Ellipses', 72, y, None)
        y += 16

        canvas.draw_ellipse(72,  y, 120, 80, fill_rgb=(220, 80, 80))
        canvas.draw_ellipse(210, y, 120, 80, fill_rgb=(80, 200, 80))
        canvas.draw_ellipse(348, y, 100, 80, stroke_rgb=(0, 0, 200), stroke_width=2.0)
        y += 100

        canvas.draw_text('Mixed shapes and lines', 72, y, None)
        y += 16

        # Crosshair inside a circle
        cx, cy, r = 160, y + 50, 40
        canvas.draw_ellipse(cx - r, cy - r, r * 2, r * 2, stroke_rgb=(0, 0, 0), stroke_width=1.0)
        canvas.draw_line(cx - r, cy, cx + r, cy, r=0, g=0, b=0, width=0.5)
        canvas.draw_line(cx, cy - r, cx, cy + r, r=0, g=0, b=0, width=0.5)

    doc.save(os.path.join(output_dir, 'example_03_shapes.pdf'))

print('Written to', os.path.join(output_dir, 'example_03_shapes.pdf'))
