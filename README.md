<p align="center">
  <img src="webapp/static/logo.png" width="200" />
</p>

<h1 align="center">SheetMusicOrganizer</h1>

[![Docker Image Version](https://img.shields.io/github/v/tag/sajiko5821/sheetmusicorganizer?label=version&logo=docker&color=2496ED)](https://github.com/sajiko5821/sheetmusicorganizer/pkgs/container/sheetmusicorganizer)
[![Build Status](https://img.shields.io/github/actions/workflow/status/sajiko5821/sheetmusicorganizer/docker.yml?branch=main&label=build&logo=github)](https://github.com/sajiko5821/sheetmusicorganizer/actions)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Automates the organization, renaming, and metadata injection of PDF sheet music.

The project has a **web frontend first** workflow and keeps the original
CLI pipeline as a legacy/power-user path.

## Project Structure

```
.
|-- webapp/
|   |-- app.py
|   |-- templates/
|   `-- static/
|-- dist/
|   |-- create_metadata.py
|   |-- rename_files.py
|   |-- write_metadata.py
|   |-- create_metadata        # onefile executable
|   |-- rename_files           # onefile executable
|   `-- write_metadata         # onefile executable
`-- build/                     # pyinstaller build artifacts
```

## Web Frontend (Recommended)

The web frontend is the primary user experience.

- Upload PDFs in the browser
- Assign/auto-detect instrument parts
- Generate renamed files + `metadata.json`
- Write PDF metadata via `pikepdf`
- Download the processed ZIP

### Run Locally

```bash
cd webapp
python app.py
```

Default development URL: `http://127.0.0.1:5001`

### Run with Docker

```bash
docker build -t sheetmusicorganizer webapp/
docker run -p 5000:5000 sheetmusicorganizer
```

## CLI Pipeline (Still Supported)

The original 3-step pipeline is still available and useful for batch workflows.

Use either:

- Python scripts in `dist/*.py` (source path)
- Onefile executables in `dist/` (sometimes called "onejar/onefile" builds)

Always run dry-run first.

### 1. Create `metadata.json`

```bash
python dist/create_metadata.py <root_directory_path> --dry-run
```

Overwrite existing metadata files when needed:

```bash
python dist/create_metadata.py <root_directory_path> --force
```

### 2. Rename PDFs

```bash
python dist/rename_files.py <root_directory_path> --dry-run
```

### 3. Write PDF metadata

```bash
python dist/write_metadata.py <root_directory_path> --dry-run
```

### Use Onefile Executables Instead of Python

```bash
./dist/create_metadata <root_directory_path> --dry-run
./dist/rename_files <root_directory_path> --dry-run
./dist/write_metadata <root_directory_path> --dry-run
```

## Build / Release CLI Onefile Executables

If you change the legacy scripts, rebuild the onefile executables from the
`dist/*.py` sources.

```bash
pip install pyinstaller
pyinstaller --onefile dist/create_metadata.py
pyinstaller --onefile dist/rename_files.py
pyinstaller --onefile dist/write_metadata.py
```

PyInstaller outputs metadata and temporary build data in `build/`.

## Attributions

<a href="https://www.flaticon.com/de/kostenlose-icons/musik-und-multimedia" title="musik und multimedia Icons">Musik und multimedia Icons erstellt von HideMaru - Flaticon</a>
