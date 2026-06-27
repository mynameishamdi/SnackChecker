# ── src/preprocessor.py ────────────────────────────────────────────────────
# Prepares any input image for the Teachable Machine Keras model.
# Input  : numpy array (BGR from OpenCV, or RGB from PIL)
# Output : numpy array of shape (1, 224, 224, 3), float32, values in [-1, 1]
# ---------------------------------------------------------------------------

import cv2
import numpy as np
from PIL import Image

TARGET_SIZE = (224, 224)   # MobileNet input size used by Teachable Machine


def preprocess_from_array(img_bgr: np.ndarray) -> np.ndarray:
    """
    Preprocess a BGR numpy array (from OpenCV webcam/imread).
    Returns a (1, 224, 224, 3) float32 array ready for model.predict().
    """
    img_rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)
    img_resized = cv2.resize(img_rgb, TARGET_SIZE, interpolation=cv2.INTER_AREA)
    
    # FIX: Teachable Machine expects values between -1 and 1
    img_normalized = (img_resized.astype(np.float32) / 127.5) - 1.0
    
    return np.expand_dims(img_normalized, axis=0)


def preprocess_from_pil(pil_image: Image.Image) -> np.ndarray:
    """
    Preprocess a PIL Image (from file upload).
    Returns a (1, 224, 224, 3) float32 array ready for model.predict().
    """
    img_rgb = pil_image.convert("RGB")
    img_resized = img_rgb.resize(TARGET_SIZE, Image.LANCZOS)
    
    # FIX: Teachable Machine expects values between -1 and 1
    img_array = (np.array(img_resized, dtype=np.float32) / 127.5) - 1.0
    
    return np.expand_dims(img_array, axis=0)


def preprocess_from_path(image_path: str) -> np.ndarray:
    """
    Preprocess an image from a file path.
    Returns a (1, 224, 224, 3) float32 array ready for model.predict().
    """
    pil_image = Image.open(image_path)
    return preprocess_from_pil(pil_image)