"""
Per-row image overlay rendering.

The data column holds a file path (absolute or relative to the Excel file).
We open it, resize to a square bounding box, apply optional opacity, and
composite it onto the certificate at the requested position.

If the path is missing or the file cannot be opened we fall back to a
labelled grey placeholder so the rest of the certificate still renders.
"""
from PIL import Image, ImageDraw, ImageFont

from app.logger import get_logger

log = get_logger(__name__)


def paste_image_field(
    value: str,
    size: int,
    opacity: int,
    base_img: Image.Image,
    cx: float,
    cy: float,
    excel_dir: str = "",
) -> None:
    """
    Composite an image from `value` (file path) onto `base_img`.

    The image is scaled to fit within a `size` x `size` bounding box
    while preserving aspect ratio.  It is centred on (cx, cy).

    Parameters
    ----------
    value      : cell value — expected to be a file path string
    size       : bounding box side length in pixels
    opacity    : 0-100 (applied to the whole layer)
    base_img   : RGBA PIL image to composite onto (mutated in-place)
    cx, cy     : centre position on the canvas
    excel_dir  : directory of the Excel file, used to resolve relative paths
    """
    img = _open_image(value, size, excel_dir)
    if img is None:
        img = _placeholder(size, str(value or "(no path)"))

    # Apply opacity by scaling the alpha channel
    if opacity < 100:
        img = img.copy()
        alpha = img.split()[3] if img.mode == "RGBA" else None
        if alpha:
            scaled = alpha.point(lambda p: int(p * opacity / 100))
            img.putalpha(scaled)

    iw, ih = img.size
    px = int(cx - iw / 2)
    py = int(cy - ih / 2)

    mask = img.split()[3] if img.mode == "RGBA" else None
    base_img.paste(img, (px, py), mask=mask)


def make_preview_image(value: str, size: int, excel_dir: str = "") -> Image.Image:
    """Return a displayable thumbnail for the canvas placeholder."""
    img = _open_image(value, size, excel_dir)
    if img is None:
        img = _placeholder(size, "IMG")
    return img


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _open_image(value: str, size: int, excel_dir: str) -> "Image.Image | None":
    """Try to open the file at `value`, resize to fit `size`, return RGBA."""
    import os

    if not value or not str(value).strip():
        return None

    path = str(value).strip()

    # Resolve relative paths against the Excel file's directory
    if not os.path.isabs(path) and excel_dir:
        candidate = os.path.join(excel_dir, path)
        if os.path.exists(candidate):
            path = candidate

    if not os.path.exists(path):
        log.warning("image field: file not found: '%s'", path)
        return None

    try:
        img = Image.open(path).convert("RGBA")
        img.thumbnail((size, size), Image.Resampling.LANCZOS)
        return img
    except Exception:
        log.exception("image field: cannot open '%s'", path)
        return None


def _placeholder(size: int, msg: str) -> Image.Image:
    img  = Image.new("RGBA", (size, size), (180, 180, 180, 200))
    draw = ImageDraw.Draw(img)
    try:
        font = ImageFont.load_default()
    except Exception:
        font = None
    draw.multiline_text(
        (size // 2, size // 2), msg,
        fill=(60, 60, 60, 255),
        font=font, anchor="mm", align="center",
    )
    return img
