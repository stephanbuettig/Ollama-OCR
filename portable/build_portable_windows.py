"""Build a portable PyInstaller distribution of the Streamlit application."""
from __future__ import annotations

import shlex
import shutil
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = REPO_ROOT / "src" / "ollama_ocr"
BUILD_DIR = REPO_ROOT / "portable" / "build"
DIST_DIR = REPO_ROOT / "portable" / "dist"
SPEC_DIR = BUILD_DIR


def _pyinstaller_command() -> list[str]:
    """Return the PyInstaller command used for the Windows portable build."""
    app_entry = SRC_DIR / "app.py"

    return [
        sys.executable,
        "-m",
        "PyInstaller",
        "--noconfirm",
        "--clean",
        "--onefile",
        "--name",
        "Ollama-OCR",
        "--distpath",
        str(DIST_DIR),
        "--workpath",
        str(BUILD_DIR),
        "--specpath",
        str(SPEC_DIR),
        "--paths",
        str(SRC_DIR),
        "--collect-all",
        "streamlit",
        "--hidden-import",
        "streamlit",
        "--collect-all",
        "ollama_ocr",
        "--hidden-import",
        "ocr_processor",
        str(app_entry),
    ]


def build() -> Path:
    """Execute PyInstaller and return the path to the generated executable."""
    if DIST_DIR.exists():
        shutil.rmtree(DIST_DIR)
    if BUILD_DIR.exists():
        shutil.rmtree(BUILD_DIR)

    BUILD_DIR.mkdir(parents=True, exist_ok=True)
    DIST_DIR.mkdir(parents=True, exist_ok=True)

    command = _pyinstaller_command()
    print("Running:", " ".join(shlex.quote(part) for part in command))
    subprocess.run(command, check=True, cwd=REPO_ROOT)

    exe_path = DIST_DIR / "Ollama-OCR.exe"
    built_binary = DIST_DIR / "Ollama-OCR"
    if built_binary.exists() and not exe_path.exists():
        built_binary.rename(exe_path)
        built_binary = exe_path

    return built_binary


if __name__ == "__main__":
    executable = build()
    print(f"Portable build created at {executable}")
