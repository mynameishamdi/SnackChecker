# ── src/ui/main_window.py ──────────────────────────────────────────────────
# Main application window with session history sidebar and Settings modal.
# Layout: [Input Panel] | [Result Panel] | [History Sidebar]
# ---------------------------------------------------------------------------

import os
import json
import shutil
import threading
from datetime import datetime
import customtkinter as ctk
from tkinter import filedialog, messagebox

from src.classifier      import SnackClassifier
from src.gemini_client   import GeminiClient
from src.ui.input_panel  import InputPanel
from src.ui.result_panel import ResultPanel
from src.translations    import get_text

from src.snack_data import (
    get_display_name, get_tier_display, get_snack, get_meter_color, calculate_teh_tarik_index
)


class MainWindow(ctk.CTk):
    WINDOW_SIZE = "1200x700" 
    CONFIDENCE_THRESHOLD = 70.0

    def __init__(self, classifier: SnackClassifier):
        super().__init__()
        self._classifier   = classifier
        
        # Setup API key and initialize Gemini internally
        user_api_key = self._setup_api_key()
        self._gemini = GeminiClient(api_key=user_api_key)
        
        self._history      = []   
        
        self.current_language   = "English"
        self.settings_window    = None
        self.compare_window     = None 
        self.current_snack      = None 
        self.current_confidence = None 

        self.title(get_text("title", self.current_language))
        self.geometry(self.WINDOW_SIZE)
        self.resizable(True, True)
        self.after(0, self._maximize_window)
        self.protocol("WM_DELETE_WINDOW", self._on_close)
        self._build_ui()

    # The API Key Popup Logic
    def _setup_api_key(self) -> str:
        """Loads the API key from a permanent location, or asks the user if it doesn't exist."""
        # Get the user's permanent home directory (e.g., C:\Users\John\)
        user_home = os.path.expanduser("~")
        settings_file = os.path.join(user_home, "snackchecker_settings.json")
        
        # 1. Try to load an existing key
        if os.path.exists(settings_file):
            try:
                with open(settings_file, "r") as f:
                    data = json.load(f)
                    if data.get("api_key"):
                        return data["api_key"]
            except Exception:
                pass # If file is corrupted, ignore and ask again

        # 2. If no key is found, show the CustomTkinter Popup
        dialog = ctk.CTkInputDialog(
            text="Welcome to SnackChecker!\n\nTo enable AI Analysis, please paste your Google Gemini API Key below.\n(You only have to do this once).", 
            title="API Key Setup"
        )
        user_key = dialog.get_input()

        # 3. Save the key so they don't have to type it next time
        if user_key:
            with open(settings_file, "w") as f:
                json.dump({"api_key": user_key}, f)
            return user_key
            
        return "" # Returns empty if they click cancel

    def _maximize_window(self):
        try: self.state('zoomed') 
        except: 
            try: self.attributes('-zoomed', True)
            except: pass

    # ── Build UI ─────────────────────────────────────────────────────────────
    def _build_ui(self):
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        header = ctk.CTkFrame(self, corner_radius=0, height=60)
        header.grid(row=0, column=0, sticky="ew")
        header.grid_propagate(False)
        header.grid_columnconfigure(0, weight=1) 
        header.grid_columnconfigure(1, weight=0) 

        self.header_title = ctk.CTkLabel(header, text=f"🥜  {get_text('title', self.current_language)}", font=ctk.CTkFont(size=18, weight="bold"))
        self.header_title.grid(row=0, column=0, padx=20, pady=(10, 2), sticky="w")

        self.header_subtitle = ctk.CTkLabel(header, text=get_text("subtitle", self.current_language), font=ctk.CTkFont(size=12), text_color="gray")
        self.header_subtitle.grid(row=1, column=0, padx=20, pady=(0, 8), sticky="w")

        self.settings_btn = ctk.CTkButton(header, text=get_text("settings", self.current_language), width=100, height=32, fg_color=("gray70", "gray30"), hover_color=("gray60", "gray20"), command=self._open_settings)
        self.settings_btn.grid(row=0, column=1, rowspan=2, padx=20, pady=10, sticky="e")

        content = ctk.CTkFrame(self, fg_color="transparent")
        content.grid(row=1, column=0, sticky="nsew", padx=12, pady=10)
        content.grid_rowconfigure(0, weight=1)
        content.grid_columnconfigure(0, weight=0)   
        content.grid_columnconfigure(1, weight=1)   
        content.grid_columnconfigure(2, weight=0)   

        self.input_panel = InputPanel(content, on_image_ready=self._on_image_ready)
        self.input_panel.grid(row=0, column=0, sticky="nsew", padx=(0, 8))

        ctk.CTkFrame(content, width=1, fg_color=("gray80", "gray30")).grid(row=0, column=1, sticky="ns", padx=(0, 8))

        self.result_panel = ResultPanel(content)
        self.result_panel.grid(row=0, column=1, sticky="nsew", padx=(0, 8))

        ctk.CTkFrame(content, width=1, fg_color=("gray80", "gray30")).grid(row=0, column=2, sticky="ns", padx=(0, 8))

        self._build_history_sidebar(content)

    def _build_history_sidebar(self, parent):
        sidebar = ctk.CTkFrame(parent, width=200, corner_radius=10)
        sidebar.grid(row=0, column=3, sticky="nsew")
        sidebar.grid_propagate(False)
        sidebar.grid_columnconfigure(0, weight=1)
        sidebar.grid_rowconfigure(1, weight=1)
        sidebar.grid_rowconfigure(2, weight=0) 

        self.history_title = ctk.CTkLabel(sidebar, text=get_text("history", self.current_language), font=ctk.CTkFont(size=13, weight="bold"), anchor="w")
        self.history_title.grid(row=0, column=0, sticky="w", padx=12, pady=(12, 6))

        self.history_scroll = ctk.CTkScrollableFrame(sidebar, fg_color="transparent", width=180)
        self.history_scroll.grid(row=1, column=0, sticky="nsew", padx=6, pady=(0, 6))
        self.history_scroll.grid_columnconfigure(0, weight=1)

        self.history_empty_label = ctk.CTkLabel(self.history_scroll, text=get_text("no_scans", self.current_language), font=ctk.CTkFont(size=11), text_color="gray")
        self.history_empty_label.grid(row=0, column=0, pady=12)

        self.compare_btn = ctk.CTkButton(
            sidebar, text=get_text("compare_btn", self.current_language),
            fg_color=("gray70", "gray30"), hover_color=("gray60", "gray20"), text_color=("gray10", "gray90"), command=self._open_compare_window
        )
        self.compare_btn.grid(row=2, column=0, padx=12, pady=12, sticky="ew")

    # ── ADVANCED Compare Feature ──────────────────────────────────────────────
    def _open_compare_window(self):
        if self.compare_window is not None and self.compare_window.winfo_exists():
            self.compare_window.focus()
            return

        self.compare_window = ctk.CTkToplevel(self)
        self.compare_window.title(get_text("compare_title", self.current_language))
        self.compare_window.geometry("900x650")
        self.compare_window.attributes("-topmost", True)
        self.compare_window.grid_columnconfigure((0, 1), weight=1)
        self.compare_window.grid_rowconfigure(1, weight=1)
        self.compare_window.grid_rowconfigure(2, weight=0)

        active_labels = self._classifier.labels
        self.snack_map = {get_display_name(lbl): lbl for lbl in active_labels}
        display_names = list(self.snack_map.keys())

        self.val_a = ctk.StringVar(value=display_names[0] if len(display_names) > 0 else "")
        self.val_b = ctk.StringVar(value=display_names[1] if len(display_names) > 1 else (display_names[0] if display_names else ""))

        drop_a = ctk.CTkOptionMenu(self.compare_window, values=display_names, variable=self.val_a, command=self._refresh_compare)
        drop_a.grid(row=0, column=0, padx=20, pady=15, sticky="ew")

        drop_b = ctk.CTkOptionMenu(self.compare_window, values=display_names, variable=self.val_b, command=self._refresh_compare)
        drop_b.grid(row=0, column=1, padx=20, pady=15, sticky="ew")

        self.frame_a = ctk.CTkFrame(self.compare_window, fg_color=("gray90", "gray15"))
        self.frame_a.grid(row=1, column=0, sticky="nsew", padx=15, pady=(0, 15))

        self.frame_b = ctk.CTkFrame(self.compare_window, fg_color=("gray90", "gray15"))
        self.frame_b.grid(row=1, column=1, sticky="nsew", padx=15, pady=(0, 15))

        self.ai_panel = ctk.CTkFrame(self.compare_window, fg_color="transparent")
        self.ai_panel.grid(row=2, column=0, columnspan=2, sticky="ew", padx=15, pady=(0, 15))
        
        self.ai_verdict_btn = ctk.CTkButton(
            self.ai_panel, text=get_text("ask_ai", self.current_language), 
            font=ctk.CTkFont(weight="bold"), fg_color="#8e44ad", hover_color="#732d91", command=self._fetch_ai_verdict
        )
        self.ai_verdict_btn.pack(pady=10)

        self.ai_verdict_lbl = ctk.CTkLabel(self.ai_panel, text="", wraplength=800, justify="center", font=ctk.CTkFont(size=14, slant="italic"))
        
        self._refresh_compare()

    def _refresh_compare(self, *args):
        for widget in self.frame_a.winfo_children(): widget.destroy()
        for widget in self.frame_b.winfo_children(): widget.destroy()
        
        self.ai_verdict_lbl.pack_forget()
        self.ai_verdict_btn.pack(pady=10)

        lbl_a = self.snack_map.get(self.val_a.get())
        lbl_b = self.snack_map.get(self.val_b.get())

        data_a = get_snack(lbl_a)
        data_b = get_snack(lbl_b)

        tier_val = {"healthy": 3, "moderate": 2, "junk": 1}
        val_a = tier_val.get(data_a.get('tier', 'moderate'), 2)
        val_b = tier_val.get(data_b.get('tier', 'moderate'), 2)
        
        self._draw_compare_card(self.frame_a, data_a, data_b, lbl_a, winner=(val_a > val_b), both_junk=(val_a==1 and val_b==1))
        self._draw_compare_card(self.frame_b, data_b, data_a, lbl_b, winner=(val_b > val_a), both_junk=(val_a==1 and val_b==1))

    def _draw_compare_card(self, parent, data_main, data_other, lbl_main, winner=False, both_junk=False):
        if not data_main: return
        lang = self.current_language
        tier = get_tier_display(lbl_main)
        
        ctk.CTkLabel(parent, text=data_main.get('display_name', 'Unknown'), font=ctk.CTkFont(size=20, weight="bold")).pack(pady=(15,2))
        
        if winner:
            ctk.CTkLabel(parent, text=get_text("winner", lang), text_color="#1D9E75", font=ctk.CTkFont(size=14, weight="bold")).pack(pady=(0,10))
        elif both_junk:
            ctk.CTkLabel(parent, text=get_text("both_junk", lang), text_color="#E24B4A", font=ctk.CTkFont(size=14, weight="bold")).pack(pady=(0,10))
        else:
            ctk.CTkLabel(parent, text=tier['label'], text_color=tier['color'], font=ctk.CTkFont(size=12, weight="bold")).pack(pady=(0,10))

        stats = [
            (get_text("calories", lang), 'base_calories', f" kcal", 600.0),
            (get_text("sugar", lang), 'sugar_grams', f"g", 50.0),
            (get_text("sodium", lang), 'sodium_dv_percent', f"% DV", 100.0),
            (get_text("fat", lang), 'fat_dv_percent', f"% DV", 100.0)
        ]

        for name, key, suffix, max_val in stats:
            val_m = data_main.get(key, 0)
            val_o = data_other.get(key, 0)
            diff = round(val_m - val_o, 1)
            
            row = ctk.CTkFrame(parent, fg_color="transparent")
            row.pack(fill="x", padx=15, pady=4)
            ctk.CTkLabel(row, text=name, anchor="w").pack(side="left")
            
            if diff < 0:
                delta_txt = f"({abs(diff)}{suffix} {get_text('less', lang)})"
                ctk.CTkLabel(row, text=delta_txt, text_color="#1D9E75", font=ctk.CTkFont(size=11, weight="bold")).pack(side="right", padx=(5,0))
            elif diff > 0:
                delta_txt = f"(+{diff}{suffix} {get_text('more', lang)})"
                ctk.CTkLabel(row, text=delta_txt, text_color="#E24B4A", font=ctk.CTkFont(size=11, weight="bold")).pack(side="right", padx=(5,0))
                
            ctk.CTkLabel(row, text=f"{val_m}{suffix}", font=ctk.CTkFont(weight="bold")).pack(side="right")
            
            pct = min(100, max(0, (val_m/max_val)*100))
            pb = ctk.CTkProgressBar(parent, progress_color=get_meter_color(pct), height=8)
            pb.pack(fill="x", padx=15, pady=(0, 10))
            pb.set(pct/100.0)
            
        if "sugar_grams" in data_main:
            tt_txt = calculate_teh_tarik_index(data_main['sugar_grams'])
            ctk.CTkLabel(parent, text=f"🧋 {get_text('equiv', lang)}: {tt_txt}", font=ctk.CTkFont(size=12, slant="italic"), text_color="#EF9F27").pack(pady=(10, 10))

    def _fetch_ai_verdict(self):
        self.ai_verdict_btn.pack_forget()
        self.ai_verdict_lbl.configure(text=get_text("ai_loading", self.current_language), text_color="gray")
        self.ai_verdict_lbl.pack(pady=10)
        
        lbl_a = self.snack_map.get(self.val_a.get())
        lbl_b = self.snack_map.get(self.val_b.get())
        lang = self.current_language
        
        threading.Thread(target=self._background_ai_call, args=(lbl_a, lbl_b, lang), daemon=True).start()
        
    def _background_ai_call(self, lbl_a, lbl_b, lang):
        try:
            verdict = self._gemini.get_comparison_verdict(lbl_a, lbl_b, lang=lang)
            self.after(0, lambda: self.ai_verdict_lbl.configure(text=verdict, text_color=("gray10", "gray90")))
        except Exception as e:
            self.after(0, lambda: self.ai_verdict_lbl.configure(text=f"Error: {e}", text_color="#E24B4A"))

    # ── Settings & Language Management ─────────────────────────────────────────
    def _open_settings(self):
        if self.settings_window is not None and self.settings_window.winfo_exists():
            self.settings_window.focus()
            return
            
        self.settings_window = ctk.CTkToplevel(self)
        self.settings_window.title(get_text("settings", self.current_language))
        self.settings_window.geometry("400x350")
        self.settings_window.resizable(False, False)
        self.settings_window.attributes("-topmost", True)
        
        ctk.CTkLabel(self.settings_window, text=get_text("lang_toggle", self.current_language), font=ctk.CTkFont(weight="bold")).pack(pady=(20, 5))
        lang_menu = ctk.CTkOptionMenu(self.settings_window, values=["English", "Bahasa Melayu"], command=self._change_language)
        lang_menu.set(self.current_language)
        lang_menu.pack(pady=5)
        
        ctk.CTkLabel(self.settings_window, text=get_text("model_swapper", self.current_language), font=ctk.CTkFont(weight="bold")).pack(pady=(20, 5))
        ctk.CTkButton(self.settings_window, text=get_text("upload_h5", self.current_language), command=self._upload_h5).pack(pady=5)
        ctk.CTkButton(self.settings_window, text=get_text("upload_lbl", self.current_language), command=self._upload_labels).pack(pady=5)
        ctk.CTkButton(self.settings_window, text=get_text("restore", self.current_language), fg_color="#E24B4A", hover_color="#C0392B", command=self._restore_defaults).pack(pady=(15, 5))

    def _change_language(self, choice):
        self.current_language = choice
        self.title(get_text("title", choice))
        self.header_title.configure(text=f"🥜  {get_text('title', choice)}")
        self.header_subtitle.configure(text=get_text('subtitle', choice))
        self.settings_btn.configure(text=get_text('settings', choice))
        self.history_title.configure(text=get_text('history', choice))
        self.compare_btn.configure(text=get_text('compare_btn', choice))
        
        if self.history_empty_label.winfo_exists():
            self.history_empty_label.configure(text=get_text('no_scans', choice))
            
        if self.settings_window and self.settings_window.winfo_exists():
            self.settings_window.destroy()
            self._open_settings() 

        if self.compare_window and self.compare_window.winfo_exists():
            self.compare_window.title(get_text("compare_title", choice))
            self.ai_verdict_btn.configure(text=get_text("ask_ai", choice))
            self._refresh_compare() 

        if self.current_snack and self.current_confidence:
            self.result_panel.show_loading(self.current_snack, self.current_confidence, choice)
            threading.Thread(target=self._refetch_translation, args=(self.current_snack, self.current_confidence, choice), daemon=True).start()
        else:
            self.result_panel.show_empty_state(choice)

    def _refetch_translation(self, snack_label, confidence, lang):
        try:
            content = self._gemini.get_snack_content(snack_label, lang=lang)
            self.after(0, self.result_panel.show_result, snack_label, confidence, content, lang)
        except Exception as e:
            self.after(0, self._show_error, str(e))

    def _upload_h5(self):
        path = filedialog.askopenfilename(title="Select Model", filetypes=[("H5 Files", "*.h5")])
        if path:
            shutil.copy(path, "model/keras_model.h5")
            self._classifier.reload_model()
            messagebox.showinfo("Success", "Custom model loaded successfully!")

    def _upload_labels(self):
        path = filedialog.askopenfilename(title="Select Labels", filetypes=[("Text Files", "*.txt")])
        if path:
            shutil.copy(path, "model/labels.txt")
            self._classifier.reload_model()
            messagebox.showinfo("Success", "Custom labels loaded successfully!")

    def _restore_defaults(self):
        try:
            shutil.copy("model/default_backup/keras_model.h5", "model/keras_model.h5")
            shutil.copy("model/default_backup/labels.txt", "model/labels.txt")
            self._classifier.reload_model()
            messagebox.showinfo("Success", "Factory default model restored!")
        except FileNotFoundError:
            messagebox.showerror("Error", "Could not find backup files in 'model/default_backup/'!")

    # ── Classification flow ──────────────────────────────────────────────────
    def _on_image_ready(self, img_array, pil_image):
        threading.Thread(target=self._classify_and_fetch, args=(img_array,), daemon=True).start()

    def _classify_and_fetch(self, img_array):
        try:
            snack_label, confidence = self._classifier.predict(img_array)

            if confidence < self.CONFIDENCE_THRESHOLD:
                self.current_snack = None 
                self.after(0, self.result_panel.show_low_confidence, confidence, self.current_language)
                self.after(0, lambda: self.input_panel.reset_btn.configure(state="normal"))
                return

            if snack_label == "background":
                self.current_snack = None 
                self.after(0, lambda: self.result_panel.show_empty_state(self.current_language))
                self.after(0, lambda: self.input_panel.reset_btn.configure(state="normal"))
                return
            
            self.current_snack = snack_label
            self.current_confidence = confidence

            self.after(0, self.result_panel.show_loading, snack_label, confidence, self.current_language)
            self.after(0, self._add_to_history, snack_label, confidence)

            content = self._gemini.get_snack_content(snack_label, lang=self.current_language)

            self.after(0, self.result_panel.show_result, snack_label, confidence, content, self.current_language)
            self.after(0, lambda: self.input_panel.reset_btn.configure(state="normal"))

        except Exception as e:
            self.after(0, self._show_error, str(e))

    # ── History ───────────────────────────────────────────────────────────────
    def _add_to_history(self, snack_label: str, confidence: float):
        self._history.append((snack_label, confidence))

        if len(self._history) == 1:
            self.history_empty_label.grid_remove()

        tier_info    = get_tier_display(snack_label)
        display_name = get_display_name(snack_label)
        row_num      = len(self._history) - 1
        current_time = datetime.now().strftime("%I:%M %p")

        item = ctk.CTkFrame(self.history_scroll, corner_radius=6, fg_color=tier_info["bg_color"])
        item.grid(row=row_num, column=0, sticky="ew", pady=(0, 4))
        item.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            item, text=f"🕒 {current_time} - {display_name}", font=ctk.CTkFont(size=11, weight="bold"),
            text_color=tier_info["color"], wraplength=160, justify="left", anchor="w",
        ).grid(row=0, column=0, padx=8, pady=(6, 2), sticky="w")

        ctk.CTkLabel(
            item, text=f"[{tier_info['label']}] • {confidence:.0f}% conf", font=ctk.CTkFont(size=10), text_color="gray", anchor="w",
        ).grid(row=1, column=0, padx=8, pady=(0, 6), sticky="w")

    def _show_error(self, message: str):
        messagebox.showerror("Error", message)
        self.input_panel.reset_btn.configure(state="normal")

    def _on_close(self):
        self.input_panel.cleanup()
        self.destroy()