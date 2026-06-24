#!/usr/bin/env python3
"""
Example 01 — Hello World

Creates a single A4 page PDF with a title and some text.

Usage:
    PDFNATIVE_LIB=/path/to/libpdfnative.so python example_01_hello_world.py
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
from majorsilence_pdf import load_library, PdfDocument, PdfStyle, A4, ALIGN_CENTER

lib_path = os.environ.get('PDFNATIVE_LIB', '')
if not lib_path:
    sys.exit('Set PDFNATIVE_LIB to the path of the pdfnative shared library.')

output_dir = os.path.join(os.path.dirname(__file__), 'output')
os.makedirs(output_dir, exist_ok=True)

lib = load_library(lib_path)

with PdfDocument(lib) as doc:
    doc.set_title('Hello World')
    doc.set_author('Majorsilence PDF')

    with doc.add_page(*A4) as canvas:
        with PdfStyle(lib) as heading:
            heading.set_size(24).set_bold()
            canvas.draw_text('Hello, PDF!', 72, 80, heading)

        with PdfStyle(lib) as body:
            body.set_size(12)
            canvas.draw_text('This PDF was created with the Majorsilence pdfnative library.', 72, 120, body)
            canvas.draw_text('No .NET runtime is required — the engine runs in-process via FFI.', 72, 140, body)

        with PdfStyle(lib) as centered:
            centered.set_size(10).set_italic().set_alignment(ALIGN_CENTER)
            canvas.draw_text('Page 1', 72, 800, centered)

    doc.save(os.path.join(output_dir, 'example_01_hello_world.pdf'))

print('Written to', os.path.join(output_dir, 'example_01_hello_world.pdf'))
