"""
Project serialisation / deserialisation.
Saves and loads .certy files (JSON under the hood).

Version history:
  2.0  initial
  2.5  added qr_size
  2.6  added active_sheet
  2.7  added img_size
  2.8  added condition_col / condition_val
"""
import json
import os

FORMAT_VERSION = "2.8"


def serialise(
    template_path: str,
    excel_path: str,
    color_space: str,
    positions: dict,
    fields: list,
    font_settings: dict,
    field_vars: dict,
    filename_pattern: str = "",
    project_path: str = "",
    active_sheet: str = "",
) -> dict:
    """
    Convert all in-memory state to a plain JSON-serialisable dict.
    Paths are stored relative to the project file location when possible.
    """
    base = os.path.dirname(os.path.abspath(project_path)) if project_path else ""

    def _rel(p):
        if not p or not base:
            return p
        try:
            return os.path.relpath(p, base)
        except ValueError:
            return p  # different drive on Windows

    field_data = {}
    for f in fields:
        s   = font_settings.get(f, {})
        vis = field_vars.get(f)
        field_data[f] = {
            "visible":       vis.get() if hasattr(vis, "get") else bool(vis),
            "size":          s["size"].get()          if "size"          in s else 32,
            "color":         s["color"].get()         if "color"         in s else "#000000",
            "font_name":     s["font_name"].get()     if "font_name"     in s else "",
            "align":         s["align"].get()         if "align"         in s else "center",
            "opacity":       s["opacity"].get()       if "opacity"       in s else 100,
            "shadow":        s["shadow"].get()        if "shadow"        in s else False,
            "shadow_offset": s["shadow_offset"].get() if "shadow_offset" in s else 4,
            "outline":       s["outline"].get()       if "outline"       in s else False,
            "outline_width": s["outline_width"].get() if "outline_width" in s else 2,
            "field_type":    s["field_type"].get()    if "field_type"    in s else "text",
            "qr_size":       s["qr_size"].get()       if "qr_size"       in s else 120,
            "img_size":      s["img_size"].get()      if "img_size"      in s else 120,
            "condition_col": s["condition_col"].get() if "condition_col" in s else "",
            "condition_val": s["condition_val"].get() if "condition_val" in s else "",
        }

    return {
        "version":          FORMAT_VERSION,
        "template_path":    _rel(template_path),
        "excel_path":       _rel(excel_path),
        "active_sheet":     active_sheet,
        "color_space":      color_space,
        "filename_pattern": filename_pattern,
        "positions":        {k: list(v) for k, v in positions.items()},
        "fields":           fields,
        "field_settings":   field_data,
    }


def save(path: str, data: dict) -> None:
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(data, fh, indent=2, ensure_ascii=False)


def load(path: str) -> dict:
    with open(path, encoding="utf-8") as fh:
        data = json.load(fh)

    base = os.path.dirname(os.path.abspath(path))

    def _abs(p):
        if not p:
            return p
        if os.path.isabs(p):
            return p
        return os.path.normpath(os.path.join(base, p))

    data["template_path"] = _abs(data.get("template_path", ""))
    data["excel_path"]    = _abs(data.get("excel_path",    ""))
    return data
