# Multimedia DBMS — Multimedia Database (Kleart Adri)

A lightweight Multimedia Database Management System built with Flask for ingesting, storing, extracting features from, and searching multimedia (images, audio, video). This repository contains the web app, dataset helpers and scripts used to download sample data (Pexels, CIFAR, ESC-50), upload to the DBMS, and run similarity search using extracted features.

## Features

- Flask-based REST API for uploading media, serving thumbnails, and search endpoints
- Automatic thumbnail generation and deep feature extraction (image / video / audio)
- Scripts to download datasets (Pexels images/videos, CIFAR, ESC-50) and upload them to the DBMS
- Resume-capable upload tools and dataset management helpers

## Repo layout

- `run.py` — application entry point (starts Flask app)
- `requirements.txt` — Python dependencies
- `setup_dataset.py` & `download_video_dataset.py` — helper scripts for downloading/uploading sample datasets
- `app/` — Flask package containing all server code
  - `app/__init__.py` — application factory and blueprint registration
  - `app/config.py` — configuration via environment variables (see `.env.example`)
  - `app/models.py` — database models
  - `app/routes/` — API and frontend route handlers
  - `app/extractors/` — media feature extraction logic
  - `app/static/` & `app/templates/` — frontend assets and HTML template
- `scripts/` — miscellaneous utilities for processing media and datasets
- `database/schema.sql` — initial database schema
- `uploads/` — place where media files are stored (ignored by Git)

## Requirements

- Python 3.10+ recommended
- System packages (recommended): `ffmpeg` (optional, used by `download_video_dataset.py` to create variations)
- Install Python dependencies:

```bash
python -m venv .venv
# Windows PowerShell
.\.venv\Scripts\Activate.ps1
# or cmd
.\.venv\Scripts\activate
pip install -r requirements.txt
```

## Configuration / Environment

Create a `.env` (or copy `.env.example`) and set at least the database URL and optional keys:

- `DATABASE_URL` — database connection (Postgres recommended)
- `REDIS_URL` — (optional) redis url if used
- `UPLOAD_FOLDER` — where files should be stored (default `uploads`)
- `SECRET_KEY` — Flask secret key

Example `.env` (minimal):

```
FLASK_ENV=development
DATABASE_URL=postgresql://user:pass@localhost:5432/multimedia_db
UPLOAD_FOLDER=uploads
SECRET_KEY=replace-me
```

## Quickstart (development)

1. Create & activate virtual environment and install deps (see Requirements).
2. Prepare environment variables (.env / system env).
3. Initialize database (Flask app will create tables automatically on startup).
4. Run the app:

```bash
# From project root
python run.py
```

The app will start on port `5000` by default. The API base is `http://localhost:5000/api`.

## Uploading media (API)

The app registers several blueprints under `/api` (see `app/__init__.py`):

- `POST /api/upload` — file upload endpoint used by dataset scripts. Accepts `file` plus `title`, `description`, `tags`.
- `GET /api/search` — search endpoint (similarity/metadata search) implemented by `app/routes/search.py`.
- `GET /api/media/<id>` — media serving endpoints in `app/routes/media.py`.

Use the scripts to upload datasets (they call the upload API with appropriate metadata):

- `python setup_dataset.py` — interactive tool to download (Pexels images/videos) and upload datasets (CIFAR, ESC-50, Pexels). Runs in the project folder and supports resume via `dataset_progress.json`.
- `python download_video_dataset.py` — dedicated Pexels video downloader with optional ffmpeg variations. Use `upload_to_dbms()` in that script to push downloaded videos to the API.

Example: run the unified dataset manager and choose options:

```bash
python setup_dataset.py
# Follow the interactive menu: 1=Download, 2=Upload, 3=Both
```

## Scripts and utilities

- `scripts/process_pending_media.py` — process and extract features for newly uploaded media.
- `scripts/verify_deep_features.py` — check presence/validity of extracted features.
- `scripts/reencode_videos.py` — helper to reencode videos to desired codec/bitrate.
- `scripts/fix_thumbnails.py` — fix or regenerate thumbnails for media items.

Check each script docstrings/comments for usage examples.

## Development notes

- The app uses SQLAlchemy with Flask-Migrate. Database models are in `app/models.py`.
- Feature extraction code lives in `app/extractors/` and can be toggled via `EXTRACT_DEEP_FEATURES` environment setting.
- The project includes CPU-friendly deep learning packages (`torch`, `torchvision`) in `requirements.txt`; GPU setup is not covered here.

## Testing and running in production

- For production, configure `FLASK_ENV=production`, set a proper `DATABASE_URL`, and run behind a WSGI server (e.g. `gunicorn`). Example:

```bash
# example (from a production server shell)
gunicorn --bind 0.0.0.0:5000 "run:app"
```

## Notes & troubleshooting

- If dataset upload scripts report `Cannot connect to server`, ensure the Flask app is running and reachable at `http://localhost:5000`.
- Large video uploads use long timeouts; check `MAX_CONTENT_LENGTH` and `UPLOAD_FOLDER` in `app/config.py`.
- `ffmpeg` is optional but recommended for `download_video_dataset.py` variations. Install ffmpeg and ensure it is on your PATH.

## Where to look in the code

- App factory: [app/**init**.py](app/__init__.py)
- Config: [app/config.py](app/config.py)
- Dataset manager: [setup_dataset.py](setup_dataset.py)
- Video dataset tool: [download_video_dataset.py](download_video_dataset.py)
- Main entry: [run.py](run.py)

## Next steps (suggested)

- Set up a local Postgres DB and update `DATABASE_URL` in `.env`.
- Run the Flask app and try uploading a small image via the UI or `POST /api/upload`.
- Run `python setup_dataset.py` to download/upload sample data.




