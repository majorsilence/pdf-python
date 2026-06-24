#!/usr/bin/env python3
"""
Example 04 — Table

Creates a styled table with a header, alternating row colours, and a border.

Usage:
    PDFNATIVE_LIB=/path/to/libpdfnative.so python example_04_table.py
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
from majorsilence_pdf import load_library, PdfDocument, PdfStyle, PdfTable, A4

lib_path = os.environ.get('PDFNATIVE_LIB', '')
if not lib_path:
    sys.exit('Set PDFNATIVE_LIB to the path of the pdfnative shared library.')

output_dir = os.path.join(os.path.dirname(__file__), 'output')
os.makedirs(output_dir, exist_ok=True)

lib = load_library(lib_path)

with PdfDocument(lib) as doc:
    doc.set_title('Table Example')

    with doc.add_page(*A4) as canvas:
        with PdfStyle(lib) as heading:
            heading.set_size(18).set_bold()
            canvas.draw_text('Table Layout', 72, 40, heading)

        with PdfStyle(lib) as label:
            label.set_size(10)
            canvas.draw_text('Sales report — styled table with header and alternating rows:', 72, 76, label)

        with PdfTable(lib, [180, 80, 90, 90]) as table:
            table.set_header_bg(26, 86, 160)
            table.set_alternate_bg(240, 245, 252)
            table.set_border(200, 200, 200, 0.5)
            table.set_cell_padding(5)

            table.add_row('Product', 'Qty', 'Unit Price', 'Total')
            table.add_row('PDF Library Pro', '3', '$400.00', '$1,200.00')
            table.add_row('Report Designer', '1', '$250.00', '$250.00')
            table.add_row('Integration Pack', '2', '$180.00', '$360.00')
            table.add_row('Support (12 mo.)', '1', '$500.00', '$500.00')
            table.add_row('', '', 'Total:', '$2,310.00')

            canvas.draw_table(table, 72, 92)

        with PdfStyle(lib) as label:
            label.set_size(10)
            canvas.draw_text('Borderless table:', 72, 330, label)

        with PdfTable(lib, [200, 100, 100]) as report_table:
            report_table.set_alternate_bg(245, 245, 245)
            report_table.set_border(0, 0, 0, 0)
            report_table.set_cell_padding(4)

            report_table.add_row('Region', 'Revenue', 'Growth')
            report_table.add_row('North America', '$1.24M', '+12%')
            report_table.add_row('Europe', '$0.89M', '+8%')
            report_table.add_row('Asia Pacific', '$0.45M', '+18%')
            report_table.add_row('Other', '$0.12M', '+3%')

            canvas.draw_table(report_table, 72, 346)

    doc.save(os.path.join(output_dir, 'example_04_table.pdf'))

print('Written to', os.path.join(output_dir, 'example_04_table.pdf'))
