"""
Scrollable field editor list in the sidebar.

Each field card exposes two render modes:
  text  -- font / size / colour / align / opacity / shadow / outline
  qr    -- QR code sized by a pixel-size spinner

Toggling the QR button swaps the visible controls in-place so the
sidebar doesn't reflow the whole list.
"""
import tkinter as tk
from tkinter import ttk

from app.constants import C
from app.ui.widgets import label

_ALIGN_OPTIONS = [("L", "left"), ("C", "center"), ("R", "right")]


class FieldList(tk.Frame):

    def __init__(self, parent):
        super().__init__(parent, bg=C["surface"])
        self.pack(fill="x")

    def rebuild(self, fields, field_vars, font_settings,
                available_fonts, update_cb, color_cb):
        for w in self.winfo_children():
            w.destroy()

        cv  = tk.Canvas(self, height=360, bg=C["surface"], highlightthickness=0)
        vsb = ttk.Scrollbar(self, orient="vertical", command=cv.yview,
                            style="Dark.Vertical.TScrollbar")
        inner = tk.Frame(cv, bg=C["surface"])
        inner.bind("<Configure>",
                   lambda e: cv.configure(scrollregion=cv.bbox("all")))
        cv.create_window((0, 0), window=inner, anchor="nw")
        cv.configure(yscrollcommand=vsb.set)

        cv.bind("<Enter>", lambda e, c=cv: c.bind_all(
            "<MouseWheel>",
            lambda ev: c.yview_scroll(int(-1 * (ev.delta / 120)), "units")))
        cv.bind("<Leave>", lambda e, c=cv: c.unbind_all("<MouseWheel>"))

        for i, field in enumerate(fields):
            _FieldCard(inner, field, field_vars, font_settings,
                       available_fonts, update_cb, color_cb,
                       alt=(i % 2 == 1))

        vsb.pack(side="right", fill="y")
        cv.pack(side="left", fill="both", expand=True)


class _FieldCard(tk.Frame):

    def __init__(self, parent, field, field_vars, font_settings,
                 available_fonts, update_cb, color_cb, alt=False):
        bg = C["row_alt"] if alt else C["surface"]
        super().__init__(parent, bg=bg)
        self.pack(fill="x")
        tk.Frame(self, bg=C["border"], height=1).pack(fill="x", side="bottom")
        self._build(field, field_vars, font_settings,
                    available_fonts, update_cb, color_cb, bg)

    def _build(self, field, field_vars, font_settings,
               available_fonts, update_cb, color_cb, bg):
        pad = tk.Frame(self, bg=bg, padx=12, pady=8)
        pad.pack(fill="x")

        s = font_settings[field]

        # ── Row 1: field name + QR toggle + visible toggle ──────────────
        r1 = tk.Frame(pad, bg=bg)
        r1.pack(fill="x", pady=(0, 5))
        tk.Label(r1, text=field.upper(), font=("Segoe UI", 7, "bold"),
                 fg=C["accent"], bg=bg).pack(side="left")

        # Visible toggle (rightmost)
        vis_frame = tk.Frame(r1, bg=bg)
        vis_frame.pack(side="right")
        tk.Label(vis_frame, text="show", font=("Segoe UI", 7),
                 fg=C["subtext"], bg=bg).pack(side="left", padx=(0, 3))
        _ToggleSwitch(vis_frame, field_vars[field],
                      lambda f=field: update_cb(f), bg=bg).pack(side="left")

        # QR mode toggle button (left of visible toggle)
        qr_btn_frame = tk.Frame(r1, bg=bg)
        qr_btn_frame.pack(side="right", padx=(0, 8))

        qr_var = s.get("field_type")
        is_qr  = (qr_var is not None) and (qr_var.get() == "qr")

        qr_btn = tk.Button(
            qr_btn_frame, text="QR",
            font=("Segoe UI", 7, "bold"),
            relief="flat", bd=0, cursor="hand2",
            padx=6, pady=2,
            bg=C["accent"]  if is_qr else C["btn_idle"],
            fg=C["white"]   if is_qr else C["subtext"],
            activebackground=C["accent2"],
            activeforeground=C["white"],
        )
        qr_btn.pack()

        # ── Text-mode controls (rows 2-5) ────────────────────────────────
        text_frame = tk.Frame(pad, bg=bg)
        text_frame.pack(fill="x")
        self._build_text_controls(
            text_frame, field, s, available_fonts, update_cb, color_cb, bg)

        # ── QR-mode controls ─────────────────────────────────────────────
        qr_frame = tk.Frame(pad, bg=bg)
        # (packed only when QR mode is active)
        self._build_qr_controls(qr_frame, field, s, update_cb, bg)

        # Wire QR toggle
        def _toggle_qr(f=field):
            current = s.get("field_type")
            if current is None:
                return
            new_type = "text" if current.get() == "qr" else "qr"
            current.set(new_type)
            active = new_type == "qr"
            qr_btn.config(
                bg=C["accent"] if active else C["btn_idle"],
                fg=C["white"]  if active else C["subtext"],
            )
            if active:
                text_frame.pack_forget()
                qr_frame.pack(fill="x")
            else:
                qr_frame.pack_forget()
                text_frame.pack(fill="x")
            update_cb(f)

        qr_btn.config(command=_toggle_qr)

        # Set initial visibility
        if is_qr:
            text_frame.pack_forget()
            qr_frame.pack(fill="x")

    # ------------------------------------------------------------------
    def _build_text_controls(self, parent, field, s,
                             available_fonts, update_cb, color_cb, bg):
        # ── Row 2: size + font ────────────────────────────────────────
        r2 = tk.Frame(parent, bg=bg)
        r2.pack(fill="x", pady=(0, 4))
        tk.Label(r2, text="Sz", font=("Segoe UI", 7),
                 fg=C["subtext"], bg=bg).pack(side="left")
        spin = tk.Spinbox(
            r2, from_=6, to=300, width=4,
            textvariable=s["size"],
            font=("Segoe UI", 8),
            bg=C["surface3"], fg=C["text"],
            buttonbackground=C["surface3"],
            insertbackground=C["text"],
            relief="flat", bd=0,
            highlightthickness=1, highlightbackground=C["border"],
            command=lambda f=field: update_cb(f),
        )
        spin.bind("<Return>", lambda e, f=field: update_cb(f))
        spin.pack(side="left", padx=(3, 8))
        tk.Label(r2, text="Font", font=("Segoe UI", 7),
                 fg=C["subtext"], bg=bg).pack(side="left")
        cb = ttk.Combobox(
            r2, values=available_fonts,
            textvariable=s["font_name"],
            width=11, state="readonly", style="Flat.TCombobox",
        )
        cb.bind("<<ComboboxSelected>>", lambda e, f=field: update_cb(f))
        cb.pack(side="left", padx=(3, 0))

        # ── Row 3: colour + alignment ─────────────────────────────────
        r3 = tk.Frame(parent, bg=bg)
        r3.pack(fill="x", pady=(0, 4))
        swatch = tk.Button(
            r3, width=3, height=1,
            bg=s["color"].get(),
            relief="flat", bd=0, cursor="hand2",
            highlightthickness=2, highlightbackground=C["border"],
            command=lambda f=field: color_cb(f),
        )
        swatch.pack(side="left", padx=(0, 5))
        s["_swatch"] = swatch
        tk.Label(r3, text="Color", font=("Segoe UI", 7),
                 fg=C["subtext"], bg=bg).pack(side="left", padx=(0, 8))

        tk.Label(r3, text="Align", font=("Segoe UI", 7),
                 fg=C["subtext"], bg=bg).pack(side="left", padx=(0, 3))
        align_var = s["align"]
        pill_refs = {}

        def _set_align(val, f=field):
            align_var.set(val)
            for v, b in pill_refs.items():
                b.config(
                    bg=C["btn_active"] if v == val else C["btn_idle"],
                    fg=C["white"]      if v == val else C["subtext"],
                )
            update_cb(f)

        for sym, val in _ALIGN_OPTIONS:
            active = align_var.get() == val
            b = tk.Button(
                r3, text=sym,
                command=lambda v=val: _set_align(v),
                bg=C["btn_active"] if active else C["btn_idle"],
                fg=C["white"]      if active else C["subtext"],
                font=("Segoe UI", 8, "bold"),
                relief="flat", bd=0, cursor="hand2",
                activebackground=C["accent2"],
                activeforeground=C["white"],
                width=2, pady=1,
            )
            b.pack(side="left", padx=(0, 2))
            pill_refs[val] = b

        # ── Row 4: opacity slider ──────────────────────────────────────
        r4 = tk.Frame(parent, bg=bg)
        r4.pack(fill="x", pady=(0, 4))
        tk.Label(r4, text="Opacity", font=("Segoe UI", 7),
                 fg=C["subtext"], bg=bg).pack(side="left")
        opac_lbl = tk.Label(r4, text="100%", font=("Segoe UI", 7),
                            fg=C["text"], bg=bg, width=4)
        opac_lbl.pack(side="right")

        def _opac_changed(val, f=field):
            opac_lbl.config(text=f"{int(float(val))}%")
            update_cb(f)

        tk.Scale(
            r4, from_=0, to=100, orient="horizontal",
            variable=s["opacity"],
            command=_opac_changed,
            bg=bg, fg=C["text"],
            troughcolor=C["surface3"],
            highlightthickness=0, relief="flat",
            showvalue=False, length=140,
        ).pack(side="left", padx=(4, 0), fill="x", expand=True)

        # ── Row 5: shadow + outline toggles ───────────────────────────
        r5 = tk.Frame(parent, bg=bg)
        r5.pack(fill="x")

        def _toggle_btn(p, label_text, var, f):
            def _toggle():
                var.set(not var.get())
                b.config(
                    bg=C["btn_active"] if var.get() else C["btn_idle"],
                    fg=C["white"]      if var.get() else C["subtext"],
                )
                update_cb(f)
            b = tk.Button(
                p, text=label_text, command=_toggle,
                bg=C["btn_active"] if var.get() else C["btn_idle"],
                fg=C["white"]      if var.get() else C["subtext"],
                font=("Segoe UI", 7),
                relief="flat", bd=0, cursor="hand2",
                activebackground=C["accent2"],
                activeforeground=C["white"],
                padx=6, pady=2,
            )
            b.pack(side="left", padx=(0, 4))
            return b

        _toggle_btn(r5, "Shadow",  s["shadow"],  field)
        tk.Label(r5, text="off", font=("Segoe UI", 6),
                 fg=C["muted"], bg=bg).pack(side="left", padx=(0, 8))
        _toggle_btn(r5, "Outline", s["outline"], field)
        tk.Label(r5, text="off", font=("Segoe UI", 6),
                 fg=C["muted"], bg=bg).pack(side="left")

    # ------------------------------------------------------------------
    def _build_qr_controls(self, parent, field, s, update_cb, bg):
        """Controls shown when a field is in QR mode."""
        row = tk.Frame(parent, bg=bg)
        row.pack(fill="x", pady=(2, 4))
        tk.Label(row, text="QR size (px)", font=("Segoe UI", 7),
                 fg=C["subtext"], bg=bg).pack(side="left")
        spin = tk.Spinbox(
            row, from_=40, to=600, width=5,
            textvariable=s.get("qr_size"),
            font=("Segoe UI", 8),
            bg=C["surface3"], fg=C["text"],
            buttonbackground=C["surface3"],
            insertbackground=C["text"],
            relief="flat", bd=0,
            highlightthickness=1, highlightbackground=C["border"],
            command=lambda f=field: update_cb(f),
        )
        spin.bind("<Return>", lambda e, f=field: update_cb(f))
        spin.pack(side="left", padx=(6, 0))

        tk.Label(
            parent,
            text="Value taken from data column at runtime.",
            font=("Segoe UI", 6), fg=C["muted"], bg=bg,
            wraplength=240, justify="left",
        ).pack(anchor="w", pady=(0, 4))


# ---------------------------------------------------------------------------
class _ToggleSwitch(tk.Canvas):
    W, H, R = 32, 16, 8

    def __init__(self, parent, var, command, bg="#ffffff"):
        super().__init__(parent, width=self.W, height=self.H,
                         bg=bg, highlightthickness=0, cursor="hand2")
        self._var = var
        self._cmd = command
        self.bind("<Button-1>", self._toggle)
        var.trace_add("write", lambda *_: self._draw())
        self._draw()

    def _draw(self):
        self.delete("all")
        on    = self._var.get()
        track = C["accent"] if on else C["surface3"]
        self._rounded_rect(0, 0, self.W, self.H, self.R, fill=track)
        kx = self.W - self.R - 2 if on else self.R + 2
        self.create_oval(kx - 5, self.H // 2 - 5, kx + 5, self.H // 2 + 5,
                         fill=C["white"], outline="")

    def _rounded_rect(self, x1, y1, x2, y2, r, **kw):
        self.create_arc(x1,      y1,      x1+2*r, y1+2*r, start=90,  extent=90,  style="pieslice", outline="", **kw)
        self.create_arc(x2-2*r, y1,      x2,     y1+2*r, start=0,   extent=90,  style="pieslice", outline="", **kw)
        self.create_arc(x1,      y2-2*r, x1+2*r, y2,     start=180, extent=90,  style="pieslice", outline="", **kw)
        self.create_arc(x2-2*r, y2-2*r, x2,     y2,     start=270, extent=90,  style="pieslice", outline="", **kw)
        self.create_rectangle(x1+r, y1,   x2-r, y2,   outline="", **kw)
        self.create_rectangle(x1,   y1+r, x2,   y2-r, outline="", **kw)

    def _toggle(self, _=None):
        self._var.set(not self._var.get())
        if self._cmd:
            self._cmd()
