"""
Left sidebar: field settings, action buttons, log output.
Clean card-based layout. Single-pixel dividers. No heavy chrome.
"""
import tkinter as tk
from tkinter import ttk

from app.constants import (
    C, SIDEBAR_W,
    FONT_FAMILY_UI, FONT_SZ_SM, FONT_SZ_MD, FONT_SZ_LG,
    PAD_SM, PAD_MD, PAD_LG,
)
from app.ui.widgets import flat_button, hsep

_OUTPUT_FORMATS = ["PDF", "PNG", "JPEG", "WebP"]


class ControlPanel(tk.Frame):

    def __init__(self, parent, preview_cmd, generate_cmd):
        super().__init__(
            parent,
            bg=C["surface2"],
            width=SIDEBAR_W,
        )
        self.pack(side="left", fill="y", padx=(0, 8), pady=0)
        self.pack_propagate(False)

        # public StringVars that core.py reads and writes
        self.filename_pattern = tk.StringVar(value="{Name}")
        self.output_format    = tk.StringVar(value="PDF")

        self._build(preview_cmd, generate_cmd)

    # ------------------------------------------------------------------
    def _build(self, preview_cmd, generate_cmd):
        # ---- section: Fields -----------------------------------------
        self._section_header("Fields")

        self.fields_frame = tk.Frame(self, bg=C["surface2"])
        self.fields_frame.pack(fill="x", padx=PAD_SM, pady=(0, PAD_SM))

        hsep(self, padx=PAD_SM)

        # ---- section: Output settings --------------------------------
        self._section_header("Output")

        out_card = tk.Frame(self, bg=C["surface2"])
        out_card.pack(fill="x", padx=PAD_SM, pady=(0, PAD_SM))

        # filename pattern
        tk.Label(
            out_card,
            text="Filename pattern",
            font=(FONT_FAMILY_UI, FONT_SZ_SM),
            fg=C["subtext"],
            bg=C["surface2"],
            anchor="w",
        ).pack(fill="x", pady=(0, 2))

        tk.Entry(
            out_card,
            textvariable=self.filename_pattern,
            font=(FONT_FAMILY_UI, FONT_SZ_SM),
            bg=C["surface"],
            fg=C["text"],
            relief="flat",
            bd=0,
            highlightthickness=1,
            highlightbackground=C["border"],
            highlightcolor=C["accent"],
            insertbackground=C["text"],
        ).pack(fill="x", ipady=4, pady=(0, PAD_SM))

        # output format dropdown
        tk.Label(
            out_card,
            text="Output format",
            font=(FONT_FAMILY_UI, FONT_SZ_SM),
            fg=C["subtext"],
            bg=C["surface2"],
            anchor="w",
        ).pack(fill="x", pady=(0, 2))

        fmt_row = tk.Frame(out_card, bg=C["surface2"])
        fmt_row.pack(fill="x", pady=(0, PAD_SM))

        for fmt in _OUTPUT_FORMATS:
            rb = tk.Radiobutton(
                fmt_row,
                text=fmt,
                variable=self.output_format,
                value=fmt,
                bg=C["surface2"],
                fg=C["text"],
                selectcolor=C["accent_dim"],
                activebackground=C["surface2"],
                activeforeground=C["text"],
                font=(FONT_FAMILY_UI, FONT_SZ_SM),
                relief="flat",
                bd=0,
                highlightthickness=0,
                cursor="hand2",
            )
            rb.pack(side="left", padx=(0, PAD_SM))

        hsep(self, padx=PAD_SM)

        # ---- section: Actions ----------------------------------------
        self._section_header("Actions")

        action_row = tk.Frame(self, bg=C["surface2"])
        action_row.pack(fill="x", padx=PAD_SM, pady=(0, PAD_SM))

        self._btn_preview = flat_button(
            action_row,
            text="Preview",
            command=preview_cmd,
            bg=C["btn_idle"],
            active_bg=C["btn_hover"],
            fg=C["text"],
            active_fg=C["text"],
            font_size=FONT_SZ_SM,
        )
        self._btn_preview.pack(side="left", fill="x", expand=True, padx=(0, 4))

        self._btn_generate = flat_button(
            action_row,
            text="Generate All",
            command=generate_cmd,
            bg=C["accent"],
            active_bg=C["accent2"],
            font_size=FONT_SZ_SM,
            bold=True,
        )
        self._btn_generate.pack(side="left", fill="x", expand=True)

        # progress bar
        self._progress = ttk.Progressbar(
            self, style="Thin.Horizontal.TProgressbar",
            orient="horizontal", mode="determinate",
        )
        self._progress.pack(fill="x", padx=PAD_SM, pady=(4, PAD_SM))

        hsep(self, padx=PAD_SM)

        # ---- section: Log --------------------------------------------
        self._section_header("Log")

        log_frame = tk.Frame(self, bg=C["surface2"])
        log_frame.pack(fill="both", expand=True, padx=PAD_SM, pady=(0, PAD_SM))

        self._log = tk.Text(
            log_frame,
            bg=C["log_bg"],
            fg=C["subtext"],
            font=(FONT_FAMILY_UI, FONT_SZ_SM),
            relief="flat",
            bd=0,
            highlightthickness=1,
            highlightbackground=C["border"],
            wrap="word",
            state="disabled",
            cursor="arrow",
            padx=8,
            pady=6,
            spacing1=2,
        )
        self._log.pack(fill="both", expand=True)

        # coloured log tags
        self._log.tag_config("ok",      foreground=C["success"])
        self._log.tag_config("err",     foreground=C["danger"])
        self._log.tag_config("warn",    foreground=C["warning"])
        self._log.tag_config("accent",  foreground=C["accent"])
        self._log.tag_config("muted",   foreground=C["muted"])

    # ------------------------------------------------------------------
    def _section_header(self, title: str) -> None:
        """Small uppercase section label."""
        tk.Label(
            self,
            text=title.upper(),
            font=(FONT_FAMILY_UI, FONT_SZ_SM - 1, "bold"),
            fg=C["muted"],
            bg=C["surface2"],
            anchor="w",
        ).pack(fill="x", padx=PAD_SM + 2, pady=(PAD_MD, 4))

    # ------------------------------------------------------------------
    def set_progress(self, value: float) -> None:
        """value: 0.0 -- 1.0"""
        self._progress["value"] = value * 100

    def append_log(self, msg: str, clear: bool = False) -> None:
        self._log.config(state="normal")
        if clear:
            self._log.delete("1.0", "end")

        # pick tag from message prefix
        tag = None
        low = msg.lower()
        if low.startswith(("error", "fail", "[err")):
            tag = "err"
        elif low.startswith(("warn", "[warn")):
            tag = "warn"
        elif low.startswith(("ok", "done", "saved", "generated", "[ok")):
            tag = "ok"
        elif low.startswith(("info", "[info")):
            tag = "accent"

        self._log.insert("end", msg + "\n", tag or "")
        self._log.see("end")
        self._log.config(state="disabled")
