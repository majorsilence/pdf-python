# majorsilence-pdf

Python bindings for the [Majorsilence PDF](https://github.com/majorsilence/Reporting) native library — generate PDF documents in-process via an AOT-compiled shared library, with no .NET runtime required at runtime.

## Features

- Text with font size, bold, italic, underline, strikethrough, colour, and alignment
- Shapes: rectangles, lines, circles, and custom strokes
- Images (embedded or from disk)
- Tables with header colours, alternating row colours, borders, and cell padding
- Multi-page documents
- Custom and system fonts, Unicode / RTL text
- Password-protected PDFs with fine-grained permission flags
- PDF merging
- Annotations and hyperlinks
- Page sizes: A3, A4, A5, Letter, Legal, Tabloid

## Installation

```
pip install majorsilence-pdf
```

The package bundles a pre-compiled native library for Linux x86-64, macOS arm64/x86-64, and Windows x86-64. No separate download is needed.

## Quick start

```python
from majorsilence_pdf import load_bundled_library, PdfDocument, PdfStyle, A4, ALIGN_CENTER

lib = load_bundled_library()

with PdfDocument(lib) as doc:
    doc.set_title("Hello World")
    doc.set_author("My App")

    with doc.add_page(*A4) as canvas:
        with PdfStyle(lib) as heading:
            heading.set_size(24).set_bold()
            canvas.draw_text("Hello, PDF!", 72, 80, heading)

        with PdfStyle(lib) as body:
            body.set_size(12)
            canvas.draw_text("Created with majorsilence-pdf — no .NET runtime required.", 72, 120, body)

    doc.save("hello.pdf")
```

## Tables

```python
from majorsilence_pdf import load_bundled_library, PdfDocument, PdfStyle, PdfTable, A4

lib = load_bundled_library()

with PdfDocument(lib) as doc:
    with doc.add_page(*A4) as canvas:
        with PdfTable(lib, [180, 80, 90, 90]) as table:
            table.set_header_bg(26, 86, 160)
            table.set_alternate_bg(240, 245, 252)
            table.set_border(200, 200, 200, 0.5)
            table.set_cell_padding(5)

            table.add_row("Product", "Qty", "Unit Price", "Total")
            table.add_row("PDF Library Pro", "3", "$400.00", "$1,200.00")
            table.add_row("Report Designer", "1", "$250.00", "$250.00")

            canvas.draw_table(table, 72, 92)

    doc.save("report.pdf")
```

## More examples

See the [`Examples/`](https://github.com/majorsilence/pdf-python/tree/main/Examples) directory for 20+ ready-to-run scripts covering shapes, images, custom fonts, Unicode/RTL text, invoices, dashboards, password protection, and PDF merging.

## License

Triple-licensed under [MIT](LICENSE-MIT), [Apache-2.0](LICENSE-APACHE), and [BSD-2-Clause](LICENSE-BSD). Choose whichever suits your project.
