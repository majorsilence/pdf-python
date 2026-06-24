#!/usr/bin/env python3
"""
Example 08 — Annotations (Hyperlinks)

Adds clickable URI hyperlink annotations using pdf_canvas_add_link.

Usage:
    PDFNATIVE_LIB=/path/to/libpdfnative.so python example_08_annotations.py
"""

import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
from majorsilence_pdf import load_library, PdfDocument, PdfStyle, A4, DECOR_UNDERLINE

lib_path = os.environ.get('PDFNATIVE_LIB', '')
if not lib_path:
    sys.exit('Set PDFNATIVE_LIB to the path of the pdfnative shared library.')

output_dir = os.path.join(os.path.dirname(__file__), 'output')
os.makedirs(output_dir, exist_ok=True)
lib = load_library(lib_path)

W, H = A4

with PdfDocument(lib) as doc:
    doc.set_title('Annotations')
    doc.set_subject('Hyperlink annotation demo')

    with doc.add_page(W, H) as canvas:
        with PdfStyle(lib) as h:
            h.set_size(18).set_bold()
            canvas.draw_text('Hyperlink Annotations', 72, 50, h)

        with PdfStyle(lib) as body:
            body.set_size(11)
            canvas.draw_text(
                'Click the links below. The blue underlined text is overlaid with a URI annotation.',
                72, 80, body,
            )

        y = 120.0

        # Each link: draw styled text, then add an annotation rectangle over it.
        links = [
            ('Majorsilence GitHub',          'https://github.com/majorsilence'),
            ('Majorsilence Reporting',        'https://github.com/majorsilence/Reporting'),
            ('PDF Specification (ISO 32000)', 'https://pdfa.org/resource/pdf-specification-archive/'),
            ('Wikipedia — PDF',               'https://en.wikipedia.org/wiki/PDF'),
        ]

        with PdfStyle(lib) as link_style:
            link_style.set_size(13).set_color(26, 86, 160).set_decoration(DECOR_UNDERLINE)
            for text, uri in links:
                canvas.draw_text(text, 72, y, link_style)
                # Approximate text width: ~7 pt per character at 13 pt
                approx_width = len(text) * 7.5
                canvas.add_link(72, y - 13, approx_width, 18, uri)
                y += 28

        y += 10
        with PdfStyle(lib) as body:
            body.set_size(10).set_color(100, 100, 100)
            canvas.draw_text('Links use pdf_canvas_add_link(canvas, x, y, width, height, uri).', 72, y, body)
            y += 16
            canvas.draw_text('The annotation rectangle is placed over the rendered text.', 72, y, body)

    doc.save(os.path.join(output_dir, 'example_08_annotations.pdf'))

print('Written to', os.path.join(output_dir, 'example_08_annotations.pdf'))
