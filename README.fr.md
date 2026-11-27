# Donkey Kong Bananza Recompilation PC — Config Légère & Sans GPU Dédié (iGPU)

🌐 **Langues** : [English (README.md)](README.md) | **Français**

Installateur Windows en **1 clic** et outil de mise à jour en **3 secondes** pour le portage PC natif de **Donkey Kong Bananza** (`dkb-pc-recomp`).  
Spécialement optimisé pour jouer en **1080p à 50–60 FPS** sur **PC légers, ordinateurs portables et cartes graphiques intégrées (iGPU) sans GPU dédié**.

> **Avertissement légal** : Ce dépôt et ses Releases ne contiennent **aucun fichier Nintendo** (aucun code du jeu, ni ExeFS, ni RomFS, ni clé). Vous devez fournir votre propre dump légal (`.nup` ou dossiers `ExeFS` + `RomFS`).

---

## À qui s'adresse ce projet ? (Who is this project for?)

Cette édition est conçue spécialement pour :
- **La recompilation PC de Donkey Kong Bananza** optimisée pour la performance.
- **Jouer sans carte graphique dédiée** (aucune RTX / RX requise).
- **Les PC légers et ordinateurs portables fins** (*low-end PC gaming*).
- **Les puces graphiques intégrées Intel** (Intel Iris Xe, Intel UHD Graphics).
- **Les puces graphiques intégrées AMD** (AMD Radeon Vega 7, Vega 8, Radeon 680M/780M).
- **L'optimisation mémoire GPU partagée (UMA)** et **faible VRAM**.
- **L'optimisation Vulkan** avec Frame Generation 2× / **3×** intégrée.

> *Si vous avez un gros GPU dédié (NVIDIA RTX / AMD RX) et cherchez la qualité visuelle maximale avant tout, tournez-vous plutôt vers le projet parent [`dkb-pc-recomp`](https://github.com/Lucas-blip-png/dkb-pc-recomp).*

---

## Benchmarks Réels (Mesurés)

Mesurés sur un PC portable réel **sans carte graphique dédiée** :
- **CPU** : AMD Ryzen 5 7530U (Zen 3, 6 cœurs / 12 threads)
- **iGPU** : AMD Radeon Vega 7 (7 CU, budget VRAM Vulkan `486 MiB`, 16 Go RAM single-channel)
- **Version du jeu** : Donkey Kong Bananza `3.2.0` (`dkb458752`)

| Scène (1080p) | Version standard | Édition Low-Spec (`v1.1.0`) | Empreinte VRAM / RAM |
| :--- | :--- | :--- | :--- |
| **Écran titre / Menus** | 46–53 FPS | **50–60 FPS** | ~315 MiB VRAM |
| **Jeu 3D calme** | 5,6–8,8 FPS (VRAM saturée) | **52–74 FPS** (`FG 3×`, `over refresh = 0`) | **315 / 486 MiB** VRAM, **4,4 Go** commit |
| **Scène lourde / Transition** | 3,5–10,9 FPS (`hitch 15–25`) | **38,5–44,4 FPS** (`hitch 0–2`) | **315 MiB** VRAM, **1,5 Go** RAM invité |

### Tableau des iGPU & État des tests

| GPU intégré (iGPU) | Statut | Performances mesurées / attendues |
| :--- | :--- | :--- |
| **AMD Radeon Vega 7 (Ryzen 5 7530U)** | **Testé et vérifié** | **1080p, 38,5–74,0 FPS** (`FG 3×`), **315 MiB** VRAM |
| **AMD Radeon Vega 8** | Théoriquement compatible | Similaire ou légèrement supérieur au Vega 7 *(retours attendus)* |
| **Intel Iris Xe** | Théoriquement compatible | Vulkan 1.3 + `x86-64-v3` supportés *(retours attendus)* |
| **Intel UHD 620 / 630** | Théoriquement compatible | Résolution interne réduite conseillée (`720p` / `960×540`) *(non testé)* |
| **Steam Deck (APU RDNA 2)** | Théoriquement compatible | Compatible `x86-64-v3` + Vulkan 1.3 *(testé sous Windows)* |

---

## Matrice de compatibilité

| Configuration | Catégorie | Statut | Notes |
| :--- | :--- | :--- | :--- |
| **Windows 10 / 11 (64 bits) + AMD Vega 7** | **Testé et vérifié** | Fonctionnel | Jeu fluide, sauvegardes, `dkb.exe --selftest` 0 échec |
| **Windows 10 / 11 + CPU x86-64-v3 + Vulkan 1.3** | **Théoriquement compatible** | Prêt | Runtime compilé en `-O3 -march=x86-64-v3` universel |
| **Autres iGPU (Iris Xe, UHD, Vega 8)** | **Rapports utilisateurs** | Ouvert | Partagez vos résultats FPS/RAM dans les Issues ! |

---

## Installation & Mises à jour en 3 secondes

1. Téléchargez **`DKB-LowSpec-Setup-v1.1.0.exe`** dans [**Releases**](https://github.com/evolis-game/donkey-kong-bananza-pc-lowspec/releases).
2. Double-cliquez dessus : une barre de progression extrait les outils, puis l'installateur s'ouvre directement en **Français** (`FR / EN / RU`).
3. Choisissez votre fichier **`.nup`** *(ou cochez **Mode avancé** pour des dossiers `ExeFS`/`RomFS`)*, la **langue** et le **dossier**, puis cliquez sur **Installer**.
4. Pour jouer, lancez **`Donkey Kong Bananza`** ou **`Jouer_DKB_Natif.bat`**.
5. Pour mettre à jour plus tard en ~3 secondes sans `.nup`, double-cliquez sur **`Mettre_a_jour_DKB.bat`**.
