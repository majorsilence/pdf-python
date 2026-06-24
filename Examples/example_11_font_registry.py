#!/usr/bin/env python3
"""
Example 11 — Font Registry

Shows text set in multiple fonts loaded from .ttf files.
Set FONT_DIR to a directory containing TrueType fonts.
If not set, the example runs with built-in Helvetica as a fallback.

Usage:
    PDFNATIVE_LIB=/path/to/libpdfnative.so \
    FONT_DIR=/usr/share/fonts/truetype/liberation \
    python example_11_font_registry.py
"""

import os, sys, glob
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
from majorsilence_pdf import load_library, PdfDocument, PdfStyle, A4

lib_path = os.environ.get('PDFNATIVE_LIB', '')
if not lib_path:
    sys.exit('Set PDFNATIVE_LIB to the path of the pdfnative shared library.')

font_dir   = os.environ.get('FONT_DIR', '')
output_dir = os.path.join(os.path.dirname(__file__), 'output')
os.makedirs(output_dir, exist_ok=True)
lib = load_library(lib_path)

W, H = A4
SAMPLE = 'The quick brown fox jumps over the lazy dog  0123456789'

with PdfDocument(lib) as doc:
    doc.set_title('Font Registry')

    with doc.add_page(W, H) as canvas:
        with PdfStyle(lib) as h:
            h.set_size(18).set_bold()
            canvas.draw_text('Font Registry', 72, 50, h)

        y = 80.0

        font_files = sorted(glob.glob(os.path.join(font_dir, '*.ttf'))) if font_dir else []

        if font_files:
            with PdfStyle(lib) as info:
                info.set_size(9).set_color(100, 100, 100)
                canvas.draw_text(f'Loaded {len(font_files)} font(s) from {font_dir}', 72, y, info)
            y += 16

            for font_path in font_files[:12]:  # cap at 12 to stay on one page
                name = os.path.splitext(os.path.basename(font_path))[0]
                with PdfStyle(lib) as lbl:
                    lbl.set_size(8).set_color(100, 100, 100)
                    canvas.draw_text(name, 72, y, lbl)
                y += 11
                with PdfStyle(lib) as s:
                    s.set_font_file(font_path).set_size(12)
                    canvas.draw_text(SAMPLE, 72, y, s)
                y += 20
                canvas.draw_line(72, y, W - 72, y, r=220, g=220, b=220, width=0.3)
                y += 6
        else:
            with PdfStyle(lib) as info:
                info.set_size(10).set_color(180, 0, 0)
                canvas.draw_text('FONT_DIR not set — falling back to built-in Helvetica.', 72, y, info)
                y += 16
                info.set_color(80, 80, 80)
                canvas.draw_text(
                    'Set FONT_DIR to a directory of .ttf files (e.g. /usr/share/fonts/truetype).',
                    72, y, info,
                )
            y += 30

            with PdfStyle(lib) as lbl:
                lbl.set_size(8).set_color(100, 100, 100)
            with PdfStyle(lib) as s:
                s.set_size(12)
            for variant, bold, italic in [
                ('Regular',     False, False),
                ('Bold',        True,  False),
                ('Italic',      False, True),
                ('Bold-Italic', True,  True),
            ]:
                with PdfStyle(lib) as lbl2:
                    lbl2.set_size(8).set_color(100, 100, 100)
                    canvas.draw_text(f'Helvetica {variant}', 72, y, lbl2)
                y += 11
                with PdfStyle(lib) as s2:
                    s2.set_size(12)
                    if bold:
                        s2.set_bold()
                    if italic:
                        s2.set_italic()
                    canvas.draw_text(SAMPLE, 72, y, s2)
                y += 20

    doc.save(os.path.join(output_dir, 'example_11_font_registry.pdf'))

print('Written to', os.path.join(output_dir, 'example_11_font_registry.pdf'))
