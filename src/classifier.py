# ── src/classifier.py ──────────────────────────────────────────────────────
# Machine Learning interface for the Teachable Machine vision model.
# 
# CRITICAL DEVELOPER NOTE:
# If you train a new model, you MUST export it from Teachable Machine as a 
# standard "Keras" model (TensorFlow tab -> Keras). 
# Do not export as TensorFlow.js or TensorFlow Lite.
# ---------------------------------------------------------------------------

import os
import numpy as np
import tensorflow as tf

from src.snack_data import CLASS_LABELS


class SnackClassifier:
    """
    Wraps the Teachable Machine Keras model.
    Usage:
        clf = SnackClassifier()
        label, confidence = clf.predict(img_array)
    """

    MODEL_PATH  = os.path.join("model", "keras_model.h5")
    LABELS_PATH = os.path.join("model", "labels.txt")

    def __init__(self):
        self.model  = None
        self.labels = []
        self._load()

    # ── Setup & Memory Management ────────────────────────────────────────────

    def _load(self):
        """Load model and labels from disk."""
        if not os.path.exists(self.MODEL_PATH):
            raise FileNotFoundError(
                f"Model not found at '{self.MODEL_PATH}'.\n"
                "Please place your keras_model.h5 in the model/ folder."
            )

        # Suppress TensorFlow info logs
        os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"
        self.model = tf.keras.models.load_model(self.MODEL_PATH, compile=False)

        # Load labels
        if os.path.exists(self.LABELS_PATH):
            self.labels = self._read_labels_file(self.LABELS_PATH)
        else:
            self.labels = CLASS_LABELS

        print(f"[Classifier] Model loaded. Classes: {self.labels}")

    def reload_model(self):
        """Safely clears Keras memory and reloads the model/labels from disk."""
        print("[Classifier] Initiating hot-swap...")
        
        # 1. Clear the old model from RAM to prevent memory leaks
        tf.keras.backend.clear_session()
        self.model = None
        self.labels = []
        
        # 2. Re-run the load sequence
        self._load()
        print("[Classifier] Hot-swap complete! New model active.")

    def _read_labels_file(self, path: str) -> list[str]:
        """Parse labels.txt file."""
        labels = []
        with open(path, "r") as f:
            for line in f:
                line = line.strip()
                if line:
                    parts = line.split(" ", 1)
                    label = parts[1] if len(parts) == 2 else parts[0]
                    labels.append(label.strip())
        return labels

    # ── Prediction ───────────────────────────────────────────────────────────

    def predict(self, img_array: np.ndarray) -> tuple[str, float]:
        """Run inference on a preprocessed image array."""
        if self.model is None:
            raise RuntimeError("Model is not loaded.")

        predictions = self.model.predict(img_array, verbose=0)
        class_index = int(np.argmax(predictions[0]))
        confidence  = float(predictions[0][class_index]) * 100.0

        if class_index < len(self.labels):
            class_label = self.labels[class_index]
        else:
            class_label = f"class_{class_index}"

        return class_label, round(confidence, 1)

    def is_loaded(self) -> bool:
        return self.model is not None