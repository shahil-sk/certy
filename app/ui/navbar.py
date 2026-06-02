"""
Top navigation bar.
Clean white bar with app title on the left and action buttons on the right.
No heavy borders -- just a single 1px bottom divider.
"""
import tkinter as tk

from app.constants import (
    C, APP_TITLE, APP_VERSION,
    FONT_FAMILY_UI, FONT_SZ_MD, FONT_SZ_SM, FONT_SZ_LG,
    PAD_MD, PAD_SM,
)


class NavBar(tk.Frame):

    def __init__(
        self, parent,
        save_cmd, load_cmd,
        load_template_cmd, load_excel_cmd,
    ):
        super().__init__(parent, bg=C["nav"], height=48)
        self.pack(fill="x")
        self.pack_propagate(False)

        self._build(
            save_cmd=save_cmd,
            load_cmd=load_cmd,
            load_template_cmd=load_template_cmd,
            load_excel_cmd=load_excel_cmd,
        )

        # single 1-px bottom border
        tk.Frame(parent, bg=C["border"], height=1).pack(fill="x")

    # ------------------------------------------------------------------
    def _build(self, save_cmd, load_cmd, load_template_cmd, load_excel_cmd):
        # -- left: logo + title
        left = tk.Frame(self, bg=C["nav"])
        left.pack(side="left", padx=(PAD_MD + 4, 0))

        # simple geometric logo mark -- two overlapping rectangles
        logo_canvas = tk.Canvas(
            left, width=22, height=22,
            bg=C["nav"], highlightthickness=0,
        )
        logo_canvas.pack(side="left", padx=(0, 8))
        # background rect
        logo_canvas.create_rectangle(2, 6, 16, 20, fill=C["accent_dim"], outline="")
        # foreground rect
        logo_canvas.create_rectangle(7, 2, 21, 16, fill=C["accent"], outline="")

        tk.Label(
            left,
            text=APP_TITLE,
            font=(FONT_FAMILY_UI, FONT_SZ_LG, "bold"),
            fg=C["text"],
            bg=C["nav"],
        ).pack(side="left")

        tk.Label(
            left,
            text=f"v{APP_VERSION}",
            font=(FONT_FAMILY_UI, FONT_SZ_SM),
            fg=C["muted"],
            bg=C["nav"],
            padx=4,
        ).pack(side="left")

        # -- right: action buttons
        right = tk.Frame(self, bg=C["nav"])
        right.pack(side="right", padx=PAD_MD)

        actions = [
            ("Load Template",  load_template_cmd, False),
            ("Load Excel",     load_excel_cmd,    False),
            ("Load Project",   load_cmd,          False),
            ("Save Project",   save_cmd,          True),
        ]

        for text, cmd, is_primary in actions:
            if is_primary:
                btn = tk.Button(
                    right, text=text, command=cmd,
                    bg=C["accent"], fg=C["text_inv"],
                    font=(FONT_FAMILY_UI, FONT_SZ_SM),
                    relief="flat", cursor="hand2",
                    activebackground=C["accent2"],
                    activeforeground=C["text_inv"],
                    bd=0, highlightthickness=0,
                    padx=12, pady=6,
                )
            else:
                btn = tk.Button(
                    right, text=text, command=cmd,
                    bg=C["nav"], fg=C["subtext"],
                    font=(FONT_FAMILY_UI, FONT_SZ_SM),
                    relief="flat", cursor="hand2",
                    activebackground=C["btn_idle"],
                    activeforeground=C["text"],
                    bd=0, highlightthickness=0,
                    padx=10, pady=6,
                )
            btn.pack(side="left", padx=2)
