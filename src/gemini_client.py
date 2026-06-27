# ── src/gemini_client.py ───────────────────────────────────────────────────
# Strictly a creative text generator — no math, no static facts.
# Uses gemini-3.5-flash with response_mime_type: application/json.
# Returns: { summary, fun_fact, cara_makan, healthier_swaps: [{name, note}, ...] }
# ---------------------------------------------------------------------------

import json
import time
from google import genai
from google.genai import types

from src.cache_manager import CacheManager
from src.snack_data    import get_display_name, get_tier

# ── Fallback Content ───────────────────────────────────────────────────────
FALLBACK_CONTENT = {
    "junk": {
        "summary": "This snack falls right into the junk category. It packs a heavy dose of sodium, processed fats, and chemical additives that can easily spike your blood pressure and cause energy crashes if eaten regularly.",
        "fun_fact": "Ultra-processed snacks make up over 25% of daily calorie intake for many Malaysian urban adults.",
        "cara_makan": "A classic late-night Mamak craving, often served with a sunny-side-up egg (telur mata) at 2 AM.",
        "healthier_swaps": [
            {"name": "Roasted Kacang Putih", "note": "A highly accessible local switch that gives you a great crunch with clean, plant-based protein."},
            {"name": "Signature Market Mixed Nuts", "note": "An excellent clean alternative if you want to completely avoid refined palm oils and heavy factory processing."},
        ],
    },
    "moderate": {
        "summary": "This one isn't terrible, but it's not ideal for daily snacking either. It provides some quick fuel but carries a bit too much refined flour and added sugar, meaning you will likely feel hungry again quite soon.",
        "fun_fact": "Many 'moderate' snacks are just one small ingredient change away from being genuinely healthy.",
        "cara_makan": "Best enjoyed by dipping (cicah) into a hot cup of local Kopi O or Milo.",
        "healthier_swaps": [
            {"name": "Organic Wholemeal Crackers", "note": "Swapping to a less refined grain keeps your blood sugar stable and keeps you full for twice as long."},
            {"name": "Local Kurma (Dates)", "note": "If you are chasing a sweet craving, a couple of dates provide natural energy alongside clean dietary fiber."},
        ],
    },
    "healthy": {
        "summary": "This is a solid, highly nutritious choice. It relies on clean ingredients without relying on synthetic flavors, delivering sustained metabolic energy to your body.",
        "fun_fact": "Choosing natural snacks like this regularly is one of the simplest changes you can make for long-term health.",
        "cara_makan": "Often eaten during Ramadhan to break fast, or as a quick energy booster before morning prayers.",
        "healthier_swaps": [],
    },
}

class GeminiClient:
    """Wraps the google-genai SDK, handles caching, and enforces JSON schemas."""
    
    MODEL_NAME = "gemini-3.5-flash"

    def __init__(self, api_key: str):
        self._cache   = CacheManager()
        self._enabled = bool(api_key and api_key != "YOUR_GEMINI_API_KEY_HERE")

        if self._enabled:
            self._client = genai.Client(api_key=api_key)
            print(f"[Gemini] Client initialised — model: {self.MODEL_NAME}")
        else:
            self._client = None
            print("[Gemini] No API key — fallback content will be used.")

    # ── Public Methods ────────────────────────────────────────────────────────

    def get_snack_content(self, snack_label: str, lang: str = "English") -> dict:
        """
        Returns { summary, fun_fact, cara_makan, healthier_swaps: [{name, note}] }
        Cache → API → Fallback, in that order.
        """
        cache_key = f"{snack_label}_{lang}"

        # 1. Return from cache if already generated in this language
        if self._cache.has(cache_key):
            print(f"[Gemini] Cache hit: {cache_key}")
            return self._cache.get(cache_key)

        # 2. Call API if key is set
        if self._enabled:
            content = self._call_api(snack_label, lang)
            if content:
                self._cache.set(cache_key, content)
                return content

        # 3. Fall back to static content
        print(f"[Gemini] Using fallback for: {snack_label}")
        tier = get_tier(snack_label)
        return FALLBACK_CONTENT.get(tier, FALLBACK_CONTENT["moderate"])

    def get_comparison_verdict(self, snack_a: str, snack_b: str, lang: str = "English") -> str:
        """Returns a 2-sentence AI verdict comparing two snacks head-to-head."""
        cache_key = f"compare_{snack_a}_{snack_b}_{lang}"
        
        if self._cache.has(cache_key): 
            return self._cache.get(cache_key)

        if not self._enabled:
            return "AI API is disabled. Review the Danger Meters above to see which snack has lower sodium and sugar to make an informed choice!"

        display_a = get_display_name(snack_a)
        display_b = get_display_name(snack_b)
        
        prompt = f"""You are a strict Malaysian nutrition expert. The user is deciding between eating '{display_a}' and '{display_b}'.
        Write a 2-sentence verdict strictly in {lang} declaring which is the better choice and EXACTLY why based on their typical nutritional profiles (sugar, fat, sodium). Do not use markdown."""
        
        max_retries = 3
        delay = 2
        
        for attempt in range(max_retries):
            try:
                print(f"\n[Gemini] Requesting VS Verdict: {snack_a} vs {snack_b} (Attempt {attempt + 1}/{max_retries})")
                response = self._client.models.generate_content(
                    model=self.MODEL_NAME, 
                    contents=prompt
                )
                verdict = response.text.strip()
                self._cache.set(cache_key, verdict)
                return verdict
            except Exception as e:
                if "503" in str(e).upper() and attempt < max_retries - 1:
                    print(f"[Gemini] Server busy (503). Retrying in {delay}s...")
                    time.sleep(delay)
                    delay *= 2
                else:
                    print(f"[Gemini] Compare API Error: {e}")
                    return "Error reaching AI. Please check your internet connection."

    # ── Internal Methods ─────────────────────────────────────────────────────

    def _build_prompt(self, snack_label: str, lang: str) -> str:
        display_name = get_display_name(snack_label)
        tier         = get_tier(snack_label)

        return f"""You are an honest, direct Malaysian nutrition expert speaking to a consumer. Speak like a real human — professional, clear, and informative.

CRITICAL RULE: You MUST write your entire response strictly in {lang}. Do not use English unless the requested language is English.

Snack name: {display_name}
Health tier: {tier}

Generate the content based on these exact constraints:
1. summary: 3 sentences in {lang}. Explain plainly why {display_name} is a {tier} choice. You MUST explicitly include at least THREE realistic nutritional facts or estimated percentages (such as total calories, sodium daily percentage, or sugar/saturated fat daily allowances).
2. fun_fact: 1 highly specific, interesting fact in {lang} about {display_name}'s history, manufacturing process, or business footprint in Malaysia.
3. cara_makan: 1-2 sentences in {lang} describing the classic, culturally unique way Malaysians consume this specific item.
4. healthier_swaps: If the tier is "healthy", return an empty array []. If the tier is "junk" or "moderate", provide an array containing exactly TWO separate alternative objects:
   - Element 1: A healthier alternative from the EXACT SAME BRAND if available in Malaysia.
   - Element 2: A much cleaner drop-in alternative from a DIFFERENT competitor brand.

Respond with ONLY a valid, raw JSON object. Do not include markdown formatting.
{{
  "summary": "...",
  "fun_fact": "...",
  "cara_makan": "...",
  "healthier_swaps": [
    {{"name": "Item 1", "note": "Why it wins..."}},
    {{"name": "Item 2", "note": "Why it wins..."}}
  ]
}}"""

    def _call_api(self, snack_label: str, lang: str) -> dict | None:
        """Call Gemini API, strip markdown, parse JSON, and strictly validate keys with a retry loop."""
        max_retries = 3
        delay = 2
        
        for attempt in range(max_retries):
            try:
                print(f"\n[DEBUG] Sending request to Gemini for: {snack_label} in {lang} (Attempt {attempt + 1}/{max_retries})...")
                response = self._client.models.generate_content(
                    model=self.MODEL_NAME,
                    contents=self._build_prompt(snack_label, lang),
                    config=types.GenerateContentConfig(
                        response_mime_type="application/json"
                    ),
                )
                raw_text = response.text.strip()

                # Strip markdown wrappers just in case the AI ignores the JSON schema rule
                if raw_text.startswith("```"):
                    raw_text = raw_text.split("```")[1]
                    if raw_text.startswith("json"):
                        raw_text = raw_text[4:]
                    raw_text = raw_text.strip()

                content = json.loads(raw_text)

                # Strict Safety Check: Validate required keys
                required_keys = ("summary", "fun_fact", "cara_makan", "healthier_swaps")
                if not all(k in content for k in required_keys):
                    raise ValueError(f"Missing keys in response: {list(content.keys())}")

                # Strict Safety Check: Ensure healthier_swaps is always a list to prevent UI crashes
                if not isinstance(content["healthier_swaps"], list):
                    content["healthier_swaps"] = []

                print(f"[Gemini] Successfully generated {lang} content for: {snack_label}")
                return content

            except json.JSONDecodeError as e:
                print(f"[Gemini] JSON parse error for {snack_label}: {e}")
                break  # Don't retry on a hard parse error, fall back immediately
                
            except Exception as e:
                if "503" in str(e).upper() and attempt < max_retries - 1:
                    print(f"[Gemini] Server busy (503). Retrying in {delay}s...")
                    time.sleep(delay)
                    delay *= 2
                else:
                    print(f"[Gemini] API error for {snack_label}: {e}")
                    break # Break out and fall back

        return None