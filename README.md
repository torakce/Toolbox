# Toolbox

Toolbox is a small collection of desktop utilities with a dashboard
interface reminiscent of Parallels Toolbox. It currently includes:

* **PDF Annotator** – open a PDF, draw freehand annotations or insert
  text and save the result.
* **Screenshot** – capture the whole screen or a user-defined region.
* **Converter** – convert images and PDF files to various formats with
  optional resizing, DPI adjustment and grayscale conversion.
* Two demonstration tiles reserved for future tools.

The application is written in Python with Tkinter for the interface and
relies on [Pillow](https://python-pillow.org) and
[PyMuPDF](https://pymupdf.readthedocs.io/) for media handling.

## Running from source

```bash
pip install -r requirements.txt
python -m toolbox.main
```

## Packaging for Windows

A batch script is provided to create a standalone executable using
[PyInstaller](https://pyinstaller.org/):

```
build.bat
```

The generated executable will appear in the `dist` directory.

## Adding new tools

Each tool lives in its own module. To add a new utility, create a new
Python file in the `toolbox` package and add a button in
`toolbox/main.py`.
