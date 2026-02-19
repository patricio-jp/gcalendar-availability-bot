# Base image
FROM python:3.11-slim

# Install dependencies for Chrome and Selenium
RUN apt-get update && apt-get install -y \
  wget \
  gnupg \
  unzip \
  # Download the key, dearmor it, and place it in keyrings
  && wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | gpg --dearmor -o /usr/share/keyrings/google-chrome-keyring.gpg \
  # Add the repository referencing the keyring
  && echo "deb [arch=amd64 signed-by=/usr/share/keyrings/google-chrome-keyring.gpg] http://dl.google.com/linux/chrome/deb/ stable main" > /etc/apt/sources.list.d/google-chrome.list \
  && apt-get update \
  && apt-get install -y google-chrome-stable \
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
# CMD to run the bot
CMD ["python", "main.py"]
