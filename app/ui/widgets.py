"""
Reusable tkinter widget factory functions.
All styling is derived from app.constants.C -- never hard-code colours here.
"""
import tkinter as tk
from tkinter import ttk

from app.constants import C, FONT_FAMILY_UI


# ---------------------------------------------------------------------------
# Basic factories
# ---------------------------------------------------------------------------
def flat_button(
    parent, text: str, command,
    bg: str, active_bg: str,
    fg: str | None = None,
    active_fg: str | None = None,
    font_size: int = 10, bold: bool = False,
    **kw,
) -> tk.Button:
    weight = "bold" if bold else "normal"
    return tk.Button(
        parent, text=text, command=command,
        bg=bg,
        fg=fg or C["text_inv"],
        relief="flat", cursor="hand2",
        font=(FONT_FAMILY_UI, font_size, weight),
        activebackground=active_bg,
        activeforeground=active_fg or C["text_inv"],
        bd=0, highlightthickness=0,
        padx=10, pady=5,
        **kw,
    )


def secondary_button(
    parent, text: str, command,
    font_size: int = 10, bold: bool = False,
    **kw,
) -> tk.Button:
    """Neutral secondary button -- no accent color."""
    weight = "bold" if bold else "normal"
    return tk.Button(
        parent, text=text, command=command,
        bg=C["btn_idle"],
        fg=C["text"],
        relief="flat", cursor="hand2",
        font=(FONT_FAMILY_UI, font_size, weight),
        activebackground=C["btn_hover"],
        activeforeground=C["text"],
        bd=0, highlightthickness=0,
        padx=10, pady=5,
        **kw,
    )


def label(
    parent, text: str,
    font_size: int = 10, bold: bool = False,
    color: str | None = None, bg: str | None = None,
    **kw,
) -> tk.Label:
    weight = "bold" if bold else "normal"
    return tk.Label(
        parent, text=text,
        font=(FONT_FAMILY_UI, font_size, weight),
        fg=color or C["text"],
        bg=bg or C["surface"],
        **kw,
    )


def hsep(parent, padx: int = 0, pady: int = 4) -> tk.Frame:
    """1-px horizontal separator in border color."""
    f = tk.Frame(parent, bg=C["border"], height=1)
    f.pack(fill="x", padx=padx, pady=pady)
    return f


def card(parent, **kw) -> tk.Frame:
    """A clean card frame with a single-pixel border."""
    return tk.Frame(
        parent,
        bg=kw.pop("bg", C["surface"]),
        highlightthickness=1,
        highlightbackground=C["border"],
        **kw,
    )


# ---------------------------------------------------------------------------
# TTK styles -- call once at startup
# ---------------------------------------------------------------------------
def setup_ttk_styles() -> None:
    s = ttk.Style()
    s.theme_use("clam")

    # progress bar
    s.configure(
        "Thin.Horizontal.TProgressbar",
        troughcolor=C["surface3"],
        background=C["accent"],
        thickness=4,
        borderwidth=0,
    )

    # combobox -- clean, no thick border
    s.configure(
        "Flat.TCombobox",
        fieldbackground=C["surface3"],
        background=C["surface3"],
        foreground=C["text"],
        selectbackground=C["accent_dim"],
        selectforeground=C["text"],
        borderwidth=1,
        relief="flat",
        arrowcolor=C["subtext"],
        padding=(6, 4),
    )
    s.map(
        "Flat.TCombobox",
        fieldbackground=[("readonly", C["surface3"]), ("focus", C["surface"])],
        foreground=[("readonly", C["text"])],
        bordercolor=[("focus", C["border2"])],
    )

    # scrollbars -- thin, warm-neutral
    for name in ("Warm.Vertical.TScrollbar", "Warm.Horizontal.TScrollbar"):
        orient = "vertical" if "Vertical" in name else "horizontal"
        s.configure(
            name,
            background=C["surface3"],
            troughcolor=C["bg"],
            borderwidth=0,
            arrowsize=10,
            arrowcolor=C["muted"],
            relief="flat",
        )
        s.map(name, background=[("active", C["border2"])])

    # also keep the old names so canvas_area still works without changes
    for old in ("Dark.Vertical.TScrollbar", "Dark.Horizontal.TScrollbar"):
        s.configure(
            old,
            background=C["surface3"],
            troughcolor=C["bg"],
            borderwidth=0,
            arrowsize=10,
            arrowcolor=C["muted"],
        )
        s.map(old, background=[("active", C["border2"])])
