from typing import Tuple
from PIL import Image
import numpy as np
import cv2

def pil_to_bgr(pil_img: Image.Image) -> np.ndarray:
    rgb = pil_img.convert("RGB")
    return cv2.cvtColor(np.array(rgb), cv2.COLOR_RGB2BGR)

def bgr_to_pil(bgr: np.ndarray) -> Image.Image:
    rgb = cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB)
    return Image.fromarray(rgb)

def make_preview(img: Image.Image, max_size: Tuple[int,int]) -> Image.Image:
    p = img.copy()
    p.thumbnail(max_size, Image.LANCZOS)
    return p
