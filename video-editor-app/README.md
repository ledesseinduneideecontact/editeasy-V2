# AI Video Editor - Montage Automatique Intelligent

Application web complète pour créer automatiquement des montages vidéo professionnels à partir de photos et vidéos, avec analyse IA locale et synchronisation musicale.

## Fonctionnalités

- **Upload intuitif** : Drag & drop pour ajouter photos et vidéos
- **Réorganisation facile** : Glissez-déposez pour réordonner vos fichiers
- **Analyse IA locale** :
  - Détection de qualité (flou, exposition, composition)
  - Détection de scènes dans les vidéos
  - Analyse de contenu (visages, objets, couleurs)
  - Analyse musicale (tempo, beats, énergie)
- **Montage intelligent** :
  - Durée adaptative selon la qualité
  - Coupures intelligentes aux changements de scène
  - Synchronisation sur les beats de la musique
  - Transitions fluides (fondu, cut, dissolve)
  - Stabilisation vidéo
  - Harmonisation des couleurs
- **Export haute qualité** : 720p, 1080p, ou 4K

## Architecture

```
video-editor-app/
├── frontend/          # Interface web (HTML/CSS/JS)
├── backend/           # Serveur Node.js/Express
├── ai-processor/      # Microservice Python d'analyse IA
├── uploads/           # Fichiers uploadés
├── outputs/           # Vidéos générées
└── temp/              # Fichiers temporaires
```

## Prérequis

### Pour installation locale

- **Node.js** 18+ et npm
- **Python** 3.10+
- **FFmpeg** 4.4+
- Au moins 4GB de RAM
- Espace disque : 2GB minimum

### Pour installation Docker

- **Docker** 20+
- **Docker Compose** 2+

## Installation

### Option 1 : Installation locale

#### 1. Cloner le projet

```bash
git clone <repository-url>
cd video-editor-app
```

#### 2. Installer FFmpeg

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
Télécharger depuis [ffmpeg.org](https://ffmpeg.org/download.html)

#### 3. Installer le backend

```bash
cd backend
npm install
```

#### 4. Installer l'AI processor

```bash
cd ../ai-processor
python -m venv venv
source venv/bin/activate  # Sur Windows: venv\Scripts\activate
pip install -r requirements.txt
```

#### 5. Configuration

```bash
cd ..
cp .env.example .env
```

Modifier `.env` selon vos besoins.

#### 6. Lancer l'application

**Terminal 1 - Backend :**
```bash
cd backend
npm start
```

**Terminal 2 - AI Processor :**
```bash
cd ai-processor
source venv/bin/activate
python app.py
```

**Accéder à l'application :**
Ouvrir http://localhost:3000 dans votre navigateur

### Option 2 : Installation Docker

#### 1. Cloner et lancer

```bash
git clone <repository-url>
cd video-editor-app
docker-compose up --build
```

#### 2. Accéder à l'application

Ouvrir http://localhost:3000 dans votre navigateur

Les conteneurs se lancent automatiquement avec :
- Backend sur le port 3000
- AI Processor sur le port 5000

## Utilisation

### 1. Upload des fichiers

1. Glissez-déposez vos photos et vidéos dans la zone d'upload
2. Ou cliquez pour sélectionner depuis votre ordinateur
3. Optionnel : Ajoutez une musique de fond

### 2. Réorganiser

- Glissez-déposez les fichiers pour les réordonner
- Supprimez les fichiers indésirables avec le bouton ×

### 3. Configurer

Ajustez les paramètres selon vos préférences :
- **Durée cible** : Automatique (basé sur musique) ou fixe
- **Style de transitions** : Automatique, doux, dynamique, ou mixte
- **Qualité** : 720p, 1080p, ou 4K
- **Synchronisation musicale** : Élevée, moyenne, ou faible
- **Options avancées** : Stabilisation, harmonisation des couleurs

### 4. Générer

1. Cliquez sur "Générer la vidéo automatiquement"
2. Patientez pendant le traitement (peut prendre quelques minutes)
3. Prévisualisez et téléchargez votre vidéo

## Comment ça marche

### 1. Analyse IA

L'AI processor analyse chaque fichier :
- **Qualité** : Détection du flou (Laplacian), exposition, contraste, résolution
- **Scènes** : Comparaison d'histogrammes pour détecter les changements
- **Contenu** : Détection de visages (Haar Cascades), analyse de composition
- **Musique** : Extraction du tempo et beats avec Librosa

### 2. Plan de montage

Le backend génère un plan intelligent :
- Calcule la durée optimale pour chaque clip selon sa qualité
- Place les transitions aux moments stratégiques
- Synchronise avec les beats de la musique
- Applique les filtres (stabilisation, color grading)

### 3. Rendu FFmpeg

FFmpeg assemble la vidéo finale :
- Redimensionne et uniformise tous les clips
- Applique les transitions et effets
- Mixe l'audio avec la musique
- Encode en haute qualité (H.264)

## API

### Endpoints

#### POST /api/upload

Upload des fichiers et démarrage du traitement.

**Body (multipart/form-data) :**
- `files[]` : Fichiers photos/vidéos
- `music` : Fichier audio (optionnel)
- `settings` : JSON avec les paramètres

**Response :**
```json
{
  "jobId": "uuid",
  "message": "Upload réussi"
}
```

#### GET /api/status/:jobId

Récupérer le statut du traitement.

**Response :**
```json
{
  "status": "processing|completed|failed",
  "progress": 75,
  "message": "Montage vidéo en cours...",
  "steps": [...],
  "videoUrl": "/outputs/video-xxx.mp4"
}
```

## Déploiement sur VPS Hostinger

### 1. Préparer le VPS

```bash
# Connexion SSH
ssh root@your-vps-ip

# Installer les dépendances
apt update && apt upgrade -y
apt install -y nodejs npm python3 python3-pip ffmpeg git docker.io docker-compose

# Activer Docker
systemctl start docker
systemctl enable docker
```

### 2. Déployer l'application

```bash
# Cloner le projet
cd /var/www
git clone <repository-url> video-editor
cd video-editor

# Lancer avec Docker
docker-compose up -d

# Vérifier les logs
docker-compose logs -f
```

### 3. Configurer Nginx (optionnel)

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

### 4. SSL avec Let's Encrypt

```bash
apt install certbot python3-certbot-nginx
certbot --nginx -d your-domain.com
```

## Performances

### Temps de traitement estimé

- 10 photos + musique : ~30 secondes
- 5 vidéos (30s chacune) + musique : ~2-3 minutes
- 20 photos + 5 vidéos + musique : ~4-5 minutes

### Optimisations

- Utilisez des fichiers de résolution raisonnable (1080p max pour les sources)
- Limitez le nombre total de fichiers (50 max recommandé)
- Pour de grandes vidéos, pré-découpez-les en clips courts

## Dépannage

### Erreur "FFmpeg not found"

```bash
# Vérifier l'installation
ffmpeg -version

# Installer si nécessaire
apt install ffmpeg  # Ubuntu/Debian
brew install ffmpeg  # macOS
```

### Erreur "AI service not available"

L'application fonctionne en mode dégradé si le service IA n'est pas disponible.

```bash
# Vérifier les logs
cd ai-processor
python app.py
```

### Erreur d'upload

Augmentez les limites dans `.env` :
```
MAX_FILE_SIZE=1048576000  # 1GB
MAX_FILES=200
```

### Vidéo de mauvaise qualité

- Augmentez la qualité : `videoQuality: "1080p"` ou `"4k"`
- Réduisez la compression FFmpeg : `-crf 18` (dans server.js)

## Technologies utilisées

- **Frontend** : HTML5, CSS3, JavaScript, Sortable.js
- **Backend** : Node.js, Express, Multer
- **IA** : Python, Flask, OpenCV, Librosa
- **Traitement vidéo** : FFmpeg
- **Containerisation** : Docker, Docker Compose

## Contribuer

Les contributions sont les bienvenues ! N'hésitez pas à :
- Signaler des bugs
- Proposer de nouvelles fonctionnalités
- Améliorer la documentation
- Soumettre des pull requests

## Licence

MIT License - Libre d'utilisation et de modification

## Support

Pour toute question ou problème :
- Ouvrir une issue sur GitHub
- Consulter la documentation FFmpeg : https://ffmpeg.org/documentation.html
- Documentation OpenCV : https://docs.opencv.org/

## Roadmap

- [ ] Support de plus de formats vidéo
- [ ] Transitions personnalisées avancées
- [ ] Détection d'objets avec YOLO
- [ ] Sous-titres automatiques
- [ ] Templates de montage prédéfinis
- [ ] Export en multiple résolutions simultanément
- [ ] Prévisualisation en temps réel
- [ ] Interface d'édition manuelle

---

Créé avec ❤️ en utilisant des technologies open-source
