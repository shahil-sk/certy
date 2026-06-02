"""
Bottom status bar.
Single line, warm neutral background, left-aligned message.
"""
import tkinter as tk

from app.constants import C, FONT_FAMILY_UI, FONT_SZ_SM, PAD_SM, PAD_MD


class StatusBar(tk.Frame):

    def __init__(self, parent):
        super().__init__(parent, bg=C["surface2"], height=26)
        self.pack(side="bottom", fill="x")
        self.pack_propagate(False)

        # 1-px top border
        tk.Frame(parent, bg=C["border"], height=1).pack(side="bottom", fill="x")

        self._var = tk.StringVar(value="Ready")
        self._dot = tk.Label(
            self, text="●",
            font=(FONT_FAMILY_UI, 8),
            fg=C["muted"], bg=C["surface2"],
        )
        self._dot.pack(side="left", padx=(PAD_MD, 4), pady=0)

        self._lbl = tk.Label(
            self,
            textvariable=self._var,
            font=(FONT_FAMILY_UI, FONT_SZ_SM),
            fg=C["subtext"],
            bg=C["surface2"],
            anchor="w",
        )
        self._lbl.pack(side="left", fill="x", expand=True)

    def set(self, msg: str, ok: bool = True) -> None:
        self._var.set(msg)
        if ok:
            self._dot.config(fg=C["success"])
            self._lbl.config(fg=C["subtext"])
        else:
            self._dot.config(fg=C["danger"])
            self._lbl.config(fg=C["danger"])
