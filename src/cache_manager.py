# ── src/cache_manager.py ───────────────────────────────────────────────────
# Saves AI-generated snack content to a local JSON file so the app only
# calls the Gemini API once per snack — after that, results load instantly
# from cache even without internet.
# ---------------------------------------------------------------------------

import os
import json

CACHE_DIR  = "cache"
CACHE_FILE = os.path.join(CACHE_DIR, "snack_cache.json")


class CacheManager:
    """
    Simple key-value cache backed by a local JSON file.
    Keys are snack labels (e.g. 'twisties').
    Values are dicts with keys: summary, fun_fact, healthier_swap.
    """

    def __init__(self):
        os.makedirs(CACHE_DIR, exist_ok=True)
        self._data = self._load()

    # ── Internal ─────────────────────────────────────────────────────────────

    def _load(self) -> dict:
        if os.path.exists(CACHE_FILE):
            try:
                with open(CACHE_FILE, "r", encoding="utf-8") as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                return {}
        return {}

    def _save(self):
        with open(CACHE_FILE, "w", encoding="utf-8") as f:
            json.dump(self._data, f, indent=2, ensure_ascii=False)

    # ── Public API ────────────────────────────────────────────────────────────

    def get(self, snack_label: str) -> dict | None:
        """Return cached content for snack_label, or None if not cached."""
        return self._data.get(snack_label)

    def set(self, snack_label: str, content: dict):
        """Save content for snack_label and persist to disk."""
        self._data[snack_label] = content
        self._save()

    def has(self, snack_label: str) -> bool:
        return snack_label in self._data

    def clear(self):
        """Clear all cached content (useful for testing)."""
        self._data = {}
        if os.path.exists(CACHE_FILE):
            os.remove(CACHE_FILE)

    def cached_snacks(self) -> list[str]:
        """Return list of snack labels that are already cached."""
        return list(self._data.keys())
