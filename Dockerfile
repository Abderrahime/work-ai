# Étape 1 : Image de base
FROM python:3.11-slim

# Étape 2 : Créer le dossier app
WORKDIR /app

# Étape 3 : Copier requirements.txt AVANT tout le reste
COPY requirements.txt .

# Étape 4 : Installer les dépendances
RUN pip install --no-cache-dir -r requirements.txt

# Étape 5 : Copier le reste du code
COPY . .

# Étape 6 : Exposer le port
EXPOSE 10000

# Étape 7 : Démarrer l'app
CMD ["uvicorn", "api.api_main:app", "--host", "0.0.0.0", "--port", "10000"]
