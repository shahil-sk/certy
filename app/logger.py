"""
Central logging configuration for Certy.

Call `get_logger(__name__)` in every module that needs logging.
Logs go to both the console (DEBUG+) and a rotating file in the
user's app-data directory (INFO+) so nothing is lost between runs.

Log file location:
  Windows  : %APPDATA%\Certy\certy.log
  macOS    : ~/Library/Logs/Certy/certy.log
  Linux    : ~/.local/share/Certy/certy.log
"""
import logging
import os
import platform
import sys
from logging.handlers import RotatingFileHandler

_LOG_MAX_BYTES  = 2 * 1024 * 1024   # 2 MB per file
_LOG_BACKUPS    = 3                  # keep certy.log + 3 rotated copies
_FMT            = "%(asctime)s  %(levelname)-8s  %(name)s  %(message)s"
_DATE_FMT       = "%Y-%m-%d %H:%M:%S"


def _log_dir() -> str:
    system = platform.system()
    if system == "Windows":
        base = os.environ.get("APPDATA", os.path.expanduser("~"))
    elif system == "Darwin":
        base = os.path.expanduser("~/Library/Logs")
    else:
        base = os.path.expanduser("~/.local/share")
    return os.path.join(base, "Certy")


def _setup() -> None:
    """Configure the root logger once.  Idempotent."""
    root = logging.getLogger("certy")
    if root.handlers:           # already configured
        return
    root.setLevel(logging.DEBUG)

    formatter = logging.Formatter(_FMT, datefmt=_DATE_FMT)

    # Console handler — DEBUG and above while developing
    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(logging.DEBUG)
    ch.setFormatter(formatter)
    root.addHandler(ch)

    # Rotating file handler — INFO and above for persistent logs
    try:
        log_dir = _log_dir()
        os.makedirs(log_dir, exist_ok=True)
        fh = RotatingFileHandler(
            os.path.join(log_dir, "certy.log"),
            maxBytes=_LOG_MAX_BYTES,
            backupCount=_LOG_BACKUPS,
            encoding="utf-8",
        )
        fh.setLevel(logging.INFO)
        fh.setFormatter(formatter)
        root.addHandler(fh)
    except OSError as exc:
        # If we cannot write to the log directory, warn once and carry on.
        root.warning("Could not create log file: %s", exc)


_setup()


def get_logger(name: str) -> logging.Logger:
    """
    Return a child logger under the 'certy' namespace.

    Usage::

        from app.logger import get_logger
        log = get_logger(__name__)
        log.debug("loaded %d fonts", n)
        log.warning("template not found: %s", path)
        log.exception("unexpected error")   # includes full traceback
    """
    # Strip the leading 'app.' so log lines read 'certy.core' not 'certy.app.core'
    short = name.removeprefix("app.") if name.startswith("app.") else name
    return logging.getLogger(f"certy.{short}")
