# Starten mit einem geeigneten Basis-Image für Python
FROM python:3.10-slim

# Installieren von hidapi-Abhängigkeiten und anderen Systempaketen
RUN apt-get update && apt-get install -y \
    libhidapi-hidraw0 \
    libusb-1.0-0 \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Setzen des Arbeitsverzeichnisses im Container
WORKDIR /app

# Kopieren ALLER Add-on-Dateien in das Arbeitsverzeichnis
COPY . .

# Installieren der Python-Abhängigkeiten
RUN pip install --no-cache-dir -r requirements.txt

# Kopieren der udev-Regeln in das Systemverzeichnis des Containers
COPY raspi-udev.rules /etc/udev/rules.d/99-raspi-hidraw.rules

# Sicherstellen, dass das run.sh Skript im Arbeitsverzeichnis ausführbar ist
RUN chmod +x run.sh

# Befehl, der beim Start des Containers ausgeführt wird
CMD ["./run.sh"]
