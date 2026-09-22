# RUSHCUT — Montage express, 100% hors ligne

## Ce que fait RushCut
- **Voice Cut** : suppression automatique des silences et hésitations
- **Beat Cut** : détection de beats → export CSV de marqueurs (importables dans votre éditeur)
- **Améliorer la voix** : dé-bruitage, compression, normalisation broadcast (ffmpeg)
- **Accélérer** : time-stretch avec voix 100% naturelle (pitch préservé)

## Installation (utilisateur final)
1. Installer **ffmpeg** : https://ffmpeg.org/download.html
   (Windows : dézipper et ajouter le dossier `bin` au PATH)
2. Lancer l'application `RushCut.exe` / `RushCut.app`

## Lancer depuis les sources (développeur)
```bash
pip install -r requirements.txt
python app/main.py
```

## Créer l'exécutable installable
- **Windows** : double-cliquer `build-exe.bat` → `dist/RushCut.exe`
- **macOS** : `chmod +x build-app.sh && ./build-app.sh` → `dist/RushCut.app`
- Optionnel : empaqueter avec Inno Setup (Windows) ou create-dmg (macOS)
  pour obtenir un vrai installateur.

## Déploiement du site vitrine
Le dossier `site-vitrine/` est un site statique : hébergez-le gratuitement sur
Cloudflare Pages, GitHub Pages ou Netlify. Mettez le lien de téléchargement
de votre `.exe` dans le bouton de la section hero.
