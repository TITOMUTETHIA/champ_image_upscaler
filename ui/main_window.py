import logging
import os
from dataclasses import dataclass
from typing import Optional

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk

try:
    from TkinterDnD2 import DND_FILES, TkinterDnD
    DND_AVAILABLE = True
except Exception:
    DND_AVAILABLE = False

from upscalers.opencv_sr import OpenCVSuperResolver
from utils.image_ops import pil_to_bgr, bgr_to_pil, make_preview

logger = logging.getLogger(__name__)

CANVAS_W, CANVAS_H = 420, 420

@dataclass
class AppState:
    src_path: Optional[str] = None
    src_image: Optional[Image.Image] = None
    upscaled_image: Optional[Image.Image] = None
    scale: int = 4

def _make_root():
    if DND_AVAILABLE:
        root = TkinterDnD.Tk()
    else:
        root = tk.Tk()
    root.title("Image Upscale App")
    root.geometry("980x560")
    root.minsize(900,520)
    return root

def _render_on_canvas(canvas: tk.Canvas, pil_img: Optional[Image.Image]):
    canvas.delete("all")
    if pil_img is None:
        return
    preview = make_preview(pil_img, (canvas.winfo_width() or CANVAS_W, canvas.winfo_height() or CANVAS_H))
    tk_img = ImageTk.PhotoImage(preview)
    canvas.image = tk_img
    canvas.create_image(canvas.winfo_width()//2, canvas.winfo_height()//2, image=tk_img, anchor=tk.CENTER)

def _open_image_from_path(path: str, state: AppState, before_canvas: tk.Canvas, status_var: tk.StringVar):
    try:
        img = Image.open(path)
        state.src_image = img
        state.src_path = path
        status_var.set(f"Loaded: {os.path.basename(path)} {img.size[0]}x{img.size[1]}")
        logger.info("Loaded image: %s", path)
        _render_on_canvas(before_canvas, img)
    except Exception as e:
        logger.exception("Failed to open image")
        messagebox.showerror("Open Error", f"Could not open image:\n{e}")

def run_app():
    state = AppState()
    root = _make_root()
    resolver = OpenCVSuperResolver(models_dir="models")

    # Top controls
    top = ttk.Frame(root, padding=10)
    top.pack(fill=tk.X)

    open_btn = ttk.Button(top, text="Open Image", command=lambda: _on_open_clicked(root, state, before_canvas, status_var))
    open_btn.pack(side=tk.LEFT)

    ttk.Label(top, text="Scale:").pack(side=tk.LEFT, padx=(12,6))
    scale_cmb = ttk.Combobox(top, values=[2,4,8], state="readonly", width=5)
    scale_cmb.set(state.scale)
    scale_cmb.pack(side=tk.LEFT)

    def on_scale_change(event):
        state.scale = int(scale_cmb.get())
        logger.info("Selected scale x%d", state.scale)

    scale_cmb.bind("<<ComboboxSelected>>", on_scale_change)

    upscale_btn = ttk.Button(top, text="Upscale", command=lambda: _on_upscale_clicked(state, resolver, after_canvas, status_var))
    upscale_btn.pack(side=tk.LEFT, padx=8)

    save_btn = ttk.Button(top, text="Save Result", command=lambda: _on_save_clicked(root, state, status_var))
    save_btn.pack(side=tk.LEFT)

    # Status bar
    status_var = tk.StringVar(value="Ready")
    status_bar = ttk.Label(root, textvariable=status_var, anchor="w", padding=(10,6))
    status_bar.pack(side=tk.BOTTOM, fill=tk.X)

    # Main preview area
    main = ttk.Frame(root, padding=10)
    main.pack(fill=tk.BOTH, expand=True)

    left = ttk.LabelFrame(main, text="Before", padding=8)
    left.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    right = ttk.LabelFrame(main, text="After", padding=8)
    right.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    before_canvas = tk.Canvas(left, width=CANVAS_W, height=CANVAS_H, bg="#222")
    before_canvas.pack(fill=tk.BOTH, expand=True)

    after_canvas = tk.Canvas(right, width=CANVAS_W, height=CANVAS_H, bg="#222")
    after_canvas.pack(fill=tk.BOTH, expand=True)

    if DND_AVAILABLE:
        def drop(event):
            path = event.data.strip('{}')
            _open_image_from_path(path, state, before_canvas, status_var)
        before_canvas.drop_target_register(DND_FILES)
        before_canvas.dnd_bind('<<Drop>>', drop)

    def on_resize(event):
        _render_on_canvas(before_canvas, state.src_image)
        _render_on_canvas(after_canvas, state.upscaled_image)

    before_canvas.bind("<Configure>", on_resize)
    after_canvas.bind("<Configure>", on_resize)

    root.mainloop()

def _on_open_clicked(root, state, before_canvas, status_var):
    filetypes = [("Image files", ".png .jpg .jpeg .bmp .webp"), ("All files","*.*")]
    path = filedialog.askopenfilename(title="Open Image", filetypes=filetypes)
    if not path:
        return
    _open_image_from_path(path, state, before_canvas, status_var)

def _on_upscale_clicked(state, resolver, after_canvas, status_var):
    if state.src_image is None:
        messagebox.showwarning("No image", "Please open an image first.")
        return
    try:
        status_var.set("Upscaling... (check terminal logs)")
        logger.info("Upscaling with scale x%d", state.scale)
        bgr = pil_to_bgr(state.src_image)
        up_bgr, method = resolver.upscale(bgr, scale=state.scale)
        up_img = bgr_to_pil(up_bgr)
        state.upscaled_image = up_img
        status_var.set(f"Done: {method} → {up_img.size[0]}x{up_img.size[1]}")
        _render_on_canvas(after_canvas, up_img)
    except Exception as e:
        logger.exception("Upscale failed")
        messagebox.showerror("Upscale Error", f"Upscale failed:\n{e}")

def _on_save_clicked(root, state, status_var):
    if state.upscaled_image is None:
        messagebox.showwarning("No result", "Nothing to save yet. Run Upscale first.")
        return
    initial = None
    if state.src_path:
        base, _ = os.path.splitext(os.path.basename(state.src_path))
        initial = f"{base}_x{state.scale}.png"
    path = filedialog.asksaveasfilename(title="Save Upscaled Image", defaultextension=".png", initialfile=initial,
                                        filetypes=[("PNG",".png"), ("JPEG",".jpg .jpeg"), ("WebP",".webp")])
    if not path:
        return
    try:
        state.upscaled_image.save(path)
        status_var.set(f"Saved: {path}")
        logger.info("Saved upscaled image to %s", path)
    except Exception as e:
        logger.exception("Save failed")
        messagebox.showerror("Save Error", f"Could not save image:\n{e}")
