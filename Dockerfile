# Base image
FROM python:3.11-slim

# Install Tini (lightweight init) to properly reap zombie processes spawned by Chrome,
# Chromium and its matching ChromeDriver from Debian repos (always version-compatible),
# plus the minimal system deps needed to run a headless browser.
RUN apt-get update && apt-get install -y --no-install-recommends \
  tini \
  chromium \
  chromium-driver \
  && apt-get clean \
  && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements and install python deps
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Environment variables should be passed via --env-file or -e

# Tini is the entrypoint: it acts as PID 1 and reaps zombie processes so that
# Chrome subprocesses (renderer, GPU, etc.) are properly cleaned up after each cycle.
ENTRYPOINT ["/usr/bin/tini", "--"]
CMD ["python", "main.py"]
