#!/usr/bin/env python3
"""
Example 17 — Images from Disk

Reads JPEG images from disk and embeds them.
Set IMAGE_DIR to a directory containing .jpg/.jpeg files, or
IMAGE_PATH to a single image file. Falls back to a synthetic image.

Usage:
    PDFNATIVE_LIB=/path/to/libpdfnative.so IMAGE_DIR=/path/to/photos python example_17_images_from_disk.py
"""

import os, sys, glob
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
from majorsilence_pdf import load_library, PdfDocument, PdfStyle, A4

lib_path = os.environ.get('PDFNATIVE_LIB', '')
if not lib_path:
    sys.exit('Set PDFNATIVE_LIB to the path of the pdfnative shared library.')

image_dir  = os.environ.get('IMAGE_DIR', '')
image_path = os.environ.get('IMAGE_PATH', '')
output_dir = os.path.join(os.path.dirname(__file__), 'output')
os.makedirs(output_dir, exist_ok=True)
lib = load_library(lib_path)

W, H   = A4
MARGIN = 50.0


def synthetic_rgb(width: int, height: int, r_base: int, g_base: int, b_base: int) -> bytes:
    """Simple solid-colour gradient tile."""
    pixels = bytearray(width * height * 3)
    idx = 0
    for py in range(height):
        for px in range(width):
            pixels[idx]     = min(255, r_base + px * 2)
            pixels[idx + 1] = min(255, g_base + py * 2)
            pixels[idx + 2] = b_base
            idx += 3
    return bytes(pixels)


# Collect image paths to embed
jpeg_paths: list[str] = []
if image_path and os.path.exists(image_path):
    jpeg_paths = [image_path]
elif image_dir and os.path.isdir(image_dir):
    jpeg_paths = sorted(
        glob.glob(os.path.join(image_dir, '*.jpg')) +
        glob.glob(os.path.join(image_dir, '*.jpeg')),
    )[:6]  # up to 6

with PdfDocument(lib) as doc:
    doc.set_title('Images from Disk')

    with doc.add_page(W, H) as canvas:
        with PdfStyle(lib) as h:
            h.set_size(18).set_bold()
            canvas.draw_text('Images from Disk', MARGIN, 40, h)

        cap_s = PdfStyle(lib).set_size(8).set_color(80, 80, 80)
        y     = 68.0

        if jpeg_paths:
            with PdfStyle(lib) as info:
                info.set_size(9).set_color(80, 80, 80)
                canvas.draw_text(f'Embedding {len(jpeg_paths)} JPEG(s)', MARGIN, y, info)
            y += 14

            thumb_w, thumb_h = 140, 105
            cols = 3
            for i, path in enumerate(jpeg_paths):
                col = i % cols
                row = i // cols
                bx  = MARGIN + col * (thumb_w + 8)
                by  = y + row * (thumb_h + 24)
                data = open(path, 'rb').read()
                canvas.draw_image(data, 0, 0, bx, by, thumb_w, thumb_h, is_jpeg=True)
                canvas.draw_text(os.path.basename(path)[:24], bx, by + thumb_h + 4, cap_s)

        else:
            with PdfStyle(lib) as info:
                info.set_size(10).set_color(160, 80, 0)
                canvas.draw_text(
                    'IMAGE_DIR or IMAGE_PATH not set. Using synthetic images.',
                    MARGIN, y, info,
                )
            y += 18

            synthetics = [
                ('Red-gradient tile',   200, 80,  0),
                ('Blue-gradient tile',  0,   80,  200),
                ('Green-gradient tile', 0,   160, 80),
                ('Purple-gradient',     120, 0,   160),
            ]
            thumb_w, thumb_h = 100, 60
            for i, (label_text, r, g, b) in enumerate(synthetics):
                data = synthetic_rgb(thumb_w, thumb_h, r, g, b)
                bx   = MARGIN + i * (thumb_w + 10)
                canvas.draw_image(data, thumb_w, thumb_h, bx, y, thumb_w, thumb_h, is_jpeg=False)
                canvas.draw_text(label_text, bx, y + thumb_h + 4, cap_s)

            y += thumb_h + 24

            with PdfStyle(lib) as note:
                note.set_size(9).set_color(130, 130, 130)
                canvas.draw_textbox(
                    'Set IMAGE_DIR=/path/to/photos to embed real JPEG images, '
                    'or IMAGE_PATH=/path/to/photo.jpg for a single image.',
                    MARGIN, y, W - 2 * MARGIN, 50, note,
                )

        cap_s.close()

    doc.save(os.path.join(output_dir, 'example_17_images_from_disk.pdf'))

print('Written to', os.path.join(output_dir, 'example_17_images_from_disk.pdf'))
