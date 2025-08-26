"""Simple PDF viewer and annotator using PyMuPDF and Tkinter."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Tuple

import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog

try:
    import fitz  # PyMuPDF
except Exception as exc:  # pylint: disable=broad-except
    raise ImportError(
        "PyMuPDF is required for the PDF annotator. Please install it before running."  # noqa: E501
    ) from exc

try:
    from PIL import Image, ImageTk
except Exception as exc:  # pylint: disable=broad-except
    raise ImportError(
        "Pillow is required for the PDF annotator. Please install it before running."  # noqa: E501
    ) from exc


@dataclass
class PageAnnotations:
    """Keep track of strokes and texts for a page."""

    strokes: List[List[Tuple[int, int]]] = field(default_factory=list)
    texts: List[Tuple[int, int, str]] = field(default_factory=list)


class PDFAnnotator:
    """Window allowing basic PDF viewing and annotation."""

    def __init__(self, master: tk.Misc) -> None:
        self.master = master
        self.window = tk.Toplevel(master)
        self.window.title("PDF Annotator")

        toolbar = tk.Frame(self.window)
        toolbar.pack(fill=tk.X)

        tk.Button(toolbar, text="Open PDF", command=self.open_pdf).pack(side=tk.LEFT)
        tk.Button(toolbar, text="Prev", command=self.prev_page).pack(side=tk.LEFT)
        tk.Button(toolbar, text="Next", command=self.next_page).pack(side=tk.LEFT)
        tk.Button(toolbar, text="Draw", command=lambda: self.set_mode("draw")).pack(side=tk.LEFT)
        tk.Button(toolbar, text="Text", command=lambda: self.set_mode("text")).pack(side=tk.LEFT)
        tk.Button(toolbar, text="Save", command=self.save_pdf).pack(side=tk.LEFT)

        self.canvas = tk.Canvas(self.window, width=800, height=600, bg="white")
        self.canvas.pack(fill=tk.BOTH, expand=True)

        self.doc: fitz.Document | None = None
        self.current_page = 0
        self.page_images: Dict[int, ImageTk.PhotoImage] = {}
        self.annotations: Dict[int, PageAnnotations] = {}
        self.mode = "draw"
        self.current_line: int | None = None

        self.canvas.bind("<ButtonPress-1>", self.on_press)
        self.canvas.bind("<B1-Motion>", self.on_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_release)

    # PDF handling ---------------------------------------------------------
    def open_pdf(self) -> None:
        path = filedialog.askopenfilename(filetypes=[("PDF", "*.pdf")])
        if not path:
            return
        try:
            self.doc = fitz.open(path)
            self.current_page = 0
            self.annotations.clear()
            self.display_page()
        except Exception as exc:  # pylint: disable=broad-except
            messagebox.showerror("Error", f"Failed to open PDF: {exc}")

    def display_page(self) -> None:
        if not self.doc:
            return
        page = self.doc[self.current_page]
        zoom = 1.5
        pix = page.get_pixmap(matrix=fitz.Matrix(zoom, zoom))
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        self.page_images[self.current_page] = ImageTk.PhotoImage(img)
        self.canvas.delete("all")
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.page_images[self.current_page])
        self.canvas.config(scrollregion=self.canvas.bbox(tk.ALL))
        self.redraw_annotations()

    def prev_page(self) -> None:
        if not self.doc:
            return
        if self.current_page > 0:
            self.current_page -= 1
            self.display_page()

    def next_page(self) -> None:
        if not self.doc:
            return
        if self.current_page < len(self.doc) - 1:
            self.current_page += 1
            self.display_page()

    # Drawing --------------------------------------------------------------
    def set_mode(self, mode: str) -> None:
        self.mode = mode

    def on_press(self, event: tk.Event) -> None:  # type: ignore[override]
        if self.mode == "draw":
            self.current_line = self.canvas.create_line(event.x, event.y, event.x, event.y, fill="red", width=2)
        elif self.mode == "text":
            text = simpledialog.askstring("Text", "Enter text")
            if text:
                self.canvas.create_text(event.x, event.y, text=text, fill="blue", anchor=tk.NW)
                page_ann = self.annotations.setdefault(self.current_page, PageAnnotations())
                page_ann.texts.append((event.x, event.y, text))

    def on_drag(self, event: tk.Event) -> None:  # type: ignore[override]
        if self.mode == "draw" and self.current_line is not None:
            coords = self.canvas.coords(self.current_line) + [event.x, event.y]
            self.canvas.coords(self.current_line, *coords)

    def on_release(self, _event: tk.Event) -> None:  # type: ignore[override]
        if self.mode == "draw" and self.current_line is not None:
            coords = self.canvas.coords(self.current_line)
            points = [(int(coords[i]), int(coords[i + 1])) for i in range(0, len(coords), 2)]
            page_ann = self.annotations.setdefault(self.current_page, PageAnnotations())
            page_ann.strokes.append(points)
            self.current_line = None

    def redraw_annotations(self) -> None:
        page_ann = self.annotations.get(self.current_page)
        if not page_ann:
            return
        for stroke in page_ann.strokes:
            flat = [v for point in stroke for v in point]
            self.canvas.create_line(*flat, fill="red", width=2)
        for x, y, text in page_ann.texts:
            self.canvas.create_text(x, y, text=text, fill="blue", anchor=tk.NW)

    # Saving ---------------------------------------------------------------
    def save_pdf(self) -> None:
        if not self.doc:
            return
        save_path = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF", "*.pdf")])
        if not save_path:
            return
        try:
            for page_num, ann in self.annotations.items():
                page = self.doc[page_num]
                shape = page.new_shape()
                for stroke in ann.strokes:
                    pdf_points = [fitz.Point(x, y) for x, y in stroke]
                    shape.draw_polyline(pdf_points, color=(1, 0, 0), width=2)
                for x, y, text in ann.texts:
                    page.insert_text((x, y), text, fontsize=12, color=(0, 0, 1))
                shape.commit()
            self.doc.save(save_path)
            messagebox.showinfo("Saved", f"Annotations saved to {save_path}")
        except Exception as exc:  # pylint: disable=broad-except
            messagebox.showerror("Error", f"Failed to save: {exc}")
