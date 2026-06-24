#!/usr/bin/env python3
"""
Example 06 — Password Protection (Security)

Creates an AES-256 password-protected PDF.  The document can only be opened
with the user password "userpass"; full editing requires "ownerpass".

Usage:
    PDFNATIVE_LIB=/path/to/libpdfnative.so python example_06_security.py
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
from majorsilence_pdf import (
    load_library, PdfDocument, PdfStyle, A4,
    PERM_PRINT, PERM_COPY_TEXT, PERM_PRINT_HIGH_QUALITY,
)

lib_path = os.environ.get('PDFNATIVE_LIB', '')
if not lib_path:
    sys.exit('Set PDFNATIVE_LIB to the path of the pdfnative shared library.')

output_dir = os.path.join(os.path.dirname(__file__), 'output')
os.makedirs(output_dir, exist_ok=True)

lib = load_library(lib_path)

with PdfDocument(lib) as doc:
    doc.set_title('Password Protected Document')
    doc.set_author('Majorsilence PDF')

    # AES-256 encryption.  User password = "userpass", owner password = "ownerpass".
    # Only print and copy-text are permitted when opened with the user password.
    doc.set_security(
        user_password='userpass',
        owner_password='ownerpass',
        permissions=PERM_PRINT | PERM_COPY_TEXT | PERM_PRINT_HIGH_QUALITY,
        aes256=True,
    )

    with doc.add_page(*A4) as canvas:
        with PdfStyle(lib) as heading:
            heading.set_size(20).set_bold()
            canvas.draw_text('Password Protected PDF', 72, 80, heading)

        with PdfStyle(lib) as body:
            body.set_size(12)
            canvas.draw_text('This document is encrypted with AES-256.', 72, 120, body)
            canvas.draw_text('Open it with password: userpass', 72, 140, body)
            canvas.draw_text('Full editing requires password: ownerpass', 72, 160, body)
            canvas.draw_text('Allowed operations: Print, CopyText, PrintHighQuality', 72, 180, body)

    out = os.path.join(output_dir, 'example_06_security.pdf')
    doc.save(out)

print('Password-protected PDF written to', out)
print('User password: userpass   |   Owner password: ownerpass')
