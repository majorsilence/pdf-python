"""
Tests for pdf_native.py — the Python FFI wrapper for pdfnative.

Requires a pdfnative shared library.  Point PDFNATIVE_LIB at the .so / .dylib /
.dll, or set PDFNATIVE_LIB to "bundled" to use the library copied into the
package's native/ directory by build-native-wheel.sh.

Examples:

    # Against a locally published library
    PDFNATIVE_LIB=/tmp/pdfnative-pub/libpdfnative.so python -m pytest

    # Against the library bundled in an installed wheel
    PDFNATIVE_LIB=bundled python -m pytest

    # Against the library bundled in the package source tree (after running
    # build-native-wheel.sh at least once so native/ is populated)
    PDFNATIVE_LIB=bundled python -m pytest
"""

import os
import tempfile
import unittest

from majorsilence_pdf.pdf_native import (
    load_library, load_bundled_library,
    PdfDocument, PdfCanvas, PdfStyle, PdfTable, PdfMerger,
    A4, LETTER,
    ALIGN_LEFT, ALIGN_CENTER, ALIGN_RIGHT,
    DECOR_UNDERLINE,
    PERM_PRINT, PERM_COPY_TEXT,
)

LIB_ENV = os.environ.get("PDFNATIVE_LIB", "")


def setUpModule():
    if not LIB_ENV:
        raise unittest.SkipTest(
            "PDFNATIVE_LIB not set — skipping pdfnative tests.\n"
            "Set it to the path of libpdfnative.so or to 'bundled'."
        )


_lib = None


def _get_lib():
    global _lib
    if _lib is None:
        if LIB_ENV == "bundled":
            _lib = load_bundled_library()
        else:
            if not os.path.isfile(LIB_ENV):
                raise unittest.SkipTest(f"PDFNATIVE_LIB={LIB_ENV!r} does not exist")
            _lib = load_library(LIB_ENV)
    return _lib


def _is_pdf(data: bytes) -> bool:
    return data[:4] == b"%PDF"


class TestHelloWorld(unittest.TestCase):
    """Minimal document: one page, one draw_text call, save to memory."""

    def test_save_to_memory_returns_pdf(self):
        lib = _get_lib()
        with PdfDocument(lib) as doc:
            doc.set_title("Test Hello World")
            with doc.add_page(*A4) as canvas:
                with PdfStyle(lib) as s:
                    s.set_size(14.0).set_bold()
                    canvas.draw_text("Hello, PDF!", 72.0, 100.0, s)
            data = doc.save_to_memory()
        self.assertGreater(len(data), 500)
        self.assertTrue(_is_pdf(data), "Expected %PDF magic bytes")

    def test_save_to_file(self):
        lib = _get_lib()
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as f:
            out = f.name
        try:
            with PdfDocument(lib) as doc:
                with doc.add_page(*A4) as canvas:
                    with PdfStyle(lib) as s:
                        s.set_size(12.0)
                        canvas.draw_text("File output test", 72.0, 100.0, s)
                doc.save(out)
            self.assertGreater(os.path.getsize(out), 500)
        finally:
            if os.path.isfile(out):
                os.unlink(out)

    def test_letter_page_size(self):
        lib = _get_lib()
        with PdfDocument(lib) as doc:
            with doc.add_page(*LETTER) as canvas:
                with PdfStyle(lib) as s:
                    s.set_size(12.0)
                    canvas.draw_text("Letter page", 72.0, 100.0, s)
            data = doc.save_to_memory()
        self.assertTrue(_is_pdf(data))


class TestDocumentMetadata(unittest.TestCase):
    """set_title / set_author / set_subject / set_creator."""

    def _build(self, **meta) -> bytes:
        lib = _get_lib()
        with PdfDocument(lib) as doc:
            for k, v in meta.items():
                getattr(doc, f"set_{k}")(v)
            with doc.add_page(*A4) as canvas:
                with PdfStyle(lib) as s:
                    s.set_size(10.0)
                    canvas.draw_text("metadata test", 72.0, 100.0, s)
            return doc.save_to_memory()

    def test_set_title(self):
        data = self._build(title="My Title")
        self.assertTrue(_is_pdf(data))

    def test_set_author(self):
        data = self._build(author="Test Author")
        self.assertTrue(_is_pdf(data))

    def test_set_subject(self):
        data = self._build(subject="Test Subject")
        self.assertTrue(_is_pdf(data))

    def test_set_creator(self):
        data = self._build(creator="Test Creator")
        self.assertTrue(_is_pdf(data))

    def test_all_metadata(self):
        data = self._build(
            title="Full Meta", author="A", subject="B", creator="C"
        )
        self.assertTrue(_is_pdf(data))


class TestTextStyles(unittest.TestCase):
    """PdfStyle variants: sizes, bold, italic, colour, alignment, decoration."""

    def _page_with_texts(self, styles_and_text):
        lib = _get_lib()
        with PdfDocument(lib) as doc:
            with doc.add_page(*A4) as canvas:
                y = 50.0
                for setup_fn, text in styles_and_text:
                    with PdfStyle(lib) as s:
                        setup_fn(s)
                        canvas.draw_text(text, 72.0, y, s)
                    y += 20.0
            return doc.save_to_memory()

    def test_various_sizes(self):
        items = [
            (lambda s: s.set_size(size), f"{size} pt text")
            for size in (8, 10, 12, 14, 18, 24, 36)
        ]
        data = self._page_with_texts(items)
        self.assertTrue(_is_pdf(data))

    def test_bold_italic(self):
        data = self._page_with_texts([
            (lambda s: s.set_size(12.0).set_bold(),             "Bold text"),
            (lambda s: s.set_size(12.0).set_italic(),           "Italic text"),
            (lambda s: s.set_size(12.0).set_bold().set_italic(), "Bold-italic"),
        ])
        self.assertTrue(_is_pdf(data))

    def test_colour(self):
        data = self._page_with_texts([
            (lambda s: s.set_size(12.0).set_color(220, 0, 0),   "Red text"),
            (lambda s: s.set_size(12.0).set_color(0, 0, 200),   "Blue text"),
            (lambda s: s.set_size(12.0).set_color(0, 160, 0),   "Green text"),
        ])
        self.assertTrue(_is_pdf(data))

    def test_alignments(self):
        data = self._page_with_texts([
            (lambda s: s.set_size(12.0).set_alignment(ALIGN_LEFT),   "Left"),
            (lambda s: s.set_size(12.0).set_alignment(ALIGN_CENTER), "Centre"),
            (lambda s: s.set_size(12.0).set_alignment(ALIGN_RIGHT),  "Right"),
        ])
        self.assertTrue(_is_pdf(data))

    def test_decoration_underline(self):
        data = self._page_with_texts([
            (lambda s: s.set_size(12.0).set_decoration(DECOR_UNDERLINE), "Underlined"),
        ])
        self.assertTrue(_is_pdf(data))


class TestShapes(unittest.TestCase):
    """draw_line, draw_rect, draw_ellipse."""

    def _shapes_page(self):
        lib = _get_lib()
        with PdfDocument(lib) as doc:
            with doc.add_page(*A4) as canvas:
                canvas.draw_line(72.0, 50.0, 400.0, 50.0)
                canvas.draw_line(72.0, 70.0, 400.0, 70.0, r=200, g=0, b=0, width=2.0)
                canvas.draw_rect(72.0, 90.0, 200.0, 60.0, fill_rgb=(26, 86, 160))
                canvas.draw_rect(300.0, 90.0, 100.0, 60.0,
                                 stroke_rgb=(200, 0, 0), stroke_width=1.5)
                canvas.draw_ellipse(72.0, 180.0, 150.0, 60.0, fill_rgb=(0, 160, 0))
            return doc.save_to_memory()

    def test_shapes_produce_pdf(self):
        self.assertTrue(_is_pdf(self._shapes_page()))


class TestTextBox(unittest.TestCase):
    """draw_textbox wraps long text to fit a bounding box."""

    LOREM = (
        "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod "
        "tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, "
        "quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat."
    )

    def test_textbox_produces_pdf(self):
        lib = _get_lib()
        with PdfDocument(lib) as doc:
            with doc.add_page(*A4) as canvas:
                with PdfStyle(lib) as s:
                    s.set_size(11.0).set_alignment(ALIGN_LEFT)
                    canvas.draw_textbox(self.LOREM, 72.0, 50.0, 400.0, 120.0, s)
            data = doc.save_to_memory()
        self.assertTrue(_is_pdf(data))

    def test_textbox_all_alignments(self):
        lib = _get_lib()
        with PdfDocument(lib) as doc:
            with doc.add_page(*A4) as canvas:
                y = 50.0
                for align in (ALIGN_LEFT, ALIGN_CENTER, ALIGN_RIGHT):
                    with PdfStyle(lib) as s:
                        s.set_size(11.0).set_alignment(align)
                        canvas.draw_textbox(self.LOREM, 72.0, y, 400.0, 80.0, s)
                    y += 100.0
            data = doc.save_to_memory()
        self.assertTrue(_is_pdf(data))


class TestTable(unittest.TestCase):
    """PdfTable staged-row API."""

    def test_basic_table(self):
        lib = _get_lib()
        with PdfDocument(lib) as doc:
            with doc.add_page(*A4) as canvas:
                with PdfTable(lib, [150.0, 80.0, 80.0]) as t:
                    t.set_header_bg(26, 86, 160)
                    t.set_alternate_bg(240, 245, 252)
                    t.set_border(200, 200, 200, 0.5)
                    t.set_cell_padding(4.0)
                    t.add_row("Product",  "Units", "Revenue")
                    t.add_row("Widget A", "100",   "$500.00")
                    t.add_row("Widget B", "200",   "$900.00")
                    canvas.draw_table(t, 72.0, 50.0)
            data = doc.save_to_memory()
        self.assertTrue(_is_pdf(data))

    def test_single_column_table(self):
        lib = _get_lib()
        with PdfDocument(lib) as doc:
            with doc.add_page(*A4) as canvas:
                with PdfTable(lib, [300.0]) as t:
                    t.set_cell_padding(3.0)
                    for i in range(5):
                        t.add_row(f"Row {i + 1}")
                    canvas.draw_table(t, 72.0, 50.0)
            data = doc.save_to_memory()
        self.assertTrue(_is_pdf(data))


class TestMultipage(unittest.TestCase):
    """Multiple pages in one document."""

    def test_three_pages(self):
        lib = _get_lib()
        with PdfDocument(lib) as doc:
            for i in range(3):
                with doc.add_page(*A4) as canvas:
                    with PdfStyle(lib) as s:
                        s.set_size(18.0).set_bold()
                        canvas.draw_text(f"Page {i + 1}", 72.0, 100.0, s)
            data = doc.save_to_memory()
        self.assertTrue(_is_pdf(data))
        self.assertGreater(len(data), 1000)


class TestImage(unittest.TestCase):
    """draw_image with raw RGB24 pixel data."""

    @staticmethod
    def _gradient(w: int, h: int) -> bytes:
        buf = bytearray(w * h * 3)
        idx = 0
        for py in range(h):
            for px in range(w):
                buf[idx]     = int(255 * px / w)
                buf[idx + 1] = int(255 * py / h)
                buf[idx + 2] = 128
                idx += 3
        return bytes(buf)

    def test_raw_rgb_image(self):
        lib = _get_lib()
        img = self._gradient(100, 60)
        with PdfDocument(lib) as doc:
            with doc.add_page(*A4) as canvas:
                canvas.draw_image(img, 100, 60, 72.0, 50.0, 100.0, 60.0, is_jpeg=False)
            data = doc.save_to_memory()
        self.assertTrue(_is_pdf(data))

    def test_scaled_image(self):
        lib = _get_lib()
        img = self._gradient(50, 50)
        with PdfDocument(lib) as doc:
            with doc.add_page(*A4) as canvas:
                canvas.draw_image(img, 50, 50, 72.0, 50.0, 200.0, 200.0, is_jpeg=False)
            data = doc.save_to_memory()
        self.assertTrue(_is_pdf(data))


class TestAnnotations(unittest.TestCase):
    """add_link URI annotations."""

    def test_hyperlink(self):
        lib = _get_lib()
        with PdfDocument(lib) as doc:
            with doc.add_page(*A4) as canvas:
                with PdfStyle(lib) as s:
                    s.set_size(13.0).set_color(26, 86, 160).set_decoration(DECOR_UNDERLINE)
                    canvas.draw_text("Majorsilence GitHub", 72.0, 100.0, s)
                canvas.add_link(72.0, 87.0, 160.0, 18.0, "https://github.com/majorsilence")
            data = doc.save_to_memory()
        self.assertTrue(_is_pdf(data))


class TestMerger(unittest.TestCase):
    """PdfMerger combines multiple PDF byte streams."""

    @staticmethod
    def _make_pdf(title: str) -> bytes:
        lib = _get_lib()
        with PdfDocument(lib) as doc:
            doc.set_title(title)
            with doc.add_page(*A4) as canvas:
                with PdfStyle(lib) as s:
                    s.set_size(14.0)
                    canvas.draw_text(title, 72.0, 100.0, s)
            return doc.save_to_memory()

    def test_merge_two_pdfs(self):
        lib = _get_lib()
        pdf1 = self._make_pdf("Document 1")
        pdf2 = self._make_pdf("Document 2")
        with PdfMerger(lib) as m:
            m.add_bytes(pdf1)
            m.add_bytes(pdf2)
            merged = m.save_to_memory()
        self.assertTrue(_is_pdf(merged))
        self.assertGreater(len(merged), len(pdf1))

    def test_merge_to_file(self):
        lib = _get_lib()
        pdf1 = self._make_pdf("Part A")
        pdf2 = self._make_pdf("Part B")
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as f:
            out = f.name
        try:
            with PdfMerger(lib) as m:
                m.add_bytes(pdf1)
                m.add_bytes(pdf2)
                m.save(out)
            self.assertGreater(os.path.getsize(out), 500)
        finally:
            if os.path.isfile(out):
                os.unlink(out)


class TestSecurity(unittest.TestCase):
    """Password-protected PDF via pdf_doc_set_security."""

    def test_password_protected_pdf(self):
        lib = _get_lib()
        with PdfDocument(lib) as doc:
            doc.set_title("Secret Document")
            doc.set_security(
                user_password="userpass",
                owner_password="ownerpass",
                permissions=PERM_PRINT | PERM_COPY_TEXT,
                aes256=True,
            )
            with doc.add_page(*A4) as canvas:
                with PdfStyle(lib) as s:
                    s.set_size(12.0)
                    canvas.draw_text("Confidential content", 72.0, 100.0, s)
            data = doc.save_to_memory()
        self.assertTrue(_is_pdf(data))
        self.assertGreater(len(data), 500)

    def test_aes128_encryption(self):
        lib = _get_lib()
        with PdfDocument(lib) as doc:
            doc.set_security(
                user_password="pass",
                owner_password="owner",
                permissions=PERM_PRINT,
                aes256=False,
            )
            with doc.add_page(*A4) as canvas:
                with PdfStyle(lib) as s:
                    s.set_size(10.0)
                    canvas.draw_text("AES-128 test", 72.0, 100.0, s)
            data = doc.save_to_memory()
        self.assertTrue(_is_pdf(data))


class TestCustomFont(unittest.TestCase):
    """set_font_file — only runs if CUSTOM_FONT_PATH env var is set."""

    def setUp(self):
        self.font_path = os.environ.get("CUSTOM_FONT_PATH", "")
        if not self.font_path or not os.path.isfile(self.font_path):
            self.skipTest("CUSTOM_FONT_PATH not set or file not found")

    def test_custom_font_renders(self):
        lib = _get_lib()
        with PdfDocument(lib) as doc:
            with doc.add_page(*A4) as canvas:
                with PdfStyle(lib) as s:
                    s.set_font_file(self.font_path).set_size(18.0)
                    canvas.draw_text("Custom font — The quick brown fox", 72.0, 100.0, s)
            data = doc.save_to_memory()
        self.assertTrue(_is_pdf(data))


class TestErrorHandling(unittest.TestCase):
    """Edge-cases that should not crash the process."""

    def test_empty_text_does_not_crash(self):
        lib = _get_lib()
        with PdfDocument(lib) as doc:
            with doc.add_page(*A4) as canvas:
                with PdfStyle(lib) as s:
                    s.set_size(12.0)
                    canvas.draw_text("", 72.0, 100.0, s)
            data = doc.save_to_memory()
        self.assertTrue(_is_pdf(data))

    def test_no_style_draw_text(self):
        lib = _get_lib()
        with PdfDocument(lib) as doc:
            with doc.add_page(*A4) as canvas:
                canvas.draw_text("No explicit style", 72.0, 100.0)
            data = doc.save_to_memory()
        self.assertTrue(_is_pdf(data))

    def test_multiple_saves_same_document(self):
        lib = _get_lib()
        with PdfDocument(lib) as doc:
            with doc.add_page(*A4) as canvas:
                with PdfStyle(lib) as s:
                    s.set_size(12.0)
                    canvas.draw_text("Repeated save", 72.0, 100.0, s)
            data1 = doc.save_to_memory()
            data2 = doc.save_to_memory()
        self.assertTrue(_is_pdf(data1))
        self.assertTrue(_is_pdf(data2))
        self.assertEqual(len(data1), len(data2))


if __name__ == "__main__":
    unittest.main()
