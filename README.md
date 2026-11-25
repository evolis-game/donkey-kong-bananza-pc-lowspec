# Donkey Kong Bananza — Low-Spec & iGPU PC Edition

🌐 **Languages**: **English** | [Français (README.fr.md)](README.fr.md)

An optimized, beginner-friendly, **one-click installer & fast updater** for the native PC static recompilation port of **Donkey Kong Bananza** (`dkb-pc-recomp`).  
Specifically tuned for **low-end PCs, laptops, handhelds, and integrated GPUs (iGPUs)** such as **AMD Radeon Vega 7 / Vega 8, Ryzen 5 7530U, Intel Iris Xe, and Steam Deck**, delivering smooth **1080p 50–60 FPS** gameplay with minimal VRAM usage.

> **Legal Notice**: This repository and its Releases contain **NO copyrighted Nintendo files** (no game code, no ExeFS, no RomFS, no keys). You must provide your own legally dumped copy of the game (`.nup` file or dumped `ExeFS` + `RomFS` folders).

---

## Table of Contents
1. [Why This Edition? (Key Optimizations)](#-why-this-edition-key-optimizations)
2. [System Requirements](#-system-requirements)
3. [How to Install (From Scratch in 1 Click)](#-how-to-install-from-scratch-in-1-click)
4. [How to Play](#-how-to-play)
5. [How to Update (3-Second Fast Updater)](#-how-to-update-3-second-fast-updater)
6. [Configuration & Tweaking (`dkb.ini`)](#-configuration--tweaking-dkbini)
7. [Troubleshooting / FAQ](#-troubleshooting--faq)

---

## Why This Edition? (Key Optimizations)

Standard builds can stutter, run out of shared VRAM, or struggle to reach 30 FPS on integrated graphics. This edition pre-configures and compiles all low-spec optimizations automatically:

| Feature | Setting / Tech | Benefit on Low-End / iGPU |
| :--- | :--- | :--- |
| **Universal CPU Build** | `-O3 -march=x86-64-v3` | Works out-of-the-box on all modern Intel & AMD CPUs (2015+) |
| **ASTC to BC3 Compression** | `astc = gpu`, `astc_bc = 1` | **4× less VRAM & memory bandwidth** used for textures |
| **UMA / Shared VRAM Tuning** | `tex_uma_host = 1`, `tex_vram_pressure = 88`, `pool_fini_wait = fence` | Prevents crashes and micro-stutters on laptops with shared memory |
| **Smart Visual Lightening** | `shadow_rate = 6`, `cubemap_rate = 4`, `smaa_bypass = 1`, `mvk_upscale_blit = 1` | Huge GPU savings with minimal visual impact |
| **Multi-Threaded Replay** | `replay_threads = 4` | Splits Vulkan draw recording across 4 CPU threads |
| **Frame Generation 2×** | Built-in `fg_pace` + `fps_limit = 30` + `realtime = 1` | Smooth **50–60 FPS** output at 1080p on Vega 7 |
| **Ready-to-Play Desktop Setup** | Auto `dkb.ini`, `Jouer_DKB_Natif.bat`, `dkb.ico`, `.lnk` shortcut | High CPU priority launcher & high-res icon created automatically |
| **3-Second Fast Updates** | `.update-cache/` + `Mettre_a_jour_DKB.bat` | Updates download only ~8–25 MB and relink in 3 seconds |

---

## System Requirements

- **OS**: Windows 10 / Windows 11 (64-bit)
- **CPU**: Any x86-64-v3 CPU (Intel Haswell / 4th Gen+ or AMD Ryzen / Excavator+)
- **GPU**: Vulkan 1.3 compatible GPU (AMD Radeon Vega 7/8, RDNA, Intel Iris Xe, NVIDIA GTX/RTX)
- **RAM**: 16 GB recommended (or 8 GB + large Windows pagefile)
- **Disk Space**: ~15–20 GB free during installation
- **Game Input**: Your own legal `.nup` file, or dumped `ExeFS` + `RomFS` folders (Supported versions: `1.0.0` and `3.2.0`)

---

## How to Install (From Scratch in 1 Click)

1. Go to the [**Releases page**](https://github.com/evolis-game/dkb-lowspec-recomp/releases) and download **`DKB-LowSpec-Setup-vX.Y.Z.exe`** (~84 MB).
2. Double-click **`DKB-LowSpec-Setup-vX.Y.Z.exe`**. *(It extracts automatically and opens the setup window — no Python, Visual Studio, or compiler installation required!)*
3. Select:
   - Your **`.nup`** file (or your `ExeFS` + `RomFS` folders)
   - Your preferred **in-game language**
   - The **destination folder** where you want the game installed (e.g. `C:\Games\DKB-Recomp`)
4. Click **Install** and wait for the process to complete:
   - Extracts and verifies game data
   - Lifts & compiles the game code and links it with the pre-optimized `x86-64-v3` runtime
   - Translates and pre-warms shaders (prevents in-game shader stutter)
   - Applies all low-spec settings (`dkb.ini`), high-priority launcher, icon, and shortcut
5. Done!

---

## How to Play

In your installation folder, launch the game using either:
- **`Donkey Kong Bananza`** (Windows shortcut with custom icon — launches in High CPU priority)
- **`Jouer_DKB_Natif.bat`** (batch launcher with High CPU priority)

> **Tip**: Press **`F1`** in-game at any time to open the settings overlay.

---

## How to Update (3-Second Fast Updater)

You do **NOT** need your `.nup` file or to wait 45 minutes recompiling when a new optimization update is released:

1. Double-click **`Mettre_a_jour_DKB.bat`** inside your game folder.
2. It automatically:
   - Checks [GitHub Releases](https://github.com/evolis-game/dkb-lowspec-recomp/releases) for the latest version
   - Downloads only the small patch archive (`dkb-lowspec-patch-*.zip`, ~8–25 MB)
   - Merges new optimization settings into `dkb.ini` **while keeping your language & custom settings**
   - Relinks `dkb.exe` in **~3 seconds** using `.update-cache/`
   - Runs `dkb.exe --selftest` to verify everything works (`0 failures`)

*(Note: Keep the `.update-cache` folder (~207 MB) inside your game directory if you want 3-second updates.)*

---

## Configuration & Tweaking (`dkb.ini`)

All performance settings are stored in `dkb.ini` in your game folder. Key options you can adjust:
- `fps_limit = 30` (Base target; paired with built-in Frame Gen for 60 FPS display)
- `astc_bc = 1` (Set to `0` only if you have a dedicated GPU with 8+ GB VRAM and want uncompressed textures)
- `shadow_rate = 6` (Update shadows every 6 frames; lower to `2` or `1` on stronger GPUs)
- `smaa_bypass = 1` (Set to `0` to re-enable SMAA anti-aliasing on stronger GPUs)

---

## Troubleshooting / FAQ

- **Windows SmartScreen says "Windows protected your PC"**: Click **More info → Run anyway** (the executable is unsigned because it is an open-source community build).
- **Can I delete my original `.nup` file after installing?** Yes! Once the installation finishes, the game is completely self-contained in your destination folder.
- **How do I change the language later?** Open `dkb.ini` and change `lang = en-US` to your code (`fr`, `es`, `de`, `ja`, `it`, `pt-BR`, etc.).
