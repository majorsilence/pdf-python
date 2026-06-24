#!/usr/bin/env python3
"""
Example 09 — Invoice

A realistic single-page invoice layout using text, lines, and a table.

Usage:
    PDFNATIVE_LIB=/path/to/libpdfnative.so python example_09_invoice.py
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

W, H   = A4
MARGIN = 60.0
BLUE_R, BLUE_G, BLUE_B = 26, 86, 160

with PdfDocument(lib) as doc:
    doc.set_title('Invoice #INV-2025-042')
    doc.set_author('Acme Corporation')

    with doc.add_page(W, H) as canvas:

        # ── Header band ────────────────────────────────────────────────────────
        canvas.draw_rect(0, 0, W, 100, fill_rgb=(BLUE_R, BLUE_G, BLUE_B))

        with PdfStyle(lib) as s:
            s.set_size(28).set_bold().set_color(255, 255, 255)
            canvas.draw_text('ACME CORPORATION', MARGIN, 30, s)
        with PdfStyle(lib) as s:
            s.set_size(11).set_color(180, 210, 255)
            canvas.draw_text('123 Enterprise Drive · Silicon Valley, CA 94025', MARGIN, 62, s)
            canvas.draw_text('billing@acme.example  ·  +1 (800) 555-0100', MARGIN, 78, s)
        with PdfStyle(lib) as s:
            s.set_size(22).set_bold().set_color(255, 255, 255)
            canvas.draw_text('INVOICE', W - 160, 40, s)

        # ── Invoice metadata (right column) ────────────────────────────────────
        y_meta = 118.0
        meta_right = W - MARGIN - 140
        with PdfStyle(lib) as label_s:
            label_s.set_size(9).set_color(100, 100, 100)
            with PdfStyle(lib) as value_s:
                value_s.set_size(10).set_bold()
                for k, v in [
                    ('Invoice No.', 'INV-2025-042'),
                    ('Date',        '2025-11-15'),
                    ('Due Date',    '2025-12-15'),
                    ('Currency',    'USD'),
                ]:
                    canvas.draw_text(k, meta_right, y_meta, label_s)
                    canvas.draw_text(v, meta_right + 70, y_meta, value_s)
                    y_meta += 16

        # ── Bill To (left column) ──────────────────────────────────────────────
        y_bill = 118.0
        with PdfStyle(lib) as s:
            s.set_size(9).set_bold().set_color(BLUE_R, BLUE_G, BLUE_B)
            canvas.draw_text('BILL TO', MARGIN, y_bill, s)
        y_bill += 14
        with PdfStyle(lib) as s:
            s.set_size(10).set_bold()
            canvas.draw_text('Globex Enterprises Ltd.', MARGIN, y_bill, s)
        y_bill += 14
        with PdfStyle(lib) as s:
            s.set_size(10)
            for line in ['Attn: Mr. H. J. Simpson', '742 Evergreen Terrace', 'Springfield, IL 62701']:
                canvas.draw_text(line, MARGIN, y_bill, s)
                y_bill += 14

        # ── Divider ────────────────────────────────────────────────────────────
        y = 220.0
        canvas.draw_line(MARGIN, y, W - MARGIN, y, r=200, g=200, b=200, width=0.5)
        y += 12

        # ── Line items table ───────────────────────────────────────────────────
        with PdfTable(lib, [210, 50, 80, 80, 80]) as t:
            t.set_header_bg(BLUE_R, BLUE_G, BLUE_B)
            t.set_alternate_bg(245, 248, 255)
            t.set_border(210, 210, 210, 0.5)
            t.set_cell_padding(5)
            t.add_row('Description',      'Qty', 'Unit Price', 'Discount', 'Line Total')
            t.add_row('PDF Library Pro',   '3',   '$400.00',    '10%',      '$1,080.00')
            t.add_row('Report Designer',   '1',   '$250.00',    '—',        '$250.00')
            t.add_row('Integration Pack',  '2',   '$180.00',    '—',        '$360.00')
            t.add_row('Priority Support',  '1',   '$500.00',    '—',        '$500.00')
            canvas.draw_table(t, MARGIN, y)
        y += 185

        # ── Totals ─────────────────────────────────────────────────────────────
        totals = [
            ('Subtotal',  '$2,190.00', False),
            ('Tax (8%)',  '$175.20',   False),
            ('Total Due', '$2,365.20', True),
        ]
        canvas.draw_line(W - 220, y, W - MARGIN, y, r=BLUE_R, g=BLUE_G, b=BLUE_B, width=0.5)
        y += 6
        for label_text, amount, is_total in totals:
            with PdfStyle(lib) as s:
                s.set_size(11 if is_total else 10)
                if is_total:
                    s.set_bold()
                canvas.draw_text(label_text, W - 220, y, s)
                canvas.draw_text(amount, W - MARGIN - 60, y, s)
            y += 18
        canvas.draw_line(W - 220, y, W - MARGIN, y, r=BLUE_R, g=BLUE_G, b=BLUE_B, width=1.0)

        # ── Footer ─────────────────────────────────────────────────────────────
        canvas.draw_line(MARGIN, H - 60, W - MARGIN, H - 60, r=200, g=200, b=200, width=0.5)
        with PdfStyle(lib) as s:
            s.set_size(8).set_color(130, 130, 130)
            canvas.draw_text('Payment terms: Net 30. Make cheques payable to Acme Corporation.', MARGIN, H - 48, s)
            canvas.draw_text('Bank: First National · Routing 021000021 · Account 123456789', MARGIN, H - 36, s)

    doc.save(os.path.join(output_dir, 'example_09_invoice.pdf'))

print('Written to', os.path.join(output_dir, 'example_09_invoice.pdf'))
