# Donkey Kong Bananza — Édition PC Légers & iGPU

🌐 **Langues** : [English (README.md)](README.md) | **Français**

Installateur tout-en-un optimisé et outil de mise à jour rapide pour le portage PC natif de **Donkey Kong Bananza** (`dkb-pc-recomp`).  
Spécialement configuré pour les **PC légers, ordinateurs portables et cartes graphiques intégrées (iGPU)** comme l'**AMD Ryzen 5 7530U / Radeon Vega 7, Vega 8, Intel Iris Xe et Steam Deck**, offrant **50–60 FPS en 1080p** avec une consommation VRAM réduite.

> **Avertissement légal** : Ce dépôt et ses Releases ne contiennent **aucun fichier du jeu Nintendo** (aucun code du jeu, ni ExeFS, ni RomFS, ni clé). Vous devez fournir votre propre dump légal du jeu (fichier `.nup` ou dossiers `ExeFS` + `RomFS`).

---

## Sommaire
1. [Pourquoi cette édition ? (Optimisations incluses)](#-pourquoi-cette-édition--optimisations-incluses)
2. [Configuration requise](#-configuration-requise)
3. [Installation depuis zéro (en 1 clic)](#-installation-depuis-zéro-en-1-clic)
4. [Comment jouer](#-comment-jouer)
5. [Mises à jour faciles (en ~3 secondes)](#-mises-à-jour-faciles-en-3-secondes)
6. [Personnalisation (`dkb.ini`)](#-personnalisation-dkbini)
7. [Foire aux questions (FAQ)](#-foire-aux-questions-faq)

---

## Pourquoi cette édition ? (Optimisations incluses)

Sur un PC portable ou un iGPU, la version standard peut saturer la VRAM partagée et chuter sous les 20–25 FPS. Cette édition intègre et pré-compile toutes les optimisations automatiquement :

| Optimisation | Réglage / Technologie | Gain sur PC léger / iGPU |
| :--- | :--- | :--- |
| **Runtime universel** | `-O3 -march=x86-64-v3` | Compatible avec tous les CPU Intel & AMD modernes (depuis ~2015) |
| **Compression ASTC → BC3** | `astc = gpu`, `astc_bc = 1` | **4× moins de VRAM et de bande passante** utilisée pour les textures |
| **Gestion mémoire UMA** | `tex_uma_host = 1`, `tex_vram_pressure = 88`, `pool_fini_wait = fence` | Supprime les micro-freezes et crashs liés à la mémoire partagée |
| **Allègement graphique ciblé** | `shadow_rate = 6`, `cubemap_rate = 4`, `smaa_bypass = 1`, `mvk_upscale_blit = 1` | Énorme gain GPU sans dénaturer l'image |
| **Replay multi-thread** | `replay_threads = 4` | Répartit les appels Vulkan sur 4 cœurs CPU |
| **Frame Generation 2×** | `fg_pace` + `fps_limit = 30` + `realtime = 1` | Fluidité **50–60 FPS** en 1080p sur Vega 7 |
| **Installation prête à jouer** | `dkb.ini`, `Jouer_DKB_Natif.bat`, `dkb.ico`, raccourci `.lnk` | Lancement en priorité CPU Haute et icône haute résolution automatiques |
| **Mises à jour en 3 secondes** | `.update-cache/` + `Mettre_a_jour_DKB.bat` | Télécharge ~8–25 Mo seulement et relinke en 3 secondes |

---

## Configuration requise

- **Système** : Windows 10 / Windows 11 (64 bits)
- **Processeur** : Tout CPU `x86-64-v3` (Intel 4e gén.+ ou AMD Ryzen+)
- **Carte graphique** : GPU compatible Vulkan 1.3 (Radeon Vega 7/8, Intel Iris Xe, NVIDIA GTX/RTX)
- **Mémoire RAM** : 16 Go recommandés (ou 8 Go avec fichier d'échange Windows étendu)
- **Espace disque** : ~15–20 Go libres pendant l'installation
- **Fichiers du jeu** : Votre fichier `.nup` légal, ou vos dossiers `ExeFS` + `RomFS` (versions `1.0.0` et `3.2.0` supportées)

---

## Installation depuis zéro (en 1 clic)

1. Rendez-vous sur la page [**Releases**](https://github.com/evolis-game/dkb-lowspec-recomp/releases) et téléchargez **`DKB-LowSpec-Setup-vX.Y.Z.exe`** (~84 Mo).
2. Double-cliquez sur **`DKB-LowSpec-Setup-vX.Y.Z.exe`**. *(Tout est inclus : aucun logiciel ou compilateur à installer à part.)*
3. Choisissez :
   - Votre fichier **`.nup`** (ou dossiers `ExeFS` + `RomFS`)
   - La **langue du jeu** (ex. Français `fr`)
   - Le **dossier de destination** (ex. `C:\Jeux\DKB-Recomp`)
4. Cliquez sur **Install** et laissez l'assistant terminer :
   - Extraction et vérification du jeu
   - Recompilation et liaison avec notre runtime optimisé `x86-64-v3`
   - Préparation du cache de shaders (évite les saccades en jeu)
   - Création de `dkb.ini`, `Jouer_DKB_Natif.bat`, `Mettre_a_jour_DKB.bat` et du raccourci avec icône

---

## Comment jouer

Dans votre dossier d'installation, lancez simplement :
- **`Donkey Kong Bananza`** (raccourci Windows avec icône — lance en priorité CPU Haute)
- ou **`Jouer_DKB_Natif.bat`**

> **Astuce** : Appuyez sur **`F1`** en jeu pour ouvrir le menu des réglages.

---

## Mises à jour faciles (en ~3 secondes)

Lorsqu'une nouvelle mise à jour est disponible, vous n'avez **PAS besoin** de votre `.nup` ni d'attendre 45 minutes :

1. Double-cliquez sur **`Mettre_a_jour_DKB.bat`** dans votre dossier de jeu.
2. L'outil va automatiquement :
   - Vérifier la dernière version sur [GitHub Releases](https://github.com/evolis-game/dkb-lowspec-recomp/releases)
   - Télécharger uniquement le petit patch (`dkb-lowspec-patch-*.zip`, ~8–25 Mo)
   - Mettre à jour `dkb.ini` **sans effacer votre langue ni vos réglages**
   - Relinker `dkb.exe` en **~3 secondes** grâce au dossier `.update-cache/`
   - Vérifier le bon fonctionnement avec `dkb.exe --selftest` (`0 failures`)

*(Note : ne supprimez pas le dossier `.update-cache` (~207 Mo) dans votre dossier de jeu si vous voulez profiter des mises à jour instantanées.)*

---

## Personnalisation (`dkb.ini`)

Tous les réglages sont dans `dkb.ini`. Quelques options utiles :
- `fps_limit = 30` (Base 30 FPS doublée à 60 FPS fluides par le Frame Gen)
- `astc_bc = 1` (Passez à `0` uniquement sur une grosse carte graphique 8+ Go de VRAM)
- `shadow_rate = 6` (Met à jour les ombres 1 frame sur 6 ; baissez à `2` ou `1` sur un GPU plus puissant)
- `smaa_bypass = 1` (Passez à `0` pour réactiver l'anticrénelage SMAA)

---

## Foire aux questions (FAQ)

- **Windows SmartScreen affiche « Windows a protégé votre ordinateur »** : cliquez sur **Informations complémentaires → Exécuter quand même** (l'exécutable n'est pas signé numériquement car c'est un projet open-source).
- **Puis-je supprimer mon fichier `.nup` après l'installation ?** Oui, une fois l'installation terminée, tout le jeu est autonome dans votre dossier de destination.
- **Comment changer la langue après coup ?** Ouvrez `dkb.ini` et modifiez `lang = fr` (ou `en-US`, `es`, `de`, `ja`, etc.).
