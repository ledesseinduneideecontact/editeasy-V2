# Guide d'Installation Windows

Guide rapide pour faire fonctionner AI Video Editor sur Windows en développement local.

## Prérequis Windows

### 1. Node.js (Obligatoire)

**Télécharger :** https://nodejs.org/

- Choisir la version LTS (18.x ou plus récent)
- Télécharger l'installateur Windows (.msi)
- Lancer l'installation avec les options par défaut
- **Important :** Cocher "Automatically install the necessary tools" pendant l'installation

**Vérifier l'installation :**
```cmd
node --version
npm --version
```

### 2. Python (Obligatoire)

**Télécharger :** https://www.python.org/downloads/

- Version 3.10 ou plus récente
- Télécharger l'installateur Windows
- **IMPORTANT :** Cocher "Add Python to PATH" pendant l'installation
- Installer avec les options par défaut

**Vérifier l'installation :**
```cmd
python --version
pip --version
```

### 3. FFmpeg (Obligatoire)

**Option 1 : Installation via Chocolatey (Recommandé)**

```cmd
# Installer Chocolatey d'abord (PowerShell admin)
Set-ExecutionPolicy Bypass -Scope Process -Force; [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072; iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))

# Installer FFmpeg
choco install ffmpeg
```

**Option 2 : Installation manuelle**

1. Aller sur https://ffmpeg.org/download.html
2. Cliquer sur "Windows builds from gyan.dev"
3. Télécharger "ffmpeg-release-full.7z"
4. Extraire dans `C:\ffmpeg`
5. Ajouter au PATH :
   - Rechercher "Variables d'environnement" dans Windows
   - Cliquer sur "Variables d'environnement"
   - Dans "Variables système", trouver "Path"
   - Cliquer "Modifier"
   - Cliquer "Nouveau"
   - Ajouter : `C:\ffmpeg\bin`
   - Cliquer "OK" sur tout
6. **Redémarrer le terminal**

**Vérifier l'installation :**
```cmd
ffmpeg -version
```

### 4. Git (Optionnel mais recommandé)

**Télécharger :** https://git-scm.com/download/win

## Installation de l'Application

### Méthode 1 : Installation Automatique (Recommandé)

1. **Télécharger le projet**
   ```cmd
   git clone <repository-url>
   cd video-editor-app
   ```

2. **Lancer l'application**
   - Double-cliquer sur `start.bat`
   - OU dans le terminal :
   ```cmd
   start.bat
   ```

Le script `start.bat` va automatiquement :
- Vérifier que tous les prérequis sont installés
- Créer un environnement virtuel Python
- Installer toutes les dépendances Node.js et Python
- Créer les dossiers nécessaires
- Créer le fichier `.env`
- Lancer les deux services
- Ouvrir votre navigateur

3. **Accéder à l'application**
   - L'application s'ouvrira automatiquement dans votre navigateur
   - URL : http://localhost:3000

### Méthode 2 : Installation Manuelle

**Terminal 1 - AI Processor (Python) :**
```cmd
cd ai-processor
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

Vous devriez voir :
```
🤖 AI Processor starting on port 5000...
 * Running on http://0.0.0.0:5000
```

**Terminal 2 - Backend (Node.js) :**
```cmd
cd backend
npm install
node server.js
```

Vous devriez voir :
```
🚀 Server running on http://localhost:3000
📁 Upload directory: C:\...\uploads
📹 Output directory: C:\...\outputs
```

**Ouvrir le navigateur :**
- Aller sur http://localhost:3000

## Dépannage Windows

### Erreur : "FFmpeg not found"

**Symptôme :**
```
[ERROR] FFmpeg is not installed!
```

**Solutions :**

1. Vérifier si FFmpeg est installé :
   ```cmd
   where ffmpeg
   ```

2. Si non trouvé, vérifier le PATH :
   ```cmd
   echo %PATH%
   ```
   Chercher `C:\ffmpeg\bin` dans la liste

3. Ajouter manuellement au PATH :
   - Windows + R → `sysdm.cpl` → Onglet "Avancé"
   - "Variables d'environnement"
   - Variables système → "Path" → "Modifier"
   - "Nouveau" → `C:\ffmpeg\bin`
   - OK → OK → OK

4. **Redémarrer le terminal** (important!)

5. Tester à nouveau :
   ```cmd
   ffmpeg -version
   ```

### Erreur : "Python not found"

**Symptôme :**
```
[ERROR] Python is not installed!
```

**Solutions :**

1. Vérifier l'installation :
   ```cmd
   python --version
   ```

2. Si ça ne fonctionne pas, essayer :
   ```cmd
   py --version
   ```

3. Si aucun ne fonctionne :
   - Réinstaller Python depuis https://www.python.org/
   - **IMPORTANT :** Cocher "Add Python to PATH"

4. Si installé mais non trouvé :
   - Ajouter au PATH : `C:\Users\VotreNom\AppData\Local\Programs\Python\Python310`
   - Et aussi : `C:\Users\VotreNom\AppData\Local\Programs\Python\Python310\Scripts`

### Erreur : "node is not recognized"

**Solutions :**

1. Réinstaller Node.js depuis https://nodejs.org/
2. Choisir "Add to PATH" pendant l'installation
3. Redémarrer le terminal

### Erreur : "Port 3000 already in use"

**Symptôme :**
```
Error: listen EADDRINUSE: address already in use :::3000
```

**Solutions :**

1. Trouver le processus utilisant le port :
   ```cmd
   netstat -ano | findstr :3000
   ```

2. Noter le PID (dernière colonne)

3. Tuer le processus :
   ```cmd
   taskkill /PID <PID> /F
   ```

   Exemple :
   ```cmd
   taskkill /PID 12345 /F
   ```

### Erreur : "Cannot find module"

**Symptôme :**
```
Error: Cannot find module 'express'
```

**Solutions :**

1. Réinstaller les dépendances :
   ```cmd
   cd backend
   rmdir /s /q node_modules
   del package-lock.json
   npm install
   ```

### Erreur : "No module named 'cv2'"

**Symptôme :**
```
ModuleNotFoundError: No module named 'cv2'
```

**Solutions :**

1. Activer l'environnement virtuel :
   ```cmd
   cd ai-processor
   venv\Scripts\activate
   ```

2. Réinstaller les dépendances :
   ```cmd
   pip install -r requirements.txt
   ```

3. Si l'erreur persiste, installer manuellement :
   ```cmd
   pip install opencv-python opencv-contrib-python
   ```

### Problèmes de permissions

**Symptôme :**
```
Error: EACCES: permission denied
```

**Solutions :**

1. Lancer le terminal en tant qu'Administrateur :
   - Clic droit sur "Invite de commandes" ou "PowerShell"
   - "Exécuter en tant qu'administrateur"

2. OU désactiver temporairement l'antivirus/pare-feu

### Upload de fichiers échoue

**Solutions :**

1. Vérifier que les dossiers existent :
   ```cmd
   dir uploads
   dir outputs
   dir temp
   ```

2. Les créer si nécessaire :
   ```cmd
   mkdir uploads
   mkdir outputs
   mkdir temp
   ```

### L'application se ferme immédiatement

**Solutions :**

1. Lancer depuis le terminal au lieu de double-cliquer
2. Vérifier les erreurs dans les logs
3. Vérifier que tous les prérequis sont installés

## Utilisation

### Démarrer l'application

```cmd
start.bat
```

Ou manuellement dans 2 terminaux séparés (voir Méthode 2).

### Arrêter l'application

- Fermer les fenêtres de terminal
- OU appuyer sur Ctrl+C dans chaque fenêtre

### Recommencer proprement

```cmd
# Arrêter tous les processus Node.js
taskkill /F /IM node.exe

# Arrêter tous les processus Python
taskkill /F /IM python.exe

# Relancer
start.bat
```

## Chemins Windows vs Linux

Le code est compatible cross-platform grâce à Node.js `path.join()`.

**Exemples de chemins :**
- Windows : `C:\Users\VotreNom\video-editor-app\uploads\file.jpg`
- Linux/Mac : `/home/username/video-editor-app/uploads/file.jpg`

Le code gère automatiquement les différences.

## Docker sur Windows (Optionnel)

Si vous préférez utiliser Docker sous Windows :

### Prérequis

- **Docker Desktop for Windows** : https://www.docker.com/products/docker-desktop
- WSL2 activé

### Installation

1. Installer Docker Desktop
2. Activer WSL2 si demandé
3. Redémarrer Windows

### Utilisation

```cmd
# Lancer
docker-compose up --build

# Arrêter
docker-compose down
```

**Avantages :**
- Pas besoin d'installer Python, Node.js, FFmpeg
- Isolation complète
- Configuration identique à la production

**Inconvénients :**
- Plus lent au démarrage
- Consomme plus de ressources
- Modifications de code nécessitent un rebuild

## Performance sur Windows

### Conseils

1. **Antivirus** : Ajouter le dossier du projet aux exclusions
2. **Windows Defender** : Peut ralentir npm install
3. **Espace disque** : Minimum 2GB libre
4. **RAM** : Minimum 4GB, recommandé 8GB

### Optimisations

1. **Node.js** : Utiliser npm ci au lieu de npm install (plus rapide)
2. **Python** : Éviter d'installer globalement, utiliser venv
3. **FFmpeg** : Les builds static sont plus rapides

## Scripts Disponibles

Dans le dossier `backend/` :
```cmd
npm start    # Lancer le serveur
npm run dev  # Lancer avec hot-reload (nodemon)
```

Dans le dossier `ai-processor/` :
```cmd
python app.py  # Lancer le service IA
```

## Tester l'Installation

### Test FFmpeg
```cmd
ffmpeg -version
ffmpeg -f lavfi -i testsrc=duration=5:size=1280x720:rate=30 -pix_fmt yuv420p test.mp4
```

### Test Backend
```cmd
curl http://localhost:3000/api/status/test
```

### Test AI Processor
```cmd
curl http://localhost:5000/health
```

Devrait retourner : `{"status":"healthy"}`

## Versions Testées

- Windows 10/11
- Node.js 18.x, 20.x
- Python 3.10, 3.11
- FFmpeg 5.0+

## Support

Problèmes Windows spécifiques :
1. Vérifier les prérequis sont bien installés
2. Vérifier le PATH système
3. Redémarrer le terminal après modification du PATH
4. Consulter le fichier DEPLOYMENT.md pour plus de détails
5. Ouvrir une issue sur GitHub avec les logs d'erreur

## Raccourcis Utiles

**PowerShell Admin :**
- Windows + X → "Windows PowerShell (Admin)"

**Variables d'environnement :**
- Windows + R → `sysdm.cpl` → Avancé → Variables d'environnement

**Gestionnaire des tâches :**
- Ctrl + Shift + Esc

**Invite de commandes :**
- Windows + R → `cmd`
