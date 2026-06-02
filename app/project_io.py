"""
Project file save / load (.certy JSON).
Version 2.5 — paths stored relative to the .certy file so moving the
              project folder never breaks template or data references.
"""
import json
import os
from datetime import datetime


def _to_relative(asset_path: str, project_path: str) -> str:
    """Return asset_path relative to the directory that holds project_path.
    Falls back to the absolute path if relpath fails (different drive on Windows)."""
    if not asset_path:
        return asset_path
    try:
        return os.path.relpath(asset_path, os.path.dirname(project_path))
    except ValueError:
        # os.path.relpath raises ValueError across Windows drive letters
        return asset_path


def _to_absolute(asset_path: str, project_path: str) -> str:
    """Resolve a possibly-relative asset_path against the project file directory."""
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
        "version":          "2.5",
        "last_modified":    datetime.now().isoformat(),
        # Store relative so the project is portable across machines / folders
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
            }
            for f in fields
        },
    }


def save(path: str, data: dict) -> None:
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(data, fh, indent=2)


def load(path: str) -> dict:
    with open(path, "r", encoding="utf-8") as fh:
        data = json.load(fh)

    # Resolve relative paths back to absolute using the project file's location
    for key in ("template_path", "excel_path"):
        data[key] = _to_absolute(data.get(key, ""), path)

    return data
