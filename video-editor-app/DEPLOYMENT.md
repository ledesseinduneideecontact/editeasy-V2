# Guide de Déploiement

Ce guide explique comment déployer l'application AI Video Editor sur un VPS Ubuntu tout en maintenant une compatibilité Windows pour le développement local.

## Architecture

L'application est conçue pour :
- **Développement local** : Windows, macOS, ou Linux avec installation native
- **Production** : VPS Ubuntu avec Docker pour isolation et performances optimales

## Développement Local (Windows)

### Prérequis Windows

1. **Node.js 18+** : https://nodejs.org/
2. **Python 3.10+** : https://python.org/
3. **FFmpeg** : https://ffmpeg.org/download.html
   - Télécharger FFmpeg
   - Extraire dans `C:\ffmpeg`
   - Ajouter `C:\ffmpeg\bin` au PATH système

### Installation sur Windows

```cmd
# Cloner le projet
git clone <repository-url>
cd video-editor-app

# Lancer l'application (installe automatiquement les dépendances)
start.bat
```

Le script `start.bat` :
- Vérifie les prérequis
- Installe les dépendances Node.js et Python
- Crée les dossiers nécessaires
- Lance les services
- Ouvre le navigateur

### Développement Manuel (Windows)

**Terminal 1 - AI Processor :**
```cmd
cd ai-processor
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

**Terminal 2 - Backend :**
```cmd
cd backend
npm install
node server.js
```

Accéder à : http://localhost:3000

## Développement Local (Linux/macOS)

### Installation

```bash
# Installer les prérequis
# Ubuntu/Debian
sudo apt update && sudo apt install -y nodejs npm python3 python3-pip ffmpeg

# macOS
brew install node python ffmpeg

# Lancer l'application
chmod +x start.sh
./start.sh
```

## Déploiement en Production (Ubuntu VPS)

### Option 1 : Déploiement Automatique (Recommandé)

```bash
# Sur votre VPS Ubuntu
git clone <repository-url>
cd video-editor-app

# Rendre le script exécutable
chmod +x deploy.sh

# Lancer le déploiement
sudo ./deploy.sh
```

Le script `deploy.sh` :
- Met à jour le système
- Installe Docker et Docker Compose
- Configure l'application
- Build et lance les conteneurs
- Configure les volumes et réseaux

### Option 2 : Déploiement Manuel

#### 1. Préparer le VPS

```bash
# Connexion SSH
ssh root@your-vps-ip

# Mise à jour système
apt update && apt upgrade -y

# Installer Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

# Installer Docker Compose
curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose

# Vérifier les installations
docker --version
docker-compose --version
```

#### 2. Déployer l'Application

```bash
# Créer le répertoire
mkdir -p /var/www/video-editor
cd /var/www/video-editor

# Cloner ou copier le projet
git clone <repository-url> .

# Configurer l'environnement
cp .env.production .env
nano .env  # Ajuster si nécessaire

# Créer les dossiers
mkdir -p uploads outputs temp

# Lancer avec Docker Compose Production
docker-compose -f docker-compose.prod.yml up -d --build

# Vérifier les logs
docker-compose -f docker-compose.prod.yml logs -f
```

#### 3. Configurer Nginx (Reverse Proxy)

```bash
# Installer Nginx
apt install -y nginx

# Créer la configuration
nano /etc/nginx/sites-available/video-editor
```

Contenu du fichier :
```nginx
server {
    listen 80;
    server_name your-domain.com;

    # Limite de taille des uploads
    client_max_body_size 1G;

    location / {
        proxy_pass http://localhost:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;

        # Timeouts pour les uploads volumineux
        proxy_connect_timeout 600;
        proxy_send_timeout 600;
        proxy_read_timeout 600;
        send_timeout 600;
    }
}
```

```bash
# Activer le site
ln -s /etc/nginx/sites-available/video-editor /etc/nginx/sites-enabled/
nginx -t
systemctl restart nginx
```

#### 4. SSL avec Let's Encrypt

```bash
# Installer Certbot
apt install -y certbot python3-certbot-nginx

# Obtenir le certificat SSL
certbot --nginx -d your-domain.com

# Renouvellement automatique (déjà configuré)
certbot renew --dry-run
```

#### 5. Configurer le Pare-feu

```bash
# Installer UFW si nécessaire
apt install -y ufw

# Configurer les règles
ufw allow 22/tcp    # SSH
ufw allow 80/tcp    # HTTP
ufw allow 443/tcp   # HTTPS

# Activer le pare-feu
ufw enable
ufw status
```

## Configuration Production vs Développement

### Fichiers de Configuration

| Environnement | Fichier Docker Compose | Fichier ENV | Dockerfiles |
|---------------|------------------------|-------------|-------------|
| Développement | `docker-compose.yml` | `.env.example` | `Dockerfile` |
| Production | `docker-compose.prod.yml` | `.env.production` | `Dockerfile.prod` |

### Différences Clés

**Développement :**
- Mode debug activé
- Hot reload
- Logs verbeux
- Pas de sécurité stricte
- Volumes montés pour édition en direct

**Production :**
- Multi-stage builds (images plus petites)
- Non-root users dans conteneurs
- Health checks activés
- Limites de ressources
- Logs rotatifs
- Gunicorn pour Python (au lieu de Flask dev server)
- Optimisations FFmpeg

## Optimisations Production

### Backend (Node.js)

```dockerfile
# Multi-stage build
FROM node:18-alpine AS builder
# ... build stage

FROM node:18-alpine
# ... runtime stage
```

- Image Alpine (plus légère)
- Dependencies en cache
- Non-root user
- Health checks

### AI Processor (Python)

```dockerfile
# Multi-stage build
FROM python:3.10-slim AS builder
# ... build dependencies

FROM python:3.10-slim
# ... runtime only
```

- Séparation build/runtime
- Seulement les dépendances runtime
- Gunicorn avec workers
- Non-root user

### Docker Compose Production

- Health checks sur tous les services
- Dépendances explicites (depends_on + condition)
- Logs rotatifs (max 10MB, 3 fichiers)
- Réseau isolé
- Volumes nommés
- Restart policies

## Commandes Utiles

### Développement (Windows)

```cmd
REM Démarrer
start.bat

REM Arrêter (Ctrl+C dans chaque fenêtre)
```

### Développement (Linux/macOS)

```bash
# Démarrer
./start.sh

# Arrêter
# Ctrl+C ou kill les PID affichés
```

### Production (Docker)

```bash
# Démarrer
docker-compose -f docker-compose.prod.yml up -d

# Arrêter
docker-compose -f docker-compose.prod.yml down

# Redémarrer
docker-compose -f docker-compose.prod.yml restart

# Voir les logs
docker-compose -f docker-compose.prod.yml logs -f

# Voir les logs d'un service spécifique
docker-compose -f docker-compose.prod.yml logs -f backend
docker-compose -f docker-compose.prod.yml logs -f ai-processor

# Mettre à jour
git pull
docker-compose -f docker-compose.prod.yml up -d --build

# Nettoyer les anciennes images
docker system prune -a

# Vérifier le statut
docker-compose -f docker-compose.prod.yml ps

# Accéder à un conteneur
docker-compose -f docker-compose.prod.yml exec backend sh
docker-compose -f docker-compose.prod.yml exec ai-processor bash
```

## Monitoring et Maintenance

### Logs

```bash
# Logs en temps réel
docker-compose -f docker-compose.prod.yml logs -f

# Logs Nginx
tail -f /var/log/nginx/access.log
tail -f /var/log/nginx/error.log
```

### Espace Disque

```bash
# Vérifier l'espace
df -h

# Nettoyer uploads/outputs anciens
find /var/www/video-editor/uploads -mtime +7 -delete
find /var/www/video-editor/outputs -mtime +7 -delete

# Nettoyer Docker
docker system prune -a --volumes
```

### Sauvegarde

```bash
# Sauvegarder les volumes
docker run --rm \
  -v video-editor_uploads:/data \
  -v $(pwd):/backup \
  alpine tar czf /backup/uploads-backup.tar.gz /data

# Restaurer
docker run --rm \
  -v video-editor_uploads:/data \
  -v $(pwd):/backup \
  alpine tar xzf /backup/uploads-backup.tar.gz -C /
```

## Dépannage

### Windows : FFmpeg non trouvé

```cmd
REM Vérifier PATH
echo %PATH%

REM Tester FFmpeg
ffmpeg -version

REM Ajouter au PATH manuellement
setx PATH "%PATH%;C:\ffmpeg\bin"
```

### Production : Conteneur ne démarre pas

```bash
# Vérifier les logs
docker-compose -f docker-compose.prod.yml logs

# Vérifier les ressources
docker stats

# Vérifier l'espace disque
df -h
```

### Upload échoue

```bash
# Vérifier les permissions
ls -la uploads/

# Corriger si nécessaire
chmod 755 uploads/
chown -R 1001:1001 uploads/
```

### Service IA non disponible

```bash
# Vérifier le health check
docker inspect video-editor-ai-processor-1 | grep -A 10 Health

# Redémarrer le service
docker-compose -f docker-compose.prod.yml restart ai-processor
```

## Performances

### Recommandations VPS

**Minimum :**
- 2 vCPU
- 4 GB RAM
- 20 GB SSD
- Ubuntu 20.04+

**Recommandé :**
- 4 vCPU
- 8 GB RAM
- 50 GB SSD
- Ubuntu 22.04+

### Optimisations

1. **FFmpeg** : Utilise tous les cores (`FFMPEG_THREADS=0`)
2. **Gunicorn** : 2 workers par défaut (ajustable)
3. **Node.js** : Mode production (pas de debug)
4. **Nginx** : Compression gzip, cache statique

## Sécurité

### Production

- [ ] Pare-feu configuré (UFW)
- [ ] SSL/TLS activé (Let's Encrypt)
- [ ] Conteneurs non-root
- [ ] Limites de taille d'upload
- [ ] Rate limiting (à implémenter si besoin)
- [ ] Logs sécurisés et rotatifs

### Bonnes Pratiques

- Ne jamais commiter `.env` avec des secrets
- Changer les ports par défaut si exposé publiquement
- Mettre à jour régulièrement les images Docker
- Surveiller les logs d'erreur
- Faire des sauvegardes régulières

## Support

En cas de problème :
1. Vérifier les logs : `docker-compose logs -f`
2. Vérifier la documentation FFmpeg
3. Ouvrir une issue sur GitHub
