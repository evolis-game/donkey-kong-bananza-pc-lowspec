"""Build DKB-LowSpec release artifacts:
1. libtotkrt.a (x86-64-v3) + totk.o (icon & manifest)
2. dkb-lowspec-patch-v<VERSION>.zip (~25 MB for 3-second updates)
3. DKB-LowSpec-Setup/ portable folder + DKB-LowSpec-Setup.exe (7z SFX if 7zr & 7zSD.sfx are present)
"""
import argparse
import os
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def build_runtime_and_rc(repo: Path, setup_base: Path, out_dir: Path, gen_dir: Path | None):
    py = setup_base / 'python' / 'python.exe'
    llvm = setup_base / 'llvm'
    deps = setup_base / 'runtime' / 'deps'
    ninja = setup_base / 'bin' / 'ninja.exe'

    out_dir.mkdir(parents=True, exist_ok=True)
    cmd = [
        str(py), str(repo / 'tools' / 'build_game.py'),
        '--make-runtime-lib',
        '--out', str(out_dir),
        '--runtime', str(repo / 'runtime'),
        '--toolchain', str(llvm),
        '--deps', str(deps),
        '--ninja', str(ninja),
    ]
    if gen_dir:
        cmd += ['--gen', str(gen_dir)]
    print('Building libtotkrt.a (x86-64-v3)...')
    subprocess.run(cmd, cwd=repo, check=True)

    windres = llvm / 'bin' / 'llvm-windres.exe'
    totk_o = out_dir / 'totk.o'
    print('Compiling totk.rc -> totk.o...')
    subprocess.run([
        str(windres), '-I', str(repo / 'runtime'), '-O', 'coff',
        str(repo / 'runtime' / 'totk.rc'), '-o', str(totk_o),
    ], cwd=repo, check=True)
    return out_dir / 'libtotkrt.a', totk_o


def build_patch_zip(repo: Path, lib: Path, totk_o: Path, dest_zip: Path, version: str):
    dest_zip.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(dest_zip, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=6) as zf:
        zf.write(lib, 'libtotkrt.a')
        zf.write(totk_o, 'totk.o')
        zf.write(repo / 'dkb.ini.example', 'dkb.ini.defaults')
        zf.write(repo / 'runtime' / 'dkb.ico', 'dkb.ico')
        zf.write(repo / 'Jouer_DKB_Natif.bat', 'Jouer_DKB_Natif.bat')
        zf.writestr('VERSION', version + '\n')
    print(f'Created patch zip: {dest_zip} ({dest_zip.stat().st_size / 1024**2:.1f} MB)')


def stage_setup_folder(repo: Path, setup_base: Path, lib: Path, stage: Path, version: str, update_repo: str | None):
    if stage.exists():
        shutil.rmtree(stage)
    stage.mkdir(parents=True)

    # Copy base runtime tools from setup_base (python, llvm, bin, licenses, THIRD_PARTY_NOTICES.md)
    for d in ('python', 'llvm', 'bin', 'licenses'):
        if (setup_base / d).is_dir():
            shutil.copytree(setup_base / d, stage / d)
    for f in ('THIRD_PARTY_NOTICES.md',):
        if (setup_base / f).is_file():
            shutil.copy2(setup_base / f, stage / f)

    # Copy our customized code (installer, recomp, tools, runtime, dkb.ini.example)
    for d in ('installer', 'recomp', 'tools', 'runtime'):
        shutil.copytree(repo / d, stage / d, ignore=shutil.ignore_patterns('__pycache__', '*.pyc'))
    if (setup_base / 'runtime' / 'deps').is_dir() and not (stage / 'runtime' / 'deps').exists():
        shutil.copytree(setup_base / 'runtime' / 'deps', stage / 'runtime' / 'deps')

    shutil.copy2(lib, stage / 'runtime' / 'libtotkrt.a')
    shutil.copy2(repo / 'dkb.ini.example', stage / 'dkb.ini.example')
    (stage / 'VERSION').write_text(version + '\n', encoding='utf-8')
    if update_repo:
        (stage / 'update_repo.txt').write_text(update_repo + '\n', encoding='utf-8')

    bat = '@echo off\r\ncd /d "%~dp0"\r\nstart "" "python\\pythonw.exe" -m installer\r\n'
    (stage / 'Lancer_Installateur.bat').write_text(bat, encoding='utf-8')
    print(f'Staged portable setup folder: {stage}')


def build_sfx(stage: Path, out_exe: Path, seven_z: Path, sfx_stub: Path):
    archive_7z = out_exe.with_suffix('.7z')
    cfg = out_exe.with_suffix('.sfx.txt')
    cfg.write_text(
        ';!@Install@!UTF-8!\n'
        'Title="DKB Low-Spec Setup"\n'
        'GUIMode="2"\n'
        'RunProgram="python\\pythonw.exe -m installer"\n'
        ';!@InstallEnd@!\n',
        encoding='utf-8',
    )
    subprocess.run([str(seven_z), 'a', '-t7z', '-mx=5', '-mmt=on', str(archive_7z), '.'], cwd=stage, check=True)
    with out_exe.open('wb') as out:
        out.write(sfx_stub.read_bytes())
        out.write(cfg.read_bytes())
        out.write(archive_7z.read_bytes())
    archive_7z.unlink(missing_ok=True)
    cfg.unlink(missing_ok=True)
    print(f'Created 7z SFX installer: {out_exe} ({out_exe.stat().st_size / 1024**2:.1f} MB)')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--setup-base', type=Path, required=True, help='Path to base DKB-Setup folder (provides python/llvm/bin/deps)')
    ap.add_argument('--out', type=Path, default=ROOT / 'dist', help='Output directory')
    ap.add_argument('--version', default=(ROOT / 'VERSION').read_text(encoding='utf-8').strip())
    ap.add_argument('--update-repo', help='Public GitHub owner/repo for auto-updates')
    ap.add_argument('--gen', type=Path, help='Generated C/layout directory for --make-runtime-lib')
    ap.add_argument('--7z', dest='seven_z', type=Path, help='Path to 7z.exe or 7zr.exe')
    ap.add_argument('--sfx', type=Path, help='Path to 7zSD.sfx')
    args = ap.parse_args()

    out = args.out.resolve()
    rt_out = out / 'rtlib-build'
    lib, totk_o = build_runtime_and_rc(ROOT, args.setup_base.resolve(), rt_out, args.gen.resolve() if args.gen else None)

    safe_ver = args.version.replace('+', '-')
    patch_zip = out / f'dkb-lowspec-patch-v{safe_ver}.zip'
    build_patch_zip(ROOT, lib, totk_o, patch_zip, args.version)

    stage = out / 'DKB-LowSpec-Setup'
    stage_setup_folder(ROOT, args.setup_base.resolve(), lib, stage, args.version, args.update_repo)

    if args.seven_z and args.sfx and args.seven_z.is_file() and args.sfx.is_file():
        build_sfx(stage, out / f'DKB-LowSpec-Setup-v{safe_ver}.exe', args.seven_z, args.sfx)
    else:
        print('Skipping 7z SFX step (pass --7z and --sfx to generate the single-file .exe).')


if __name__ == '__main__':
    main()
