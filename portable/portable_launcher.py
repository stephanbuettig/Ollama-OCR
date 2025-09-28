"""Launch the Ollama OCR Streamlit application for portable builds."""
from __future__ import annotations

import logging
import subprocess
import sys
from pathlib import Path
from typing import Iterable

LOGGER_NAME = "portable_launcher"
LOG_FILE_NAME = "portable_launcher.log"
LOGS_DIR_NAME = "logs"


def resolve_bundle_dir() -> Path:
    """Return the directory that contains the bundled application."""
    if getattr(sys, "frozen", False):  # Support PyInstaller style bundles.
        if hasattr(sys, "_MEIPASS"):
            return Path(sys._MEIPASS)  # type: ignore[attr-defined]
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parent


def _configure_logger(bundle_dir: Path) -> tuple[logging.Logger, Path]:
    """Create a logger that writes to the bundle-specific log file."""
    logs_dir = bundle_dir / LOGS_DIR_NAME
    logs_dir.mkdir(parents=True, exist_ok=True)

    log_path = logs_dir / LOG_FILE_NAME
    logger = logging.getLogger(LOGGER_NAME)
    logger.setLevel(logging.INFO)
    logger.propagate = False

    # Avoid adding duplicate handlers if the module is imported multiple times.
    existing_file_handler_paths = {
        Path(getattr(handler, "baseFilename", ""))
        for handler in logger.handlers
        if isinstance(handler, logging.FileHandler)
    }
    if log_path not in existing_file_handler_paths:
        file_handler = logging.FileHandler(log_path, encoding="utf-8")
        file_handler.setFormatter(
            logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
        )
        logger.addHandler(file_handler)

    return logger, log_path


def _candidate_app_paths(bundle_dir: Path) -> Iterable[Path]:
    """Yield possible locations of the Streamlit application script."""
    relative_candidates = [
        Path("src") / "ollama_ocr" / "app.py",
        Path("app.py"),
    ]

    for candidate in relative_candidates:
        yield bundle_dir / candidate
        yield bundle_dir.parent / candidate


def _locate_streamlit_app(bundle_dir: Path, logger: logging.Logger) -> Path:
    """Locate the Streamlit application script relative to the bundle directory."""
    for app_path in _candidate_app_paths(bundle_dir):
        if app_path.exists():
            logger.info("Found Streamlit app at %s", app_path)
            return app_path

    raise FileNotFoundError(
        "Could not locate the Streamlit application. Expected app.py relative to the bundle."
    )


def _launch_streamlit(app_path: Path, logger: logging.Logger) -> None:
    """Launch Streamlit for the provided app script."""
    command = [sys.executable, "-m", "streamlit", "run", str(app_path)]
    logger.info("Executing command: %s", " ".join(command))
    subprocess.run(command, check=True, cwd=app_path.parent)


# Configure logging at import time so errors during startup are captured.
BUNDLE_DIR = resolve_bundle_dir()
LOGGER, LOG_PATH = _configure_logger(BUNDLE_DIR)


def main() -> None:
    """Entry point used by the portable launcher."""
    LOGGER.info("Starting portable launcher from bundle directory %s", BUNDLE_DIR)
    app_path = _locate_streamlit_app(BUNDLE_DIR, LOGGER)
    _launch_streamlit(app_path, LOGGER)


if __name__ == "__main__":
    try:
        main()
    except Exception:  # pragma: no cover - defensive logging for runtime errors
        LOGGER.exception("Portable launcher failed with an unexpected error.")
        message = (
            "An unexpected error occurred. Please check the log file at "
            f"'{LOG_PATH}' for details."
        )
        print(message, file=sys.stderr)
        raise SystemExit(1) from None
