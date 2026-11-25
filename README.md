# DKB Low-Spec Recomp (PC Légers & iGPU)

Version optimisée et clé-en-main du portage PC natif de **Donkey Kong Bananza** (basée sur `dkb-pc-recomp`), spécialement configurée pour offrir une expérience fluide (**1080p, 50–60 FPS**) sur les configurations légères et cartes graphiques intégrées (ex. **AMD Ryzen 5 7530U / Radeon Vega 7**, iGPU avec VRAM partagée).

> **Avertissement légal** : Ce dépôt et ses Releases ne contiennent **aucun fichier du jeu** (aucun code Nintendo, ni ExeFS, ni RomFS, ni clé). Vous devez fournir votre propre dump légal du jeu (`.nup` ou dossiers `ExeFS`/`RomFS`).

---

## Fonctionnalités & Optimisations incluses

- **Runtime universel `x86-64-v3` (`-O3`)** : compatible avec tous les processeurs Intel et AMD modernes.
- **Compression ASTC -> BC3 (`astc_bc = 1`)** : divise par 4 l'empreinte VRAM et la bande passante mémoire sur iGPU.
- **Gestion mémoire UMA optimisée (`tex_uma_host = 1`, `tex_vram_pressure = 88`, `pool_fini_wait = fence`)** : élimine les saccades et saturations mémoire sur VRAM partagée.
- **Allègement graphique intelligent** :
  - Décimation temporelle des ombres (`shadow_rate = 6`) et des cubemaps (`cubemap_rate = 4`).
  - Bypass SMAA (`smaa_bypass = 1`) et blit rapide (`mvk_upscale_blit = 1`).
  - Répartition multi-thread du replay NVN (`replay_threads = 4`).
- **Frame Generation & Pacing** intégrés dans [dkb.ini.example](dkb.ini.example) pour atteindre 50–60 FPS fluides en jeu.
- **Package prêt à jouer** : crée automatiquement `dkb.ini`, `Jouer_DKB_Natif.bat` (priorité CPU Haute), l'icône `dkb.ico` et le raccourci Windows `Donkey Kong Bananza.lnk`.
- **Mises à jour en ~3 secondes** : grâce au cache d'objets (`.update-cache/`), les futures mises à jour ne téléchargent que ~8–25 Mo et relinkent `dkb.exe` sans ré-extraire le jeu ni recompiler les 274 fichiers C.

---

## Installation depuis zéro (1 seul exécutable)

1. Téléchargez **`DKB-LowSpec-Setup-vX.Y.Z.exe`** depuis l'onglet [**Releases**](../../releases).
2. Double-cliquez dessus pour lancer l'installateur graphique.
3. Sélectionnez votre fichier **`.nup`** (ou dossier ExeFS + RomFS), choisissez la langue du jeu et le dossier d'installation.
4. Patientez pendant l'extraction, la compilation initiale et la préparation des shaders.
5. Lancez le jeu via le raccourci **`Donkey Kong Bananza`** ou **`Jouer_DKB_Natif.bat`**.

---

## Mises à jour faciles (en ~3 secondes)

Lorsqu'une nouvelle version est publiée sur GitHub Releases :
1. Double-cliquez simplement sur **`Mettre_a_jour_DKB.bat`** dans votre dossier de jeu.
2. L'outil vérifie la dernière version, télécharge uniquement le petit patch (`dkb-lowspec-patch-*.zip`), met à jour `dkb.ini` **sans effacer votre langue**, relinke `dkb.exe` en quelques secondes et vérifie le binaire (`--selftest`).

*(Note : le dossier `.update-cache/` d'environ 207 Mo dans le dossier du jeu permet cette mise à jour instantanée. Ne le supprimez pas si vous souhaitez profiter des mises à jour rapides.)*
