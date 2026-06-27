# ── src/snack_data.py ──────────────────────────────────────────────────────
# Central data dictionary — static nutrition database + deterministic math.
#
# CRITICAL DEVELOPER NOTE:
# The dictionary keys in SNACK_DATABASE below MUST exactly match the spelling 
# and format of the classes defined in your Teachable Machine 'labels.txt'.
# (e.g., if labels.txt says "1 instant_noodles", the key must be "instant_noodles").
# ---------------------------------------------------------------------------

# ── Teh Tarik Sugar & Exercise Constants ─────────────────────────────────────
TEH_TARIK_SUGAR_G      = 18.0   # grams of sugar in one glass of teh tarik
BADMINTON_KCAL_PER_MIN = 7.5    # average kcal burned per minute of badminton

# ── Class labels ────────────────────────────────────────────────────────────
# EXACT MATCH to your new labels.txt! Order is critical!
CLASS_LABELS = [
    "background",
    "instant_noodles",
    "chips",
    "chocolate",
    "biscuits",
    "instant_drink"
]

# ── Nutrition Database (Categorical Averages) ─────────────────────────────────
SNACK_DATABASE = {
    "background": {
        "display_name":      "No Snack Detected",
        "tier":              "moderate",
        "is_local":          False,
        "origin":            "N/A",
        "halal_certified":   False,
        "halal_source":      "N/A",
        "safety_certs":      [],
        "base_calories":     0,
        "sugar_grams":       0.0,
        "sodium_dv_percent": 0,
        "fat_dv_percent":    0,
        "sat_fat_dv_percent": 0,
    },
    "instant_noodles": {
        "display_name":      "Instant Noodles",
        "tier":              "junk",
        "is_local":          True, 
        "origin":            "Various Brands",
        "halal_certified":   True,
        "halal_source":      "Usually JAKIM/MUI",
        "safety_certs":      ["MeSTI"],
        "base_calories":     400,
        "sugar_grams":       3.0,
        "sodium_dv_percent": 65,
        "fat_dv_percent":    25,
        "sat_fat_dv_percent": 35,
    },
    "chips": {
        "display_name":      "Savoury Chips & Snacks",
        "tier":              "junk",
        "is_local":          True,
        "origin":            "Various Brands",
        "halal_certified":   True,
        "halal_source":      "Usually JAKIM",
        "safety_certs":      ["MeSTI"],
        "base_calories":     160,
        "sugar_grams":       1.0,  
        "sodium_dv_percent": 18,
        "fat_dv_percent":    12,
        "sat_fat_dv_percent": 10,
    },
    "chocolate": {
        "display_name":      "Chocolate & Sweet Snacks",
        "tier":              "junk",
        "is_local":          False,
        "origin":            "Various Brands",
        "halal_certified":   True,
        "halal_source":      "Usually JAKIM/MUI",
        "safety_certs":      [],
        "base_calories":     250,
        "sugar_grams":       25.0,
        "sodium_dv_percent": 2,     
        "fat_dv_percent":    15,
        "sat_fat_dv_percent": 20,
    },
    "biscuits": {
        "display_name":      "Processed Biscuits",
        "tier":              "moderate",
        "is_local":          True,
        "origin":            "Various Brands",
        "halal_certified":   True,
        "halal_source":      "Usually JAKIM",
        "safety_certs":      ["MeSTI"],
        "base_calories":     150,
        "sugar_grams":       6.0,
        "sodium_dv_percent": 10,
        "fat_dv_percent":    12,
        "sat_fat_dv_percent": 15,
    },
    "instant_drink": {
        "display_name":      "3-in-1 Instant Drinks",
        "tier":              "moderate",
        "is_local":          True,
        "origin":            "Various Brands",
        "halal_certified":   True,
        "halal_source":      "Usually JAKIM",
        "safety_certs":      ["MeSTI"],
        "base_calories":     120,
        "sugar_grams":       15.0,
        "sodium_dv_percent": 3,
        "fat_dv_percent":    4,
        "sat_fat_dv_percent": 6,
    }
}

# ── Tier display metadata ────────────────────────────────────────────────────
TIER_DISPLAY = {
    "junk": {
        "label":        "JUNK SNACK",
        "color":        "#E24B4A",
        "bg_color":     "#FCEBEB",
        "swap_heading": "Try this instead! 💡",
    },
    "moderate": {
        "label":        "MODERATELY HEALTHY",
        "color":        "#EF9F27",
        "bg_color":     "#FAEEDA",
        "swap_heading": "A slightly better option:",
    },
    "healthy": {
        "label":        "HEALTHY SNACK",
        "color":        "#1D9E75",
        "bg_color":     "#E1F5EE",
        "swap_heading": "Great choice! 💪",
    },
}

# ── Exercise Burn Rates ──────────────────────────────────────────────────────
SPORT_KCAL_PER_MIN = {
    "Jogging / Running 🏃": 10.0,
    "Futsal ⚽": 8.5,
    "Badminton 🏸": 7.5,
    "Cycling 🚲": 6.0,
    "Mall Walking 🛍️": 3.5
}

# ── Danger meter colour thresholds ───────────────────────────────────────────
def get_meter_color(dv_percent: int) -> str:
    if dv_percent <= 30:
        return "#1D9E75"   # green — low
    elif dv_percent <= 60:
        return "#EF9F27"   # amber — moderate
    else:
        return "#E24B4A"   # red — high

# ── Math functions ────────────────────────────────────────────────────────────
def calculate_teh_tarik_index(sugar_grams: float) -> str:
    """Returns e.g. '1.4 glasses of Teh Tarik'"""
    glasses = round(sugar_grams / TEH_TARIK_SUGAR_G, 1)
    if glasses < 0.1:
        return "< 0.1 glasses of Teh Tarik"
    return f"{glasses} glass{'es' if glasses != 1.0 else ''} of Teh Tarik 🧋"

def calculate_burn_minutes(calories: int, sport_name: str) -> str:
    """Calculates minutes needed for a specific sport selection."""
    rate = SPORT_KCAL_PER_MIN.get(sport_name, 7.5)
    
    # Safety catch to prevent divide by zero for 'background' scans
    if rate <= 0: return "0 mins"
    
    minutes = round(calories / rate)
    clean_name = sport_name.replace(" 🏃", "").replace(" ⚽", "").replace(" 🏸", "").replace(" 🚲", "").replace(" 🛍️", "")
    return f"{minutes} mins of {clean_name}"

def calculate_badminton_minutes(calories: int) -> str:
    """Legacy helper fallback for backwards compatibility across older files."""
    minutes = round(calories / BADMINTON_KCAL_PER_MIN)
    return f"{minutes} mins of Badminton 🏸"

# ── Lookup helpers ────────────────────────────────────────────────────────────
def get_sport_options() -> list[str]:
    """Returns the list of sports for the UI dropdown."""
    return list(SPORT_KCAL_PER_MIN.keys())

def get_snack(snack_label: str) -> dict:
    """Returns the snack data, or a safe fallback structure for custom uploaded models."""
    if snack_label in SNACK_DATABASE:
        return SNACK_DATABASE[snack_label]
    
    # Custom Model Fallback to ensure safety across varying uploaded architectures
    return {
        "display_name":      snack_label.replace("_", " ").title(),
        "tier":              "moderate", 
        "is_local":          False,
        "origin":            "Unknown Source",
        "halal_certified":   False,
        "halal_source":      "N/A",
        "safety_certs":      [],
        "base_calories":     0,
        "sugar_grams":       0.0,
        "sodium_dv_percent": 0,
        "fat_dv_percent":    0,
        "sat_fat_dv_percent": 0,
    }

def get_display_name(snack_label: str) -> str:
    snack = get_snack(snack_label)
    return snack["display_name"]

def get_tier(snack_label: str) -> str:
    snack = get_snack(snack_label)
    return snack["tier"]

def get_tier_display(snack_label: str) -> dict:
    tier = get_tier(snack_label)
    return TIER_DISPLAY[tier]