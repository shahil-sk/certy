"""
Project file save / load (.certy JSON).
Version 2.7  --  adds img_size to persisted field settings.
"""
import json
import os
from datetime import datetime

from app.logger import get_logger

log = get_logger(__name__)


def _to_relative(asset_path: str, project_path: str) -> str:
    if not asset_path:
        return asset_path
    try:
        return os.path.relpath(asset_path, os.path.dirname(project_path))
    except ValueError:
        return asset_path


def _to_absolute(asset_path: str, project_path: str) -> str:
    if not asset_path:
        return asset_path
    if os.path.isabs(asset_path):
        return asset_path
    return os.path.normpath(
        os.path.join(os.path.dirname(project_path), asset_path)
    )


def serialise(
    template_path, excel_path, color_space,
    positions, fields, font_settings, field_vars,
    filename_pattern="",
    project_path="",
) -> dict:
    def _get(var, default=None):
        try:    return var.get()
        except: return default

    return {
        "version":          "2.7",
        "last_modified":    datetime.now().isoformat(),
        "template_path":    _to_relative(template_path, project_path),
        "excel_path":       _to_relative(excel_path,    project_path),
        "color_space":      color_space,
        "filename_pattern": filename_pattern,
        "positions":        positions,
        "field_settings":   {
            f: {
                "size":          _get(font_settings[f]["size"],         32),
                "color":         _get(font_settings[f]["color"],        "#000000"),
                "visible":       _get(field_vars[f],                    True),
                "font_name":     _get(font_settings[f]["font_name"],    ""),
                "align":         _get(font_settings[f]["align"],        "center"),
                "opacity":       _get(font_settings[f].get("opacity"),  100),
                "shadow":        _get(font_settings[f].get("shadow"),   False),
                "shadow_offset": _get(font_settings[f].get("shadow_offset"), 4),
                "outline":       _get(font_settings[f].get("outline"),  False),
                "outline_width": _get(font_settings[f].get("outline_width"), 2),
                "field_type":    _get(font_settings[f].get("field_type"), "text"),
                "qr_size":       _get(font_settings[f].get("qr_size"),  120),
                "img_size":      _get(font_settings[f].get("img_size"), 120),
            }
            for f in fields
        },
    }


def save(path: str, data: dict) -> None:
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(data, fh, indent=2)
    log.info("project saved to '%s'", path)


def load(path: str) -> dict:
    with open(path, "r", encoding="utf-8") as fh:
        data = json.load(fh)
    for key in ("template_path", "excel_path"):
        data[key] = _to_absolute(data.get(key, ""), path)
    log.info("project loaded from '%s' (version %s)", path, data.get("version", "?"))
    return data
