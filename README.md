# champ_image_upscaler
# Image Upscale App (Tkinter + OpenCV DNN SR)

## What it does
- Load an image (PNG/JPEG/BMP/WebP)
- Upscale using OpenCV DNN super-resolution models (or fall back to bicubic)
- Before / After preview
- Choose scale: 2x, 4x, 8x
- Save result
- Optional drag-and-drop (needs TkinterDnD2)

## Quick start (local machine)
1. Create & activate venv:
   - macOS/Linux:
     ```
     python3 -m venv .venv
     source .venv/bin/activate
     ```
   - Windows (PowerShell):
     ```
     py -3 -m venv .venv
     .venv\Scripts\Activate.ps1
     ```
2. Install:
