"""Utilities for generating Windows launcher batch files."""

from __future__ import annotations

from pathlib import Path
from textwrap import dedent


def _write_launcher_batch(
    executable: Path,
    launcher_path: Path,
    log_path: Path,
) -> str:
    """Write a Windows batch file used to launch an executable.

    Parameters
    ----------
    executable:
        Absolute path to the executable that should be invoked by the batch file.
    launcher_path:
        Destination path for the batch file that will be written.
    log_path:
        Path to the log file that receives stdout/stderr from the executable.
    """
    launcher_path.parent.mkdir(parents=True, exist_ok=True)

    script = "\r\n".join(
        line.rstrip()
        for line in dedent(
            f"""
            @echo off
            setlocal

            set "APP_EXECUTABLE={executable}"
            set "LOG_FILE={log_path}"

            echo Launching %APP_EXECUTABLE% > "%LOG_FILE%"
            "%APP_EXECUTABLE%" %* >> "%LOG_FILE%" 2>&1
            set "EXIT_CODE=%ERRORLEVEL%"

            if %EXIT_CODE% neq 0 (
                echo Application exited with code %EXIT_CODE%.
                echo Log file: %LOG_FILE%
                if errorlevel 1 pause
            )

            exit /b %EXIT_CODE%
            """
        ).strip().splitlines()
    ) + "\r\n"

    launcher_path.write_text(script, encoding="utf-8")
    return script


__all__ = ["_write_launcher_batch"]
