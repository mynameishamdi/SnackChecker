# ── src/ui/result_panel.py ─────────────────────────────────────────────────
# Right panel — The Interactive Health Dashboard.
# Consumes both static math (snack_data) and AI text (gemini_client).
# ---------------------------------------------------------------------------

import os
import customtkinter as ctk
from PIL import Image

from src.snack_data import (
    get_snack, get_meter_color, calculate_teh_tarik_index, 
    calculate_burn_minutes, get_sport_options
)
from src.translations import get_text

class ResultPanel(ctk.CTkFrame):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, fg_color="transparent", **kwargs)
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
        self.container = ctk.CTkFrame(self, fg_color="transparent")
        self.container.grid(row=0, column=0, sticky="nsew")
        self.show_empty_state("English")

    def _clear(self):
        for widget in self.container.winfo_children():
            widget.destroy()
        self.container.grid_rowconfigure("all", weight=0)
        self.container.grid_columnconfigure(0, weight=1)

    def show_empty_state(self, lang="English"):
        self._clear()
        ctk.CTkLabel(
            self.container, 
            text=get_text("waiting", lang), 
            font=ctk.CTkFont(size=14, slant="italic"),
            text_color="gray"
        ).pack(expand=True)

    def show_low_confidence(self, confidence: float, lang="English"):
        self._clear()
        ctk.CTkLabel(self.container, text="⚠️ Unrecognized Snack", font=ctk.CTkFont(size=18, weight="bold"), text_color="#E24B4A").pack(pady=(100, 10))
        ctk.CTkLabel(self.container, text=f"Confidence is too low ({confidence:.0f}%).\nPlease try again.", text_color="gray").pack()

    def show_loading(self, snack_label: str, confidence: float, lang="English"):
        self._clear()
        ctk.CTkLabel(self.container, text=f"{get_text('analyzing', lang)} '{snack_label}'...", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=(100, 10))
        ctk.CTkLabel(self.container, text=get_text('consulting', lang), text_color="gray").pack()

    def show_result(self, snack_label: str, confidence: float, ai_content: dict, lang: str = "English"):
        self._clear()
        self.current_lang = lang # Store for button callbacks
        
        metadata = get_snack(snack_label)
        scroll = ctk.CTkScrollableFrame(self.container, fg_color="transparent")
        scroll.pack(fill="both", expand=True)

        self._build_header(scroll, metadata)
        self._build_danger_meters(scroll, metadata, lang)
        self._build_burn_calculator(scroll, metadata, lang)
        
        if "summary" in ai_content:
            self._build_text_card(scroll, get_text("analysis", lang), ai_content["summary"])
            
        if "fun_fact" in ai_content:
            self._build_text_card(scroll, get_text("did_you_know", lang), ai_content["fun_fact"])
            
        if "cara_makan" in ai_content:
            self._build_text_card(scroll, get_text("cara_makan", lang), ai_content["cara_makan"])
            
        if "healthier_swaps" in ai_content:
            self._build_swap_card(scroll, ai_content["healthier_swaps"], lang)

    def _build_header(self, parent, metadata):
        header_frame = ctk.CTkFrame(parent, fg_color="transparent")
        header_frame.pack(fill="x", pady=(0, 15))
        
        ctk.CTkLabel(header_frame, text=metadata.get("display_name", "Unknown Snack"), font=ctk.CTkFont(size=22, weight="bold")).pack(anchor="w")
        
        badge_row = ctk.CTkFrame(header_frame, fg_color="transparent")
        badge_row.pack(fill="x", pady=(5, 0))
        
        is_local = metadata.get("is_local", False)
        loc_text = "Buatan Malaysia" if is_local else "Imported"
        loc_img = "buatan_malaysia.png" if is_local else "imported.png"
        self._create_graceful_badge(badge_row, loc_text, loc_img, "#2980b9").pack(side="left", padx=(0, 5))
        
        if metadata.get("halal_certified", False):
            self._create_graceful_badge(badge_row, "Halal", "halal.png", "#1D9E75").pack(side="left", padx=(0, 5))
            
        for cert in metadata.get("safety_certs", []):
            self._create_graceful_badge(badge_row, cert, f"{cert.lower()}.png", "#8e44ad").pack(side="left", padx=(0, 5))

    def _create_graceful_badge(self, parent, text, filename, color):
        path = os.path.join("assets", "logos", filename)
        try:
            img = Image.open(path)
            ctk_img = ctk.CTkImage(light_image=img, dark_image=img, size=(20, 20))
            return ctk.CTkLabel(parent, text=f" {text}", image=ctk_img, compound="left", fg_color=color, text_color="white", corner_radius=6, padx=8, pady=4, font=ctk.CTkFont(size=11, weight="bold"))
        except FileNotFoundError:
            return ctk.CTkLabel(parent, text=text, fg_color=color, text_color="white", corner_radius=6, padx=8, pady=4, font=ctk.CTkFont(size=11, weight="bold"))

    def _build_danger_meters(self, parent, metadata, lang):
        card = self._create_card(parent, get_text("danger_meters", lang))
        
        sodium_dv = metadata.get("sodium_dv_percent", 0)
        fat_dv = metadata.get("fat_dv_percent", 0)
        sugar_g = metadata.get("sugar_grams", 0.0)
        sugar_dv = min(100, int((sugar_g / 50.0) * 100))

        self._add_meter(card, get_text("sodium", lang), sodium_dv)
        self._add_meter(card, get_text("fat", lang), fat_dv)
        self._add_meter(card, f"{get_text('sugar', lang)} ({sugar_g}g)", sugar_dv)
        
        teh_tarik_txt = calculate_teh_tarik_index(sugar_g)
        ctk.CTkLabel(card, text=f"🧋 {get_text('equiv', lang)}: {teh_tarik_txt}", font=ctk.CTkFont(size=12, slant="italic"), text_color="#EF9F27").pack(anchor="w", padx=10, pady=(0, 10))

    def _add_meter(self, parent, label, percent):
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.pack(fill="x", padx=10, pady=5)
        ctk.CTkLabel(frame, text=f"{label} ({percent}%)", font=ctk.CTkFont(size=12)).pack(side="left")
        color = get_meter_color(percent)
        pb = ctk.CTkProgressBar(frame, progress_color=color, height=12)
        pb.pack(side="right", fill="x", expand=True, padx=(10, 0))
        pb.set(percent / 100.0)

    def _build_burn_calculator(self, parent, metadata, lang):
        card = self._create_card(parent, get_text("burn_calc", lang))
        self.current_cals = metadata.get("base_calories", 0)
        
        row = ctk.CTkFrame(card, fg_color="transparent")
        row.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkLabel(row, text=get_text("select_act", lang)).pack(side="left", padx=(0, 10))
        
        sports = get_sport_options()
        self.sport_dropdown = ctk.CTkOptionMenu(row, values=sports, command=self._on_sport_change)
        self.sport_dropdown.set(sports[0])
        self.sport_dropdown.pack(side="left")
        
        self.burn_result_label = ctk.CTkLabel(card, text="", font=ctk.CTkFont(size=16, weight="bold"), text_color="#1D9E75")
        self.burn_result_label.pack(anchor="center", pady=(0, 10))
        self._on_sport_change(sports[0])

    def _on_sport_change(self, selected_sport):
        result_text = calculate_burn_minutes(self.current_cals, selected_sport)
        self.burn_result_label.configure(text=f"{get_text('requires', self.current_lang)} {result_text}")

    def _build_swap_card(self, parent, swaps_array, lang):
        card = self._create_card(parent, get_text("swaps", lang))
        
        if not swaps_array:
            ctk.CTkLabel(card, text=get_text("great_choice", lang), text_color="#1D9E75", font=ctk.CTkFont(weight="bold")).pack(pady=10)
            ctk.CTkLabel(card, text=get_text("keep_up", lang)).pack(pady=(0,10))
            return

        self.swaps = swaps_array
        self.current_swap_idx = 0
        
        self.swap_title = ctk.CTkLabel(card, text="", font=ctk.CTkFont(size=14, weight="bold"))
        self.swap_title.pack(anchor="w", padx=10, pady=(5, 0))
        self.swap_note = ctk.CTkLabel(card, text="", wraplength=450, justify="left")
        self.swap_note.pack(anchor="w", padx=10, pady=(0, 10))
        
        self._update_swap_ui()
        ctk.CTkButton(card, text=get_text("see_another", lang), fg_color="transparent", border_width=1, text_color=("gray10", "gray90"), command=self._cycle_swap).pack(pady=(0, 10))

    def _cycle_swap(self):
        self.current_swap_idx = (self.current_swap_idx + 1) % len(self.swaps)
        self._update_swap_ui()

    def _update_swap_ui(self):
        active_swap = self.swaps[self.current_swap_idx]
        self.swap_title.configure(text=f"{get_text('try_this', self.current_lang)} {active_swap.get('name', 'Alternative')}")
        self.swap_note.configure(text=active_swap.get('note', ''))

    def _build_text_card(self, parent, title, text_content):
        card = self._create_card(parent, title)
        ctk.CTkLabel(card, text=text_content, wraplength=450, justify="left").pack(anchor="w", padx=10, pady=10)

    def _create_card(self, parent, title):
        card = ctk.CTkFrame(parent, corner_radius=10, fg_color=("gray90", "gray15"))
        card.pack(fill="x", pady=8)
        ctk.CTkLabel(card, text=title, font=ctk.CTkFont(size=14, weight="bold")).pack(anchor="w", padx=10, pady=(10, 0))
        return card