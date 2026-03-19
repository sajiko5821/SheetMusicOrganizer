import io
import os
import re
import json
import zipfile
import tempfile
import argparse
from flask import Flask, request, jsonify, render_template, send_file

# pikepdf wird optional importiert, damit der Server auch ohne es startet
try:
    import pikepdf
    PIKEPDF_AVAILABLE = True
except ImportError:
    PIKEPDF_AVAILABLE = False

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 100 * 1024 * 1024  # 100 MB upload limit per request
ALLOWED_UPLOAD_EXTENSIONS = {".pdf"}


@app.errorhandler(413)
def request_entity_too_large(_error):
    return jsonify({"error": "Upload zu groß (max. 100 MB pro Anfrage)."}), 413

# --------------------------------------------------------------------------
# Bekannte Instrument-Codes (für Frontend-Dropdown + Auto-Erkennung)
# --------------------------------------------------------------------------
INSTRUMENT_CODES = [
    "trb_1", "trb_2", "trb_3", "trb_4", "trb_set",
    "trp_1", "trp_2", "trp_3", "trp_4",
    "alto_sax_1", "alto_sax_2",
    "tenor_sax_1", "tenor_sax_2",
    "bari_sax",
    "guitar", "bass", "piano", "drums",
    "score",
]

# Mapping Dateiname-Substring → Instrument-Code (für Auto-Erkennung)
AUTO_DETECT_MAP = {
    "trombone-1": "trb_1", "trombone_1": "trb_1", "trb_1": "trb_1",
    "trombone-2": "trb_2", "trombone_2": "trb_2", "trb_2": "trb_2",
    "trombone-3": "trb_3", "trombone_3": "trb_3", "trb_3": "trb_3",
    "trombone-4": "trb_4", "trombone_4": "trb_4", "trb_4": "trb_4",
    "trombone-set": "trb_set", "trombone_set": "trb_set", "trb_set": "trb_set",
    "trumpet-1": "trp_1", "trumpet_1": "trp_1", "trp_1": "trp_1",
    "trumpet-2": "trp_2", "trumpet_2": "trp_2", "trp_2": "trp_2",
    "trumpet-3": "trp_3", "trumpet_3": "trp_3", "trp_3": "trp_3",
    "trumpet-4": "trp_4", "trumpet_4": "trp_4", "trp_4": "trp_4",
    "alto-sax-1": "alto_sax_1", "alto_sax_1": "alto_sax_1",
    "alto-sax-2": "alto_sax_2", "alto_sax_2": "alto_sax_2",
    "tenor-sax-1": "tenor_sax_1", "tenor_sax_1": "tenor_sax_1",
    "tenor-sax-2": "tenor_sax_2", "tenor_sax_2": "tenor_sax_2",
    "bari-sax": "bari_sax", "bari_sax": "bari_sax",
    "guitar": "guitar", "bass": "bass",
    "piano": "piano", "drums": "drums",
    "score": "score",
}


def clean_name(name: str) -> str:
    """Wandelt Pretty Name in dateisystem-sicheren Namen um (wie in rename_files.py)."""
    name = name.lower()
    name = re.sub(r"[\s\-]+", "_", name)
    return name


# --------------------------------------------------------------------------
# Routen
# --------------------------------------------------------------------------

@app.route("/")
def index():
    return render_template(
        "index.html",
        instrument_codes=INSTRUMENT_CODES,
        auto_detect_map=json.dumps(AUTO_DETECT_MAP),
        pikepdf_available=PIKEPDF_AVAILABLE,
    )


@app.route("/api/process", methods=["POST"])
def api_process():
    pretty_name     = request.form.get("pretty_name", "").strip()
    author          = request.form.get("author", "").strip()
    extra_keywords  = [k.strip() for k in request.form.getlist("extra_keywords[]") if k.strip()]
    codes           = request.form.getlist("codes[]")
    files       = request.files.getlist("pdfs[]")

    # --- Validierung ---
    if not pretty_name:
        return jsonify({"error": "Kein Stückname angegeben."}), 400
    if not files or all(f.filename == "" for f in files):
        return jsonify({"error": "Keine PDF-Dateien hochgeladen."}), 400
    if len(files) != len(codes):
        return jsonify({"error": "Anzahl Dateien und Codes stimmt nicht überein."}), 400
    for i, uploaded_file in enumerate(files):
        filename = uploaded_file.filename or ""
        extension = os.path.splitext(filename)[1].lower()
        if extension not in ALLOWED_UPLOAD_EXTENSIONS:
            return jsonify({"error": f"Ungültige Datei {i+1}: nur PDF erlaubt."}), 400

        # Zusätzlich: Content-Type und Magic-Header prüfen, damit keine Nicht-PDFs durchrutschen
        mimetype = (uploaded_file.mimetype or "").lower()
        if mimetype not in ("application/pdf", "application/x-pdf"):
            return jsonify({"error": f"Ungültige Datei {i+1}: nur PDF-Uploads erlaubt (Content-Type)."}), 400

        # Ersten Bytes des Streams prüfen: ein gültiges PDF beginnt mit '%PDF-'
        try:
            # Position merken, wenige Bytes lesen, danach zurückspulen
            pos = uploaded_file.stream.tell()
            header = uploaded_file.stream.read(5)
            uploaded_file.stream.seek(pos)
        except Exception:
            return jsonify({"error": f"Ungültige Datei {i+1}: Datei konnte nicht gelesen werden."}), 400

        if header != b"%PDF-":
            return jsonify({"error": f"Ungültige Datei {i+1}: Datei ist kein gültiges PDF."}), 400

    for i, code in enumerate(codes):
        normalized_code = code.strip()
        if not normalized_code:
            return jsonify({"error": f"Kein Instrument-Code für Datei {i+1} angegeben."}), 400
        if normalized_code not in INSTRUMENT_CODES:
            return jsonify({"error": f"Ungültiger Instrument-Code für Datei {i+1}: {normalized_code}"}), 400

    cleaned_name = clean_name(pretty_name)
    logs = []

    with tempfile.TemporaryDirectory() as tmpdir:
        piece_dir = os.path.join(tmpdir, pretty_name)
        os.makedirs(piece_dir)

        # --- PDFs speichern & umbenennen ---
        saved_files = []   # (abs_path, code)
        for file, code in zip(files, codes):
            code = code.strip()
            new_filename = f"{cleaned_name}_{code}.pdf"
            dest = os.path.join(piece_dir, new_filename)
            file.save(dest)
            saved_files.append((dest, code))
            logs.append(f"✓  Gespeichert: {new_filename}")

        # --- metadata.json ---
        base_keywords = extra_keywords if extra_keywords else ["Skyline-BigBand"]
        metadata = {
            "Title": pretty_name,
            "Author": author,
            "Subject": "",
            "Keywords": base_keywords,
        }
        with open(os.path.join(piece_dir, "metadata.json"), "w", encoding="utf-8") as f:
            json.dump(metadata, f, indent=4, ensure_ascii=False)
        logs.append("✓  metadata.json erstellt")

        # --- PDF-Metadaten ---
        if PIKEPDF_AVAILABLE:
            for pdf_path, stimme in saved_files:
                try:
                    with pikepdf.Pdf.open(pdf_path, allow_overwriting_input=True) as pdf:
                        pdf.docinfo["/Title"]    = pikepdf.String(f"{pretty_name} - {stimme}")
                        kw_list = base_keywords + [stimme]
                        pdf.docinfo["/Author"]   = pikepdf.String(author)
                        pdf.docinfo["/Subject"]  = pikepdf.String("")
                        pdf.docinfo["/Keywords"] = pikepdf.String(", ".join(kw_list))
                        pdf.save(pdf_path)
                    logs.append(f"✓  PDF-Metadaten: {os.path.basename(pdf_path)}")
                except (OSError, pikepdf.PdfError, KeyError) as e:
                    logs.append(f"⚠  Metadaten-Fehler ({os.path.basename(pdf_path)}): {e}")
        else:
            logs.append("⚠  pikepdf nicht verfügbar – PDF-Metadaten nicht gesetzt")

        # --- ZIP im RAM bauen ---
        EXCLUDE = {"metadata.json"}
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zf:
            for root, _, filenames in os.walk(piece_dir):
                for fname in filenames:
                    if fname in EXCLUDE:
                        continue
                    abs_path = os.path.join(root, fname)
                    arc_name = os.path.relpath(abs_path, tmpdir)
                    zf.write(abs_path, arc_name)

        zip_buffer.seek(0)
        return send_file(
            zip_buffer,
            mimetype="application/zip",
            as_attachment=True,
            download_name=f"{cleaned_name}.zip",
        )


# --------------------------------------------------------------------------
# Start
# --------------------------------------------------------------------------
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="SheetMusicOrganizer Web-GUI")
    parser.add_argument("--port", type=int, default=5001, help="Port (Standard: 5001)")
    parser.add_argument("--host", default="127.0.0.1", help="Host (Standard: 127.0.0.1)")
    args = parser.parse_args()
    print(f"SheetMusicOrganizer läuft auf http://{args.host}:{args.port}")
    app.run(host=args.host, port=args.port, debug=False)
