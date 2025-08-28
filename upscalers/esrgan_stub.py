"""
Placeholder for ESRGAN / Real-ESRGAN integration.
To implement later with realesrgan + basicsr packages and model weights.
API: .upscale(img_bgr, scale) -> (up_bgr, method_str)
"""
from typing import Tuple
import numpy as np

class ESRGANUpscalerStub:
    def __init__(self):
        pass

    def upscale(self, img_bgr: np.ndarray, scale: int = 4) -> Tuple[np.ndarray, str]:
        raise NotImplementedError("ESRGAN not implemented. Use OpenCV SR for now.")
