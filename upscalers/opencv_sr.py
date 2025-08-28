import os
import logging
from typing import Optional, Tuple

import cv2
import numpy as np

logger = logging.getLogger(__name__)

SUPPORTED_MODELS = {
    # model_name_lower: (opencv_model_name, default_scale, allowed_scales)
    "espcn": ("espcn", 4, {2,3,4}),
    "edsr": ("edsr", 4, {2,3,4}),
    "fsrcnn": ("fsrcnn", 4, {2,3,4}),
    "lapsrn": ("lapsrn", 8, {8})
}

DEFAULT_MODEL_ORDER = ["edsr", "espcn", "fsrcnn", "lapsrn"]

class OpenCVSuperResolver:
    """
    Uses cv2.dnn_superres if available. Falls back to bicubic resize if not.
    """
    def __init__(self, models_dir: str = "models"):
        self.models_dir = models_dir

    def _find_model_path(self, target_scale: int) -> Optional[tuple[str, str, int]]:
        # Try exact match
        for name in DEFAULT_MODEL_ORDER:
            _, default_scale, scales = SUPPORTED_MODELS[name]
            if target_scale in scales:
                filename = f"{name.upper()}_x{target_scale}.pb"
                path = os.path.join(self.models_dir, filename)
                if os.path.isfile(path):
                    return name, path, target_scale
        # fallback to default models
        for name in DEFAULT_MODEL_ORDER:
            _, default_scale, _ = SUPPORTED_MODELS[name]
            filename = f"{name.upper()}_x{default_scale}.pb"
            path = os.path.join(self.models_dir, filename)
            if os.path.isfile(path):
                return name, path, default_scale
        return None

    def upscale(self, img_bgr: np.ndarray, scale: int = 4) -> Tuple[np.ndarray, str]:
        try:
            from cv2 import dnn_superres
        except Exception as e:
            logger.warning("dnn_superres not available: %s. Using bicubic.", e)
            return self._bicubic(img_bgr, scale), "Bicubic (no dnn_superres)"

        found = self._find_model_path(scale)
        if not found:
            logger.warning("No SR model found. Using bicubic.")
            return self._bicubic(img_bgr, scale), "Bicubic (no model)"

        model_name, model_path, model_scale = found
        opencv_name = SUPPORTED_MODELS[model_name][0]
        try:
            sr = dnn_superres.DnnSuperResImpl_create()
            logger.info("Loading %s model (x%d) from %s", model_name.upper(), model_scale, model_path)
            sr.readModel(model_path)
            sr.setModel(opencv_name, model_scale)
            result = sr.upsample(img_bgr)
            if model_scale != scale:
                factor = scale / model_scale
                new_w = int(result.shape[1] * factor)
                new_h = int(result.shape[0] * factor)
                result = cv2.resize(result, (new_w, new_h), interpolation=cv2.INTER_CUBIC)
            return result, f"OpenCV {model_name.upper()} x{scale}"
        except Exception as e:
            logger.exception("OpenCV SR failed. Falling back to bicubic.")
            return self._bicubic(img_bgr, scale), "Bicubic (sr failed)"

    @staticmethod
    def _bicubic(img_bgr: np.ndarray, scale: int) -> np.ndarray:
        h, w = img_bgr.shape[:2]
        return cv2.resize(img_bgr, (w*scale, h*scale), interpolation=cv2.INTER_CUBIC)
