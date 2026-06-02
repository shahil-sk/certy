"""
Sheet picker dialog -- shown when an xlsx has multiple sheets.
Clean modal: white background, list of sheets, confirm / cancel.
"""
import tkinter as tk

from app.constants import (
    C, FONT_FAMILY_UI,
    FONT_SZ_SM, FONT_SZ_MD, FONT_SZ_LG,
    PAD_SM, PAD_MD, PAD_LG,
)


class SheetPickerDialog(tk.Toplevel):

    def __init__(self, parent, sheet_names: list[str]):
        super().__init__(parent)
        self.title("Select Sheet")
        self.resizable(False, False)
        self.configure(bg=C["surface"])
        self.grab_set()

        self._result: str | None = None
        self._build(sheet_names)
        self._center(parent)

    # ------------------------------------------------------------------
    def _build(self, names: list[str]) -> None:
        # header
        tk.Label(
            self,
            text="Select a sheet",
            font=(FONT_FAMILY_UI, FONT_SZ_LG, "bold"),
            fg=C["text"],
            bg=C["surface"],
        ).pack(anchor="w", padx=PAD_LG, pady=(PAD_LG, PAD_SM))

        tk.Label(
            self,
            text="This workbook contains multiple sheets.",
            font=(FONT_FAMILY_UI, FONT_SZ_SM),
            fg=C["subtext"],
            bg=C["surface"],
        ).pack(anchor="w", padx=PAD_LG, pady=(0, PAD_MD))

        # list frame with 1px border
        list_outer = tk.Frame(
            self,
            bg=C["border"],
            padx=1, pady=1,
        )
        list_outer.pack(fill="x", padx=PAD_LG, pady=(0, PAD_MD))

        list_inner = tk.Frame(list_outer, bg=C["surface"])
        list_inner.pack(fill="x")

        self._var = tk.StringVar(value=names[0] if names else "")

        for name in names:
            rb = tk.Radiobutton(
                list_inner,
                text=name,
                variable=self._var,
                value=name,
                font=(FONT_FAMILY_UI, FONT_SZ_SM),
                fg=C["text"],
                bg=C["surface"],
                selectcolor=C["accent_dim"],
                activebackground=C["surface2"],
                activeforeground=C["text"],
                relief="flat",
                bd=0,
                highlightthickness=0,
                anchor="w",
                cursor="hand2",
            )
            rb.pack(fill="x", padx=PAD_SM, pady=2)

        # divider
        tk.Frame(self, bg=C["border"], height=1).pack(fill="x", padx=PAD_LG)

        # buttons
        btn_row = tk.Frame(self, bg=C["surface"])
        btn_row.pack(fill="x", padx=PAD_LG, pady=PAD_MD)

        tk.Button(
            btn_row,
            text="Cancel",
            command=self.destroy,
            bg=C["btn_idle"], fg=C["text"],
            relief="flat", cursor="hand2",
            font=(FONT_FAMILY_UI, FONT_SZ_SM),
            activebackground=C["btn_hover"],
            activeforeground=C["text"],
            bd=0, highlightthickness=0,
            padx=12, pady=6,
        ).pack(side="right", padx=(4, 0))

        tk.Button(
            btn_row,
            text="Open Sheet",
            command=self._confirm,
            bg=C["accent"], fg=C["text_inv"],
            relief="flat", cursor="hand2",
            font=(FONT_FAMILY_UI, FONT_SZ_SM, "bold"),
            activebackground=C["accent2"],
            activeforeground=C["text_inv"],
            bd=0, highlightthickness=0,
            padx=12, pady=6,
        ).pack(side="right")

    def _confirm(self) -> None:
        self._result = self._var.get()
        self.destroy()

    def _center(self, parent) -> None:
        self.update_idletasks()
        pw = parent.winfo_width() or 800
        ph = parent.winfo_height() or 600
        px = parent.winfo_rootx()
        py = parent.winfo_rooty()
        w, h = self.winfo_width(), self.winfo_height()
        x = px + (pw - w) // 2
        y = py + (ph - h) // 2
        self.geometry(f"+{x}+{y}")

    @property
    def result(self) -> str | None:
        return self._result
