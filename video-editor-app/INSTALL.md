# Guide d'installation détaillé

## Installation rapide (Linux/macOS)

```bash
# 1. Installer les prérequis système
# Ubuntu/Debian
sudo apt update && sudo apt install -y nodejs npm python3 python3-pip ffmpeg git

# macOS
brew install node python ffmpeg git

# 2. Cloner et démarrer
git clone <repository-url>
cd video-editor-app
chmod +x start.sh
./start.sh
```

## Installation rapide (Windows)

1. Installer Node.js depuis https://nodejs.org/
2. Installer Python depuis https://python.org/
3. Installer FFmpeg depuis https://ffmpeg.org/download.html
4. Cloner le projet
5. Double-cliquer sur `start.bat`

## Installation Docker (toutes plateformes)

```bash
# Installer Docker Desktop depuis https://docker.com/

# Lancer l'application
docker-compose up --build

# Accéder à http://localhost:3000
```

## Installation manuelle détaillée

### 1. Prérequis

#### Node.js et npm

**Vérifier l'installation :**
```bash
node --version  # Doit être >= 18.0.0
npm --version
```

**Installer si nécessaire :**
- Ubuntu/Debian : `sudo apt install nodejs npm`
- macOS : `brew install node`
- Windows : Télécharger depuis https://nodejs.org/

#### Python 3.10+

**Vérifier l'installation :**
```bash
python3 --version  # Doit être >= 3.10
pip3 --version
```

**Installer si nécessaire :**
- Ubuntu/Debian : `sudo apt install python3 python3-pip python3-venv`
- macOS : `brew install python`
- Windows : Télécharger depuis https://python.org/

#### FFmpeg

**Vérifier l'installation :**
```bash
ffmpeg -version
```

**Installer si nécessaire :**

**Ubuntu/Debian :**
```bash
sudo apt update
sudo apt install ffmpeg
```

**macOS :**
```bash
brew install ffmpeg
```

**Windows :**
1. Télécharger depuis https://ffmpeg.org/download.html
2. Extraire dans `C:\ffmpeg`
3. Ajouter `C:\ffmpeg\bin` au PATH système

### 2. Configuration du backend

```bash
cd backend

# Installer les dépendances
npm install

# Vérifier l'installation
npm list
```

**Dépendances installées :**
- express : Serveur web
- cors : Gestion CORS
- multer : Upload de fichiers
- uuid : Génération d'identifiants uniques
- axios : Requêtes HTTP vers le service IA

### 3. Configuration de l'AI processor

```bash
cd ai-processor

# Créer un environnement virtuel
python3 -m venv venv

# Activer l'environnement
# Linux/macOS :
source venv/bin/activate
# Windows :
venv\Scripts\activate

# Installer les dépendances
pip install -r requirements.txt

# Vérifier l'installation
pip list
```

**Dépendances installées :**
- Flask : Framework web Python
- opencv-python : Traitement d'images/vidéos
- numpy : Calculs numériques
- librosa : Analyse audio
- scipy : Fonctions scientifiques
- scikit-learn : Machine learning
- Pillow : Manipulation d'images

### 4. Configuration de l'environnement

```bash
# Retour au dossier racine
cd ..

# Copier le fichier de configuration
cp .env.example .env

# Éditer avec vos paramètres
nano .env  # ou votre éditeur préféré
```

**Variables importantes :**
```env
PORT=3000                                    # Port du serveur backend
AI_SERVICE_URL=http://localhost:5000        # URL du service IA
MAX_FILE_SIZE=524288000                     # 500MB max par fichier
MAX_FILES=100                               # 100 fichiers max
```

### 5. Créer les dossiers nécessaires

```bash
mkdir -p uploads outputs temp
```

### 6. Lancer l'application

**Option A : Avec les scripts de démarrage**

Linux/macOS :
```bash
./start.sh
```

Windows :
```bash
start.bat
```

**Option B : Manuellement (2 terminaux)**

**Terminal 1 - AI Processor :**
```bash
cd ai-processor
source venv/bin/activate  # Windows: venv\Scripts\activate
python app.py
```

Vous devriez voir :
```
🤖 AI Processor starting on port 5000...
 * Running on http://0.0.0.0:5000
```

**Terminal 2 - Backend :**
```bash
cd backend
node server.js
```

Vous devriez voir :
```
🚀 Server running on http://localhost:3000
📁 Upload directory: /path/to/uploads
📹 Output directory: /path/to/outputs
```

### 7. Accéder à l'application

Ouvrir votre navigateur sur : **http://localhost:3000**

## Vérification de l'installation

### Test de FFmpeg

```bash
# Créer une vidéo de test
ffmpeg -f lavfi -i testsrc=duration=10:size=1280x720:rate=30 -pix_fmt yuv420p test.mp4

# Si ça fonctionne, FFmpeg est bien installé
```

### Test du backend

```bash
curl http://localhost:3000/api/status/test
# Devrait retourner une erreur 404 (normal, le job n'existe pas)
```

### Test de l'AI processor

```bash
curl http://localhost:5000/health
# Devrait retourner : {"status":"healthy"}
```

## Dépannage

### "Port 3000 already in use"

```bash
# Trouver et tuer le processus
# Linux/macOS :
lsof -ti:3000 | xargs kill -9

# Windows :
netstat -ano | findstr :3000
taskkill /PID <PID> /F
```

### "Module not found" (Node.js)

```bash
cd backend
rm -rf node_modules package-lock.json
npm install
```

### "No module named 'cv2'" (Python)

```bash
cd ai-processor
source venv/bin/activate
pip install opencv-python
```

### Erreurs de permissions (Linux)

```bash
# Donner les bonnes permissions
chmod -R 755 uploads outputs temp
sudo chown -R $USER:$USER uploads outputs temp
```

### FFmpeg introuvable sur Windows

1. Vérifier que FFmpeg est dans le PATH :
   ```cmd
   echo %PATH%
   ```
2. Ajouter manuellement :
   - Panneau de configuration → Système → Paramètres système avancés
   - Variables d'environnement → PATH → Modifier
   - Ajouter : `C:\ffmpeg\bin`

## Installation en production (VPS)

### Prérequis serveur

- Ubuntu 20.04+ ou Debian 11+
- 4GB RAM minimum
- 20GB espace disque
- Accès root ou sudo

### Installation complète

```bash
# 1. Connexion SSH
ssh root@your-vps-ip

# 2. Mise à jour du système
apt update && apt upgrade -y

# 3. Installation des dépendances
apt install -y nodejs npm python3 python3-pip python3-venv ffmpeg git nginx certbot python3-certbot-nginx

# 4. Cloner le projet
cd /var/www
git clone <repository-url> video-editor
cd video-editor

# 5. Configuration
cp .env.example .env
nano .env  # Ajuster les paramètres

# 6. Installation Docker (optionnel mais recommandé)
apt install -y docker.io docker-compose
systemctl start docker
systemctl enable docker

# 7. Lancer avec Docker
docker-compose up -d

# 8. Configurer Nginx
nano /etc/nginx/sites-available/video-editor
```

**Configuration Nginx :**
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
        client_max_body_size 500M;
    }
}
```

```bash
# Activer le site
ln -s /etc/nginx/sites-available/video-editor /etc/nginx/sites-enabled/
nginx -t
systemctl reload nginx

# 9. SSL avec Let's Encrypt
certbot --nginx -d your-domain.com

# 10. Auto-démarrage
# Créer un service systemd
nano /etc/systemd/system/video-editor.service
```

**Service systemd :**
```ini
[Unit]
Description=AI Video Editor
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/var/www/video-editor
ExecStart=/usr/bin/docker-compose up
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
# Activer le service
systemctl enable video-editor
systemctl start video-editor
```

## Mise à jour

```bash
# Arrêter l'application
# Ctrl+C ou :
docker-compose down

# Mettre à jour le code
git pull

# Réinstaller les dépendances si nécessaire
cd backend && npm install && cd ..
cd ai-processor && source venv/bin/activate && pip install -r requirements.txt && cd ..

# Redémarrer
docker-compose up -d
# ou
./start.sh
```

## Désinstallation

```bash
# Arrêter les services
docker-compose down

# Supprimer les conteneurs et images
docker-compose down --rmi all --volumes

# Supprimer le projet
cd ..
rm -rf video-editor-app

# Désinstaller les dépendances (optionnel)
# apt remove nodejs python3 ffmpeg  # Linux
# brew uninstall node python ffmpeg  # macOS
```

## Support

En cas de problème :
1. Vérifier les logs : `docker-compose logs -f`
2. Consulter la documentation FFmpeg
3. Ouvrir une issue sur GitHub
