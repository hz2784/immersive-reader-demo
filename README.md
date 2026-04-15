# Immersive Reader — Full-Stack Feature Demo

An end-to-end prototype of word-synchronised audio reading, built on a
PHP/Laravel/MySQL backend and an Alpine + Tailwind frontend.

**[▶ Live demo (frontend only)](https://hz2784.github.io/immersive-reader-demo/)** — hosted on GitHub Pages.
Falls back to a bundled JSON snapshot since the Laravel API can't run on
GitHub Pages. To see the full stack (API + MySQL), clone and run locally
(instructions below).

- Click any word → audio seeks to that position
- As audio plays, the current word is highlighted in real time
- Human-voice narration (not browser TTS)
- Dyslexia-friendly typography panel + bionic-reading toggle + speed control

---

## Architecture

```
┌── Preprocessing (offline, one-off per chapter) ────────────┐
│  narrator.mp3  ──►  Whisper small.en  ──►  timings.json    │
│                     (local, free, MIT)                     │
└────────────────────────────┬───────────────────────────────┘
                             │ POST /api/chapters/{id}/timings
                             ▼
┌── Backend (Laravel + MySQL) ───────────────────────────────┐
│  Route ► Controller ► Eloquent ► chapters.timings_json     │
└────────────────────────────┬───────────────────────────────┘
                             │ GET /api/chapters/{id}/timings
                             ▼
┌── Frontend (Alpine + Tailwind) ────────────────────────────┐
│  Fetch → render <span> per word → sync on audio events     │
└────────────────────────────────────────────────────────────┘
```

**Key design choice:** Whisper runs only at upload time. The runtime path
(what end users hit) is pure PHP + MySQL — no Python needed on production
servers.

---

## Stack

| Layer          | Tool         | Role                                  |
|----------------|--------------|---------------------------------------|
| Language       | PHP 8.2+     | Backend                               |
| Framework      | Laravel 11   | Routing, ORM, validation              |
| Database       | MySQL 9      | Stores word timings as JSON column    |
| Package mgr    | Composer     | PHP dependencies                      |
| Frontend       | Alpine JS    | Reactive UI component                 |
| Styling        | Tailwind CSS | Pre-built via CLI (no browser JIT)    |
| Preprocessing  | OpenAI Whisper `small.en` | Word-level transcription |

---

## Repo layout

```
immersive-reader-demo/
├── index.html                 ← Frontend single-page demo
├── style.css                  ← Pre-built Tailwind
├── input.css                  ← Tailwind source
├── serve.py                   ← Tiny static server for local dev
├── audio/
│   ├── ALWAYS_HERE_FOR_YOU_HALAHMY_CH00{1,2}.mp3
│   ├── word_timings.json      ← Word-level timestamps (Whisper output)
│   └── word_timings.js        ← Same data, as a <script> fallback
├── alignment/
│   ├── convert_and_upload.py  ← Format + POST to Laravel API
│   ├── chapter_2.txt          ← Reference text used for aeneas run
│   └── chapter_2_aeneas.json  ← aeneas output (alternative aligner)
└── reader-api/                ← Laravel backend
    ├── app/Http/Controllers/ChapterController.php
    ├── app/Models/Chapter.php
    ├── database/migrations/*_create_chapters_table.php
    ├── database/seeders/ChapterSeeder.php
    └── routes/api.php
```

---

## Running locally

### Prerequisites
- PHP ≥ 8.2 and Composer
- MySQL running locally (or switch to SQLite by editing `.env`)
- Python 3.9+ (only if you want to re-run alignment)

### 1. Backend
```bash
cd reader-api
cp .env.example .env
composer install
php artisan key:generate

# make sure MySQL has an empty `reader_api` database
mysql -u root -e "CREATE DATABASE reader_api"

php artisan migrate --seed
php artisan serve --port=8001
```

### 2. Frontend
In a second terminal, from the repo root:
```bash
python3 serve.py
```
Open <http://localhost:8000>. The page fetches timings from
`http://localhost:8001/api/chapters/2/timings`, falling back to the
bundled `word_timings.json` if the API is unreachable.

---

## API

### `GET /api/chapters/{id}/timings`
```json
{
  "chapter_id": 2,
  "title": "Chapter 2",
  "audio_url": "/ALWAYS_HERE_FOR_YOU_HALAHMY_CH002.mp3",
  "timings": {
    "duration": 816.68,
    "paragraphs": [
      {
        "id": "p0",
        "text": "Chapter 2. Madison and the Bessies ...",
        "words": [
          {"text": "Chapter", "start": 0.68, "end": 1.28},
          {"text": "2.",      "start": 1.28, "end": 1.84}
        ]
      }
    ]
  }
}
```

### `POST /api/chapters/{id}/timings`
Uploads word timings. Body: the same `timings` shape as above.
Returns `{chapter_id, paragraph_count, updated_at}`.

The POST route is open in this demo for convenience. In production it
should be behind admin auth and rate-limited.

---

## Preprocessing pipeline

To generate `word_timings.json` for a new chapter:

```bash
# 1. Transcribe with word-level timestamps (free, runs locally)
whisper chapter_3.mp3 --model small.en \
                      --word_timestamps True \
                      --output_format json

# 2. Convert Whisper output to the API schema and POST it
python alignment/convert_and_upload.py
```

Notes:
- Whisper's `small.en` model (~500 MB) is MIT-licensed; weights download
  once to `~/.cache/whisper/`.
- Runtime on an Apple Silicon Mac is roughly 1× realtime (10-min audio
  takes ~10 min).
- An `aeneas`-based alternative is also included under `alignment/` for
  cases where you already have authoritative text and want to force-align
  to it.

---

## Frontend features (Alpine component)

| Feature                   | Notes                                               |
|---------------------------|-----------------------------------------------------|
| Word-sync highlight       | Updates on `audio.timeupdate` (~4 Hz)               |
| Click-to-seek             | `<span data-start>` click sets `audio.currentTime`  |
| Bionic reading            | Bolds first half of each word                       |
| Playback speed            | Presets 0.8×–2.5× + fine stepper                    |
| Typography panel          | Font, size, spacing, line-height (persists locally) |
| Narration mode            | Human voice (fallback: browser TTS)                 |

---

## Roadmap

- [ ] Auto-advance to next chapter on audio end
- [ ] Per-user reading-speed memory (server-side)
- [ ] Queue-based Whisper worker for scale
- [ ] Admin UI for uploading chapters
