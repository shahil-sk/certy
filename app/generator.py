"""
Certificate generation worker.
Runs on a background thread; communicates back via callbacks.

Supported output formats:
  PDF   -- vector container wrapping the rendered PNG
  PNG   -- lossless raster
  JPEG  -- compressed raster, smallest file size
  WebP  -- modern lossy/lossless, best for web sharing
"""
import io
import os
import re
import threading
from collections import Counter

from PIL import Image

from app.helpers import px_to_mm, safe_filename
from app.image_renderer import draw_text_on_image
from app.logger import get_logger

log = get_logger(__name__)

_TOKEN_RE = re.compile(r"\{(\w+)\}")

_JPEG_QUALITY = 85
_WEBP_QUALITY = 88  # 0-100; 88 gives good fidelity at ~40% of JPEG size


def _build_filename(pattern: str, student: dict, idx: int, fields: list) -> str:
    if pattern and pattern.strip():
        def _repl(m):
            key = m.group(1).lower()
            if key == "serial":
                return str(idx + 1).zfill(3)
            val = student.get(key, "")
            return safe_filename(val) if val else m.group(0)
        name = _TOKEN_RE.sub(_repl, pattern.strip())
        return name or f"cert_{idx + 1}"
    parts = [student.get(fields[i], "") for i in range(min(2, len(fields)))]
    return safe_filename(*parts) or f"cert_{idx + 1}"


def _find_duplicates(excel_data: list, fields: list) -> list:
    if not fields:
        return []
    key    = fields[0]
    counts = Counter(r.get(key, "").strip() for r in excel_data)
    return [(v, c, key) for v, c in counts.items() if c > 1 and v]


def inject_serial(excel_data: list) -> list:
    """Return a copy of excel_data with a 'serial' key added to every row."""
    return [{**row, "serial": str(i + 1).zfill(3)}
            for i, row in enumerate(excel_data)]


def _save_pdf(img: Image.Image, dest: str, pdf_w: float, pdf_h: float) -> None:
    from fpdf import FPDF
    buf = io.BytesIO()
    img.save(buf, format="PNG", optimize=True)
    buf.seek(0)
    pdf = FPDF(unit="mm", format=(pdf_w, pdf_h))
    pdf.add_page()
    pdf.image(buf, x=0, y=0, w=pdf_w, h=pdf_h)
    pdf.output(dest)


def _save_png(img: Image.Image, dest: str, **_) -> None:
    img.save(dest, format="PNG", optimize=True)


def _save_jpeg(img: Image.Image, dest: str, **_) -> None:
    # JPEG has no alpha channel; flatten onto white.
    if img.mode in ("RGBA", "LA"):
        bg = Image.new("RGB", img.size, (255, 255, 255))
        bg.paste(img, mask=img.split()[-1])
        img = bg
    else:
        img = img.convert("RGB")
    img.save(dest, format="JPEG", quality=_JPEG_QUALITY, optimize=True)


def _save_webp(img: Image.Image, dest: str, **_) -> None:
    # WebP supports RGBA natively, so no flattening needed.
    img.save(dest, format="WEBP", quality=_WEBP_QUALITY, method=6)


# Maps format name -> (file extension, save callable)
_FORMAT_HANDLERS = {
    "PDF":  (".pdf",  _save_pdf),
    "PNG":  (".png",  _save_png),
    "JPEG": (".jpg",  _save_jpeg),
    "WEBP": (".webp", _save_webp),
}


def run(
    excel_data: list,
    fields: list,
    field_vars: dict,
    font_settings: dict,
    available_fonts: dict,
    original_image: Image.Image,
    positions: dict,
    out_dir: str,
    color_mode: str,
    on_progress,
    on_log,
    on_done,
    lock: threading.Lock,
    filename_pattern: str = "",
    output_format: str = "PDF",
    excel_dir: str = "",
) -> None:
    sub      = color_mode
    total    = len(excel_data)
    iw, ih   = original_image.size
    pdf_w    = px_to_mm(iw)
    pdf_h    = px_to_mm(ih)
    out_sub  = os.path.join(out_dir, sub)
    os.makedirs(out_sub, exist_ok=True)

    fmt      = output_format.upper()
    ext, _   = _FORMAT_HANDLERS.get(fmt, _FORMAT_HANDLERS["PDF"])
    enriched = inject_serial(excel_data)
    all_fields = fields + (["serial"] if "serial" not in fields else [])

    def _worker():
        count = 0
        log.info(
            "generation started: %d records, mode=%s, format=%s, output=%s",
            total, sub, fmt, out_dir,
        )
        on_log("Starting generation...", True)
        on_log(f"Records: {total}   Mode: {sub}   Format: {fmt}   Output: {out_dir}", False)
        if filename_pattern:
            on_log(f"Filename pattern: {filename_pattern}", False)

        dupes = _find_duplicates(excel_data, fields)
        if dupes:
            on_log(f"[warn] {len(dupes)} duplicate(s) in '{fields[0]}':", False)
            log.warning("%d duplicate value(s) in column '%s'", len(dupes), fields[0])
            for val, cnt, _ in dupes[:5]:
                on_log(f"  \u2022 '{val}'  x{cnt}", False)
            if len(dupes) > 5:
                on_log(f"  ... and {len(dupes)-5} more", False)

        on_log("-" * 44, False)

        for idx, student in enumerate(enriched):
            try:
                img = draw_text_on_image(
                    original_image.copy().convert("RGB"),
                    all_fields, field_vars, font_settings,
                    available_fonts, student, positions,
                    excel_dir=excel_dir,
                )
                name = _build_filename(filename_pattern, student, idx, fields)
                dest = os.path.join(out_sub, f"{name}_certificate{ext}")

                _, save_fn = _FORMAT_HANDLERS[fmt]
                if fmt == "PDF":
                    save_fn(img, dest, pdf_w, pdf_h)
                else:
                    save_fn(img, dest)

                count += 1
                log.debug("[%d/%d] saved %s", idx + 1, total, dest)
                on_log(f"[{idx+1}/{total}]  {name}_certificate{ext}", False)

            except Exception:
                log.exception("failed to generate certificate %d", idx + 1)
                on_log(f"[error]  cert {idx+1}: see certy.log for details", False)

            on_progress((idx + 1) / total * 100)

        on_log("-" * 44, False)
        on_log(f"Done  {count}/{total} certificates saved.", False)
        log.info(
            "generation finished: %d/%d saved to %s",
            count, total, out_sub,
        )
        on_done(count, total)
        lock.release()

    threading.Thread(target=_worker, daemon=True).start()
