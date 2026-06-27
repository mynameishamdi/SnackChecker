# ── app.py ─────────────────────────────────────────────────────────────────
# Entry point for the SnackChecker AI Application.
#
# DEVELOPER SETUP INSTRUCTIONS:
#   1. Model: Place your exported Teachable Machine model at `model/keras_model.h5`
#   2. Labels: Place the exported text labels at `model/labels.txt`
#   3. API Key: No hardcoding required! The GUI automatically prompts the user 
#      for their Gemini API key on first launch and saves it to `settings.json`.
# ---------------------------------------------------------------------------

import sys
import os
import customtkinter as ctk

# ── Resolve path for PyInstaller standalone .exe ────────────────────────────
# When packaged, sys._MEIPASS points to the temp folder with bundled files.
if getattr(sys, "frozen", False):
    BASE_DIR = sys._MEIPASS
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
os.chdir(BASE_DIR)

# ── App theme ─────────────────────────────────────────────────────────────────
ctk.set_appearance_mode("System")    # follows OS light/dark setting
ctk.set_default_color_theme("green")

# ── Startup ───────────────────────────────────────────────────────────────────
def main():
    from src.classifier    import SnackClassifier
    from src.ui.main_window import MainWindow

    # Load model (shows error dialog if model/keras_model.h5 is missing)
    try:
        classifier = SnackClassifier()
    except FileNotFoundError as e:
        import tkinter as tk
        from tkinter import messagebox
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror("Model Not Found", str(e))
        root.destroy()
        sys.exit(1)

    # Launch window (GeminiClient is now safely initialized inside MainWindow!)
    window = MainWindow(classifier=classifier)
    window.mainloop()


if __name__ == "__main__":
    main()