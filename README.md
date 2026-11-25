# Donkey Kong Bananza PC Recompilation — Low-End PC & Integrated GPU (No Dedicated GPU Required)

🌐 **Languages**: **English** | [Français (README.fr.md)](README.fr.md)

An optimized, beginner-friendly, **one-click Windows installer & 3-second fast updater** for the native PC static recompilation port of **Donkey Kong Bananza** (`dkb-pc-recomp`).  
Delivering smooth **1080p 50–60 FPS** gameplay on modest laptops and **integrated graphics (iGPUs) without a dedicated GPU**.

> **Legal Notice**: This repository and its Releases contain **NO copyrighted Nintendo files** (no game code, no ExeFS, no RomFS, no decryption keys). You must provide your own legally dumped copy of the game (`.nup` file or extracted `ExeFS` + `RomFS` folders).

---

## Who is this project for?

This edition is built for players looking for:
- **Donkey Kong Bananza PC recompilation** tuned for performance first.
- **Playing without a dedicated GPU** (no NVIDIA RTX / AMD RX card required).
- **Low-end PC gaming** on thin laptops, budget desktops, and mini-PCs.
- **Intel integrated graphics** (Intel Iris Xe, Intel UHD Graphics).
- **AMD integrated graphics** (AMD Radeon Vega 7, Vega 8, Radeon 680M/780M).
- **Shared GPU memory optimization** (UMA laptop memory tuning).
- **Low VRAM optimization** (4× smaller texture footprint via ASTC→BC3).
- **Vulkan performance optimization** & built-in 2× Frame Generation.

> *If you have a powerful dedicated GPU (RTX / RX) and want maximum raw visual fidelity, use the upstream [`dkb-pc-recomp`](https://github.com/Lucas-blip-png/dkb-pc-recomp) project instead.*

---

## Real Benchmarks (Measured)

Tested on a real thin-and-light laptop with **no dedicated GPU**:
- **CPU**: AMD Ryzen 5 7530U (Zen 3, 6 cores / 12 threads)
- **iGPU**: AMD Radeon Vega 7 (7 CU, 486 MiB local Vulkan budget, 16 GB RAM single-channel)
- **Game Version**: Donkey Kong Bananza `3.2.0` (`dkb458752`)

| Scenario (1080p) | Stock Defaults | Low-Spec Edition (`v1.0.0`) | VRAM Usage |
| :--- | :--- | :--- | :--- |
| **Title / Menus** | 46–53 FPS | **46–60 FPS** | ~345 MiB |
| **Calm 3D Gameplay** | 5.6–8.8 FPS (VRAM full) | **60.0 FPS** (`over refresh = 0`) | **431 / 486 MiB** |
| **Tunnel Transition** | Heavy stutter | **55.7–56.3 FPS** | ~431 MiB |
| **Heavy Cavern Peak** | 3.5–5.6 FPS | **46.6–47.6 FPS** (~23–24 FPS internal × 2× FG) | ~431 MiB |

### iGPU Comparison & Reporting Status

| Integrated GPU (iGPU) | Status | Measured / Expected Performance |
| :--- | :--- | :--- |
| **AMD Radeon Vega 7 (Ryzen 5 7530U)** | **Tested & Verified** | **1080p, 47–60 FPS** (FG 2×), ~431 MiB VRAM |
| **AMD Radeon Vega 8** | Theoretically compatible | Expected similar or slightly faster than Vega 7 *(community reports welcome)* |
| **Intel Iris Xe** | Theoretically compatible | Vulkan 1.3 + `x86-64-v3` supported *(community reports welcome)* |
| **Intel UHD 620 / 630** | Theoretically compatible | Lower internal res recommended (`720p` / `960×540`) *(untested)* |
| **Steam Deck (RDNA 2 APU)** | Theoretically compatible | `x86-64-v3` + Vulkan 1.3 compatible *(Windows tested; Linux upstream)* |

---

## Compatibility Matrix

| Hardware / OS | Category | Status | Notes |
| :--- | :--- | :--- | :--- |
| **Windows 10 / 11 (64-bit) + AMD Vega 7** | **Tested & Verified** | Working | Full playthrough start, saves, `dkb.exe --selftest` 0 failures |
| **Windows 10 / 11 + Modern Intel/AMD x86-64-v3 + Vulkan 1.3** | **Theoretically Compatible** | Ready | Runtime compiled with portable `-O3 -march=x86-64-v3` |
| **Community iGPUs (Iris Xe, UHD, Vega 8, 680M/780M)** | **User Reports Needed** | Open | Share your FPS/VRAM results in GitHub Issues! |

---

## Key Optimizations Included

| Feature | Setting / Tech | Benefit on Low-End / iGPU |
| :--- | :--- | :--- |
| **Universal CPU Build** | `-O3 -march=x86-64-v3` | Compatible with all modern Intel & AMD CPUs (Haswell / Ryzen+) |
| **ASTC to BC3 Compression** | `astc = gpu`, `astc_bc = 1` | **4× less VRAM & memory bandwidth** for textures |
| **UMA / Shared VRAM Tuning** | `tex_uma_host = 1`, `tex_vram_pressure = 88`, `pool_fini_wait = fence` | Eliminates shared-memory stutters and VRAM overflow |
| **Smart GPU Lightening** | `shadow_rate = 6`, `cubemap_rate = 4`, `smaa_bypass = 1`, `mvk_upscale_blit = 1` | Huge iGPU frame-time savings |
| **Multi-Threaded Replay** | `replay_threads = 4` | Splits Vulkan command recording across 4 CPU threads |
| **Frame Generation 2×** | Built-in `fg_pace` + `fps_limit = 30` + `realtime = 1` | Smooth **50–60 FPS** output at 1080p |
| **Desktop Ready** | Auto `dkb.ini`, `Jouer_DKB_Natif.bat`, `dkb.ico`, `.lnk` shortcut | High CPU priority launcher & custom icon created automatically |
| **3-Second Fast Updates** | `.update-cache/` + `Mettre_a_jour_DKB.bat` | Updates download only ~8.4 MB and relink in ~3 seconds |

---

## How to Install (From Scratch in 1 Click)

1. Download **`DKB-LowSpec-Setup-v1.0.0.exe`** (~83.7 MB) from [**Releases**](https://github.com/evolis-game/donkey-kong-bananza-pc-lowspec/releases).
2. Double-click **`DKB-LowSpec-Setup-v1.0.0.exe`** *(if SmartScreen warns, click More info → Run anyway)*.
3. A progress window unpacks the tools, then opens the installer (`FR` / `EN` / `RU` supported).
4. Select:
   - Your **`.nup`** file *(or tick **Advanced** to select existing `ExeFS` and `RomFS` folders)*
   - Your **Game language**
   - Your **Install folder**
5. Click **Install**. Once finished, launch **`Donkey Kong Bananza`** (shortcut) or **`Jouer_DKB_Natif.bat`**.

---

## How to Update (3-Second Fast Updater)

No `.nup` file or 45-minute recompile needed:
1. Double-click **`Mettre_a_jour_DKB.bat`** in your game folder.
2. It downloads the latest `dkb-lowspec-patch-*.zip` (~8.4 MB), merges new settings into `dkb.ini` **while keeping your language**, relinks `dkb.exe` in **~3 seconds** using `.update-cache/`, and runs `dkb.exe --selftest`.
