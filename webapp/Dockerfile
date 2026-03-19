# ---- Build stage ----
FROM python:3.12-slim AS builder

WORKDIR /build
COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# ---- Runtime stage ----
FROM python:3.12-slim

# Nicht-privilegierter User
RUN useradd --create-home appuser
WORKDIR /app

# Installierte Pakete aus Build-Stage übernehmen
COPY --from=builder /install /usr/local

# App-Code kopieren
COPY app.py .
COPY templates/ templates/
COPY static/ static/

USER appuser

EXPOSE 5000

# Gunicorn als Produktions-WSGI-Server
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "2", "--timeout", "120", "app:app"]
