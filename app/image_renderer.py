"""
All PIL drawing operations live here.
No tkinter widgets are created in this module.

Per-field controls:
  size, color, font_name, align     -- text fields
  opacity   (0-100 int)             -- layer alpha
  shadow    (bool)                  -- drop shadow (text only)
  shadow_offset (int, px)           -- shadow distance
  outline   (bool)                  -- stroke around text
  outline_width (int, px)           -- stroke width
  field_type (str)                  -- "text" | "qr" | "image"
  qr_size   (int, px)               -- QR bounding box side length
  img_size  (int, px)               -- image overlay bounding box side length
"""
import io
import os

from PIL import Image, ImageDraw, ImageFilter

from app.helpers import hex_to_rgb
from app.font_manager import resolve_font
from app.logger import get_logger

log = get_logger(__name__)

_LANCZOS = Image.Resampling.LANCZOS

_ANCHOR = {
    "left":   "lm",
    "center": "mm",
    "right":  "rm",
}


def _get(var, default=""):
    """Read a tkinter Var or plain value safely."""
    try:
        return var.get()
    except AttributeError:
        return var if var is not None else default


def _draw_text_layer(
    size_px, text, font, color_rgb, opacity,
    shadow, shadow_offset, outline, outline_width,
    anchor, x, y, canvas_w, canvas_h, base_img,
):
    r, g, b = color_rgb[:3]
    alpha   = max(0, min(255, int(opacity / 100 * 255)))

    if shadow and shadow_offset > 0:
        sh_layer = Image.new("RGBA", (canvas_w, canvas_h), (0, 0, 0, 0))
        sh_draw  = ImageDraw.Draw(sh_layer)
        sh_draw.text(
            (x + shadow_offset, y + shadow_offset), text, font=font,
            fill=(0, 0, 0, min(alpha, 180)), anchor=anchor,
        )
        sh_layer = sh_layer.filter(
            ImageFilter.GaussianBlur(radius=max(1, shadow_offset // 2)))
        base_img.alpha_composite(sh_layer)

    if outline and outline_width > 0:
        out_layer = Image.new("RGBA", (canvas_w, canvas_h), (0, 0, 0, 0))
        out_draw  = ImageDraw.Draw(out_layer)
        for ox in range(-outline_width, outline_width + 1):
            for oy in range(-outline_width, outline_width + 1):
                if ox == 0 and oy == 0:
                    continue
                out_draw.text(
                    (x + ox, y + oy), text, font=font,
                    fill=(0, 0, 0, alpha), anchor=anchor,
                )
        base_img.alpha_composite(out_layer)

    txt_layer = Image.new("RGBA", (canvas_w, canvas_h), (0, 0, 0, 0))
    txt_draw  = ImageDraw.Draw(txt_layer)
    txt_draw.text((x, y), text, font=font, fill=(r, g, b, alpha), anchor=anchor)
    base_img.alpha_composite(txt_layer)


def _paste_qr(qr_img: Image.Image, x: float, y: float, base_img: Image.Image):
    """Paste a QR image centred on (x, y) onto base_img."""
    qw, qh = qr_img.size
    px = int(x - qw / 2)
    py = int(y - qh / 2)
    if qr_img.mode == "RGBA":
        base_img.paste(qr_img, (px, py), mask=qr_img.split()[3])
    else:
        base_img.paste(qr_img.convert("RGBA"), (px, py))


def draw_text_on_image(
    img, fields, field_vars, font_settings,
    available_fonts, student, positions,
    excel_dir: str = "",
):
    """Render all visible fields onto img and return it."""
    img    = img.convert("RGBA")
    iw, ih = img.size

    for field in fields:
        var = field_vars.get(field)
        if var is None or not _get(var):
            continue
        if field not in positions:
            continue
        try:
            x, y       = positions[field]
            s          = font_settings[field]
            field_type = _get(s.get("field_type"), "text")

            if field_type == "qr":
                from app.qr_renderer import make_qr_image
                qr_size = max(20, _get(s.get("qr_size"), 120))
                value   = student.get(field, "")
                qr_img  = make_qr_image(value, qr_size)
                _paste_qr(qr_img, x, y, img)

            elif field_type == "image":
                from app.image_field_renderer import paste_image_field
                img_size = max(20, _get(s.get("img_size"), 120))
                opacity  = _get(s.get("opacity"), 100)
                value    = student.get(field, "")
                paste_image_field(value, img_size, opacity, img, x, y, excel_dir)

            else:
                size  = _get(s["size"],         32)
                color = _get(s["color"],         "#000000")
                fname = _get(s["font_name"],     "")
                align = _get(s.get("align"),     "center")
                opac  = _get(s.get("opacity"),   100)
                shad  = _get(s.get("shadow"),    False)
                shoff = _get(s.get("shadow_offset"), 4)
                outl  = _get(s.get("outline"),   False)
                outw  = _get(s.get("outline_width"), 2)

                font   = resolve_font(available_fonts, fname, size)
                text   = student.get(field, "")
                anchor = _ANCHOR.get(align, "mm")

                _draw_text_layer(
                    size_px=size, text=text, font=font,
                    color_rgb=hex_to_rgb(color),
                    opacity=opac, shadow=shad, shadow_offset=shoff,
                    outline=outl, outline_width=outw,
                    anchor=anchor, x=x, y=y,
                    canvas_w=iw, canvas_h=ih, base_img=img,
                )

        except Exception:
            log.exception("failed to render field '%s'", field)

    return img.convert("RGB")


def render_placeholder(
    field, font_settings, available_fonts, excel_data,
    scale_x, scale_y, zoom=1.0,
):
    """
    Return a PIL Image of the sample text / QR / image scaled for the canvas.
    """
    s          = font_settings[field]
    field_type = _get(s.get("field_type"), "text")

    if field_type == "qr":
        from app.qr_renderer import make_qr_image
        qr_size = max(20, _get(s.get("qr_size"), 120))
        value   = (excel_data[0].get(field, field) if excel_data else field) or field
        qr_img  = make_qr_image(value, qr_size)
        sw = max(int(qr_size / scale_x * zoom), 1)
        sh = max(int(qr_size / scale_y * zoom), 1)
        return qr_img.resize((sw, sh), _LANCZOS)

    if field_type == "image":
        from app.image_field_renderer import make_preview_image
        img_size = max(20, _get(s.get("img_size"), 120))
        value    = (excel_data[0].get(field, "") if excel_data else "") or ""
        img      = make_preview_image(value, img_size)
        sw = max(int(img_size / scale_x * zoom), 1)
        sh = max(int(img_size / scale_y * zoom), 1)
        return img.resize((sw, sh), _LANCZOS)

    # text path
    size  = _get(s["size"],     32)
    color = _get(s["color"],    "#000000")
    fname = _get(s["font_name"], "")
    opac  = _get(s.get("opacity"), 100)
    font  = resolve_font(available_fonts, fname, size)
    text  = (excel_data[0].get(field, field) if excel_data else field) or field

    tmp  = Image.new("RGBA", (1, 1))
    draw = ImageDraw.Draw(tmp)
    try:
        bbox = font.getbbox(text)
        tw = max(bbox[2] - bbox[0], 1)
        th = max(bbox[3] - bbox[1], 1)
        ox = -bbox[0]
        oy = -bbox[1]
    except Exception:
        tw = max(int(draw.textlength(text, font=font)), 1)
        th = max(size, 1)
        ox, oy = 0, 0

    r, g, b = hex_to_rgb(color)[:3]
    alpha   = max(0, min(255, int(opac / 100 * 255)))

    img  = Image.new("RGBA", (tw, th), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    draw.text((ox, oy), text, font=font, fill=(r, g, b, alpha))

    sw = max(int(tw / scale_x * zoom), 1)
    sh = max(int(th / scale_y * zoom), 1)
    return img.resize((sw, sh), _LANCZOS)


def image_to_bytes(img: Image.Image) -> bytes:
    buf = io.BytesIO()
    img.convert("RGB").save(buf, format="PNG", optimize=True)
    buf.seek(0)
    return buf.read()
