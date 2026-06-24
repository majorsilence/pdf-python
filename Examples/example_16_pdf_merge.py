#!/usr/bin/env python3
"""
Example 05 — PDF Merge

Creates two PDF documents in memory and merges them into a single file.

Usage:
    PDFNATIVE_LIB=/path/to/libpdfnative.so python example_05_merge.py
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
from majorsilence_pdf import load_library, PdfDocument, PdfStyle, PdfMerger, A4

lib_path = os.environ.get('PDFNATIVE_LIB', '')
if not lib_path:
    sys.exit('Set PDFNATIVE_LIB to the path of the pdfnative shared library.')

output_dir = os.path.join(os.path.dirname(__file__), 'output')
os.makedirs(output_dir, exist_ok=True)

lib = load_library(lib_path)


def make_page(title: str, body: str) -> bytes:
    """Return a single-page PDF as bytes."""
    with PdfDocument(lib) as doc:
        doc.set_title(title)
        with doc.add_page(*A4) as canvas:
            with PdfStyle(lib) as h:
                h.set_size(20).set_bold()
                canvas.draw_text(title, 72, 80, h)
            with PdfStyle(lib) as b:
                b.set_size(12)
                canvas.draw_text(body, 72, 120, b)
        return doc.save_to_memory()


pdf1 = make_page('Document 1 — Cover', 'This is the first document, rendered into memory.')
pdf2 = make_page('Document 2 — Appendix', 'This is the second document, also rendered into memory.')

with PdfMerger(lib) as merger:
    merger.add_bytes(pdf1)
    merger.add_bytes(pdf2)
    out = os.path.join(output_dir, 'example_05_merge.pdf')
    merger.save(out)

print('Merged PDF written to', out)
