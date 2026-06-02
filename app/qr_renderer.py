"""
QR code generation helpers.
Isolated here so the rest of the app never imports `qrcode` directly.

Each call to `make_qr_image` returns a square RGBA PIL Image whose
side length is `size` pixels.  The QR is black on a transparent
background so it composites cleanly onto any certificate colour.

Dependency: pip install qrcode[pil]
"""
from PIL import Image

from app.logger import get_logger

log = get_logger(__name__)


def make_qr_image(data: str, size: int) -> Image.Image:
    """
    Render `data` as a QR code and return a square RGBA image of
    side length `size` pixels.

    Falls back to a labelled placeholder if `qrcode` is not installed
    or `data` is empty, so the rest of the app always gets a valid image.
    """
    if not data or not data.strip():
        return _placeholder(size, "(empty)")

    try:
        import qrcode  # type: ignore
        from qrcode.constants import ERROR_CORRECT_M  # type: ignore
    except ImportError:
        log.warning("qrcode library not installed. Run: pip install qrcode[pil]")
        return _placeholder(size, "qrcode\nnot installed")

    try:
        qr = qrcode.QRCode(
            error_correction=ERROR_CORRECT_M,
            box_size=10,
            border=2,
        )
        qr.add_data(data)
        qr.make(fit=True)

        # Make a black-on-white PIL image, then convert to RGBA and
        # replace white with transparent so it blends onto any background.
        rgb = qr.make_image(fill_color="black", back_color="white").convert("RGBA")
        pixels = rgb.load()
        w, h = rgb.size
        for y in range(h):
            for x in range(w):
                r, g, b, a = pixels[x, y]
                # white (or near-white) pixels become transparent
                if r > 200 and g > 200 and b > 200:
                    pixels[x, y] = (255, 255, 255, 0)

        return rgb.resize((size, size), Image.Resampling.LANCZOS)

    except Exception:
        log.exception("QR generation failed for data='%s'", data[:40])
        return _placeholder(size, "QR\nerror")


def _placeholder(size: int, msg: str) -> Image.Image:
    """Grey square with centred message — shown when QR cannot be generated."""
    from PIL import ImageDraw, ImageFont
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
