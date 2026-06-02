"""
Font loading and caching.
All font I/O is isolated here so the rest of the app never calls
ImageFont.truetype() directly.
"""
import os
from functools import lru_cache

from PIL import ImageFont

from app.helpers import resource_path
from app.logger import get_logger

log = get_logger(__name__)


def load_available_fonts() -> dict:
    """Scan the fonts/ directory and return {name: path} sorted alphabetically."""
    fonts: dict = {}
    fonts_dir = resource_path("fonts")
    os.makedirs(fonts_dir, exist_ok=True)
    if os.path.isdir(fonts_dir):
        for f in sorted(os.listdir(fonts_dir)):
            if f.lower().endswith((".ttf", ".otf")):
                fonts[os.path.splitext(f)[0]] = os.path.join(fonts_dir, f)
    if not fonts:
        log.warning("no fonts found in '%s', falling back to arial.ttf", fonts_dir)
        fonts["Default"] = "arial.ttf"
    else:
        log.debug("loaded %d font(s) from '%s'", len(fonts), fonts_dir)
    return dict(sorted(fonts.items(), key=lambda x: x[0].lower()))


@lru_cache(maxsize=64)
def get_font(path: str, size: int) -> ImageFont.FreeTypeFont:
    """Load and cache a font by (path, size).  Falls back to default on failure."""
    try:
        return ImageFont.truetype(path, size)
    except Exception:
        log.warning("could not load font '%s' at size %d, using default", path, size)
        return ImageFont.load_default()


def resolve_font(available: dict, name: str, size: int) -> ImageFont.FreeTypeFont:
    """Look up name in the available dict, then return a cached font object."""
    path = available.get(name, "arial.ttf")
    return get_font(path, size)
