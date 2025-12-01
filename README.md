# SheetMusicOrganizer

This repository contains a set of Python scripts designed to automate the organization, standardization, and metadata injection for a collection of PDF sheet music files, particularly optimized for Big Band arrangements with instrument parts (Stimmen) housed in individual folders.

The primary goal is to ensure consistency in file naming and to embed essential metadata (Title, Author, Subject, Keywords) directly into the PDF documents using a structured workflow.

## 🚀 Features

The repository provides three distinct scripts to handle the end-to-end processing of your sheet music collection:

1. ```create_metadata```:

- Recursively searches a root directory for folders containing .pdf files.
- Creates a metadata.json file in each of those folders.
- Sets the initial Title field in the JSON to the name of the folder.

2. ```rename_files```:

- Renames PDF files to a standardized format: `{cleaned_directory_name}_{short_instrument_code}.pdf`.
- Uses a configurable `DEFAULT_TARGET_MAP` to convert long instrument names (e.g., "trombone-1") found in the original filename to short codes (e.g., "trb_1").

3. ```write_metadata```:

- Reads the generated `metadata.json` file.
- Uses the short instrument code from the standardized filename (e.g., "trb_1") to augment the PDF's Title (e.g., "Take the A Train - TRB_1").
- Injects the Title, Author, Subject, and Keywords into the PDF's internal metadata fields using the pikepdf library.

## 📋 Prerequisites

To run these scripts, you need to download the latest Executables. There is no need to install additional libraries.

## 🛠️ Usage Workflow

The intended workflow involves running the three scripts sequentially. Always use the --dry-run (-n) flag first to preview changes before applying them.

### Step 1: Generate Metadata Files

This script creates the `metadata.json` file in every directory that contains PDF files, setting the initial Title based on the folder name.

```
./create_metadata <root_directory_path>

# Example (Dry Run)
./create_metadata /path/to/my/Scores --dry-run
```

### Step 2: Standardize File Names

This script renames the PDF files within each directory. This step is crucial as the renaming ensures a consistent format (`<piece_name>_<instrument_code>.pdf`), which is later used by the metadata injector.

Example Before Renaming: `/path/to/Scores/My Big Band Tune/My Big Band Tune - Trombone-1.pdf`

Example After Renaming: `/path/to/Scores/My Big Band Tune/my_big_band_tune_trb_1.pdf`

```
./rename_files <root_directory_path>

# Example (Execute Rename)
./rename_files /path/to/my/Scores --dry-run
```

### Step 3: Inject Metadata into PDFs

This script opens each PDF, reads its corresponding ```metadata.json```, and embeds the document information (Title, Author, Subject, Keywords) into the PDF's internal structure.

```
./write_metadata <root_directory_path>

# Example (Execute Metadata Injection)
write_metadata /path/to/my/Scores --dry-run
```

## 💻 Development

If there are new changes you need to create a new release. For this use:
```
pip install pyinstaller
```

Afterward create the Executable for each of the main scripts. The `--onefile` flag is highly recommended to bundle everything into a single, clean executable.

```
pyinstaller --onefile create_metadata.py
pyinstaller --onefile rename_files.py
pyinstaller --onefile write_metadata.py
```