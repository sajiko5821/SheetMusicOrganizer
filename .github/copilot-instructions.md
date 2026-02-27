# Copilot Instructions — SheetMusicOrganizer

## Überblick
Dieses Repo organisiert PDF-Noten in einer **3‑Schritt CLI-Pipeline** (rekursiv via `os.walk()`):
1) `create_metadata.py` legt pro PDF-Ordner eine `metadata.json` an.
2) `rename_files.py` benennt PDFs nach `{cleaned_directory_name}_{instrument_code}.pdf` um.
3) `write_metadata.py` schreibt PDF-DocInfo (`/Title`, `/Author`, `/Subject`, `/Keywords`) via `pikepdf`.

## Workflow (immer erst Dry-Run)
Alle Skripte unterstützen `-n/--dry-run` (keine Dateisystem-/PDF-Änderungen):
- `python create_metadata.py <root> -n`
- `python rename_files.py <root> -n`
- `python write_metadata.py <root> -n`

In `dist/` liegen bereits gebaute Executables (`dist/create_metadata`, `dist/rename_files`, `dist/write_metadata`).

## Repo-spezifische Konventionen
- `metadata.json` (aus `create_metadata.py`):
  - `Title` = **Original-Ordnername** (nicht „cleaned“), `Author`/`Subject` leer
  - `Keywords` startet als Liste mit `"Skyline-BigBand"` (UTF‑8, `ensure_ascii=False` beibehalten)
- Umbenennung (aus `rename_files.py`):
  - Ordnername wird lowercase und Leerzeichen/Hyphens → `_` (`get_directory_name()`)
  - Matching ist Substring-basiert auf `filename.lower()`; Keys in `DEFAULT_TARGET_MAP` sollten lowercase sein
- Instrument-Codes sind aktuell doppelt gepflegt:
  - `rename_files.py`: `DEFAULT_TARGET_MAP` (z.B. `"trombone-1" -> "trb_1"`)
  - `write_metadata.py`: `target_strings = ["trb_1", "trb_2", "trb_3", "trb_4", "trb_set"]`
  - Bei neuen Stimmen beide Stellen konsistent halten
- Metadaten-Schreiben (aus `write_metadata.py`):
  - Titel: `"{Title} - {stimme}"` (stimme aus Dateiname), `stimme` wird auch zu Keywords hinzugefügt
  - PDF wird mit `allow_overwriting_input=True` geöffnet; Fehlerpfade fangen `OSError`, `pikepdf.PdfError`, `KeyError`

## Abhängigkeiten/Release
- Nur `write_metadata.py` braucht bei Source-Ausführung `pikepdf`.
- Releases/Executables: `pyinstaller --onefile create_metadata.py` (analog für die anderen Skripte; siehe README).

## Web-App (`webapp/`)
- Flask-App (`app.py`) mit Gunicorn als WSGI-Server (Port 5000).
- Abhängigkeiten: `webapp/requirements.txt` (`flask`, `pikepdf`, `gunicorn`).
- Lokal starten: `python webapp/app.py` (Development-Server, nicht für Produktion).

## Docker
- `webapp/Dockerfile`: Multi-Stage-Build auf Basis `python:3.12-slim`, läuft als nicht-privilegierter User.
- `webapp/.dockerignore`: schließt `__pycache__`, `.venv` etc. aus.
- Lokal bauen & testen:
  ```bash
  docker build -t sheetmusicorganizer webapp/
  docker run -p 5000:5000 sheetmusicorganizer
  ```

## CI/CD – GitHub Actions
- Workflow: `.github/workflows/docker.yml`
- Trigger: Push auf `main`/`master` oder Git-Tag `v*`
- Pusht ins GHCR (`ghcr.io/<owner>/sheetmusicorganizer`) via `GITHUB_TOKEN` – **kein manueller PAT nötig**.
- Tag-Logik:
  - Jeder Trigger → `:<commit-sha>`
  - Push auf `main`/`master` → zusätzlich `:latest`
  - Git-Tag (z. B. `v1.0.0`) → zusätzlich `:<tag>`
- Voraussetzung: GitHub → Settings → Actions → General → **Read and write permissions** aktiviert.
