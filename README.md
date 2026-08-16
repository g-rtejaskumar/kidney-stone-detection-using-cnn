# NephroScan — Kidney Stone Detection with CNN

An academic deep-learning project that detects kidney stones in medical imaging.
Upload a kidney ultrasound/CT scan and a convolutional neural network (TensorFlow/Keras)
returns a verdict with a confidence score — no login required.

Live demo deployed on Render: `https://kidney-stone-detection-l1n2.onrender.com`

## Features

- **Prediction console** — upload a scan (drag & drop or browse), see it analyzed in a
  scan viewport, and read the result with a confidence bar.
- **Simulated training console** — real training takes hours (5 epochs on ~10,000
  images), so the demo replays a completed run: a progress bar with epoch-by-epoch log
  completes in ~8 seconds and returns the final metrics without training anything.
- **Model performance report** — accuracy/loss curves per epoch, classification report
  (precision, recall, F1), and the full training configuration.
- **No authentication** — the site is fully public; user/admin login and registration
  were removed.

## Screenshots

| Home | Prediction console |
| :---: | :---: |
| ![Home](screenshots/home.png) | ![Prediction](screenshots/prediction.png) |

| Training console | Model performance |
| :---: | :---: |
| ![Training](screenshots/training.png) | ![Performance](screenshots/performance.png) |

## Stack

- Django 6 + SQLite (`dj-database-url` for Postgres on Render)
- CNN — 6 Conv2D blocks + BatchNorm + Dropout, input 224×224×3, trained for 5 epochs
  on 10,000 kidney images (20% validation split)
- Inference runs the model as **TF-Lite** (`kidney_stone_model.tflite`, 45 MB) through
  the lightweight **LiteRT** runtime (`ai-edge-litert`, ~18 MB) instead of full
  TensorFlow — peak memory ~130 MB, so it fits Render's free 512 MB tier
- Bootstrap 5 + Chart.js, dark "radiology suite" UI
- Gunicorn + WhiteNoise for production

Recreate the .tflite from the .h5 at any time with `python tools/convert_model.py`
(local TensorFlow only — it is not a deployment dependency).

## Run locally

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate   |   macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

Open http://127.0.0.1:8000

## Deploy to Render

The repo ships with a **Render blueprint** (`render.yaml`), so deployment is a
one-click import:

1. Push this repository to GitHub.
2. Go to [render.com](https://render.com) → **New** → **Blueprint**.
3. Select this repository and click **Apply**.
4. Render creates the web service with the build command (`./build.sh`), start
   command (`gunicorn KSD.wsgi:application`), Python 3.12 runtime, and env vars
   (`DEBUG=false`, generated `SECRET_KEY`) already configured.

Deployment takes a few minutes — the dependency install is small because
TensorFlow is not installed on the server.

Alternatively, create a **Web Service** manually and set:

| Setting | Value |
| --- | --- |
| Runtime | Python 3 (reads `runtime.txt` → 3.12.10) |
| Build command | `./build.sh` |
| Start command | `gunicorn KSD.wsgi:application --timeout 120 --workers 1` |
| Plan | Free (512 MB RAM is enough — prediction peaks ~130 MB) |
| Env vars | `DEBUG=false`, `SECRET_KEY` (generate) |

`ALLOWED_HOSTS` and `CSRF_TRUSTED_ORIGINS` accept any `*.onrender.com` subdomain, so
no changes are needed after Render assigns the URL.

## Project structure

```
KSD/        Django project (settings, urls)
Users/      App: prediction, simulated training, model performance views
templates/  base.html + home / prediction / training / model_performance
static/     Static assets
kidney_stone_model.h5   Trained CNN (134 MB)
```

## Academic notes

This is a demonstration project for a portfolio. The prediction endpoint runs a real
pre-trained model; the training page is intentionally simulated to keep the demo
interactive. In a full research setup you would train on a GPU for several hours and
report the validation metrics shown on the Performance page.
