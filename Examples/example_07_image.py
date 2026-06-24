#!/usr/bin/env python3
"""
Example 07 — Image

Embeds a programmatically generated RGB24 image and, if JPEG_PATH is set,
also embeds a JPEG loaded from disk.

Usage:
    PDFNATIVE_LIB=/path/to/libpdfnative.so python example_07_image.py
    PDFNATIVE_LIB=... JPEG_PATH=/path/to/photo.jpg python example_07_image.py
"""

import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
from majorsilence_pdf import load_library, PdfDocument, PdfStyle, A4

lib_path = os.environ.get('PDFNATIVE_LIB', '')
if not lib_path:
    sys.exit('Set PDFNATIVE_LIB to the path of the pdfnative shared library.')

jpeg_path  = os.environ.get('JPEG_PATH', '')
output_dir = os.path.join(os.path.dirname(__file__), 'output')
os.makedirs(output_dir, exist_ok=True)
lib = load_library(lib_path)

W, H = A4


def make_gradient(width: int, height: int) -> bytes:
    """Generate a width×height RGB24 colour gradient."""
    pixels = bytearray(width * height * 3)
    idx = 0
    for py in range(height):
        for px in range(width):
            pixels[idx]     = int(255 * px / width)        # R: left→right
            pixels[idx + 1] = int(255 * py / height)       # G: top→bottom
            pixels[idx + 2] = 180                           # B: constant
            idx += 3
    return bytes(pixels)


def make_checkerboard(width: int, height: int, cell: int = 20) -> bytes:
    """Generate a black-and-white checkerboard."""
    pixels = bytearray(width * height * 3)
    idx = 0
    for py in range(height):
        for px in range(width):
            v = 255 if ((px // cell) + (py // cell)) % 2 == 0 else 60
            pixels[idx] = pixels[idx + 1] = pixels[idx + 2] = v
            idx += 3
    return bytes(pixels)


with PdfDocument(lib) as doc:
    doc.set_title('Image Embedding')

    with doc.add_page(W, H) as canvas:
        with PdfStyle(lib) as h:
            h.set_size(18).set_bold()
            canvas.draw_text('Image Embedding', 72, 40, h)

        label = PdfStyle(lib)
        label.set_size(10)

        y = 70.0

        # ── Synthetic gradient (raw RGB24) ─────────────────────────────────────
        canvas.draw_text('Synthetic gradient (raw RGB24, 300×150 pixels):', 72, y, label)
        y += 14
        grad = make_gradient(300, 150)
        canvas.draw_image(grad, 300, 150, 72, y, 300, 150, is_jpeg=False)
        y += 165

        # ── Checkerboard ───────────────────────────────────────────────────────
        canvas.draw_text('Checkerboard pattern (raw RGB24, 200×100):', 72, y, label)
        y += 14
        checker = make_checkerboard(200, 100)
        canvas.draw_image(checker, 200, 100, 72, y, 200, 100, is_jpeg=False)
        y += 115

        # ── Scaled versions ────────────────────────────────────────────────────
        canvas.draw_text('Same gradient at different scales:', 72, y, label)
        y += 14
        x_pos = 72
        for draw_w, draw_h in ((80, 40), (120, 60), (160, 80)):
            canvas.draw_image(grad, 300, 150, x_pos, y, draw_w, draw_h, is_jpeg=False)
            canvas.draw_text(f'{draw_w}×{draw_h} pts', x_pos, y + draw_h + 2, label)
            x_pos += draw_w + 10
        y += 100

        # ── JPEG from disk ─────────────────────────────────────────────────────
        if jpeg_path and os.path.exists(jpeg_path):
            canvas.draw_text(f'JPEG from disk: {os.path.basename(jpeg_path)}', 72, y, label)
            y += 14
            jpeg_bytes = open(jpeg_path, 'rb').read()
            canvas.draw_image(jpeg_bytes, 0, 0, 72, y, 200, 150, is_jpeg=True)
        else:
            canvas.draw_text('Set JPEG_PATH=/path/to/photo.jpg to embed a JPEG from disk.', 72, y, label)

        label.close()

    doc.save(os.path.join(output_dir, 'example_07_image.pdf'))

print('Written to', os.path.join(output_dir, 'example_07_image.pdf'))
