# Journal technique d'optimisation — `dkb.exe` (Donkey Kong Bananza 3.2.0)

> Document évolutif : chaque étape depuis la toute première compilation du jeu, chaque modification de code, incident, solution et mesure future est ajoutée chronologiquement dans ce document pour conserver une trace complète et vérifiable.

---

## 1. Plateforme cible et contexte du projet

- **Processeur (CPU)** : AMD Ryzen 5 7530U (architecture Zen 3, 6 cœurs / 12 threads)
- **GPU intégré (iGPU / UMA)** : AMD Radeon Vega 7 (7 CU, ID vendeur `0x1002`, device `0x15e7`, driver AMD `23.19`, Vulkan `1.3.260`)
- **Mémoire vidéo et système** :
  - Tas Vulkan `heap 0` (`DEVICE_LOCAL`) : `256 MiB`
  - Tas Vulkan `heap 2` (`DEVICE_LOCAL | HOST_VISIBLE | HOST_COHERENT`) : `256 MiB` (budget VRAM combiné rapporté : **486 MiB**)
  - Tas Vulkan `heap 1` (mémoire hôte système partagée) : `7584 MiB` (RAM PC totale : `15.31 GiB` single-channel)
- **Jeu & Exécutable** : *Donkey Kong Bananza* v3.2.0 (`dkb458752`) + DLC `1.0.0`, recompilé statiquement en exécutable PC natif via `dkb-pc-recomp` (`DKB-Setup 0.4.0+8d45dcc`)
- **Dossier du jeu compilé** : [DKB-Recomp](file:///C:/Users/shlom/Downloads/DKB-Recomp)
- **Sources runtime personnalisées** : [runtime](file:///C:/Users/shlom/.gemini/antigravity/brain/1c73a8f1-de39-4dda-8cb2-3cdbd1dfbc49/scratch/DKB-Setup-src/DKB-Setup/runtime)
- **Sauvegarde transférée et préservée** : [559d6597ce3e657b23ed020cf32fe211](file:///C:/Users/shlom/Downloads/DKB-Recomp/profile/save/559d6597ce3e657b23ed020cf32fe211)

---

## 2. Phase 0 — Recompilation initiale du jeu et premiers lancements

### 2.1. Extraction et compilation statique depuis le `.nup` (`DKB-Setup 0.4.0+8d45dcc`)
- **Objectif** : quitter l'émulateur Eglantine pour exécuter *Donkey Kong Bananza* (`3.2.0` + DLC `1.0.0`) nativement sur PC.
- **Technique mise en œuvre** :
  - Vérification de l'espace disque disponible (`~19 Go` libres sur `C:`, `~18 Go` sur `G:`).
  - Téléchargement et extraction de `DKB-Setup-0.4.0+8d45dcc-windows.zip` (`129,5 Mo`).
  - Lancement de la chaîne complète de recompilation vers [DKB-Recomp](file:///C:/Users/shlom/Downloads/DKB-Recomp) :
    1. `check` (vérification des binaires jeu/mise à jour)
    2. `dkb_data` (`199 s`, extraction/préparation des données)
    3. `lift` (`111 s`, traduction statique des instructions Switch vers C)
    4. `compile` (`274` fichiers générés compilés en exécutable natif)
    5. `dkb_shaders` (`~18 800` shaders traduits à l'avance via `6` workers `totk_xlate.exe`)
    6. `dkb_verify` (vérification d'intégrité)
- **Installation et sauvegarde** :
  - Création du raccourci [Jouer_DKB_Natif.bat](file:///C:/Users/shlom/Downloads/DKB-Recomp/Jouer_DKB_Natif.bat) (lancement en priorité CPU Haute).
  - Copie des `4` fichiers de sauvegarde Eglantine (`caption.sav`, `config.sav`, `0\emerush.sav`, `0\progress.sav` — `2,5 MiB`) dans le profil natif.
  - Suppression des dossiers temporaires d'installation (`dkb-tmp`, `DKB-Setup-0.4.0`), libérant `21,94 Go` sur `C:`.

### 2.2. Premiers tests en jeu et recherche de la baseline stock (`5,6 FPS -> 22,4 FPS`)
- **Test de démarrage (menus / écran titre, 18 s)** :
  - `boot: passed`, `1031` frames affichées en français (`Ver. 3.2.0` / `Ver. DLC 1.0.0`), `0` shader manquant, `0` erreur de validation.
  - Performances en menu : **`46,3` à `53,3 FPS` moyens** (pointes jusqu'à **`57,7`–`60,8 FPS`**), `345 / 486 MiB` VRAM.
- **Premiers lancements en jeu 3D (tunnel minier — *Site d'extraction de bananes*)** :
  - Captures de référence : [capture_1_entree_tunnel.png](file:///C:/Users/shlom/Downloads/DKB-Recomp/captures/capture_1_entree_tunnel.png), [capture_2_tunnel_3d.png](file:///C:/Users/shlom/Downloads/DKB-Recomp/captures/capture_2_tunnel_3d.png), [capture_3_cristaux_3d.png](file:///C:/Users/shlom/Downloads/DKB-Recomp/captures/capture_3_cristaux_3d.png).
  - **Problème #1 : Effondrement à `5,6`–`8,8 FPS` (`frame 1920 : 113,4 ms`) au premier profil**
    - Cause : `frame_gen = 2x`, `tex_vram_pressure = 75` et `1920x1080` saturaient la VRAM à `487–488 / 486 MiB`, montaient `present gpu` à `16,8`–`27,3 ms` et poussaient la RAM privée à `9`–`12 Go` avec swap Windows.
    - En abaissant brutalement à `scene_res = 3.0` avant ajustement VRAM, le jeu tombait même à `3,5`–`5,6 FPS` (`90,5`–`125,0 ms` GPU).
  - **Solutions appliquées dans [dkb.ini](file:///C:/Users/shlom/Downloads/DKB-Recomp/dkb.ini) (baseline stock optimisée)** :
    - Passage temporaire à `frame_gen = off` (`present gpu` ramené de `27,3 ms` à `0,49 ms`), `tex_vram_pressure = 55`, `window_size = 1280x720`, `window_mode = windowed`, `operation_mode = handheld`, `astc = gpu`, `astc_bc = 1`, `split_draws = 16`, `split_us = 100`, `scene_res = auto`.
    - **Gain obtenu** : passage de `5,6–8,8 FPS` à **`18,4`–`22,4 FPS`** (`1% low 19,0 FPS`, moyenne mixte menus+3D `38,4 FPS`, `gpu avg 35,02 ms`, `replay avg 22,31 ms`, VRAM `444–445 / 486 MiB`, RAM stabilisée à `5,2–5,5 Go` sans swap) — soit presque **×3 en 3D**.
  - **Réglages testés et rejetés en version stock** :
    - `scene_res = 2.0` sur le binaire d'origine : coupait/dégradait l'affichage 2D ou faisait chuter à `16,4 FPS` (`gpu avg 50,9 ms`).
    - `TOTK_REPLAY_THREADS=6` sur le binaire d'origine : régression à `18,6 FPS` (`worst frame 229 ms`) par contention CPU sans les contournements runtime ultérieurs.
    - `split_draws = 0` : régression de `22,4 FPS` à **`13,7 FPS`** (l'envoi en petits lots permet à la Vega 7 de recouvrir le travail CPU/GPU).

### 2.3. Étude parallèle (Xiaomi Pad 8 Pro / Android)
- Analyse effectuée à la demande de l'utilisateur pour porter le jeu nativement en APK sur Xiaomi Pad 8 Pro (Snapdragon 8 Elite / Adreno 830) : `dkb-pc-recomp` génère uniquement du code **x86-64 Windows/Linux** (`exe` / ELF) et dépend d'un runtime PC/Vulkan spécifique ; obtenir un APK Android ARM64 natif est donc exclu sans réécriture/portage lourd du recompilateur et du runtime. Décision actée : concentrer l'effort sur une **réécriture structurelle du runtime PC**.

---

## 3. Diagnostics approfondis et mise en place de la chaîne de recompilation incrémentale

### 3.1. Profilage structurel (`passes.txt` & `DKB_SKIP_DRAWS=1`)
Avant d'écrire du code C/Vulkan, deux mesures de référence ont localisé exactement où passait chaque milliseconde :
1. **Dump GPU d'une trame 3D (`frame 1850`, `passes.txt`)** :
   - **`7 701` à `7 895` draw calls / frame**, répartis notamment en :
     - `pass 0172` + `pass 0173` : **`3 736` draws en `1368x1368`** (deux shadow maps).
     - `pass 0187` + `pass 0202` : **`3 548` draws en `1280x720`** (pré-passe opaque G-buffer + éclairage principal).
   - Replay CPU : `21,5` à `22,3 ms` par trame en monothread ; `~15 500` vérifications de descripteurs/textures par frame.
2. **Mesure du plafond CPU pur (`DKB_SKIP_DRAWS=1`, zéro dessin GPU)** :
   - CPU + simulation : **`40,1`–`50,1 FPS`** (`interval 24,92 ms`, `render busy avg 14,29 ms`, `replay avg 4,07 ms`).
   - Les seuls **compute dispatches et clears GPU** prenaient encore **`10,39 ms`** sur la Vega 7.

### 3.2. Chaîne de compilation C/LLVM incrémentale
Plutôt que de recompiler à chaque fois les 274 chunks du jeu en ~80 min, un répertoire incrémental persistant (`C:\Users\shlom\Downloads\dkb-custom-build`) a été créé en extrayant le kit source `DKB-Setup` :
- **Total des objets** : `403` objets (`223` `main` + `51` `sdk` + `129` `runtime`), compilés avec Clang/LLVM en **`-O3 -march=znver3 -mtune=znver3`** (optimisé Ryzen 5 7530U) via Ninja (`--jobs 8`).
- **Première compilation complète (`Build #1`)** : terminée en **13 minutes** grâce au cache.
- **Itérations suivantes sur `runtime/` (`Builds #2 à #7`)** : recompilation et édition de liens en **~3 à 9 secondes**.

Commande standard utilisée :
```powershell
$setup = 'C:\Users\shlom\.gemini\antigravity\brain\1c73a8f1-de39-4dda-8cb2-3cdbd1dfbc49\scratch\DKB-Setup-src\DKB-Setup'
$py = "$setup\python\python.exe"
$work = 'C:\Users\shlom\Downloads\dkb-custom-build'
$dest = 'C:\Users\shlom\Downloads\DKB-Recomp'
& $py "$setup\tools\build_game.py" --version dkb458752 --expected "$setup\tools\data\expected-dkb458752.json" `
  --gen "$work\gen" --out "$work\build" --modules main,sdk `
  --exefs "$dest\exefs" --romfs "$dest\romfs" --profile "$dest\profile" `
  --runtime "$setup\runtime" --toolchain "$setup\llvm" --deps "$setup\runtime\deps" `
  --ninja "$setup\bin\ninja.exe" --jobs 8
Copy-Item "$work\build\dkb.exe" "$dest\dkb.exe" -Force
```

### 3.3. Protocole de validation systématique
1. **`dkb.exe --selftest`** après chaque compilation : vérifie le dispatch (`191050` fonctions), la mémoire et l'intégrité (`selftest: passed (0 failures)`).
2. **Test reproductible automatisé (`--seconds 52`)** via `TOTK_INPUT_SCRIPT` ([input_play.txt](file:///C:/Users/shlom/.gemini/antigravity/brain/1c73a8f1-de39-4dda-8cb2-3cdbd1dfbc49/scratch/input_play.txt)) pilotant le jeu dans le tunnel minier et l'éboulement, avec contrôle de `validation errors 0`, `shader failures 0`, `frametime:`, `perf:` et `fg:`.
3. **Inspection visuelle directe** des captures pleine résolution (`TOTK_SHOTS_FULL=1` / `--shot`).

---

## 4. Historique chronologique des Builds #1 à #7, problèmes et solutions

### Build #1 — Déblocage résolution, décimation des ombres, cache texture par frame et Zen 3 (`Bench A` & `B`)
- **Modifications de code** :
  1. **`dkb_wide.c`** : déblocage de `output_res` sous `720p` (jusqu'à `640x360`, ex. `960x540`) et extension de `scene_res` jusqu'à `4.0`.
  2. **`vk_exec.h` / `vk_exec.c` / `vk_exec_draw.c`** : ajout de `TOTK_SHADOW_RATE` pour décimer temporellement les deux shadow maps `1368x1368` (conservation de la dernière profondeur valide entre mises à jour et saut des clears associés).
  3. **`vk_texture.c`** : ajout de `TOTK_TEX_FRAME_EPOCH=1` pour ne pas re-vérifier plusieurs fois par image les textures statiques déjà validées (`~15 300` checks ramenés à `177–240` écritures/frame hors bind).
  4. **`vk_sync.c` & `tools/build_game.py`** : ajout de `TOTK_PERF_AFTER_FRAME` pour profiler les sous-passes GPU tardives, et passage des drapeaux CPU à `-O3 -march=znver3 -mtune=znver3`.
- **Ce que `Bench A` et `Bench B` ont révélé (`960x540` / `scene_res = 1.5`)** :
  - Sous `TOTK_TRACE=perf`, le jeu tournait entre `13,8` et `17,1 FPS` (`gpu avg 44,3–54,8 ms`), malgré la capture propre [benchA_960_sh4.png](file:///C:/Users/shlom/Downloads/DKB-Recomp/captures/benchA_960_sh4.png).
  - Le profilage GPU détaillé (`passes.txt` à la `frame 2050`) a mis au jour **deux goulets majeurs inattendus** :
    - Un dispatch compute final (`3582d55d1149d49b`) prenant à lui seul **`~20 ms` GPU**.
    - En `960x540` (`Bench A`/`B`), l'UI était rendue en `1920x1080` pendant que la 3D passait en `1280x720`, poussant la VRAM à `457 / 486 MiB` et provoquant une seconde passe lente à `8,4`–`8,7 ms` sans draw.

---

### Build #2 — Court-circuit des ombres dans `walk()`/`par_walk()` et extension des filtres (`Bench C` & `D`)
- **Technique appliquée** :
  - [vk_exec.c](file:///C:/Users/shlom/.gemini/antigravity/brain/1c73a8f1-de39-4dda-8cb2-3cdbd1dfbc49/scratch/DKB-Setup-src/DKB-Setup/runtime/vk_exec.c#L2583-L2585) : court-circuit de `OP_DRAW`, `OP_DRAW_IDX` et `OP_DRAW_IDX_IND` directement dans `walk()` et `par_walk()` quand `ex->skip_shadow` est actif (`resolve_rt(ex); if (ex->skip_shadow) break;`), évitant `draws_seen++`, `par_watch` et `vk_exec_op_draw()`.
  - [vk_exec_draw.c](file:///C:/Users/shlom/.gemini/antigravity/brain/1c73a8f1-de39-4dda-8cb2-3cdbd1dfbc49/scratch/DKB-Setup-src/DKB-Setup/runtime/vk_exec_draw.c#L169) : extension de `SkipList.list` de `16` à `64` entrées (`sl->n < 64`) et ajout de `skip_cs_listed(ex)` dans `op_dispatch_ind`.
- **Résultats mesurés** :
  - **Bench C** (`1280x720`, `scene_res = auto`, `shadow_rate = 4`, avec `TOTK_TRACE=perf`) : `15,7` à `19,2 FPS` (`gpu avg 38,6–49,6 ms`, VRAM `445 / 486 MiB`).
  - **Bench D** (`1280x720`, `scene_res = 2.0`, `shadow_rate = 6`, avec `TOTK_SKIP_FS` sur les passes de flou bloom — capture [benchD_1280_sc2_skipblur.png](file:///C:/Users/shlom/Downloads/DKB-Recomp/captures/benchD_1280_sc2_skipblur.png)) : les passes G-buffer + opaque ont été **divisées par deux** (`3,9 ms`), mais la passe finale (`e27e4707534b74e8`) consommait encore **`17,6 ms` GPU** et la VRAM grimpait à **`461 / 486 MiB`** (`gpu avg 48,78 ms`, `15,4 FPS` sous trace).
- **Diagnostic clé** : deux murs restaient face au 60 FPS :
  1. Le mur WDDM au-dessus de ~`450 MiB` (`461 / 486 MiB` `DEVICE_LOCAL`) déclenchant de la pagination PCIe/RAM.
  2. Le shader compute d'upscale du jeu (`e27e4707534b74e8` / `3582d55d1149d49b`) prenant `~17,6–20,4 ms` à chaque trame lorsque `scene_res != auto`.

---

### Build #3 & #4 — Hiérarchie mémoire UMA (`TEX_UMA_HOST`), cache sans verrou et blit upscaler (`Bench E`, `F`, `G`)
- **Problème #2 : Saturation VRAM `DEVICE_LOCAL` à `461 / 486 MiB`**
  - Toutes les textures étaient allouées avec `VMA_MEMORY_USAGE_AUTO_PREFER_DEVICE`, remplissant les `486 MiB` `DEVICE_LOCAL` avec des textures ASTC/compressées statiques et provoquant la pagination WDDM des cibles de rendu chaudes.
- **Solution implémentée (`TEX_UMA_HOST`)** :
  - [cfg.c](file:///C:/Users/shlom/.gemini/antigravity/brain/1c73a8f1-de39-4dda-8cb2-3cdbd1dfbc49/scratch/DKB-Setup-src/DKB-Setup/runtime/cfg.c#L51) : ajout de `TEX_UMA_HOST` (défaut `1`, plage `0..2`).
  - [vk_texture.c](file:///C:/Users/shlom/.gemini/antigravity/brain/1c73a8f1-de39-4dda-8cb2-3cdbd1dfbc49/scratch/DKB-Setup-src/DKB-Setup/runtime/vk_texture.c#L515-L558) : dans `create_tex()`, sur iGPU (`VK_PHYSICAL_DEVICE_TYPE_INTEGRATED_GPU`), tant que `used < budget / 100 * 78`, les textures restent en `DEVICE_LOCAL` ; au-delà de 78 %, les textures compressées (`f.vk != f.ideal` ou blocs >= 4x4) et non-render-targets sont placées sur le tas hôte `heap 1` (`host_bits`, `HOST_CACHED`), avec repli sur `VMA_MEMORY_USAGE_AUTO_PREFER_DEVICE` si l'allocation échoue.
  - **Impact** : VRAM stabilisée autour de **`408–419 / 486 MiB`**, éliminant les chutes de pagination WDDM.
- **Solution implémentée (Verrou texture & Upscaler matériel)** dans [vk_exec_draw.c](file:///C:/Users/shlom/.gemini/antigravity/brain/1c73a8f1-de39-4dda-8cb2-3cdbd1dfbc49/scratch/DKB-Setup-src/DKB-Setup/runtime/vk_exec_draw.c#L3930-L3980) :
  - Activation du chemin rapide sans verrou `tex_info_hit()` dans `bind_resources()` dès le thread principal de replay (`!slice`), ne prenant `vk_texture_lock()` qu'en cas de cache miss.
  - Déblocage de `TOTK_MVK_UPSCALE_BLIT` pour AMD Radeon Vega 7 (initialement réservé à MoltenVK) et association aux shaders compute d'upscale du jeu (`0xe27e4707534b74e8ull` et `0x3582d55d1149d49bull`), remplacés par un `vkCmdBlitImage` bilinéaire matériel.
- **Mesure `Bench F` (`TOTK_TRACE=perf` toujours actif)** :
  - Le bloc final complet passe de **`20,4 ms`** à **`3,0–5,0 ms` GPU**.
  - `gpu avg` global tombe de `48,78 ms` à **`29,70 ms`** (**`23,3–24,8 FPS`** *malgré `~5,6 ms` d'instrumentation `perf` par frame*), avec rendu net vérifié dans [benchF_1280_sc2_blit.png](file:///C:/Users/shlom/Downloads/DKB-Recomp/captures/benchF_1280_sc2_blit.png).
- **Incident résolu (`PID 12304`)** :
  - Au premier test non instrumenté, une instance oubliée de `dkb.exe` (`PID 12304`) tournait en arrière-plan, divisant les performances (`13,0 FPS`, mémoire résidente `659 MiB`) et verrouillant le binaire sur disque. Instance fermée par l'utilisateur avant relance.
- **Mesure `Bench G` (sans `TOTK_TRACE=perf`)** :
  - **`40,1 FPS` moyens** (`1% low 31,2 FPS`, pire trame `34,9 ms`, **`0` trame > 50 ms**).

---

### Build #5 — Bypass SMAA (`SMAA_BYPASS`), décimation cubemap (`CUBEMAP_RATE`) et campagne Pacing/Thread (`Bench H1` à `K3`)
- **Analyse préalable (`passes.txt`, 106 passes)** :
  - `pass 0008..0015` : 8 passes de génération mipmap cubemap (`nvn2 cd628627047f397a`, `128x128` -> `1x1`).
  - `pass 0090..0092` : 3 passes SMAA (`3c050d9686cf358a`, `5ea510329f353dba`, `1daec4428216177b`).
- **Technique appliquée** :
  - [cfg.c](file:///C:/Users/shlom/.gemini/antigravity/brain/1c73a8f1-de39-4dda-8cb2-3cdbd1dfbc49/scratch/DKB-Setup-src/DKB-Setup/runtime/cfg.c) : ajout de `CUBEMAP_RATE` (`0..8`) et `SMAA_BYPASS` (`0|1`).
  - [vk_exec.h](file:///C:/Users/shlom/.gemini/antigravity/brain/1c73a8f1-de39-4dda-8cb2-3cdbd1dfbc49/scratch/DKB-Setup-src/DKB-Setup/runtime/vk_exec.h#L134) & [vk_exec.c](file:///C:/Users/shlom/.gemini/antigravity/brain/1c73a8f1-de39-4dda-8cb2-3cdbd1dfbc49/scratch/DKB-Setup-src/DKB-Setup/runtime/vk_exec.c#L615) : exposition de `vk_exec_resolve_targets()`.
  - [vk_exec_draw.c](file:///C:/Users/shlom/.gemini/antigravity/brain/1c73a8f1-de39-4dda-8cb2-3cdbd1dfbc49/scratch/DKB-Setup-src/DKB-Setup/runtime/vk_exec_draw.c#L3696-L3757) : `smaa_bypass_draw()` saute détection de bords et calcul de poids, remplace la passe de mélange (`1daec4428216177b`) par un `vkCmdCopyImage`/`vkCmdBlitImage` direct de `fs tex 0` vers `color[0]`, puis appelle `vk_texture_gpu_written`. `post_fx_skip()` décime `cd628627047f397a` selon `CUBEMAP_RATE`.
- **Incidents rencontrés et corrigés** :
  - **Problème #3 — Écran noir (`Bench H1`)** : l'ajout de `afa38b930769e645` (`pass 0041` / affichage final) dans `TOTK_SKIP_FS` donnait une image noire `(0,0,0,0)`. → Retiré dès **Bench H2**.
  - **Problème #4 — Purges ASTC et crash config `perf`** : `tex_vram_pressure = 55` provoquait `201,7 ms` de ré-uploads ASTC malgré `tex_uma_host = 1` → relevé à **`88`** ; et `TOTK_TRACE=perf` plantait faute de ligne par défaut pour `TOTK_PERF_AFTER_FRAME` dans `cfg.c` ([vk_sync.c](file:///C:/Users/shlom/.gemini/antigravity/brain/1c73a8f1-de39-4dda-8cb2-3cdbd1dfbc49/scratch/DKB-Setup-src/DKB-Setup/runtime/vk_sync.c#L154)) → contourné par `TOTK_PERF_AFTER_FRAME=0` en benchmark.
- **Campagne Pacing / Threads / Frame Gen (`Bench H3` → `K3`)** :
  - **`Bench H3` vs `Bench I1` (`TOTK_REALTIME=1`)** : sans `realtime = 1`, [nvn_api_obj.c](file:///C:/Users/shlom/.gemini/antigravity/brain/1c73a8f1-de39-4dda-8cb2-3cdbd1dfbc49/scratch/DKB-Setup-src/DKB-Setup/runtime/nvn_api_obj.c#L729-L732) dormait `20,3 ms/frame` dans `pacing` (`25%` du temps) au verrou 2 vsyncs. Activer `TOTK_REALTIME=1` + passer de `fsr` (`+5,7 ms`) à `bilinear` a abaissé `pacing` à **`0%`** (`33,0 -> 37,3 FPS`).
  - **`Bench I2` (`TOTK_REPLAY_THREADS=6`)** : par défaut à `0` sur AMD dans [vk_exec.c](file:///C:/Users/shlom/.gemini/antigravity/brain/1c73a8f1-de39-4dda-8cb2-3cdbd1dfbc49/scratch/DKB-Setup-src/DKB-Setup/runtime/vk_exec.c#L1915), forcer `6` threads sur les 6 cœurs Zen 3 a découpé 185–194 passes en ~1050 slices, réduisant le replay (`11,21 -> 9,95 ms`) et montant le `1% low` de **`22,0` à `25,3 FPS`** (`45,2 FPS` moyens sur 54 s).
  - **`Bench J1` (`TOTK_REPLAY_ASYNC=1` + `NX2_READ_NOWAIT=1`)** : rejeté, l'attente de drain (`6%`) et les attentes de lots (`7,57 ms` vs `1,83 ms`) baissaient le `1% low` à `19,1 FPS`.
  - **`Bench K1` (`scene_res=2.5`)** : rejeté (`873x491` ratait `mvk_upscale_blit`, `gpu avg` doublé à `38,9 ms`, `21,7 FPS`).
  - **`Bench K3` (`scene_res=1.5` + `frame_gen=2x`)** : GPU plafonnait à `26,3 ms` → seulement `27,4 -> 54,7 FPS`.
  - **`Bench K2` (`scene_res=2.0`, `fps_limit=30`, `frame_gen=2x`, `realtime=1`, `bilinear`)** : **`30,0 -> 60,0 FPS`** verrouillés (`hitch 0`, `gpu 20,2 ms`, `vram 419 MiB`).
  - **Problème #5 — `upscaler = fsr` + `frame_gen = 2x` (`final_verify` vs `final_verify2`)** : en `1280x720`, `fsr` + `frame_gen = 2x` montait la VRAM à `446 / 486 MiB` et faisait chuter à `21,9 -> 43,8 FPS`. Le passage à `bilinear` a ramené la VRAM à `418 MiB` et rétabli `30,0 -> 60,0 FPS`.

---

### Build #6 & #7 — Suppression des bandes lumineuses et correction du zoom 1,5x (`Tests Z1` à `Z4`)
> Incident signalé par l'utilisateur après inspection visuelle ([media_1794872606621_f90da8fa.jpg](file:///C:/Users/shlom/.gemini/antigravity/brain/1c73a8f1-de39-4dda-8cb2-3cdbd1dfbc49/.user_uploaded/media_1794872606621_f90da8fa.jpg)) : apparition de bandes lumineuses verticales et image fortement zoomée ne montrant pas tout l'écran d'origine.

- **Problème #6 : Bandes lumineuses verticales (`skip_fs`)**
  - **Cause** : filtrer les passes de bloom/flou (`493de5886aceff57`, `2dd2dad8e143d196`, `3fdb47eab58f60c2`, `a9952cdf3061209e`) dans `skip_fs` laissait des tampons intermédiaires corrompus ensuite réinjectés en stries lumineuses verticales dans la passe finale (`pass 0072`).
  - **Solution** : suppression définitive de `skip_fs` dans [dkb.ini](file:///C:/Users/shlom/Downloads/DKB-Recomp/dkb.ini). Vérifié dès **Test Z1** : disparition à 100 % des bandes lumineuses.
- **Problème #7 : Cadrage zoomé 1,5x (`output_res = 1280x720` et `scene_res = 2.0`)**
  - **Preuve par captures comparatives** :
    - `1280x720` + `scene_res = 2.0` → **zoomé 1,5x** ([f01518.png](file:///C:/Users/shlom/.gemini/antigravity/brain/1c73a8f1-de39-4dda-8cb2-3cdbd1dfbc49/scratch/shots_final2/f01518.png)).
    - `1280x720` + `scene_res = auto` (**Test Z3**) → **toujours zoomé 1,5x** ([f01550.png](file:///C:/Users/shlom/.gemini/antigravity/brain/1c73a8f1-de39-4dda-8cb2-3cdbd1dfbc49/scratch/shots_z3/f01550.png)) ! Sur Bananza 3.2.0 avec `dkbwide`, même `output_res = 1280x720` recadrait la scène 3D dans les `2/3` supérieurs gauches.
    - **`output_res = 1920x1080` + `scene_res = auto`** → **aucun zoom, plein cadrage complet 16:9** ([f01441.png](file:///C:/Users/shlom/.gemini/antigravity/brain/1c73a8f1-de39-4dda-8cb2-3cdbd1dfbc49/scratch/shots_vanilla/f01441.png) et [f01487.png](file:///C:/Users/shlom/.gemini/antigravity/brain/1c73a8f1-de39-4dda-8cb2-3cdbd1dfbc49/scratch/shots_z1/f01487.png)).
- **Diagnostic et optimisations finales (`Build #6` & `Build #7`)** :
  - **Build #6** (`Test Z1`/`Z2`) : ajout du shader `0x02884179c98d49e6ull` dans `mvk_upscale_cs()` ([vk_exec_draw.c](file:///C:/Users/shlom/.gemini/antigravity/brain/1c73a8f1-de39-4dda-8cb2-3cdbd1dfbc49/scratch/DKB-Setup-src/DKB-Setup/runtime/vk_exec_draw.c#L3925-L3929)) ; en `1920x1080` `auto`, le jeu utilise en fait un quad bilinéaire léger (`pass 0087`) et atteignait `25,9–27,1 -> 51,5–54,2 FPS`.
  - **Dump `frame 1300` en `1920x1080 auto`** : découverte que la passe cubemap dynamique **`pass 0005`** (`128x128`, `6` layers) exécutait encore **246 draws à chaque trame** sans être couverte par `CUBEMAP_RATE`.
  - **Build #7** : extension de `resolve_rt()` dans [vk_exec.c](file:///C:/Users/shlom/.gemini/antigravity/brain/1c73a8f1-de39-4dda-8cb2-3cdbd1dfbc49/scratch/DKB-Setup-src/DKB-Setup/runtime/vk_exec.c#L599-L618) pour décimer également `pass 0005` (`128x128`, `layers == 6`, `ex->pass_depth`) selon `(f / 6) % cube_rate != 0` dès `f >= 120` (`cubemap_rate = 4`).
- **Validation finale actuelle (`Test Z4` — [z4_verify.log](file:///C:/Users/shlom/.gemini/antigravity/brain/1c73a8f1-de39-4dda-8cb2-3cdbd1dfbc49/scratch/z4_verify.log))** :
  - `selftest: passed (0 failures)`, `boot: passed` (`1474` trames exécutées, `0` erreur de validation Vulkan, `0` échec shader).
  - Capture vérifiée visuellement : [f01424.png](file:///C:/Users/shlom/.gemini/antigravity/brain/1c73a8f1-de39-4dda-8cb2-3cdbd1dfbc49/scratch/shots_z4/f01424.png) — image 1080p nette, cadrage complet sans zoom, aucune bande verticale.
  - VRAM stabilisée : **`436 / 486 MiB`**.
  - Performances avec `frame_gen = 2x` : **58,2–60,0 FPS affichés** (`29,1–30,0 FPS` réels) en jeu normal, et **52,8–53,8 FPS affichés** (`26,4–26,9 FPS` réels) au pic de l'éboulement lourd.

---

## 5. Tableau récapitulatif complet des résultats mesurés

| Phase / Benchmark | Build & Configuration clé | Résolution / Cadrage | FPS réels -> affichés (ou natifs) | VRAM (`device-local`) | Observation / État visuel |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **1er lancement 3D** | Stock + `frame_gen=2x`, `1080p`, `vram=75` | 1920x1080 | `5,6–8,8 FPS` | `488 / 486 MiB` | Saturation VRAM + swap Windows `9–12 Go` |
| **Baseline stock optimisée** | Stock `dkb.ini` (`FG=off`, `vram=55`, `astc_bc=1`) | 1280x720 | `18,4–22,4 FPS` (`1% low 19,0`) | `445 / 486 MiB` | Propre mais limité à `~22 FPS` (`35 ms` GPU) |
| **Test CPU pur** | `DKB_SKIP_DRAWS=1` (`0` draw graphique) | — | `40,1–50,1 FPS` | — | Mesure du plafond CPU (`14,3 ms`) + computes (`10,4 ms`) |
| **Bench D (Build #2)** | `walk()` shadow skip (`rate=6`), `skip_fs`, `sc=2.0` | 1280x720 (`sc=2.0`) | `15,4 FPS` *(avec `TRACE=perf`)* | `461 / 486 MiB` | Saturation WDDM + upscale compute à `17,6 ms` |
| **Bench F (Build #4)** | + `TEX_UMA_HOST=1`, sans-verrou, `MVK_BLIT=1` | 1280x720 (`sc=2.0`) | `23,3–24,8 FPS` *(avec `TRACE=perf`)* | `408 / 486 MiB` | Upscale `20,4 ms -> 3–5 ms`, VRAM sous seuil WDDM |
| **Bench G (Build #4)** | Idem sans `TOTK_TRACE=perf` | 1280x720 (`sc=2.0`) | `40,1 FPS` (`1% low 31,2`) | `408 / 486 MiB` | Aucune trame > `50 ms`, zoom 1,5x + stries bloom |
| **Bench I2 (Build #5)** | + `SMAA_BYPASS=1`, `CUBE=4`, `REALTIME=1`, `THREADS=6` | 1280x720 (`sc=2.0`) | `37,5 FPS` lourd / `45,2` moy. 54s | `410 / 486 MiB` | Pacing supprimé (`25% -> 0%`), zoom 1,5x + stries |
| **Bench K2 (Build #5)** | + `FPS_LIMIT=30`, `FRAME_GEN=2x`, `bilinear` | 1280x720 (`sc=2.0`) | `30,0 -> 60,0 FPS` (`hitch 0`) | `419 / 486 MiB` | 60 FPS verrouillés, mais zoom 1,5x + stries bloom |
| **Test Z3 (Build #6)** | `1280x720`, `scene_res=auto`, `skip_fs` retiré, `FG=2x` | 1280x720 (`auto`) | `29,7–30,0 -> 59,4–59,5 FPS` | `408 / 486 MiB` | 0 bande lumineuse, mais toujours zoom 1,5x |
| **Test Z4 (Build #7, actuel)** | `1920x1080`, `scene_res=auto`, `CUBE=4 (pass 5)`, `FG=2x` | **1920x1080 (`auto`)** | **26,4–30,0 -> 52,8–60,0 FPS** | **`436 / 486 MiB`** | **Plein cadrage complet, net, 0 bande lumineuse** |

---

## 6. Inventaire des fichiers modifiés et configuration active

### Fichiers sources modifiés dans [runtime](file:///C:/Users/shlom/.gemini/antigravity/brain/1c73a8f1-de39-4dda-8cb2-3cdbd1dfbc49/scratch/DKB-Setup-src/DKB-Setup/runtime) et `tools/`
- `dkb_wide.c` : support `output_res` sous 720p et `scene_res` jusqu'à `4.0`.
- `cfg.c` : ajout des paramètres `TEX_UMA_HOST`, `SMAA_BYPASS`, `CUBEMAP_RATE`, `SHADOW_RATE`, `TEX_FRAME_EPOCH`.
- `vk_texture.c` : placement UMA hôte `heap 1` (`TEX_UMA_HOST`) pour éviter la saturation `DEVICE_LOCAL`, et cache d'époque par image (`TEX_FRAME_EPOCH`).
- `vk_exec.h` & `vk_exec.c` : exposition `vk_exec_resolve_targets()`, court-circuit des draws d'ombres décimées dans `walk()`/`par_walk()`, décimation `SHADOW_RATE`, et décimation de la passe cubemap `pass 0005` (`128x128`, 6 layers) via `CUBEMAP_RATE`.
- `vk_exec_draw.c` : lecture sans verrou `tex_info_hit()` sur cache hit, extension de `SkipList` à `64` entrées (`draw` + `dispatch`), `smaa_bypass_draw()` (copie/blit direct remplaçant SMAA), `post_fx_skip()` pour les mipmaps cubemap, et déblocage de `mvk_upscale_blit()` sur AMD avec hashes `0xe27e4707534b74e8`, `0x3582d55d1149d49b` et `0x02884179c98d49e6`.
- `vk_sync.c` & `tools/build_game.py` : support `TOTK_PERF_AFTER_FRAME` et drapeaux de compilation `-O3 -march=znver3 -mtune=znver3`.

### Paramètres actifs dans [dkb.ini](file:///C:/Users/shlom/Downloads/DKB-Recomp/dkb.ini)
- `[frame rate]` : `fps_limit = 30`, `realtime = 1`
- `[performance]` : `astc = gpu`, `astc_bc = 1`, `tex_vram_pressure = 88`, `tex_uma_host = 1`, `pool_fini_wait = fence`, `replay_threads = 4`, `mvk_upscale_blit = 1`, `smaa_bypass = 1`, `shadow_rate = 6`, `cubemap_rate = 4`, `split_draws = 64`, `split_us = 1000`
- `[display]` : `vk_present = immediate`, `window_size = 1920x1080`, `window_mode = borderless`, `fullscreen = 1`, `output_res = 1920x1080`, `upscaler = fsr` *(inactif tant que `output_res == window_size`)*, `scene_res = auto`, `smaa = off`, `frame_gen = 2x`, `perf_overlay = fps`

---

## 7. Journal des évolutions futures

### 2026-11-17 — Mise en ligne sur dépôt GitHub privé (`shlomoe26/dkb-recomp-vega7`)
- **Dépôt** : `https://github.com/shlomoe26/dkb-recomp-vega7` (**privé**, branche `main`, commit initial `f154f7f`).
- **Dossier Git local** : [dkb-recomp-vega7](file:///C:/Users/shlom/Downloads/dkb-recomp-vega7).
- **Contenu versionné (`788` fichiers, `46,03 Mo` avant compression Git)** :
  - Sources C/Vulkan modifiées (`runtime/`, sans `runtime/deps/`), outils et scripts de recompilation (`tools/`, `recomp/`, `installer/`, `licenses/`).
  - Configuration vérifiée ([dkb.ini](file:///C:/Users/shlom/Downloads/dkb-recomp-vega7/dkb.ini)), lanceur ([Jouer_DKB_Natif.bat](file:///C:/Users/shlom/Downloads/dkb-recomp-vega7/Jouer_DKB_Natif.bat)), journal technique (`JOURNAL_OPTIMISATIONS_DKB.md`), script d'entrées (`scripts/input_play.txt`), logs (`benchmarks/`) et captures représentatives (`captures/`, incluant [bug_user_bandes_zoom.jpg](file:///C:/Users/shlom/Downloads/dkb-recomp-vega7/captures/bug_user_bandes_zoom.jpg) et [test_z4_1080_final_f01424.png](file:///C:/Users/shlom/Downloads/dkb-recomp-vega7/captures/test_z4_1080_final_f01424.png)).
  - Exclusions via `.gitignore` : binaires générés `>100 Mo` (`dkb.exe` `~193 Mo`), données/caches du jeu (`romfs/`, `exefs/`, `aoc-1/`, `shader-cache/`, `*.bin`), sauvegarde personnelle (`profile/`) et toolchains (`llvm/`, `python/`, `runtime/deps/`, `dkb-custom-build/`).
- **Note espace disque** : nettoyage des captures intermédiaires redondantes dans le scratch (`~62,5 Mo` restants sur `C:` après création du dépôt).

### 2026-11-17 — Builds #8 & #9 : Optimisation de stabilité sans perte de qualité (`Test Z5b`)
- **Objectif** : réduire les micro-saccades et les temps morts CPU/GPU/VRAM tout en conservant exactement le rendu **1080p `scene_res = auto`** sans baisse visuelle.
- **Diagnostic (`perf_z4_diag.log` + `z4_verify.log`)** :
  - `fg_pace_over_refresh()` (seuil initial `1.05x`, soit `63 Hz` / `31,75 ms`) jetait **20 à 48 images générées par bloc de 5 s** dès la moindre variation autour de 30 FPS (`shown` chutait à `47 FPS`).
  - `pool_fini_wait = idle` bloquait la file Vulkan (`vkQueueWaitIdle`, `65 ms` sur les transitions de zone) et le seuil `TEX_UMA_HOST` à `78%` laissait la VRAM monter jusqu'à `451–455 / 486 MiB` (seuil de pagination WDDM).
  - Avec `replay_threads = 6`, le thread principal attendait `103,9 ms` sur ses workers avec `83,0 ms` de contention sur le verrou texture (`6` workers + threads jeu sur 6 cœurs physiques).
- **Campagne A/B sans perte visuelle** :
  - *Rejetés* : `tex_uma_host = 2` (**Stab 1**, trop de textures sorties de la VRAM rapide : chute à `21,0 FPS`), `replay_async = 1` + `heap_lazy = 0` (**Stab 2**, commit RAM monté à `11,5 Go` et `136` trames > `50 ms`), `sync_nowait_wb` (**Bench L1**, `0 FPS` gagné et spam log `write-back kept`), `replay_threads = 6` + `split = 16/100` (**Bench L4**, `141` trames > `50 ms`, pic `1013 ms`).
  - *Retenus (Build #8 & #9)* :
    1. [fg_pace.h](file:///C:/Users/shlom/.gemini/antigravity/brain/1c73a8f1-de39-4dda-8cb2-3cdbd1dfbc49/scratch/DKB-Setup-src/DKB-Setup/runtime/fg_pace.h#L23-L29) : marge `fg_pace_over_refresh` portée de `1.05` à **`1.35`** (évite les faux `over refresh` autour de 30 FPS).
    2. [vk_texture.c](file:///C:/Users/shlom/.gemini/antigravity/brain/1c73a8f1-de39-4dda-8cb2-3cdbd1dfbc49/scratch/DKB-Setup-src/DKB-Setup/runtime/vk_texture.c#L538-L539) : seuil de délestage `TEX_UMA_HOST` abaissé de `78%` à **`65%`** pour maintenir la VRAM `DEVICE_LOCAL` sous le seuil WDDM.
    3. [dkb.ini](file:///C:/Users/shlom/Downloads/DKB-Recomp/dkb.ini#L68-L106) : ajout de **`pool_fini_wait = fence`**, passage à **`replay_threads = 4`** et **`split_draws = 64`**, **`split_us = 1000`**.
- **Résultats vérifiés (`--selftest` 0 échec, capture [z5_check.png](file:///C:/Users/shlom/.gemini/antigravity/brain/1c73a8f1-de39-4dda-8cb2-3cdbd1dfbc49/scratch/z5_check.png), **Test Z5b** sans `--shot` en priorité Haute)** :
  - `over refresh` en jeu tombé à **`0`** sur toute la partie après l'intro (`60,0 FPS` fixes en jeu calme, `55,7–56,3 FPS` en transition tunnel, `46,6–47,6 FPS` au pic de la caverne lourde).
  - VRAM stabilisée à **`431 / 486 MiB`** (au lieu de `451–455 MiB`), pire pic de chargement abaissé de **`963,3 ms` (`Test Z4`) à `592,9–783,7 ms`** (`pool release wait` `21–41 ms` vs `65 ms`).
  - Limite matérielle restante sans toucher à la qualité : la bande passante ASTC lors du changement de zone (`~38 M texels` décodés d'un coup) et la charge shader 1080p dans l'éboulement profond (`~23–24 FPS` réels).

### 2026-11-17 (après-midi) — Intégration de l'icône complète DK + Pauline (`runtime/dkb.ico`)
- Remplacement de l'icône d'origine (`62 758` octets, banane dorée) dans [dkb.ico](file:///C:/Users/shlom/Downloads/dkb-recomp-vega7/runtime/dkb.ico) et `DKB-Setup/runtime/dkb.ico` par l'icône complète DK + Pauline (`230 271` octets, `6` résolutions `16x16` à `256x256` 32 bits RGBA).
- Recompilation de la ressource [totk.rc](file:///C:/Users/shlom/Downloads/dkb-recomp-vega7/runtime/totk.rc) et édition de liens dans [dkb.exe](file:///C:/Users/shlom/Downloads/DKB-Recomp/dkb.exe) (`.rsrc 0.2 MiB`, `compile: 1.1 s`, `link: 3.7 s`).
- Vérification `dkb.exe --selftest` : `passed (0 failures)` (`EXIT=0`), puis synchronisation sur `shlomoe26/dkb-recomp-vega7`.

### 2026-11-17 (soir) — Remplacement de l'icône par `dk_punch_carre_fond_final.ico`
- Remplacement de [dkb.ico](file:///C:/Users/shlom/Downloads/DKB-Recomp/dkb.ico), `DKB-Setup/runtime/dkb.ico` et [runtime/dkb.ico](file:///C:/Users/shlom/Downloads/dkb-recomp-vega7/runtime/dkb.ico) par `dk_punch_carre_fond_final.ico`.
- Recompilation de `totk.rc` (`1,4 s`) et édition de liens dans [dkb.exe](file:///C:/Users/shlom/Downloads/DKB-Recomp/dkb.exe) (`1,8 s`), vérifié par `--selftest` (`0` échec).

### 2026-11-18 — Icône DK Punch avec fond carré arrondi jaune doré (`dkb.ico`)
- Recolorisation du fond gris foncé de `dk_punch_carre_fond_final.ico` vers un dégradé jaune doré (`#FFDC20 → #F7B600`) en conservant la transparence du carré arrondi et les contours de DK, exporté en `7` résolutions (`16` à `256` px RGBA) vers [dkb.ico](file:///C:/Users/shlom/Downloads/DKB-Recomp/dkb.ico), `DKB-Setup/runtime/dkb.ico` et [runtime/dkb.ico](file:///C:/Users/shlom/Downloads/dkb-recomp-vega7/runtime/dkb.ico).
- Recompilation de `totk.rc` (`1,4 s`), édition de liens dans [dkb.exe](file:///C:/Users/shlom/Downloads/DKB-Recomp/dkb.exe) (`1,7 s`) et vérification `--selftest` (`0` échec), puis synchronisation sur `shlomoe26/dkb-recomp-vega7`.

### 2026-11-25 — Nouvelle icône officielle pleine `dk_bananza_icone_plein.png` (`dkb.ico`)
- Conversion de `dk_bananza_icone_plein.png` (1024x1024 RGBA) vers `dkb.ico` (207 107 octets, 7 résolutions de 16x16 à 256x256 px).
- Déploiement dans `C:\Users\shlom\Downloads\DKB-Recomp\dkb.ico`, `DKB-Setup\runtime\dkb.ico` et `dkb-recomp-vega7\runtime\dkb.ico`.
- Recompilation de la ressource `totk.rc` et réédition des liens de `dkb.exe` via Clang/LLD/Ninja (202 225 664 octets, `.rsrc 0.2 MiB`).
- Raccourci Windows `Donkey Kong Bananza.lnk` réassigné vers la nouvelle icône et cache d'icônes rafraîchi.
- Vérification `dkb.exe --selftest` : `passed (0 failures)`.

*(Les prochaines compilations, correctifs, optimisations et benchmarks seront ajoutés à la suite ci-dessous.)*
