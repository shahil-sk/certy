"""
Misc dialogs: certificate preview, colour pickers.
"""
import tkinter as tk
from tkinter import colorchooser

from PIL import ImageTk

from app.constants import (
    C, FONT_FAMILY_UI, FONT_SZ_SM, FONT_SZ_MD,
    PAD_SM, PAD_MD, PAD_LG,
)
from app.helpers import cmyk_to_hex


# ---------------------------------------------------------------------------
def show_preview(parent, pil_image) -> None:
    """Show a certificate preview in a centered modal window."""
    win = tk.Toplevel(parent)
    win.title("Preview")
    win.configure(bg=C["surface"])
    win.grab_set()
    win.resizable(True, True)

    # constrain to 90% of screen
    sw = parent.winfo_screenwidth()
    sh = parent.winfo_screenheight()
    max_w = int(sw * 0.9)
    max_h = int(sh * 0.85)

    img_w, img_h = pil_image.size
    scale = min(max_w / img_w, max_h / img_h, 1.0)
    disp_w = max(int(img_w * scale), 1)
    disp_h = max(int(img_h * scale), 1)

    resized = pil_image.resize((disp_w, disp_h))
    photo   = ImageTk.PhotoImage(resized)

    # toolbar
    bar = tk.Frame(win, bg=C["surface2"], height=36)
    bar.pack(fill="x")
    bar.pack_propagate(False)
    tk.Label(
        bar,
        text="Certificate Preview",
        font=(FONT_FAMILY_UI, FONT_SZ_MD, "bold"),
        fg=C["text"], bg=C["surface2"],
    ).pack(side="left", padx=PAD_MD)
    tk.Button(
        bar,
        text="Close",
        command=win.destroy,
        bg=C["surface2"], fg=C["subtext"],
        relief="flat", cursor="hand2",
        font=(FONT_FAMILY_UI, FONT_SZ_SM),
        activebackground=C["btn_idle"],
        activeforeground=C["text"],
        bd=0, highlightthickness=0,
        padx=10, pady=6,
    ).pack(side="right", padx=PAD_SM)

    # 1px divider
    tk.Frame(win, bg=C["border"], height=1).pack(fill="x")

    # image
    lbl = tk.Label(win, image=photo, bg=C["canvas_bg"])
    lbl.image = photo  # keep reference
    lbl.pack(padx=PAD_MD, pady=PAD_MD)

    win.update_idletasks()
    # center on parent
    pw = parent.winfo_width()
    ph = parent.winfo_height()
    px = parent.winfo_rootx()
    py = parent.winfo_rooty()
    w  = win.winfo_width()
    h  = win.winfo_height()
    win.geometry(f"+{px + (pw - w) // 2}+{py + (ph - h) // 2}")


# ---------------------------------------------------------------------------
def pick_color_rgb(parent, initial: str = "#000000") -> str | None:
    """Open the system colour picker; return hex string or None."""
    _, hex_color = colorchooser.askcolor(
        color=initial, parent=parent, title="Pick colour")
    return hex_color


def pick_color_cmyk(parent, initial_hex: str = "#000000") -> str | None:
    """
    Simple CMYK input dialog.
    Returns an RGB hex string (converted from CMYK) or None on cancel.
    """
    win = tk.Toplevel(parent)
    win.title("CMYK Colour")
    win.configure(bg=C["surface"])
    win.resizable(False, False)
    win.grab_set()

    result: list[str | None] = [None]

    tk.Label(
        win,
        text="CMYK Colour",
        font=(FONT_FAMILY_UI, FONT_SZ_MD, "bold"),
        fg=C["text"], bg=C["surface"],
    ).pack(anchor="w", padx=PAD_LG, pady=(PAD_LG, PAD_SM))

    form = tk.Frame(win, bg=C["surface"])
    form.pack(padx=PAD_LG, pady=(0, PAD_MD))

    entries: dict[str, tk.Entry] = {}
    for i, ch in enumerate(("C", "M", "Y", "K")):
        tk.Label(
            form, text=ch,
            font=(FONT_FAMILY_UI, FONT_SZ_SM, "bold"),
            fg=C["subtext"], bg=C["surface"], width=2,
        ).grid(row=0, column=i * 2, padx=(0, 4))
        e = tk.Entry(
            form, width=5,
            font=(FONT_FAMILY_UI, FONT_SZ_SM),
            fg=C["text"], bg=C["surface3"],
            relief="flat", bd=0,
            highlightthickness=1,
            highlightbackground=C["border"],
            highlightcolor=C["accent"],
            insertbackground=C["text"],
        )
        e.insert(0, "0")
        e.grid(row=0, column=i * 2 + 1, padx=(0, 12))
        entries[ch] = e

    tk.Frame(win, bg=C["border"], height=1).pack(fill="x", padx=PAD_LG)

    btn_row = tk.Frame(win, bg=C["surface"])
    btn_row.pack(fill="x", padx=PAD_LG, pady=PAD_MD)

    def _cancel():
        win.destroy()

    def _ok():
        try:
            vals = [max(0, min(100, int(entries[c].get()))) for c in "CMYK"]
            result[0] = cmyk_to_hex(*vals)
        except ValueError:
            pass
        win.destroy()

    tk.Button(
        btn_row, text="Cancel", command=_cancel,
        bg=C["btn_idle"], fg=C["text"],
        relief="flat", cursor="hand2",
        font=(FONT_FAMILY_UI, FONT_SZ_SM),
        activebackground=C["btn_hover"],
        activeforeground=C["text"],
        bd=0, highlightthickness=0, padx=12, pady=6,
    ).pack(side="right", padx=(4, 0))

    tk.Button(
        btn_row, text="Apply", command=_ok,
        bg=C["accent"], fg=C["text_inv"],
        relief="flat", cursor="hand2",
        font=(FONT_FAMILY_UI, FONT_SZ_SM, "bold"),
        activebackground=C["accent2"],
        activeforeground=C["text_inv"],
        bd=0, highlightthickness=0, padx=12, pady=6,
    ).pack(side="right")

    win.update_idletasks()
    pw = parent.winfo_width()
    ph = parent.winfo_height()
    px = parent.winfo_rootx()
    py = parent.winfo_rooty()
    w  = win.winfo_width()
    h  = win.winfo_height()
    win.geometry(f"+{px + (pw - w) // 2}+{py + (ph - h) // 2}")

    win.wait_window()
    return result[0]
