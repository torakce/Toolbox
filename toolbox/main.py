"""Main dashboard application for Toolbox.

Provides buttons to launch individual utilities such as PDF Annotator,
Screenshot tool and Image/PDF converter. Two additional tiles are
placeholders to showcase how new tools can be added.

This application targets Windows but uses cross platform libraries where
possible. Each tool lives in its own module for modularity and future
extension.
"""

from tkinter import Tk, Button, messagebox
from tkinter import N, S, E, W

try:
    from pdf_annotator import PDFAnnotator
except Exception as exc:  # pylint: disable=broad-except
    PDFAnnotator = None
    pdf_error = exc

try:
    from screenshot_tool import ScreenshotTool
except Exception as exc:  # pylint: disable=broad-except
    ScreenshotTool = None
    screenshot_error = exc

try:
    from converter import ConverterTool
except Exception as exc:  # pylint: disable=broad-except
    ConverterTool = None
    converter_error = exc


class Dashboard(Tk):
    """Main dashboard window with tiles arranged in a grid."""

    def __init__(self) -> None:
        super().__init__()
        self.title("Toolbox")
        self.configure(padx=20, pady=20)
        self.create_tiles()

    def create_tiles(self) -> None:
        """Create buttons for the tools."""
        buttons = [
            ("PDF Annotator", self.open_pdf_annotator),
            ("Screenshot", self.open_screenshot),
            ("Converter", self.open_converter),
            ("Coming soon", lambda: messagebox.showinfo("Toolbox", "Demo tile")),
            ("Coming soon", lambda: messagebox.showinfo("Toolbox", "Demo tile")),
        ]

        rows = 2
        cols = 3
        for index, (text, command) in enumerate(buttons):
            row = index // cols
            col = index % cols
            btn = Button(self, text=text, width=20, height=5, command=command)
            btn.grid(row=row, column=col, padx=10, pady=10, sticky=(N, S, E, W))

        for i in range(rows):
            self.rowconfigure(i, weight=1)
        for j in range(cols):
            self.columnconfigure(j, weight=1)

    def open_pdf_annotator(self) -> None:
        if PDFAnnotator is None:
            messagebox.showerror("Missing dependency", f"Cannot open PDF annotator: {pdf_error}")
            return
        PDFAnnotator(self)

    def open_screenshot(self) -> None:
        if ScreenshotTool is None:
            messagebox.showerror("Missing dependency", f"Cannot open screenshot tool: {screenshot_error}")
            return
        ScreenshotTool(self)

    def open_converter(self) -> None:
        if ConverterTool is None:
            messagebox.showerror("Missing dependency", f"Cannot open converter: {converter_error}")
            return
        ConverterTool(self)


if __name__ == "__main__":
    Dashboard().mainloop()
