"""Fast 3-second updater for DKB Low-Spec / Vega 7 builds.

Downloads a small (~25 MB) patch archive from GitHub Releases (or applies a local
patch zip via --apply) containing libtotkrt.a, totk.o, dkb.ico, and dkb.ini.defaults,
merges new optimization keys into dkb.ini while keeping the player's language,
and relinks dkb.exe using the cached main/sdk objects in .update-cache/.
"""
import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import urllib.request
import zipfile
from pathlib import Path

DEFAULT_REPO = os.environ.get('DKB_UPDATE_REPO', 'evolis-game/donkey-kong-bananza-pc-lowspec')
TIMEOUT = 15
LINK_LIBS = [
    '-lpsapi', '-lbcrypt', '-luser32', '-lgdi32', '-ldwmapi', '-limm32',
    '-lwinmm', '-lvulkan-1', '-lSDL3', '-lopus', '-l:libvpx.a', '-l:libzstd.a',
    '-l:libc++.a', '-l:libc++abi.a', '-l:libunwind.a', '-l:libwinpthread.a',
]
PRESERVED_KEYS = {'lang', 'totk_lang'}


def read_repo(dest: Path, cli_repo: str | None) -> str:
    if cli_repo:
        return cli_repo.strip()
    cfg = dest / 'update_repo.txt'
    if cfg.is_file():
        return cfg.read_text(encoding='utf-8').strip()
    return DEFAULT_REPO


def parse_version(v: str):
    m = re.fullmatch(r'v?(\d+(?:\.\d+)*)(?:[-+].*)?', str(v).strip())
    return tuple(int(x) for x in m.group(1).split('.')) if m else None


def fetch_latest_release(repo: str) -> dict:
    url = f'https://api.github.com/repos/{repo}/releases/latest'
    req = urllib.request.Request(url, headers={
        'User-Agent': 'dkb-lowspec-updater',
        'Accept': 'application/vnd.github+json',
    })
    with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
        return json.load(resp)


def find_toolchain(dest: Path, llvm_arg: Path | None, deps_arg: Path | None):
    candidates_llvm = [
        llvm_arg,
        dest / '.update-cache' / 'llvm',
        dest.parent / 'DKB-LowSpec-Setup' / 'llvm',
        dest.parent / 'DKB-Setup' / 'llvm',
    ]
    candidates_deps = [
        deps_arg,
        dest / '.update-cache' / 'deps',
        dest.parent / 'DKB-LowSpec-Setup' / 'runtime' / 'deps',
        dest.parent / 'DKB-Setup' / 'runtime' / 'deps',
    ]
    clang = next((p / 'bin' / 'clang.exe' for p in candidates_llvm if p and (p / 'bin' / 'clang.exe').is_file()), None)
    deps_lib = next((p / 'lib' for p in candidates_deps if p and (p / 'lib').is_dir()), None)
    return clang, deps_lib


def merge_ini(dest_ini: Path, defaults_ini: Path):
    """Update optimization keys from defaults_ini while preserving user's language and custom comments."""
    if not defaults_ini.is_file():
        return
    if not dest_ini.is_file():
        shutil.copy2(defaults_ini, dest_ini)
        return

    kv_re = re.compile(r'^\s*([A-Za-z0-9_]+)\s*=\s*(.*?)\s*$')
    new_vals = {}
    for line in defaults_ini.read_text(encoding='utf-8-sig').splitlines():
        m = kv_re.match(line)
        if m and m.group(1).lower() not in PRESERVED_KEYS:
            new_vals[m.group(1).lower()] = (m.group(1), m.group(2))

    lines = dest_ini.read_text(encoding='utf-8-sig').splitlines()
    seen = set()
    for i, line in enumerate(lines):
        m = kv_re.match(line)
        if m:
            k = m.group(1).lower()
            seen.add(k)
            if k in new_vals:
                orig_key, val = new_vals[k]
                lines[i] = f'{orig_key} = {val}'

    missing = [f'{k} = {v}' for kl, (k, v) in new_vals.items() if kl not in seen]
    if missing:
        lines.append('')
        lines.append('# Added by fast_update')
        lines.extend(missing)

    tmp = dest_ini.with_suffix('.ini.tmp')
    tmp.write_text('\n'.join(lines) + '\n', encoding='utf-8', newline='\n')
    os.replace(tmp, dest_ini)


def relink_exe(dest: Path, patch_dir: Path, clang: Path, deps_lib: Path):
    cache = dest / '.update-cache'
    objs = []
    for sub in ('main', 'sdk'):
        d = cache / sub
        if not d.is_dir():
            raise RuntimeError(f'Missing object cache: {d}')
        objs.extend(sorted(d.glob('*.o')))

    rt_cache = cache / 'runtime'
    if not rt_cache.is_dir():
        raise RuntimeError(f'Missing runtime object cache: {rt_cache}')
    for obj in sorted(rt_cache.glob('*.o')):
        if obj.name in ('modules.o', 'romfs.o', 'patches.o', 'ov_zstd.o'):
            objs.append(obj)

    lib = patch_dir / 'libtotkrt.a'
    if not lib.is_file():
        raise RuntimeError(f'Missing libtotkrt.a in patch: {lib}')

    out_tmp = dest / 'dkb.exe.new'
    rsp = cache / 'link_update.rsp'
    rsp.write_text('\n'.join(str(o).replace('\\', '/') for o in objs) + '\n', encoding='utf-8')

    cmd = [
        str(clang),
        '-fuse-ld=lld',
        '-Wl,--stack,16777216',
        f'@{rsp}',
        '-Wl,--whole-archive', str(lib), '-Wl,--no-whole-archive',
        '-L', str(deps_lib),
        *LINK_LIBS,
        '-o', str(out_tmp),
    ]
    print('Relinking dkb.exe...')
    subprocess.run(cmd, check=True)
    os.replace(out_tmp, dest / 'dkb.exe')


def apply_patch_zip(dest: Path, zip_path: Path, clang: Path, deps_lib: Path):
    with tempfile.TemporaryDirectory(prefix='dkb-upd-') as tmp:
        tmp_dir = Path(tmp)
        with zipfile.ZipFile(zip_path, 'r') as zf:
            zf.extractall(tmp_dir)

        relink_exe(dest, tmp_dir, clang, deps_lib)
        merge_ini(dest / 'dkb.ini', tmp_dir / 'dkb.ini.defaults')

        for fname in ('dkb.ico', 'Jouer_DKB_Natif.bat', 'VERSION'):
            src = tmp_dir / fname
            if src.is_file():
                shutil.copy2(src, dest / fname)

    print('Running selftest...')
    res = subprocess.run([str(dest / 'dkb.exe'), '--selftest'], cwd=dest)
    if res.returncode != 0:
        raise RuntimeError(f'dkb.exe --selftest failed with exit code {res.returncode}')
    print('Update applied and verified (0 failures)!')


def main():
    ap = argparse.ArgumentParser(description='Fast 3-second updater for DKB Low-Spec')
    ap.add_argument('--dest', type=Path, default=Path('.'), help='Game install directory')
    ap.add_argument('--repo', help='GitHub owner/repo for Releases')
    ap.add_argument('--apply', type=Path, help='Apply a local patch zip instead of downloading')
    ap.add_argument('--check', action='store_true', help='Only check for a newer release')
    ap.add_argument('--llvm', type=Path, help='Path to llvm-mingw directory')
    ap.add_argument('--deps', type=Path, help='Path to runtime/deps directory')
    args = ap.parse_args()

    dest = args.dest.resolve()
    clang, deps_lib = find_toolchain(dest, args.llvm, args.deps)

    if args.apply:
        if not clang or not deps_lib:
            sys.exit('Error: Could not find llvm/bin/clang.exe or runtime/deps/lib. Pass --llvm and --deps.')
        apply_patch_zip(dest, args.apply.resolve(), clang, deps_lib)
        return

    repo = read_repo(dest, args.repo)
    if not repo:
        sys.exit('No update repository configured. Set update_repo.txt or pass --repo owner/name.')

    cur_ver = (dest / 'VERSION').read_text(encoding='utf-8').strip() if (dest / 'VERSION').is_file() else '0.0.0'
    info = fetch_latest_release(repo)
    tag = info.get('tag_name', '')
    cur_t, new_t = parse_version(cur_ver), parse_version(tag)
    print(f'Current: {cur_ver} | Latest: {tag}')
    if cur_t and new_t and new_t <= cur_t:
        print('Already up to date.')
        return
    if args.check:
        print(f'Update available: {tag} -> {info.get("html_url")}')
        return

    asset = next((a for a in info.get('assets', []) if a['name'].endswith('.zip') and 'patch' in a['name'].lower()), None)
    if not asset:
        sys.exit('No patch .zip asset found in the latest GitHub release.')
    if not clang or not deps_lib:
        sys.exit('Error: Could not find llvm/bin/clang.exe or runtime/deps/lib for relinking.')

    with tempfile.TemporaryDirectory(prefix='dkb-dl-') as tmp:
        dl_path = Path(tmp) / asset['name']
        print(f'Downloading {asset["name"]} ({asset["size"] / 1024**2:.1f} MB)...')
        urllib.request.urlretrieve(asset['browser_download_url'], dl_path)
        apply_patch_zip(dest, dl_path, clang, deps_lib)


if __name__ == '__main__':
    main()
