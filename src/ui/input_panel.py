# ── src/ui/input_panel.py ──────────────────────────────────────────────────
# Left panel of the app window.
# Handles: webcam feed, image file upload, preview display, capture trigger.
# ---------------------------------------------------------------------------

import threading
import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk
import cv2
import numpy as np
import customtkinter as ctk


class InputPanel(ctk.CTkFrame):
    """
    Left panel — provides webcam and upload input methods.
    Calls on_image_ready(img_array, pil_preview) when the user captures/selects.

    on_image_ready receives:
      img_array  : np.ndarray ready for model.predict (already preprocessed)
      pil_image  : original PIL Image for display
    """

    PREVIEW_W = 380
    PREVIEW_H = 280

    def __init__(self, parent, on_image_ready, **kwargs):
        super().__init__(parent, fg_color="transparent", **kwargs)
        self._on_image_ready = on_image_ready
        self._cap            = None      # OpenCV VideoCapture
        self._running        = False     # webcam loop flag
        self._current_frame  = None      # latest BGR frame from webcam
        self._build_ui()

    # ── Build UI ─────────────────────────────────────────────────────────────

    def _build_ui(self):
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=0)
        self.grid_columnconfigure(0, weight=1)

        # Preview image
        self.preview_label = ctk.CTkLabel(
            self,
            text="No image selected.\nUse Webcam or Upload below.",
            width=self.PREVIEW_W,
            height=self.PREVIEW_H,
            fg_color=("gray85", "gray20"),
            corner_radius=10,
            font=ctk.CTkFont(size=13),
        )
        self.preview_label.grid(row=0, column=0, sticky="n", pady=(0, 12))

        # Controls frame
        controls = ctk.CTkFrame(self, fg_color="transparent")
        controls.grid(row=1, column=0, sticky="ew")
        controls.grid_columnconfigure((0, 1), weight=1)

        # Mode buttons row
        self.webcam_btn = ctk.CTkButton(
            controls,
            text="📷  Start Webcam",
            command=self._start_webcam,
            width=175,
        )
        self.webcam_btn.grid(row=0, column=0, padx=(0, 6), pady=(0, 8), sticky="ew")

        self.upload_btn = ctk.CTkButton(
            controls,
            text="📁  Upload Image",
            command=self._upload_image,
            width=175,
        )
        self.upload_btn.grid(row=0, column=1, padx=(6, 0), pady=(0, 8), sticky="ew")

        # Capture / Scan Again
        self.action_btn = ctk.CTkButton(
            controls,
            text="📸  Capture",
            command=self._capture,
            state="disabled",
            fg_color="#1D9E75",
            hover_color="#16785A",
            height=40,
            font=ctk.CTkFont(size=14, weight="bold"),
        )
        self.action_btn.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(0, 8))

        self.reset_btn = ctk.CTkButton(
            controls,
            text="🔄  Scan Again",
            command=self._reset,
            state="disabled",
            fg_color=("gray75", "gray30"),
            height=36,
        )
        self.reset_btn.grid(row=2, column=0, columnspan=2, sticky="ew")

        # Status label
        self.status_label = ctk.CTkLabel(
            controls,
            text="",
            font=ctk.CTkFont(size=12),
            text_color="gray",
        )
        self.status_label.grid(row=3, column=0, columnspan=2, pady=(6, 0))

    # ── Webcam ────────────────────────────────────────────────────────────────

    def _start_webcam(self):
        if self._running:
            return
            
        # FIX 1: cv2.CAP_DSHOW prevents the Windows MSMF driver crash!
        self._cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
        
        # Fallback to standard driver if DirectShow fails for some reason
        if not self._cap.isOpened():
            self._cap = cv2.VideoCapture(0)
            
        if not self._cap.isOpened():
            self._set_status("No webcam found. Use Upload instead.", error=True)
            return

        self._running = True
        self.webcam_btn.configure(text="⏹  Stop Webcam", command=self._stop_webcam)
        self.upload_btn.configure(state="disabled")
        self.action_btn.configure(state="normal", text="📸  Capture")
        self._set_status("Webcam active — press Capture when ready.")
        threading.Thread(target=self._webcam_loop, daemon=True).start()

    def _stop_webcam(self):
        self._running = False
        if self._cap:
            self._cap.release()
            self._cap = None
        self.webcam_btn.configure(text="📷  Start Webcam", command=self._start_webcam)
        self.upload_btn.configure(state="normal")
        self.action_btn.configure(state="disabled")
        self._show_placeholder()
        self._set_status("")

    def _webcam_loop(self):
        """Runs in background thread — reads frames and updates preview."""
        while self._running:
            ret, frame = self._cap.read()
            if not ret:
                break
            self._current_frame = frame
            pil_img = self._bgr_to_pil(frame)
            self._update_preview(pil_img)

    # ── Upload ────────────────────────────────────────────────────────────────

    def _upload_image(self):
        path = filedialog.askopenfilename(
            title="Select a snack image",
            filetypes=[("Image files", "*.jpg *.jpeg *.png *.bmp *.webp")],
        )
        if not path:
            return

        try:
            pil_img = Image.open(path).convert("RGB")
            self._current_frame = None     # not webcam
            self._uploaded_pil  = pil_img
            self._update_preview(pil_img)
            self.action_btn.configure(state="normal", text="✅  Classify This Image")
            self._set_status("Image loaded. Click Classify to analyse.")
        except Exception as e:
            self._set_status(f"Could not open image: {e}", error=True)

    # ── Capture / classify ────────────────────────────────────────────────────

    def _capture(self):
        """Freeze the current frame (webcam or upload) and send for classification."""
        from src.preprocessor import preprocess_from_array, preprocess_from_pil

        if self._current_frame is not None:
            # Webcam mode — freeze frame
            frame   = self._current_frame.copy()
            pil_img = self._bgr_to_pil(frame)
            img_arr = preprocess_from_array(frame)
        elif hasattr(self, "_uploaded_pil"):
            # Upload mode
            pil_img = self._uploaded_pil
            img_arr = preprocess_from_pil(pil_img)
        else:
            self._set_status("No image to classify.", error=True)
            return

        # Stop webcam if running so the frame is frozen
        if self._running:
            self._stop_webcam()
            self._update_preview(pil_img)

        # Disable buttons during classification
        self.action_btn.configure(state="disabled")
        self.upload_btn.configure(state="disabled")
        self.reset_btn.configure(state="normal")
        self._set_status("Classifying...")

        # Hand off to main window callback
        self._on_image_ready(img_arr, pil_img)

    # ── Reset ─────────────────────────────────────────────────────────────────

    def _reset(self):
        self._stop_webcam()
        if hasattr(self, "_uploaded_pil"):
            del self._uploaded_pil
        self._current_frame = None
        self._show_placeholder()
        self.upload_btn.configure(state="normal")
        self.action_btn.configure(state="disabled", text="📸  Capture")
        self.reset_btn.configure(state="disabled")
        self._set_status("")

    # ── Helpers ───────────────────────────────────────────────────────────────

    def _update_preview(self, pil_img: Image.Image):
        """Resize and display a PIL image in the preview label (thread-safe)."""
        display_img = pil_img.copy()
        
        try:
            resample_filter = Image.Resampling.LANCZOS
        except AttributeError:
            resample_filter = Image.LANCZOS
            
        display_img.thumbnail((self.PREVIEW_W, self.PREVIEW_H), resample_filter)
        ctk_img = ctk.CTkImage(light_image=display_img, dark_image=display_img, size=display_img.size)
        
        # Pass the image directly to a dedicated UI thread function
        self.after(0, self._safe_render, ctk_img)

    def _safe_render(self, ctk_img):
        """Runs strictly on the main UI thread to prevent Garbage Collection crashes."""
        self.preview_label.configure(image=ctk_img, text="")
        # Save the memory reference ON the main thread so it doesn't get deleted!
        self.preview_label.image = ctk_img

    def _show_placeholder(self):
        self.after(0, lambda: self.preview_label.configure(
            image=None,
            text="No image selected.\nUse Webcam or Upload below.",
        ))

    def _bgr_to_pil(self, bgr_frame: np.ndarray) -> Image.Image:
        rgb = cv2.cvtColor(bgr_frame, cv2.COLOR_BGR2RGB)
        return Image.fromarray(rgb)

    def _set_status(self, msg: str, error: bool = False):
        color = "#E24B4A" if error else "gray"
        self.after(0, lambda: self.status_label.configure(text=msg, text_color=color))

    def cleanup(self):
        """Call this when the window closes to release the webcam."""
        self._running = False
        if self._cap:
            self._cap.release()