# Étape 1 : Image de base
FROM python:3.11-slim

# Étape 2 : Créer le dossier app
WORKDIR /app

# Install system dependencies, Firefox, and required libraries
RUN apt-get update && \
    apt-get install -y wget gnupg2 curl build-essential firefox-esr && \
    rm -rf /var/lib/apt/lists/*

# Install geckodriver (Firefox driver for Selenium)
ENV GECKODRIVER_VERSION=0.34.0
RUN wget --no-verbose -O /tmp/geckodriver.tar.gz "https://github.com/mozilla/geckodriver/releases/download/v$GECKODRIVER_VERSION/geckodriver-v$GECKODRIVER_VERSION-linux64.tar.gz" && \
    tar -C /usr/local/bin -xzf /tmp/geckodriver.tar.gz && \
    rm /tmp/geckodriver.tar.gz

# Étape 3 : Copier requirements.txt AVANT tout le reste
COPY api/requirements.txt .

# Étape 4 : Installer les dépendances
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Étape 5 : Copier le reste du code
COPY api/ ./api/

# Étape 6 : Exposer le port
EXPOSE 10000

# Étape 7 : Démarrer l'app
CMD ["uvicorn", "api.api_main:app", "--host", "0.0.0.0", "--port", "10000"]
