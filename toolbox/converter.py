"""Image and PDF conversion utility."""

from __future__ import annotations

import os
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

try:
    from PIL import Image
except Exception as exc:  # pylint: disable=broad-except
    raise ImportError(
        "Pillow is required for the converter. Please install it before running."  # noqa: E501
    ) from exc

try:
    import fitz  # PyMuPDF
except Exception as exc:  # pylint: disable=broad-except
    raise ImportError(
        "PyMuPDF is required for the converter. Please install it before running."  # noqa: E501
    ) from exc


class ConverterTool:
    """Window for converting images and PDFs to various formats."""

    def __init__(self, master: tk.Misc) -> None:
        self.master = master
        self.window = tk.Toplevel(master)
        self.window.title("Converter")

        frm = tk.Frame(self.window)
        frm.pack(padx=10, pady=10)

        tk.Button(frm, text="Choose file", command=self.choose_file).grid(row=0, column=0, sticky=tk.W)
        self.file_label = tk.Label(frm, text="No file")
        self.file_label.grid(row=0, column=1, columnspan=3)

        tk.Label(frm, text="Format").grid(row=1, column=0, sticky=tk.W)
        self.format_var = tk.StringVar(value="PNG")
        formats = ["JPEG", "PNG", "TIFF", "BMP", "GIF", "WEBP", "PDF"]
        ttk.Combobox(frm, textvariable=self.format_var, values=formats, state="readonly").grid(row=1, column=1, sticky=tk.W)

        tk.Label(frm, text="Width").grid(row=2, column=0, sticky=tk.W)
        self.width_entry = tk.Entry(frm, width=5)
        self.width_entry.grid(row=2, column=1, sticky=tk.W)
        tk.Label(frm, text="Height").grid(row=2, column=2, sticky=tk.W)
        self.height_entry = tk.Entry(frm, width=5)
        self.height_entry.grid(row=2, column=3, sticky=tk.W)

        tk.Label(frm, text="DPI").grid(row=3, column=0, sticky=tk.W)
        self.dpi_entry = tk.Entry(frm, width=5)
        self.dpi_entry.grid(row=3, column=1, sticky=tk.W)
        self.gray_var = tk.BooleanVar()
        tk.Checkbutton(frm, text="Grayscale", variable=self.gray_var).grid(row=3, column=2, sticky=tk.W)

        tk.Button(frm, text="Convert", command=self.convert).grid(row=4, column=0, columnspan=4, pady=5)

        self.input_path: str | None = None

    def choose_file(self) -> None:
        path = filedialog.askopenfilename(filetypes=[("All", "*.*"), ("Images", "*.png;*.jpg;*.jpeg;*.bmp;*.gif"), ("PDF", "*.pdf")])
        if path:
            self.input_path = path
            self.file_label.config(text=os.path.basename(path))

    def convert(self) -> None:
        if not self.input_path:
            messagebox.showwarning("No file", "Please select a file to convert.")
            return
        out_format = self.format_var.get().upper()
        save_path = filedialog.asksaveasfilename(defaultextension=f".{out_format.lower()}")
        if not save_path:
            return
        width = self._parse_int(self.width_entry.get())
        height = self._parse_int(self.height_entry.get())
        dpi = self._parse_int(self.dpi_entry.get())
        grayscale = self.gray_var.get()

        try:
            if self.input_path.lower().endswith(".pdf"):
                self._convert_pdf(self.input_path, save_path, out_format, width, height, dpi, grayscale)
            else:
                self._convert_image(self.input_path, save_path, out_format, width, height, dpi, grayscale)
            messagebox.showinfo("Done", f"File saved to {save_path}")
        except Exception as exc:  # pylint: disable=broad-except
            messagebox.showerror("Error", f"Conversion failed: {exc}")

    # Helpers ---------------------------------------------------------------
    def _parse_int(self, value: str) -> int | None:
        try:
            return int(value)
        except ValueError:
            return None

    def _convert_image(self, src: str, dst: str, fmt: str, width: int | None, height: int | None, dpi: int | None, gray: bool) -> None:
        img = Image.open(src)
        img = img.convert("L" if gray else "RGB")
        if width and height:
            img = img.resize((width, height))
        params = {}
        if dpi:
            params["dpi"] = (dpi, dpi)
        img.save(dst, format=fmt, **params)

    def _convert_pdf(self, src: str, dst: str, fmt: str, width: int | None, height: int | None, dpi: int | None, gray: bool) -> None:
        doc = fitz.open(src)
        images = []
        for page in doc:
            pix = page.get_pixmap(dpi=dpi or 150)
            img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
            if gray:
                img = img.convert("L")
            if width and height:
                img = img.resize((width, height))
            images.append(img)
        if fmt in {"TIFF", "GIF", "PDF"}:
            images[0].save(dst, format=fmt, save_all=True, append_images=images[1:])
        else:
            base, ext = os.path.splitext(dst)
            for i, img in enumerate(images, start=1):
                img.save(f"{base}_{i}{os.path.splitext(dst)[1]}", format=fmt)
