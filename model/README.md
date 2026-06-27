# model/ folder

Place your exported Teachable Machine files here:

| File | Where to get it |
|------|----------------|
| `keras_model.h5` | Export → Keras → Download |
| `labels.txt` | Included in the Keras export zip |

## How to export from Teachable Machine

1. Go to https://teachablemachine.withgoogle.com
2. Open your trained Image Project
3. Click **Export Model**
4. Select the **Tensorflow** tab
5. Choose **Keras** format
6. Click **Download my model**
7. Unzip the downloaded file
8. Copy `keras_model.h5` and `labels.txt` into this folder

## Important

- `labels.txt` must list your classes in the same order as your Teachable Machine training
- The class names in `labels.txt` must match the keys in `src/snack_data.py`
- Both files are in `.gitignore` — share them with your group via a shared drive or USB
