"""Install missing dependencies on first use."""
import importlib
import shutil
import subprocess
import sys

from .config import PACKAGES


def ensure_package(module):
    """Import a module, pip-installing it into the current interpreter if missing."""
    try:
        return importlib.import_module(module)
    except ImportError:
        pass
    pip_name = PACKAGES.get(module, module)
    print(f"Installing {pip_name} ...")
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "-q", pip_name], check=True)
    except subprocess.CalledProcessError:
        sys.exit(
            f"Could not install {pip_name}. Use a virtualenv and retry:\n"
            "  python3 -m venv .venv && source .venv/bin/activate"
        )
    importlib.invalidate_caches()
    return importlib.import_module(module)


def ensure_ffmpeg():
    if shutil.which("ffmpeg"):
        return
    if shutil.which("brew"):
        print("Installing ffmpeg with Homebrew ...")
        subprocess.run(["brew", "install", "ffmpeg"], check=True)
        if shutil.which("ffmpeg"):
            return
    sys.exit("ffmpeg is required for this format. Install it (brew/apt install ffmpeg) or use --format mp3.")
