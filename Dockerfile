# Basis-Image
FROM python:3.11-slim

# Arbeitsverzeichnis
WORKDIR /app

# Abhängigkeiten kopieren und installieren
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Skript kopieren
COPY unifi2mqtt.py .

# Standard-Entrypoint
ENTRYPOINT ["python", "unifi2mqtt.py"]