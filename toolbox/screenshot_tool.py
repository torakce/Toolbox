"""Screenshot utility using Tkinter and Pillow."""

import tkinter as tk
from tkinter import filedialog, messagebox

try:
    from PIL import ImageGrab
except Exception as exc:  # pylint: disable=broad-except
    raise ImportError(
        "Pillow is required for the screenshot tool. Please install it before running."  # noqa: E501
    ) from exc


class ScreenshotTool:
    """Window that provides full screen and region screenshot capabilities."""

    def __init__(self, master: tk.Misc) -> None:
        self.master = master
        self.window = tk.Toplevel(master)
        self.window.title("Screenshot")
        tk.Button(self.window, text="Full Screen", command=self.full_screen).pack(fill=tk.X)
        tk.Button(self.window, text="Region", command=self.region).pack(fill=tk.X)

    def full_screen(self) -> None:
        path = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG", "*.png"), ("JPEG", "*.jpg")])
        if not path:
            return
        try:
            img = ImageGrab.grab()
            img.save(path)
            messagebox.showinfo("Saved", f"Screenshot saved to {path}")
        except Exception as exc:  # pylint: disable=broad-except
            messagebox.showerror("Error", f"Failed to capture screenshot: {exc}")

    def region(self) -> None:
        selector = _RegionSelector(self.master)
        self.master.wait_window(selector.top)
        if selector.bbox:
            path = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG", "*.png"), ("JPEG", "*.jpg")])
            if not path:
                return
            try:
                img = ImageGrab.grab(bbox=selector.bbox)
                img.save(path)
                messagebox.showinfo("Saved", f"Screenshot saved to {path}")
            except Exception as exc:  # pylint: disable=broad-except
                messagebox.showerror("Error", f"Failed to capture screenshot: {exc}")


class _RegionSelector:
    """Transparent fullscreen window to select a region."""

    def __init__(self, master: tk.Misc) -> None:
        self.top = tk.Toplevel(master)
        self.top.attributes("-fullscreen", True)
        self.top.attributes("-alpha", 0.3)
        self.top.configure(bg="gray")
        self.start_x = self.start_y = 0
        self.bbox = None

        self.canvas = tk.Canvas(self.top, cursor="cross")
        self.canvas.pack(fill=tk.BOTH, expand=True)
        self.rect = None

        self.canvas.bind("<ButtonPress-1>", self.on_press)
        self.canvas.bind("<B1-Motion>", self.on_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_release)

    def on_press(self, event: tk.Event) -> None:  # type: ignore[override]
        self.start_x, self.start_y = event.x, event.y
        self.rect = self.canvas.create_rectangle(self.start_x, self.start_y, self.start_x, self.start_y, outline="red")

    def on_drag(self, event: tk.Event) -> None:  # type: ignore[override]
        if self.rect is not None:
            self.canvas.coords(self.rect, self.start_x, self.start_y, event.x, event.y)

    def on_release(self, event: tk.Event) -> None:  # type: ignore[override]
        if self.rect is not None:
            end_x, end_y = event.x, event.y
            self.bbox = (min(self.start_x, end_x), min(self.start_y, end_y), max(self.start_x, end_x), max(self.start_y, end_y))
        self.top.destroy()
