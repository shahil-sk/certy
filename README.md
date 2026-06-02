<div align="center">

# Certy
<img src="icon.svg" width="280" alt="Certy logo" />

**Certy** is a desktop app for bulk certificate generation from a PNG template and a spreadsheet.

[![Build Status](https://img.shields.io/github/actions/workflow/status/shahil-sk/certy/build.yml?style=for-the-badge)](https://github.com/shahil-sk/certy/actions)
[![Latest Release](https://img.shields.io/github/v/release/shahil-sk/certy?style=for-the-badge)](https://github.com/shahil-sk/certy/releases/latest)
[![License](https://img.shields.io/github/license/shahil-sk/certy?style=for-the-badge)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.7+-blue?style=for-the-badge&logo=python)](https://python.org)
[![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20Linux%20%7C%20macOS-black?style=for-the-badge)](https://github.com/shahil-sk/certy/releases)
[![Ko-Fi](https://img.shields.io/badge/Support-Ko--Fi-ff5f5f?style=for-the-badge&logo=kofi&logoColor=white)](https://ko-fi.com/shahilsk)

<br>

[Download](https://github.com/shahil-sk/certy/releases/latest) &bull;
[Development](#development) &bull;
[Contributors](#contributors)

</div>

## About

**Certy** turns a PNG template and a spreadsheet into a full batch of certificates with no code required.

Load your design, drag fields into position, map your data, and generate a PDF for every row in your spreadsheet. Supports custom fonts, RGB and CMYK color modes, live preview, QR code fields, image overlay fields, and reusable `.certy` project files.

## Features

- **Drag-and-drop field placement** — click and drag each field directly onto the canvas. No coordinate guessing.
- **Canvas zoom** — zoom in/out with `+` / `-` buttons, `Ctrl+Scroll`, or keyboard shortcuts (`Ctrl+=`, `Ctrl+-`, `Ctrl+0` to reset). Field positions stay accurate at any zoom level.
- **Live preview** — render one real certificate before committing to the full batch.
- **Row navigator** — step through any data row on the canvas to check how each certificate will look.
- **Batch output** — one file per data row, automatically named from your spreadsheet fields. Supports PDF, PNG, JPEG, and WebP.
- **QR code fields** — map any column to a QR code; rendered directly onto the certificate.
- **Image overlay fields** — embed per-row images (photos, signatures) from paths in your spreadsheet.
- **Custom fonts** — drop any `.ttf` or `.otf` into `fonts/` and it appears in the selector immediately.
- **RGB and CMYK** — switch color modes for screen or print output.
- **Conditional fields** — show or hide a field based on the value of another column.
- **Project files** — save your session as a `.certy` file and reload it later.
- **Undo / Redo** — `Ctrl+Z` / `Ctrl+Y` for placeholder positions.
- **Non-blocking UI** — generation runs in a background thread with a live progress bar.

## Preview
<img width="1340" height="812" alt="image" src="https://github.com/user-attachments/assets/cdb78bb3-7a6d-43f4-a06d-040b174db056" />

## Installation

Download the latest release for your platform:

### [Windows](https://github.com/shahil-sk/certy/releases/latest) | [Linux](https://github.com/shahil-sk/certy/releases/latest) | [macOS](https://github.com/shahil-sk/certy/releases/latest)

## Development

```bash
git clone https://github.com/shahil-sk/certy.git
cd certy
python3 -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate
pip install -r requirements.txt
python3 main.py
```

To add custom fonts, drop `.ttf` or `.otf` files into the `fonts/` folder.

### Optional dependency

QR code fields require one extra package:

```bash
pip install "qrcode[pil]>=7.4.2"
```

Without it the app still runs normally — QR fields display a placeholder on the canvas and are skipped during export.

## How to use it

1. **Load template** — select a PNG certificate background.
2. **Load Excel** — select an `.xlsx` or `.csv` file where row 1 is field headers.
3. **Place fields** — drag each field label to its position on the canvas. Use zoom (`+` / `-`) for precision.
4. **Style fields** — set font, size, color, alignment, opacity, shadow, and outline per field.
5. **Set field type** — choose `text`, `qr`, or `image` per field as needed.
6. **Preview** — step through rows with the row navigator and render a sample certificate.
7. **Generate** — choose output format (PDF / PNG / JPEG / WebP), pick an output folder, and watch the progress bar.
8. **Save project** — write a `.certy` file for next time.

## Tech stack

| Library | Purpose |
|---|---|
| [Pillow](https://python-pillow.org/) | Image rendering and raster export |
| [openpyxl](https://openpyxl.readthedocs.io/) | Reading `.xlsx` data files |
| [fpdf2](https://py-pdf.github.io/fpdf2/) | Writing output PDFs |
| [qrcode\[pil\]](https://github.com/lincolnloop/python-qrcode) | QR code generation *(optional)* |
| Tkinter (stdlib) | Desktop GUI |
| csv (stdlib) | Reading `.csv` data files |

# Support the Project

If you enjoy the project and want to support future development:

<p align="left">
  <a href="https://ko-fi.com/shahilsk">
    <img src="https://ko-fi.com/img/githubbutton_sm.svg" alt="Ko-Fi">
  </a>
</p>

## License

[Apache License 2.0](LICENSE)
