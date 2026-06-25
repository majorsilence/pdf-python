"""
pdf_native.py — Python FFI wrapper for the pdfnative shared library.

Loads the Majorsilence PDF engine in-process via ctypes — no subprocess
is spawned, no .NET runtime is required on the host.

Platform-specific library filenames:
  Linux:   libpdfnative.so
  macOS:   libpdfnative.dylib
  Windows: pdfnative.dll

Usage:
    from majorsilence_pdf.pdf_native import load_library, PdfDocument, PdfStyle, PdfTable, PdfMerger

    lib = load_library('/path/to/libpdfnative.so')

    with PdfDocument(lib) as doc:
        doc.set_title('My Report')
        with doc.add_page(595.28, 841.89) as canvas:
            canvas.draw_text('Hello, PDF!', 72, 100)
        doc.save('/tmp/output.pdf')

    # Or export to bytes
    with PdfDocument(lib) as doc:
        with doc.add_page() as canvas:
            canvas.draw_text('Hello', 72, 100)
        data = doc.save_to_memory()

Page sizes (points):
    A4     = (595.28, 841.89)    Letter = (612.0, 792.0)
    A3     = (841.89, 1190.55)   Legal  = (612.0, 1008.0)
    A5     = (419.53, 595.28)    Tabloid= (792.0, 1224.0)
"""

import ctypes
import contextlib
import glob
import os
import platform


def load_library(lib_path: str) -> ctypes.CDLL:
    """
    Load the pdfnative shared library from *lib_path* and initialize the engine.

    Call this once per process before creating any PdfDocument instances.
    Returns the loaded CDLL object to pass to PdfDocument, PdfTable, etc.
    """
    lib_path = os.path.abspath(lib_path)
    lib_dir  = os.path.dirname(lib_path)

    # Set PDFNATIVE_LIB_DIR before loading so pdf_init() can register a DllImportResolver
    # that finds P/Invoke sibling libraries in this directory.
    os.environ['PDFNATIVE_LIB_DIR'] = lib_dir

    # Pre-load all shared libraries in the directory with RTLD_GLOBAL before the final
    # load below.  On .NET 10+, runtime components (libSystem.Native.so etc.) are shared
    # libraries whose symbols must be globally visible for pdfnative.so to load correctly.
    ext = '.dylib' if platform.system() == 'Darwin' else '.so'
    for sibling in sorted(glob.glob(os.path.join(lib_dir, f'*{ext}'))):
        try:
            ctypes.CDLL(sibling, ctypes.RTLD_GLOBAL)
        except OSError:
            pass

    lib = ctypes.CDLL(lib_path)
    _bind_symbols(lib)

    ret = lib.pdf_init()
    if ret != 0:
        raise RuntimeError(f"pdf_init failed: {_decode(lib.pdf_last_error())}")

    return lib


def load_bundled_library() -> ctypes.CDLL:
    """
    Load the pdfnative library bundled alongside this package.

    Raises FileNotFoundError if no native library is present.
    Call load_library() with an explicit path as an alternative.
    """
    native_dir = os.path.join(os.path.dirname(__file__), "native")
    system = platform.system()
    if system == "Linux":
        lib_name = "pdfnative.so"
    elif system == "Darwin":
        lib_name = "pdfnative.dylib"
    elif system == "Windows":
        lib_name = "pdfnative.dll"
    else:
        raise RuntimeError(f"Unsupported platform: {system}")
    lib_path = os.path.join(native_dir, lib_name)
    if not os.path.exists(lib_path):
        raise FileNotFoundError(
            f"No bundled native library found at {lib_path}. "
            "Call load_library() with an explicit path instead."
        )
    return load_library(lib_path)


# ── Page size constants (points) ──────────────────────────────────────────────

A4      = (595.28, 841.89)
A3      = (841.89, 1190.55)
A5      = (419.53, 595.28)
LETTER  = (612.0,  792.0)
LEGAL   = (612.0,  1008.0)
TABLOID = (792.0,  1224.0)

# ── Style alignment and decoration constants ──────────────────────────────────

ALIGN_LEFT   = 0
ALIGN_CENTER = 1
ALIGN_RIGHT  = 2

DECOR_NONE          = 0
DECOR_UNDERLINE     = 1
DECOR_STRIKETHROUGH = 2
DECOR_OVERLINE      = 3

# ── Encryption permission flags ───────────────────────────────────────────────

PERM_PRINT              =    4
PERM_MODIFY_CONTENT     =    8
PERM_COPY_TEXT          =   16
PERM_ADD_ANNOTATIONS    =   32
PERM_FILL_FORMS         =  256
PERM_EXTRACT_TEXT       =  512
PERM_ASSEMBLE           = 1024
PERM_PRINT_HIGH_QUALITY = 2048
PERM_ALL                =   -1


# ── Public classes ────────────────────────────────────────────────────────────

class PdfDocument:
    """A PDF document. Use as a context manager to ensure close() is called."""

    def __init__(self, lib: ctypes.CDLL):
        self._lib = lib
        h = lib.pdf_doc_create()
        if not h:
            _raise(lib, "pdf_doc_create")
        self._handle = h

    def set_title(self, title: str) -> "PdfDocument":
        _check(self._lib.pdf_doc_set_title(self._handle, _enc(title)), self._lib, "pdf_doc_set_title")
        return self

    def set_author(self, author: str) -> "PdfDocument":
        _check(self._lib.pdf_doc_set_author(self._handle, _enc(author)), self._lib, "pdf_doc_set_author")
        return self

    def set_subject(self, subject: str) -> "PdfDocument":
        _check(self._lib.pdf_doc_set_subject(self._handle, _enc(subject)), self._lib, "pdf_doc_set_subject")
        return self

    def set_creator(self, creator: str) -> "PdfDocument":
        _check(self._lib.pdf_doc_set_creator(self._handle, _enc(creator)), self._lib, "pdf_doc_set_creator")
        return self

    def set_security(
        self,
        user_password: str = "",
        owner_password: "str | None" = None,
        permissions: int = PERM_ALL,
        aes256: bool = True,
    ) -> "PdfDocument":
        """
        Apply password-based AES encryption.

        aes256=True  → AES-256 (default, PDF 2.0)
        aes256=False → AES-128 (PDF 1.5+)
        permissions  → bitmask of PERM_* constants; -1 = allow all.
        """
        enc_version = 0 if aes256 else 1
        owner = _enc(owner_password) if owner_password is not None else None
        _check(
            self._lib.pdf_doc_set_security(
                self._handle, _enc(user_password), owner, permissions, enc_version
            ),
            self._lib, "pdf_doc_set_security",
        )
        return self

    def add_page(self, width: float = 595.28, height: float = 841.89) -> "PdfCanvas":
        """Add a page and return a PdfCanvas for drawing on it."""
        h = self._lib.pdf_doc_add_page(self._handle, width, height)
        if not h:
            _raise(self._lib, "pdf_doc_add_page")
        return PdfCanvas(self._lib, h)

    def save(self, path: str) -> None:
        """Write the completed document to *path*."""
        _check(self._lib.pdf_doc_save_file(self._handle, _enc(path)), self._lib, "pdf_doc_save_file")

    def save_to_memory(self) -> bytes:
        """Write the completed document to memory and return the PDF bytes."""
        out_data = ctypes.c_void_p(0)
        out_size = ctypes.c_int(0)
        _check(
            self._lib.pdf_doc_save_buffer(self._handle, ctypes.byref(out_data), ctypes.byref(out_size)),
            self._lib, "pdf_doc_save_buffer",
        )
        try:
            return ctypes.string_at(out_data.value, out_size.value)
        finally:
            self._lib.pdf_free(out_data)

    def close(self) -> None:
        if self._handle:
            self._lib.pdf_doc_close(self._handle)
            self._handle = None

    def __enter__(self) -> "PdfDocument":
        return self

    def __exit__(self, *args) -> None:
        self.close()


class PdfCanvas:
    """A drawing canvas for one page. Use as a context manager."""

    def __init__(self, lib: ctypes.CDLL, handle):
        self._lib    = lib
        self._handle = handle

    def draw_text(
        self,
        text: str,
        x: float,
        y: float,
        style: "PdfStyle | None" = None,
    ) -> "PdfCanvas":
        """Draw *text* with its baseline at (*x*, *y*)."""
        style_h = style._handle if style else None
        _check(
            self._lib.pdf_canvas_draw_text(self._handle, _enc(text), x, y, style_h),
            self._lib, "pdf_canvas_draw_text",
        )
        return self

    def draw_textbox(
        self,
        text: str,
        x: float,
        y: float,
        width: float,
        height: float,
        style: "PdfStyle | None" = None,
        line_spacing: float = 0.0,
    ) -> int:
        """
        Draw word-wrapped text in a box.  Returns the character offset of the
        first character that did not fit (== len(text) if all text was rendered).
        """
        style_h = style._handle if style else None
        ret = self._lib.pdf_canvas_draw_textbox(
            self._handle, _enc(text), x, y, width, height, style_h, line_spacing
        )
        if ret < 0:
            _raise(self._lib, "pdf_canvas_draw_textbox")
        return ret

    def draw_line(
        self,
        x1: float, y1: float,
        x2: float, y2: float,
        r: int = 0, g: int = 0, b: int = 0,
        width: float = 1.0,
    ) -> "PdfCanvas":
        """Draw a straight line from (*x1*, *y1*) to (*x2*, *y2*)."""
        _check(
            self._lib.pdf_canvas_draw_line(self._handle, x1, y1, x2, y2, r, g, b, width),
            self._lib, "pdf_canvas_draw_line",
        )
        return self

    def draw_rect(
        self,
        x: float, y: float,
        width: float, height: float,
        fill_rgb: "tuple[int,int,int] | None" = None,
        stroke_rgb: "tuple[int,int,int] | None" = None,
        stroke_width: float = 1.0,
    ) -> "PdfCanvas":
        """Draw a rectangle.  Pass fill_rgb and/or stroke_rgb as (r,g,b) tuples."""
        fr, fg, fb = fill_rgb   if fill_rgb   else (0, 0, 0)
        sr, sg, sb = stroke_rgb if stroke_rgb else (0, 0, 0)
        _check(
            self._lib.pdf_canvas_draw_rect(
                self._handle, x, y, width, height,
                fr, fg, fb, 1 if fill_rgb else 0,
                sr, sg, sb, stroke_width, 1 if stroke_rgb else 0,
            ),
            self._lib, "pdf_canvas_draw_rect",
        )
        return self

    def draw_ellipse(
        self,
        x: float, y: float,
        width: float, height: float,
        fill_rgb: "tuple[int,int,int] | None" = None,
        stroke_rgb: "tuple[int,int,int] | None" = None,
        stroke_width: float = 1.0,
    ) -> "PdfCanvas":
        """Draw an ellipse bounded by the given rectangle."""
        fr, fg, fb = fill_rgb   if fill_rgb   else (0, 0, 0)
        sr, sg, sb = stroke_rgb if stroke_rgb else (0, 0, 0)
        _check(
            self._lib.pdf_canvas_draw_ellipse(
                self._handle, x, y, width, height,
                fr, fg, fb, 1 if fill_rgb else 0,
                sr, sg, sb, stroke_width, 1 if stroke_rgb else 0,
            ),
            self._lib, "pdf_canvas_draw_ellipse",
        )
        return self

    def draw_image(
        self,
        data: bytes,
        pixel_width: int,
        pixel_height: int,
        x: float, y: float,
        w: float, h: float,
        is_jpeg: bool = False,
    ) -> "PdfCanvas":
        """
        Draw an image at (*x*, *y*) scaled to (*w* x *h*) points.

        *data* must be either JPEG bytes (is_jpeg=True) or raw RGB24 bytes
        (pixel_width * pixel_height * 3 bytes, is_jpeg=False).
        """
        buf = (ctypes.c_uint8 * len(data)).from_buffer_copy(data)
        _check(
            self._lib.pdf_canvas_draw_image(
                self._handle, buf, len(data),
                pixel_width, pixel_height, 1 if is_jpeg else 0,
                x, y, w, h,
            ),
            self._lib, "pdf_canvas_draw_image",
        )
        return self

    def draw_table(self, table: "PdfTable", x: float, y: float) -> "PdfCanvas":
        """Draw *table* with its top-left corner at (*x*, *y*)."""
        _check(
            self._lib.pdf_canvas_draw_table(self._handle, table._handle, x, y),
            self._lib, "pdf_canvas_draw_table",
        )
        return self

    def add_link(
        self,
        x: float, y: float,
        width: float, height: float,
        uri: str,
    ) -> "PdfCanvas":
        """Add a clickable hyperlink over the given rectangular area."""
        _check(
            self._lib.pdf_canvas_add_link(self._handle, x, y, width, height, _enc(uri)),
            self._lib, "pdf_canvas_add_link",
        )
        return self

    def close(self) -> None:
        if self._handle:
            self._lib.pdf_canvas_close(self._handle)
            self._handle = None

    def __enter__(self) -> "PdfCanvas":
        return self

    def __exit__(self, *args) -> None:
        self.close()


class PdfStyle:
    """
    A text style handle.  Defaults: Helvetica 12 pt black left-aligned.

    Use as a context manager to ensure close() is called:

        with PdfStyle(lib) as style:
            style.set_size(18).set_bold()
            canvas.draw_text('Hello', 72, 100, style)
    """

    def __init__(self, lib: ctypes.CDLL):
        self._lib = lib
        h = lib.pdf_style_create()
        if not h:
            _raise(lib, "pdf_style_create")
        self._handle = h

    def set_font_family(self, family: str) -> "PdfStyle":
        _check(self._lib.pdf_style_set_font_family(self._handle, _enc(family)), self._lib, "pdf_style_set_font_family")
        return self

    def set_font_file(self, path: str) -> "PdfStyle":
        _check(self._lib.pdf_style_set_font_file(self._handle, _enc(path)), self._lib, "pdf_style_set_font_file")
        return self

    def set_size(self, points: float) -> "PdfStyle":
        _check(self._lib.pdf_style_set_size(self._handle, points), self._lib, "pdf_style_set_size")
        return self

    def set_color(self, r: int, g: int, b: int) -> "PdfStyle":
        _check(self._lib.pdf_style_set_color(self._handle, r, g, b), self._lib, "pdf_style_set_color")
        return self

    def set_bold(self, bold: bool = True) -> "PdfStyle":
        _check(self._lib.pdf_style_set_bold(self._handle, 1 if bold else 0), self._lib, "pdf_style_set_bold")
        return self

    def set_italic(self, italic: bool = True) -> "PdfStyle":
        _check(self._lib.pdf_style_set_italic(self._handle, 1 if italic else 0), self._lib, "pdf_style_set_italic")
        return self

    def set_alignment(self, alignment: int) -> "PdfStyle":
        """0 = left, 1 = center, 2 = right.  Use ALIGN_* constants."""
        _check(self._lib.pdf_style_set_alignment(self._handle, alignment), self._lib, "pdf_style_set_alignment")
        return self

    def set_decoration(self, decoration: int) -> "PdfStyle":
        """0 = none, 1 = underline, 2 = strikethrough, 3 = overline.  Use DECOR_* constants."""
        _check(self._lib.pdf_style_set_decoration(self._handle, decoration), self._lib, "pdf_style_set_decoration")
        return self

    def close(self) -> None:
        if self._handle:
            self._lib.pdf_style_close(self._handle)
            self._handle = None

    def __enter__(self) -> "PdfStyle":
        return self

    def __exit__(self, *args) -> None:
        self.close()


class PdfTable:
    """
    A table layout handle.

    Usage:
        with PdfTable(lib, [180, 80, 90, 90]) as table:
            table.set_header_bg(26, 86, 160)
            table.set_alternate_bg(240, 245, 252)
            table.set_border(200, 200, 200, 0.5)
            table.add_row('Product', 'Qty', 'Unit Price', 'Total')
            table.add_row('Widget',  '3',  '$10.00',     '$30.00')
            canvas.draw_table(table, 72, 100)
    """

    def __init__(self, lib: ctypes.CDLL, col_widths: "list[float]"):
        self._lib = lib
        arr = (ctypes.c_float * len(col_widths))(*col_widths)
        h = lib.pdf_table_create(arr, len(col_widths))
        if not h:
            _raise(lib, "pdf_table_create")
        self._handle = h

    def set_header_bg(self, r: int, g: int, b: int) -> "PdfTable":
        _check(self._lib.pdf_table_set_header_bg(self._handle, r, g, b), self._lib, "pdf_table_set_header_bg")
        return self

    def set_alternate_bg(self, r: int, g: int, b: int) -> "PdfTable":
        _check(self._lib.pdf_table_set_alternate_bg(self._handle, r, g, b), self._lib, "pdf_table_set_alternate_bg")
        return self

    def set_border(self, r: int, g: int, b: int, width: float) -> "PdfTable":
        _check(self._lib.pdf_table_set_border(self._handle, r, g, b, width), self._lib, "pdf_table_set_border")
        return self

    def set_cell_padding(self, padding: float) -> "PdfTable":
        _check(self._lib.pdf_table_set_cell_padding(self._handle, padding), self._lib, "pdf_table_set_cell_padding")
        return self

    def add_row(self, *cells: str) -> "PdfTable":
        """Stage all *cells* and commit them as one row."""
        for cell in cells:
            _check(
                self._lib.pdf_table_stage_cell(self._handle, _enc(str(cell))),
                self._lib, "pdf_table_stage_cell",
            )
        _check(self._lib.pdf_table_commit_row(self._handle), self._lib, "pdf_table_commit_row")
        return self

    def close(self) -> None:
        if self._handle:
            self._lib.pdf_table_close(self._handle)
            self._handle = None

    def __enter__(self) -> "PdfTable":
        return self

    def __exit__(self, *args) -> None:
        self.close()


class PdfMerger:
    """
    Merges multiple PDF documents into one.

    Usage:
        with PdfMerger(lib) as merger:
            merger.add_bytes(pdf_bytes_1)
            merger.add_bytes(pdf_bytes_2)
            merger.save('/tmp/merged.pdf')
    """

    def __init__(self, lib: ctypes.CDLL):
        self._lib = lib
        h = lib.pdf_merge_create()
        if not h:
            _raise(lib, "pdf_merge_create")
        self._handle = h

    def add_bytes(self, data: bytes) -> "PdfMerger":
        """Add a PDF supplied as bytes to the merge queue."""
        buf = (ctypes.c_uint8 * len(data)).from_buffer_copy(data)
        _check(
            self._lib.pdf_merge_add_bytes(self._handle, buf, len(data)),
            self._lib, "pdf_merge_add_bytes",
        )
        return self

    def save(self, path: str) -> None:
        """Merge all added PDFs and write the result to *path*."""
        _check(self._lib.pdf_merge_save_file(self._handle, _enc(path)), self._lib, "pdf_merge_save_file")

    def save_to_memory(self) -> bytes:
        """Merge all added PDFs and return the result as bytes."""
        out_data = ctypes.c_void_p(0)
        out_size = ctypes.c_int(0)
        _check(
            self._lib.pdf_merge_save_buffer(self._handle, ctypes.byref(out_data), ctypes.byref(out_size)),
            self._lib, "pdf_merge_save_buffer",
        )
        try:
            return ctypes.string_at(out_data.value, out_size.value)
        finally:
            self._lib.pdf_free(out_data)

    def close(self) -> None:
        if self._handle:
            self._lib.pdf_merge_close(self._handle)
            self._handle = None

    def __enter__(self) -> "PdfMerger":
        return self

    def __exit__(self, *args) -> None:
        self.close()


# ── Internal helpers ──────────────────────────────────────────────────────────

def _bind_symbols(lib: ctypes.CDLL) -> None:
    c_int      = ctypes.c_int
    c_float    = ctypes.c_float
    c_uint8    = ctypes.c_uint8
    c_void_p   = ctypes.c_void_p
    c_char_p   = ctypes.c_char_p
    POINTER    = ctypes.POINTER

    lib.pdf_init.restype  = c_int
    lib.pdf_init.argtypes = []

    lib.pdf_doc_create.restype  = c_void_p
    lib.pdf_doc_create.argtypes = []

    for fn in ('pdf_doc_set_title', 'pdf_doc_set_author', 'pdf_doc_set_subject', 'pdf_doc_set_creator'):
        getattr(lib, fn).restype  = c_int
        getattr(lib, fn).argtypes = [c_void_p, c_char_p]

    lib.pdf_doc_set_security.restype  = c_int
    lib.pdf_doc_set_security.argtypes = [c_void_p, c_char_p, c_char_p, c_int, c_int]

    lib.pdf_doc_add_page.restype  = c_void_p
    lib.pdf_doc_add_page.argtypes = [c_void_p, c_float, c_float]

    lib.pdf_doc_save_file.restype  = c_int
    lib.pdf_doc_save_file.argtypes = [c_void_p, c_char_p]

    lib.pdf_doc_save_buffer.restype  = c_int
    lib.pdf_doc_save_buffer.argtypes = [c_void_p, POINTER(c_void_p), POINTER(c_int)]

    lib.pdf_doc_close.restype  = None
    lib.pdf_doc_close.argtypes = [c_void_p]

    lib.pdf_canvas_draw_text.restype  = c_int
    lib.pdf_canvas_draw_text.argtypes = [c_void_p, c_char_p, c_float, c_float, c_void_p]

    lib.pdf_canvas_draw_textbox.restype  = c_int
    lib.pdf_canvas_draw_textbox.argtypes = [c_void_p, c_char_p, c_float, c_float, c_float, c_float, c_void_p, c_float]

    lib.pdf_canvas_draw_line.restype  = c_int
    lib.pdf_canvas_draw_line.argtypes = [c_void_p, c_float, c_float, c_float, c_float, c_uint8, c_uint8, c_uint8, c_float]

    lib.pdf_canvas_draw_rect.restype  = c_int
    lib.pdf_canvas_draw_rect.argtypes = [
        c_void_p, c_float, c_float, c_float, c_float,
        c_uint8, c_uint8, c_uint8, c_int,
        c_uint8, c_uint8, c_uint8, c_float, c_int,
    ]

    lib.pdf_canvas_draw_ellipse.restype  = c_int
    lib.pdf_canvas_draw_ellipse.argtypes = [
        c_void_p, c_float, c_float, c_float, c_float,
        c_uint8, c_uint8, c_uint8, c_int,
        c_uint8, c_uint8, c_uint8, c_float, c_int,
    ]

    lib.pdf_canvas_draw_image.restype  = c_int
    lib.pdf_canvas_draw_image.argtypes = [
        c_void_p, POINTER(c_uint8), c_int, c_int, c_int, c_int,
        c_float, c_float, c_float, c_float,
    ]

    lib.pdf_canvas_draw_table.restype  = c_int
    lib.pdf_canvas_draw_table.argtypes = [c_void_p, c_void_p, c_float, c_float]

    lib.pdf_canvas_add_link.restype  = c_int
    lib.pdf_canvas_add_link.argtypes = [c_void_p, c_float, c_float, c_float, c_float, c_char_p]

    lib.pdf_canvas_close.restype  = None
    lib.pdf_canvas_close.argtypes = [c_void_p]

    lib.pdf_style_create.restype  = c_void_p
    lib.pdf_style_create.argtypes = []

    lib.pdf_style_set_font_family.restype  = c_int
    lib.pdf_style_set_font_family.argtypes = [c_void_p, c_char_p]

    lib.pdf_style_set_font_file.restype  = c_int
    lib.pdf_style_set_font_file.argtypes = [c_void_p, c_char_p]

    lib.pdf_style_set_size.restype  = c_int
    lib.pdf_style_set_size.argtypes = [c_void_p, c_float]

    lib.pdf_style_set_color.restype  = c_int
    lib.pdf_style_set_color.argtypes = [c_void_p, c_uint8, c_uint8, c_uint8]

    lib.pdf_style_set_bold.restype  = c_int
    lib.pdf_style_set_bold.argtypes = [c_void_p, c_int]

    lib.pdf_style_set_italic.restype  = c_int
    lib.pdf_style_set_italic.argtypes = [c_void_p, c_int]

    lib.pdf_style_set_alignment.restype  = c_int
    lib.pdf_style_set_alignment.argtypes = [c_void_p, c_int]

    lib.pdf_style_set_decoration.restype  = c_int
    lib.pdf_style_set_decoration.argtypes = [c_void_p, c_int]

    lib.pdf_style_close.restype  = None
    lib.pdf_style_close.argtypes = [c_void_p]

    lib.pdf_table_create.restype  = c_void_p
    lib.pdf_table_create.argtypes = [POINTER(c_float), c_int]

    lib.pdf_table_set_header_bg.restype  = c_int
    lib.pdf_table_set_header_bg.argtypes = [c_void_p, c_uint8, c_uint8, c_uint8]

    lib.pdf_table_set_alternate_bg.restype  = c_int
    lib.pdf_table_set_alternate_bg.argtypes = [c_void_p, c_uint8, c_uint8, c_uint8]

    lib.pdf_table_set_border.restype  = c_int
    lib.pdf_table_set_border.argtypes = [c_void_p, c_uint8, c_uint8, c_uint8, c_float]

    lib.pdf_table_set_cell_padding.restype  = c_int
    lib.pdf_table_set_cell_padding.argtypes = [c_void_p, c_float]

    lib.pdf_table_stage_cell.restype  = c_int
    lib.pdf_table_stage_cell.argtypes = [c_void_p, c_char_p]

    lib.pdf_table_commit_row.restype  = c_int
    lib.pdf_table_commit_row.argtypes = [c_void_p]

    lib.pdf_table_close.restype  = None
    lib.pdf_table_close.argtypes = [c_void_p]

    lib.pdf_merge_create.restype  = c_void_p
    lib.pdf_merge_create.argtypes = []

    lib.pdf_merge_add_bytes.restype  = c_int
    lib.pdf_merge_add_bytes.argtypes = [c_void_p, POINTER(c_uint8), c_int]

    lib.pdf_merge_save_file.restype  = c_int
    lib.pdf_merge_save_file.argtypes = [c_void_p, c_char_p]

    lib.pdf_merge_save_buffer.restype  = c_int
    lib.pdf_merge_save_buffer.argtypes = [c_void_p, POINTER(c_void_p), POINTER(c_int)]

    lib.pdf_merge_close.restype  = None
    lib.pdf_merge_close.argtypes = [c_void_p]

    lib.pdf_free.restype  = None
    lib.pdf_free.argtypes = [c_void_p]

    lib.pdf_last_error.restype  = ctypes.c_char_p
    lib.pdf_last_error.argtypes = []


def _enc(s: str) -> bytes:
    return s.encode("utf-8")


def _decode(raw) -> str:
    if raw is None:
        return "unknown error"
    if isinstance(raw, bytes):
        return raw.decode("utf-8")
    return str(raw)


def _check(ret: int, lib: ctypes.CDLL, fn: str) -> None:
    if ret != 0:
        _raise(lib, fn)


def _raise(lib: ctypes.CDLL, fn: str) -> None:
    err = lib.pdf_last_error()
    raise RuntimeError(f"{fn} failed: {_decode(err)}")
