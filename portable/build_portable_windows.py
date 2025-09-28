"""Build a portable Windows distribution of the Ollama OCR Streamlit app.

The script automates the following steps:

1. Installs PyInstaller if it is missing.
2. Bundles the application and its dependencies into a single directory.
3. Adds helper launch scripts and documentation for end users.
4. Compresses the bundle into a zip archive ready for distribution.

Run this script on Windows with Python 3.10+ installed:

    python portable\build_portable_windows.py

"""

from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
import textwrap
import zipfile
from pathlib import Path
from typing import Iterable


PROJECT_ROOT = Path(__file__).resolve().parents[1]
PORTABLE_DIR = Path(__file__).resolve().parent
DIST_NAME = "Ollama-OCR"
ZIP_NAME = f"{DIST_NAME}-portable.zip"


def _ensure_pyinstaller() -> None:
    try:
        import PyInstaller  # noqa: F401
    except ImportError:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])


def _clean_previous_build(dist_path: Path, build_path: Path, zip_path: Path) -> None:
    for path in (dist_path, build_path):
        if path.exists():
            shutil.rmtree(path)
    if zip_path.exists():
        zip_path.unlink()


def _pyinstaller_command(dist_path: Path, build_path: Path, icon_path: Path | None) -> list[str]:
    launcher_path = PORTABLE_DIR / "portable_launcher.py"
    app_dir = PROJECT_ROOT / "src" / "ollama_ocr"
    add_data = os.pathsep.join([str(app_dir), "app"])

    command = [
        sys.executable,
        "-m",
        "PyInstaller",
        "--noconfirm",
        "--clean",
        f"--distpath={dist_path}",
        f"--workpath={build_path}",
        "--name",
        DIST_NAME,
        "--add-data",
        add_data,
        "--hidden-import",
        "streamlit.web.bootstrap",
        "--hidden-import",
        "streamlit.runtime.scriptrunner.magic_funcs",
    ]

    if icon_path and icon_path.exists():
        command.extend(["--icon", str(icon_path)])

    command.append(str(launcher_path))
    return command


def _write_portable_readme(dist_folder: Path) -> None:
    readme_text = textwrap.dedent(
        """
        Ollama OCR Portable
        ====================

        This bundle contains the Ollama OCR Streamlit web application packaged as a
        standalone Windows program. Python and the project's dependencies are
        included, so no additional installation is required.

        Requirements
        ------------
        * Windows 10 or later (64-bit).
        * [Ollama](https://ollama.com/download) installed locally with the
          required vision models already pulled.
        * Access to the Ollama API on http://localhost:11434 (default).

        Usage
        -----
        1. Extract the contents of this zip archive to any folder.
        2. Double-click ``Start Ollama OCR.bat`` or launch ``Ollama-OCR.exe``.
        3. Your browser will open automatically at http://localhost:8501 with the app.
        4. Keep the console window open while using the application. Close it to stop.

        Notes
        -----
        * Ensure Ollama is running before launching the app.
        * The application runs locally; no internet connection is required after models
          are downloaded.
        * Generated logs are stored in the ``logs`` directory created next to the executable.
        """
    ).strip()

    (dist_folder / "README_portable.txt").write_text(readme_text, encoding="utf-8")


def _write_launcher_batch(dist_folder: Path) -> None:
    batch_content = textwrap.dedent(
        rf"""@echo off
        setlocal
        cd /d "%~dp0"
        if not exist logs mkdir logs
        echo Starting Ollama OCR Portable...
        call "%~dp0{DIST_NAME}.exe"
        endlocal
        """
    ).strip()

    (dist_folder / "Start Ollama OCR.bat").write_text(batch_content, encoding="utf-8")


def _copy_support_files(dist_folder: Path, extra_files: Iterable[Path]) -> None:
    for file_path in extra_files:
        if file_path.exists():
            target = dist_folder / file_path.name
            if file_path.is_dir():
                if target.exists():
                    shutil.rmtree(target)
                shutil.copytree(file_path, target)
            else:
                shutil.copy2(file_path, target)


def _create_zip(dist_folder: Path, zip_path: Path) -> None:
    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for file in dist_folder.rglob("*"):
            archive.write(file, file.relative_to(dist_folder.parent))


def build(icon: str | None = None) -> Path:
    dist_path = PORTABLE_DIR / "dist"
    build_path = PORTABLE_DIR / "build"
    zip_path = PROJECT_ROOT / ZIP_NAME

    _ensure_pyinstaller()
    _clean_previous_build(dist_path, build_path, zip_path)

    command = _pyinstaller_command(dist_path, build_path, Path(icon) if icon else None)
    subprocess.check_call(command)

    dist_folder = dist_path / DIST_NAME
    _write_portable_readme(dist_folder)
    _write_launcher_batch(dist_folder)

    _copy_support_files(dist_folder, [PROJECT_ROOT / "logo_file.jpg"])
    _create_zip(dist_folder, zip_path)

    return zip_path


def main() -> None:
    parser = argparse.ArgumentParser(description="Build the Ollama OCR portable Windows bundle.")
    parser.add_argument("--icon", help="Optional path to a .ico file used as the application icon.")
    args = parser.parse_args()

    zip_path = build(icon=args.icon)
    print(f"Portable build created at: {zip_path}")


if __name__ == "__main__":
    main()
