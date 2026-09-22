# RUSHCUT v2 — Installation 100% automatique

## Le principe
- **Pour toi (développeur)** : double-clique `build-all.bat` → il installe
  Python-dépendances, télécharge ffmpeg, compile l'exe et crée l'installateur.
- **Pour tes clients** : un seul fichier `RushCut-Setup.exe`. Ils le
  téléchargent, double-cliquent, c'est installé. **Rien d'autre à installer.**
- **Filet de sécurité** : même sans ffmpeg embarqué, l'app le télécharge et
  l'installe toute seule au premier lancement (dans `%USERPROFILE%\.rushcut`).

## Build Windows (une seule commande)
1. Installe Python 3.10+ (coche "Add Python to PATH")
2. Double-clique `build-all.bat`
3. Résultat :
   - `installer/RushCut-Setup.exe` ← **à distribuer** (si Inno Setup installé)
   - ou `dist/RushCut.exe` ← fonctionne aussi seul (~90 Mo, ffmpeg inclus)

## Build macOS
```bash
chmod +x build-app.sh && ./build-app.sh
```

## Lancer depuis les sources (test rapide)
```bash
pip install -r requirements.txt
python app/main.py
```
(ffmpeg sera téléchargé automatiquement au 1er lancement)

## Déployer le site vitrine
Héberge `site-vitrine/index.html` sur Cloudflare Pages / GitHub Pages (gratuit).
Remplace `href="RushCut.exe"` par le lien de téléchargement de ton Setup.

## Fonctions
Voice Cut (silences) · Beat Cut (marqueurs CSV) · Amélioration vocale ·
Accélération pitch-préservé — tout en local, aucun cloud.
