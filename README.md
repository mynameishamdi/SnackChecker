<div align="center">

# 🥜 Malaysian Quick-Bites Classifier

**An AI-powered desktop app that classifies Malaysian snacks and delivers an instant, interactive health dashboard.**

[![Python](https://img.shields.io/badge/Python-3.11-blue?logo=python&logoColor=white)](https://python.org)
[![TensorFlow](https://img.shields.io/badge/TensorFlow-2.15-orange?logo=tensorflow&logoColor=white)](https://tensorflow.org)
[![CustomTkinter](https://img.shields.io/badge/UI-CustomTkinter-green)](https://github.com/TomSchimansky/CustomTkinter)
[![Gemini](https://img.shields.io/badge/AI-Gemini%203.5%20Flash-purple?logo=google)](https://ai.google.dev)
[![SDG 3](https://img.shields.io/badge/SDG-3%20Good%20Health-4CAF50)](https://sdgs.un.org/goals/goal3)
[![Platform](https://img.shields.io/badge/Platform-Windows-0078D6?logo=windows)](https://github.com)

*BITI 1113 Artificial Intelligence — Universiti Teknikal Malaysia Melaka (UTeM) — Sem 2, 2025/2026*

</div>

---

## 📌 What Is This?
SnackChecker is a desktop computer vision application designed to bridge the gap between highly processed everyday snacks and consumer health awareness. Built for a university Artificial Intelligence course (BITI 1113), this app scans Malaysian snacks in real-time, calculates nutritional danger levels, and uses Generative AI to suggest healthier local swaps.

Point your webcam at any Malaysian snack — or upload a photo — and the app instantly tells you:

- Whether it's **Junk**, **Moderately Healthy**, or **Healthy**
- How much **sodium, sugar, and fat** it contains (as % of daily value)
- The equivalent in **glasses of Teh Tarik** (sugar index)
- How long you need to exercise to **burn it off**
- An AI-generated **health summary, fun fact, and cultural context**
- **Healthier swap suggestions** you can cycle through
- A **side-by-side comparison** of any two snack categories

All powered by a Teachable Machine model + Google Gemini 3.5 Flash, wrapped in a fully bilingual (English / Bahasa Melayu) CustomTkinter desktop app.

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| 📷 **Webcam + Upload** | Scan live or upload a photo |
| 🧠 **AI Classification** | 6 Malaysian snack categories via Teachable Machine |
| ⚠️ **Danger Meters** | Sodium, Sugar, Sat. Fat progress bars with colour coding |
| 🧋 **Teh Tarik Index** | Sugar equivalent in glasses of teh tarik |
| 🏃 **Burn It Off Calculator** | 5 sports — Jogging, Futsal, Badminton, Cycling, Mall Walking |
| 💡 **AI Health Dashboard** | Summary, Fun Fact, Cara Makan — all via Gemini 3.5 Flash |
| 🔄 **Smart Swaps Cycler** | Cycle through healthier alternatives |
| ⚖️ **Head-to-Head Comparison** | Compare any two snack categories side by side |
| 🤖 **AI Verdict** | Ask Gemini which of two snacks is the better choice |
| 📜 **Session History** | Timestamped log of all scans this session |
| 🌐 **Bilingual** | Full English / Bahasa Melayu toggle |
| 🔁 **Model Hot-Swap** | Load your own Teachable Machine model via Settings |
| 💾 **Smart Caching** | Gemini only called once per snack — works offline after first scan |

---

## 🍟 Snack Categories

The default model classifies snacks into 6 broad Malaysian categories:

| Label | Category | Tier |
|-------|----------|------|
| `instant_noodles` | Instant Noodles (Mi Sedaap, Maggi, etc.) | 🔴 Junk |
| `chips` | Savoury Chips & Snacks (Twisties, Mister Potato, etc.) | 🔴 Junk |
| `chocolate` | Chocolate & Sweet Snacks (Choki Choki, Kit Kat, etc.) | 🔴 Junk |
| `biscuits` | Processed Biscuits (Ritz, Julie's, Oreo, etc.) | 🟡 Moderate |
| `instant_drink` | 3-in-1 Instant Drinks (Milo, Nestum, Nescafé, etc.) | 🟡 Moderate |
| `background` | No snack detected | — |

> 💡 You can swap in your own Teachable Machine model via **Settings → Model Swapper** to classify different items.

---

## 🚀 Quick Start

### Option A — I just want to run the app (No Python needed)

1. Go to the [**Releases**](../../releases/latest) page
2. Download `SnackChecker.exe`
3. Double-click to run — no installation needed
4. *(Optional)* Get a free Gemini API key to enable AI content — see [Getting an API Key](#-getting-a-gemini-api-key)

### Option B — I'm a developer (Run from source)

```bash
# 1. Clone the repo
git clone https://github.com/mynameishamdi/SnackChecker.git
cd SnackChecker

# 2. Create and activate a virtual environment
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # Mac/Linux

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run the app
python app.py
```

---

## 🔑 Getting a Gemini API Key

The app works without an API key — it falls back to built-in content. But for AI-generated summaries, fun facts, and smart swaps, you need a free Gemini key:

1. Go to **https://aistudio.google.com/apikey**
2. Sign in with a Google account
3. Click **Create API key** → select or create a project
4. Copy the key (starts with `AIza...`)
5. Paste it into the popup box the first time you run the application!

> **Free tier limits:** 1,500 requests/day and 1 million tokens/day — more than enough for this app.
> After each snack is scanned once, the result is cached locally and the API is never called again for that snack.

---

## 🗂️ Project Structure

```
SnackChecker/
│
├── app.py                    # Entry point — run this
├── requirements.txt          # Python dependencies
│
├── model/
│   ├── keras_model.h5        # Trained Teachable Machine model
│   └── labels.txt            # Class labels (must match model output order)
│
├── src/
│   ├── classifier.py         # Loads model, runs predictions, hot-swap support
│   ├── preprocessor.py       # Resizes + normalises images for model input
│   ├── snack_data.py         # Static nutrition DB + Teh Tarik/burn math
│   ├── gemini_client.py      # Gemini API + caching layer
│   ├── cache_manager.py      # Persists AI responses to cache/snack_cache.json
│   ├── translations.py       # English / Bahasa Melayu string dictionary
│   └── ui/
│       ├── main_window.py    # Root window, history sidebar, settings, compare
│       ├── input_panel.py    # Webcam feed + image upload + capture button
│       └── result_panel.py   # Full health dashboard (meters, cards, swaps)
│
├── assets/
│   └── logos/                # Optional: halal.png, buatan_malaysia.png, etc.
│                             # App falls back to text badges if images missing
└── cache/
    └── snack_cache.json      # Auto-generated — AI responses saved here
```

---

## 🛠️ Tech Stack

| Layer | Tool | Purpose |
|-------|------|---------|
| ML Training | Google Teachable Machine | Train and export image classifier |
| ML Runtime | TensorFlow 2.15 + Keras | Load `.h5` model, run predictions |
| AI Content | Google Gemini 3.5 Flash | Generate summaries, fun facts, swaps |
| UI Framework | CustomTkinter | Modern desktop interface |
| Image Processing | OpenCV + Pillow | Webcam capture, preprocessing |
| Language | Python 3.11 | Core application |
| Packaging | PyInstaller | Build standalone `.exe` |

---

## 🧑‍💻 Training Your Own Model

Want to classify different snacks or add new categories?

1. Go to **https://teachablemachine.withgoogle.com** → **Image Project**
2. Create classes with the **exact same labels** as listed in `src/snack_data.py`
3. Record or upload 100–150 images per class
4. Train and test the model
5. Export → **Tensorflow** tab → **Keras** → Download
6. Unzip the download and place `keras_model.h5` and `labels.txt` in `model/`
7. Restart the app — or use **Settings → Model Swapper** to load without restarting

> If you add new categories, also update `SNACK_DATABASE` in `src/snack_data.py` with nutrition data.

---

## 🌍 SDG Connection

This project directly supports **SDG 3 — Good Health and Well-being**, specifically target 3.4 which aims to reduce premature mortality from non-communicable diseases.

Malaysia has one of the **highest obesity rates in Southeast Asia** — over 50% of adults are overweight or obese (NHMS 2019, Ministry of Health Malaysia). Poor snacking habits are a major contributor. This app makes nutrition information instant, accessible, and culturally relevant for everyday Malaysians.

---

## 📦 Building the Standalone .exe

```bash
pyinstaller \
  --onefile \
  --windowed \
  --name "SnackChecker" \
  --add-data "model/keras_model.h5;model/" \
  --add-data "model/labels.txt;model/" \
  --add-data "assets/;assets/" \
  app.py
```

The `.exe` will be in `dist/SnackChecker.exe`. Upload it as a GitHub Release asset.

---

## 📚 References

- Institute for Public Health (IPH). (2019). *National Health and Morbidity Survey (NHMS) 2019*. Ministry of Health Malaysia.
- Howard, A. G., et al. (2017). *MobileNets: Efficient convolutional neural networks for mobile vision applications.* arXiv:1704.04861.
- World Health Organization. (2024). *Obesity and overweight.* https://www.who.int/news-room/fact-sheets/detail/obesity-and-overweight
- Google. (2024). *Teachable Machine.* https://teachablemachine.withgoogle.com
- Streamlit Inc. (2024). *CustomTkinter documentation.* https://customtkinter.tomschimansky.com

---

<div align="center">

*BITI 1113 Artificial Intelligence | Faculty of Information & Communication Technology | UTeM | Sem 2 2025/2026*

</div>

   This entire application was initially built in only 4 days