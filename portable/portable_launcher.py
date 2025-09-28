"""Portable launcher for the Ollama OCR Streamlit application.

This module is designed to be used as the entry point when building a
standalone Windows distribution with PyInstaller. It keeps the Streamlit
application co-located with the executable and starts it programmatically,
so the final bundle can be run without installing Python or the project's
dependencies.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path


APP_SUBDIR = "app"


def _resolve_base_path() -> Path:
    """Return the directory that contains the packaged application files."""
    packed_path = getattr(sys, "_MEIPASS", None)
    if packed_path:
        return Path(packed_path)
    return Path(__file__).resolve().parent


def _locate_app_directory(base_path: Path) -> Path:
    """Locate the directory that contains the Streamlit application."""
    packaged_app_dir = base_path / APP_SUBDIR
    if packaged_app_dir.exists():
        return packaged_app_dir

    # Fallback for running the launcher directly from the source tree.
    repo_root = Path(__file__).resolve().parents[1]
    source_app_dir = repo_root / "src" / "ollama_ocr"
    if source_app_dir.exists():
        return source_app_dir

    raise FileNotFoundError(
        "Unable to locate the Streamlit application directory. "
        "Ensure the portable bundle was generated correctly."
    )


def _configure_environment(app_dir: Path) -> None:
    """Prepare environment variables and import paths before running Streamlit."""
    sys.path.insert(0, str(app_dir))
    os.environ.setdefault("STREAMLIT_SERVER_HEADLESS", "false")
    os.environ.setdefault("STREAMLIT_BROWSER_GATHER_USAGE_STATS", "false")
    os.environ.setdefault("PYTHONUTF8", "1")


def _run_streamlit(app_dir: Path) -> None:
    """Run the Streamlit application programmatically."""
    from streamlit.web import bootstrap

    app_script = app_dir / "app.py"
    if not app_script.exists():
        raise FileNotFoundError(
            "Streamlit entry script 'app.py' not found in portable bundle."
        )

    # Change working directory so relative file operations behave as expected.
    os.chdir(app_dir)

    bootstrap.run(
        str(app_script),
        "",
        [],
        {},
    )


def main() -> None:
    base_path = _resolve_base_path()
    app_dir = _locate_app_directory(base_path)
    _configure_environment(app_dir)
    _run_streamlit(app_dir)


if __name__ == "__main__":
    main()
