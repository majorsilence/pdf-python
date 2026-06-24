#!/usr/bin/env python3
"""
Example 19 — Text Wrapping

Demonstrates pdf_canvas_draw_textbox: long text constrained to a box,
overflow continuation, and alignment modes.

Usage:
    PDFNATIVE_LIB=/path/to/libpdfnative.so python example_19_text_wrapping.py
"""

import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
from majorsilence_pdf import load_library, PdfDocument, PdfStyle, A4, ALIGN_LEFT, ALIGN_CENTER, ALIGN_RIGHT

lib_path = os.environ.get('PDFNATIVE_LIB', '')
if not lib_path:
    sys.exit('Set PDFNATIVE_LIB to the path of the pdfnative shared library.')

output_dir = os.path.join(os.path.dirname(__file__), 'output')
os.makedirs(output_dir, exist_ok=True)
lib = load_library(lib_path)

W, H   = A4
MARGIN = 60.0
TW     = W - 2 * MARGIN   # text box width

LOREM = (
    'Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod '
    'tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, '
    'quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo '
    'consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse '
    'cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non '
    'proident, sunt in culpa qui officia deserunt mollit anim id est laborum.'
)

with PdfDocument(lib) as doc:
    doc.set_title('Text Wrapping')

    with doc.add_page(W, H) as canvas:
        with PdfStyle(lib) as h:
            h.set_size(18).set_bold()
            canvas.draw_text('Text Wrapping with draw_textbox', MARGIN, 44, h)

        y = 70.0
        lbl_s = PdfStyle(lib).set_size(9).set_bold().set_color(26, 86, 160)

        # ── Left-aligned (default) ─────────────────────────────────────────────
        canvas.draw_text('Left-aligned (full width)', MARGIN, y, lbl_s)
        y += 12
        with PdfStyle(lib) as s:
            s.set_size(11).set_alignment(ALIGN_LEFT)
            canvas.draw_textbox(LOREM, MARGIN, y, TW, 80, s)
        canvas.draw_rect(MARGIN, y, TW, 80, stroke_rgb=(200, 200, 200), stroke_width=0.3)
        y += 92

        # ── Centred ────────────────────────────────────────────────────────────
        canvas.draw_text('Centred', MARGIN, y, lbl_s)
        y += 12
        with PdfStyle(lib) as s:
            s.set_size(11).set_alignment(ALIGN_CENTER)
            canvas.draw_textbox(LOREM, MARGIN, y, TW, 80, s)
        canvas.draw_rect(MARGIN, y, TW, 80, stroke_rgb=(200, 200, 200), stroke_width=0.3)
        y += 92

        # ── Right-aligned ──────────────────────────────────────────────────────
        canvas.draw_text('Right-aligned', MARGIN, y, lbl_s)
        y += 12
        with PdfStyle(lib) as s:
            s.set_size(11).set_alignment(ALIGN_RIGHT)
            canvas.draw_textbox(LOREM, MARGIN, y, TW, 80, s)
        canvas.draw_rect(MARGIN, y, TW, 80, stroke_rgb=(200, 200, 200), stroke_width=0.3)
        y += 92

        # ── Narrow column (forces many line breaks) ────────────────────────────
        canvas.draw_text('Narrow column (160 pt wide)', MARGIN, y, lbl_s)
        y += 12
        with PdfStyle(lib) as s:
            s.set_size(10).set_alignment(ALIGN_LEFT)
            canvas.draw_textbox(LOREM, MARGIN, y, 160, 200, s)
        canvas.draw_rect(MARGIN, y, 160, 200, stroke_rgb=(200, 200, 200), stroke_width=0.3)

        # Second column for overflow continuation
        with PdfStyle(lib) as s:
            s.set_size(10).set_alignment(ALIGN_LEFT)
            canvas.draw_textbox(LOREM, MARGIN + 180, y, 160, 200, s)
        canvas.draw_rect(MARGIN + 180, y, 160, 200, stroke_rgb=(200, 200, 200), stroke_width=0.3)

        lbl_s.close()

    doc.save(os.path.join(output_dir, 'example_19_text_wrapping.pdf'))

print('Written to', os.path.join(output_dir, 'example_19_text_wrapping.pdf'))
