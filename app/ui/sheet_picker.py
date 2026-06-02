"""
Sheet picker dialog.
Shown when the user opens an xlsx workbook with more than one sheet.
Returns the chosen sheet name, or None if the dialog was dismissed.
"""
import tkinter as tk
from tkinter import ttk

from app.constants import C


class SheetPickerDialog(tk.Toplevel):
    """
    Modal sheet picker.

    Usage:
        dlg = SheetPickerDialog(parent, sheet_names)
        parent.wait_window(dlg)
        chosen = dlg.result  # str or None
    """

    def __init__(self, parent: tk.Misc, names: list[str]):
        super().__init__(parent)
        self.title("Select sheet")
        self.resizable(False, False)
        self.configure(bg=C["surface"])
        self.result: str | None = None

        self._build(names)
        self._centre(parent)

        # Make modal
        self.grab_set()
        self.focus_set()
        self.protocol("WM_DELETE_WINDOW", self._cancel)

    # ------------------------------------------------------------------
    def _build(self, names: list[str]) -> None:
        pad = dict(padx=16, pady=8)

        tk.Label(
            self,
            text="This workbook has multiple sheets.\nSelect the sheet to load:",
            font=("Segoe UI", 9),
            fg=C["text"], bg=C["surface"],
            justify="left",
        ).pack(anchor="w", padx=16, pady=(14, 4))

        # Listbox in a frame so we can add a scrollbar cleanly
        list_frame = tk.Frame(self, bg=C["surface"])
        list_frame.pack(fill="both", expand=True, padx=16, pady=4)

        vsb = ttk.Scrollbar(list_frame, orient="vertical",
                            style="Dark.Vertical.TScrollbar")
        vsb.pack(side="right", fill="y")

        self._listbox = tk.Listbox(
            list_frame,
            font=("Segoe UI", 9),
            bg=C["surface3"], fg=C["text"],
            selectbackground=C["accent"],
            selectforeground=C["white"],
            activestyle="none",
            relief="flat", bd=0,
            highlightthickness=1,
            highlightbackground=C["border"],
            yscrollcommand=vsb.set,
            height=min(len(names), 10),
        )
        self._listbox.pack(side="left", fill="both", expand=True)
        vsb.configure(command=self._listbox.yview)

        for name in names:
            self._listbox.insert(tk.END, name)
        self._listbox.selection_set(0)
        self._listbox.bind("<Double-Button-1>", lambda _: self._confirm())

        # Buttons
        btn_row = tk.Frame(self, bg=C["surface"])
        btn_row.pack(fill="x", padx=16, pady=(4, 14))

        tk.Button(
            btn_row, text="Cancel",
            command=self._cancel,
            bg=C["surface2"], fg=C["subtext"],
            relief="flat", bd=0, cursor="hand2",
            font=("Segoe UI", 9),
            activebackground=C["surface3"],
            activeforeground=C["text"],
            padx=14, pady=6,
        ).pack(side="right", padx=(6, 0))

        tk.Button(
            btn_row, text="Load sheet",
            command=self._confirm,
            bg=C["accent"], fg=C["white"],
            relief="flat", bd=0, cursor="hand2",
            font=("Segoe UI", 9, "bold"),
            activebackground=C["accent2"],
            activeforeground=C["white"],
            padx=14, pady=6,
        ).pack(side="right")

    # ------------------------------------------------------------------
    def _centre(self, parent: tk.Misc) -> None:
        self.update_idletasks()
        pw = parent.winfo_rootx() + parent.winfo_width()  // 2
        ph = parent.winfo_rooty() + parent.winfo_height() // 2
        w  = self.winfo_width()
        h  = self.winfo_height()
        self.geometry(f"+{pw - w // 2}+{ph - h // 2}")

    def _confirm(self) -> None:
        sel = self._listbox.curselection()
        if sel:
            self.result = self._listbox.get(sel[0])
        self.destroy()

    def _cancel(self) -> None:
        self.result = None
        self.destroy()
