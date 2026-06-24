#!/usr/bin/env python3
"""
Example 10 — Dashboard

A sales dashboard: KPI tiles, a data table, and a bar chart drawn with rectangles.

Usage:
    PDFNATIVE_LIB=/path/to/libpdfnative.so python example_10_dashboard.py
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
MARGIN = 40.0

with PdfDocument(lib) as doc:
    doc.set_title('Q4 2025 Sales Dashboard')

    with doc.add_page(W, H) as canvas:

        # ── Title bar ──────────────────────────────────────────────────────────
        canvas.draw_rect(0, 0, W, 52, fill_rgb=(30, 30, 50))
        with PdfStyle(lib) as s:
            s.set_size(18).set_bold().set_color(255, 255, 255)
            canvas.draw_text('Q4 2025  ·  Sales Dashboard', MARGIN, 16, s)
        with PdfStyle(lib) as s:
            s.set_size(9).set_color(160, 180, 220)
            canvas.draw_text('Generated 2025-12-31', MARGIN, 38, s)

        # ── KPI tiles (2×2 grid) ───────────────────────────────────────────────
        kpis = [
            ('Total Revenue', '$4.2M',  '+12%', (26,  86,  160)),
            ('New Customers', '1,840',  '+8%',  (0,  140,  80)),
            ('Avg Order',     '$2,283', '+5%',  (180, 80,  0)),
            ('NPS Score',     '72',     '+4pt', (120, 0,   160)),
        ]
        tile_w, tile_h = 110, 75
        for i, (title, value, delta, (r, g, b)) in enumerate(kpis):
            col, row = i % 2, i // 2
            bx = MARGIN + col * (tile_w + 8)
            by = 62 + row * (tile_h + 8)
            canvas.draw_rect(bx, by, tile_w, tile_h, fill_rgb=(r, g, b))
            with PdfStyle(lib) as s:
                s.set_size(8).set_color(200, 220, 255)
                canvas.draw_text(title, bx + 6, by + 10, s)
            with PdfStyle(lib) as s:
                s.set_size(20).set_bold().set_color(255, 255, 255)
                canvas.draw_text(value, bx + 6, by + 34, s)
            with PdfStyle(lib) as s:
                s.set_size(9).set_color(200, 255, 200)
                canvas.draw_text(delta, bx + 6, by + 58, s)

        # ── Regional breakdown table ───────────────────────────────────────────
        table_x = MARGIN + 2 * (tile_w + 8) + 16
        with PdfStyle(lib) as s:
            s.set_size(11).set_bold()
            canvas.draw_text('Regional Breakdown', table_x, 64, s)

        with PdfTable(lib, [110, 60, 60, 50]) as t:
            t.set_header_bg(30, 30, 50)
            t.set_alternate_bg(245, 245, 250)
            t.set_border(210, 210, 210, 0.4)
            t.set_cell_padding(4)
            t.add_row('Region',         'Revenue', 'Units', 'Chg')
            t.add_row('North America',  '$1.7M',   '612',   '+14%')
            t.add_row('Europe',         '$1.2M',   '441',   '+9%')
            t.add_row('Asia Pacific',   '$0.9M',   '320',   '+18%')
            t.add_row('LATAM',          '$0.3M',   '110',   '+6%')
            t.add_row('Other',          '$0.1M',   '40',    '+2%')
            canvas.draw_table(t, table_x, 78)

        # ── Quarterly bar chart ────────────────────────────────────────────────
        chart_top = 230.0
        with PdfStyle(lib) as s:
            s.set_size(11).set_bold()
            canvas.draw_text('Quarterly Revenue', MARGIN, chart_top, s)

        chart_top += 16
        chart_h   = 120.0
        chart_bot = chart_top + chart_h
        bar_w     = 40.0
        gap       = 20.0
        revenues  = [2.2, 2.8, 3.5, 4.2]  # $M
        quarters  = ['Q1', 'Q2', 'Q3', 'Q4']
        max_rev   = max(revenues)

        # Axis lines
        canvas.draw_line(MARGIN, chart_top, MARGIN, chart_bot, r=150, g=150, b=150, width=0.5)
        canvas.draw_line(MARGIN, chart_bot, MARGIN + len(revenues) * (bar_w + gap) + gap, chart_bot, r=150, g=150, b=150, width=0.5)

        with PdfStyle(lib) as lbl:
            lbl.set_size(9).set_color(80, 80, 80)
            for i, (rev, qtr) in enumerate(zip(revenues, quarters)):
                bx = MARGIN + gap + i * (bar_w + gap)
                bh = chart_h * rev / max_rev
                by = chart_bot - bh
                canvas.draw_rect(bx, by, bar_w, bh, fill_rgb=(26, 86, 160))
                canvas.draw_text(f'${rev}M', bx + 2, by - 12, lbl)
                canvas.draw_text(qtr, bx + 12, chart_bot + 6, lbl)

        # ── Product mix (pie substitute: stacked bars) ─────────────────────────
        mix_y = chart_bot + 40
        with PdfStyle(lib) as s:
            s.set_size(11).set_bold()
            canvas.draw_text('Product Mix (% of Revenue)', MARGIN, mix_y, s)
        mix_y += 14

        products = [
            ('PDF Library',   42, (26,  86,  160)),
            ('Report Engine', 28, (0,  140,  80)),
            ('Integration',   18, (220, 120, 0)),
            ('Support',       12, (160, 0,   80)),
        ]
        bar_total_w = W - 2 * MARGIN
        x_cur       = MARGIN
        with PdfStyle(lib) as s:
            s.set_size(8).set_color(255, 255, 255)
            for name, pct, (r, g, b) in products:
                seg_w = bar_total_w * pct / 100
                canvas.draw_rect(x_cur, mix_y, seg_w, 22, fill_rgb=(r, g, b))
                if seg_w > 30:
                    canvas.draw_text(f'{pct}%', x_cur + 4, mix_y + 7, s)
                x_cur += seg_w

        # Legend
        mix_y += 30
        with PdfStyle(lib) as s:
            s.set_size(9)
            for i, (name, pct, (r, g, b)) in enumerate(products):
                lx = MARGIN + i * 115
                canvas.draw_rect(lx, mix_y, 10, 10, fill_rgb=(r, g, b))
                canvas.draw_text(f'{name} ({pct}%)', lx + 14, mix_y + 2, s)

    doc.save(os.path.join(output_dir, 'example_10_dashboard.pdf'))

print('Written to', os.path.join(output_dir, 'example_10_dashboard.pdf'))
