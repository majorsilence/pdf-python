#!/usr/bin/env python3
"""
Example 05 — Multi-Page Document

Creates a three-page document: cover, content, and summary.

Usage:
    PDFNATIVE_LIB=/path/to/libpdfnative.so python example_05_multipage.py
"""

import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
from majorsilence_pdf import load_library, PdfDocument, PdfStyle, PdfTable, A4

lib_path = os.environ.get('PDFNATIVE_LIB', '')
if not lib_path:
    sys.exit('Set PDFNATIVE_LIB to the path of the pdfnative shared library.')

output_dir = os.path.join(os.path.dirname(__file__), 'output')
os.makedirs(output_dir, exist_ok=True)
lib = load_library(lib_path)

W, H = A4

with PdfDocument(lib) as doc:
    doc.set_title('Multi-Page Document')
    doc.set_author('Majorsilence PDF')

    # ── Page 1: Cover ──────────────────────────────────────────────────────────
    with doc.add_page(W, H) as canvas:
        canvas.draw_rect(0, 0, W, 200, fill_rgb=(26, 86, 160))

        with PdfStyle(lib) as s:
            s.set_size(32).set_bold().set_color(255, 255, 255)
            canvas.draw_text('Annual Report 2025', 72, 80, s)

        with PdfStyle(lib) as s:
            s.set_size(14).set_color(200, 220, 255)
            canvas.draw_text('Majorsilence Corporation', 72, 130, s)

        with PdfStyle(lib) as s:
            s.set_size(12)
            canvas.draw_text('This document was generated with the Majorsilence PDF library.', 72, 250, s)
            canvas.draw_text('It demonstrates a multi-page layout with a cover, content page, and summary.', 72, 270, s)

        with PdfStyle(lib) as s:
            s.set_size(10).set_color(120, 120, 120)
            canvas.draw_text('Page 1 of 3', 72, H - 40, s)

    # ── Page 2: Content ────────────────────────────────────────────────────────
    with doc.add_page(W, H) as canvas:
        with PdfStyle(lib) as s:
            s.set_size(18).set_bold()
            canvas.draw_text('Section 1 — Overview', 72, 60, s)

        canvas.draw_line(72, 80, W - 72, 80, r=26, g=86, b=160, width=1.5)

        with PdfStyle(lib) as s:
            s.set_size(11)
            body = (
                'Lorem ipsum dolor sit amet, consectetur adipiscing elit. '
                'Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. '
                'Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris.'
            )
            canvas.draw_textbox(body, 72, 96, W - 144, 80, s)

        with PdfStyle(lib) as s:
            s.set_size(14).set_bold()
            canvas.draw_text('Key Metrics', 72, 200, s)

        metrics = [('Revenue',       '$4.2M'), ('Customers', '1,840'),
                   ('New Products',  '12'),    ('Net Score',  '72')]
        for i, (name, value) in enumerate(metrics):
            col = i % 2
            row = i // 2
            bx = 72 + col * 230
            by = 220 + row * 80
            canvas.draw_rect(bx, by, 210, 65, fill_rgb=(240, 245, 252), stroke_rgb=(200, 210, 230), stroke_width=0.5)
            with PdfStyle(lib) as s:
                s.set_size(10).set_color(80, 80, 80)
                canvas.draw_text(name, bx + 10, by + 14, s)
            with PdfStyle(lib) as s:
                s.set_size(20).set_bold().set_color(26, 86, 160)
                canvas.draw_text(value, bx + 10, by + 40, s)

        with PdfStyle(lib) as s:
            s.set_size(10).set_color(120, 120, 120)
            canvas.draw_text('Page 2 of 3', 72, H - 40, s)

    # ── Page 3: Summary table ──────────────────────────────────────────────────
    with doc.add_page(W, H) as canvas:
        with PdfStyle(lib) as s:
            s.set_size(18).set_bold()
            canvas.draw_text('Section 2 — Regional Summary', 72, 60, s)

        canvas.draw_line(72, 80, W - 72, 80, r=26, g=86, b=160, width=1.5)

        with PdfTable(lib, [160, 90, 90, 90, 90]) as t:
            t.set_header_bg(26, 86, 160)
            t.set_alternate_bg(240, 245, 252)
            t.set_border(200, 200, 200, 0.5)
            t.set_cell_padding(5)
            t.add_row('Region',        'Q1',     'Q2',     'Q3',     'Q4')
            t.add_row('North America', '$1.1M',  '$1.0M',  '$1.2M',  '$1.4M')
            t.add_row('Europe',        '$0.7M',  '$0.8M',  '$0.9M',  '$0.8M')
            t.add_row('Asia Pacific',  '$0.3M',  '$0.4M',  '$0.4M',  '$0.5M')
            t.add_row('Other',         '$0.1M',  '$0.1M',  '$0.1M',  '$0.1M')
            t.add_row('Total',         '$2.2M',  '$2.3M',  '$2.6M',  '$2.8M')
            canvas.draw_table(t, 72, 96)

        with PdfStyle(lib) as s:
            s.set_size(10).set_color(120, 120, 120)
            canvas.draw_text('Page 3 of 3', 72, H - 40, s)

    doc.save(os.path.join(output_dir, 'example_05_multipage.pdf'))

print('Written to', os.path.join(output_dir, 'example_05_multipage.pdf'))
