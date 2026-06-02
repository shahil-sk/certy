"""
Scrollable field editor list in the sidebar.

Each field card exposes three render modes:
  text  -- font / size / colour / align / opacity / shadow / outline
  qr    -- QR code sized by a pixel-size spinner
  image -- per-row image overlay sized by a pixel-size spinner

Each card also has an optional condition row:
  "if [column] == [value]"  -- field is only rendered when the condition holds
"""
import tkinter as tk
from tkinter import ttk

from app.constants import C, FONT_FAMILY_UI, FONT_SZ_SM
from app.ui.widgets import label

_ALIGN_OPTIONS = [("L", "left"), ("C", "center"), ("R", "right")]


class FieldList(tk.Frame):

    def __init__(self, parent):
        super().__init__(parent, bg=C["surface2"])
        self.pack(fill="x")

    def rebuild(self, fields, field_vars, font_settings,
                available_fonts, update_cb, color_cb):
        for w in self.winfo_children():
            w.destroy()

        cv  = tk.Canvas(self, height=360, bg=C["surface2"], highlightthickness=0)
        vsb = ttk.Scrollbar(self, orient="vertical", command=cv.yview,
                            style="Dark.Vertical.TScrollbar")
        inner = tk.Frame(cv, bg=C["surface2"])
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
        # alternate rows: very subtle warm tint, no heavy stripe
        bg = C["row_alt"] if alt else C["surface"]
        super().__init__(parent, bg=bg)
        self.pack(fill="x")
        # single 1px bottom separator
        tk.Frame(self, bg=C["border"], height=1).pack(fill="x", side="bottom")
        self._build(field, field_vars, font_settings,
                    available_fonts, update_cb, color_cb, bg)

    def _build(self, field, field_vars, font_settings,
               available_fonts, update_cb, color_cb, bg):
        pad = tk.Frame(self, bg=bg, padx=10, pady=8)
        pad.pack(fill="x")

        s = font_settings[field]

        # -- Row 1: field name + mode toggles + visible toggle ---------------
        r1 = tk.Frame(pad, bg=bg)
        r1.pack(fill="x", pady=(0, 5))

        # field name label -- warm teal, uppercase, small
        tk.Label(
            r1, text=field.upper(),
            font=(FONT_FAMILY_UI, 8, "bold"),
            fg=C["accent"], bg=bg,
        ).pack(side="left")

        # Visible toggle (rightmost)
        vis_frame = tk.Frame(r1, bg=bg)
        vis_frame.pack(side="right")
        tk.Label(
            vis_frame, text="show",
            font=(FONT_FAMILY_UI, 7),
            fg=C["muted"], bg=bg,
        ).pack(side="left", padx=(0, 3))
        _ToggleSwitch(
            vis_frame, field_vars[field],
            lambda f=field: update_cb(f), bg=bg,
        ).pack(side="left")

        # Mode toggle buttons
        mode_frame = tk.Frame(r1, bg=bg)
        mode_frame.pack(side="right", padx=(0, 8))

        ft_var   = s.get("field_type")
        cur_type = ft_var.get() if ft_var else "text"

        def _mode_btn(text, mode):
            active = cur_type == mode
            b = tk.Button(
                mode_frame, text=text,
                font=(FONT_FAMILY_UI, 7, "bold"),
                relief="flat", bd=0, cursor="hand2",
                padx=6, pady=2,
                bg=C["accent"]      if active else C["btn_idle"],
                fg=C["text_inv"]    if active else C["subtext"],
                activebackground=C["accent2"],
                activeforeground=C["text_inv"],
            )
            b.pack(side="left", padx=(0, 2))
            return b

        qr_btn  = _mode_btn("QR",  "qr")
        img_btn = _mode_btn("IMG", "image")

        # -- Mode-specific frames --------------------------------------------
        text_frame = tk.Frame(pad, bg=bg)
        text_frame.pack(fill="x")
        self._build_text_controls(
            text_frame, field, s, available_fonts, update_cb, color_cb, bg)

        qr_frame = tk.Frame(pad, bg=bg)
        self._build_size_controls(
            qr_frame, field, s, "qr_size", "QR size (px)", 40, 600, update_cb, bg)

        img_frame = tk.Frame(pad, bg=bg)
        self._build_size_controls(
            img_frame, field, s, "img_size", "Image size (px)", 20, 800, update_cb, bg)
        self._build_opacity_row(img_frame, field, s, update_cb, bg)

        self._build_condition_row(pad, field, s, update_cb, bg)

        _frames = {"text": text_frame, "qr": qr_frame, "image": img_frame}

        def _show_mode(mode):
            for m, f in _frames.items():
                if m == mode:
                    f.pack(fill="x")
                else:
                    f.pack_forget()

        _show_mode(cur_type)

        def _switch(new_type, f=field):
            if ft_var is None:
                return
            ft_var.set(new_type)
            _show_mode(new_type)
            for btn, mode in ((qr_btn, "qr"), (img_btn, "image")):
                active = new_type == mode
                btn.config(
                    bg=C["accent"]      if active else C["btn_idle"],
                    fg=C["text_inv"]    if active else C["subtext"],
                )
            update_cb(f)

        qr_btn.config( command=lambda: _switch("text" if ft_var.get() == "qr"    else "qr"))
        img_btn.config(command=lambda: _switch("text" if ft_var.get() == "image" else "image"))

    # ------------------------------------------------------------------
    def _build_condition_row(self, parent, field, s, update_cb, bg):
        col_var = s.get("condition_col")
        val_var = s.get("condition_val")
        if col_var is None or val_var is None:
            return

        wrapper = tk.Frame(parent, bg=bg)
        wrapper.pack(fill="x", pady=(4, 0))

        header_row = tk.Frame(wrapper, bg=bg)
        header_row.pack(fill="x")

        detail = tk.Frame(wrapper, bg=bg)
        has_condition = bool(col_var.get().strip())

        toggle_btn = tk.Button(
            header_row,
            text="\u2713 if..." if has_condition else "if...",
            font=(FONT_FAMILY_UI, 7),
            relief="flat", bd=0, cursor="hand2",
            padx=5, pady=1,
            bg=C["accent"]    if has_condition else C["btn_idle"],
            fg=C["text_inv"]  if has_condition else C["subtext"],
            activebackground=C["accent2"],
            activeforeground=C["text_inv"],
        )
        toggle_btn.pack(side="left")

        tk.Label(
            header_row,
            text="show only when column = value",
            font=(FONT_FAMILY_UI, 6), fg=C["muted"], bg=bg,
        ).pack(side="left", padx=(5, 0))

        HINT_COL = "e.g. grade"
        HINT_VAL = "e.g. A"

        entry_row = tk.Frame(detail, bg=bg)
        entry_row.pack(fill="x", pady=(3, 0))

        def _make_hint_entry(parent_frame, var, hint, width=9):
            e = tk.Entry(
                parent_frame,
                width=width,
                font=(FONT_FAMILY_UI, 8),
                bg=C["surface3"], fg=C["text"],
                insertbackground=C["accent"],
                relief="flat", bd=0,
                highlightthickness=1,
                highlightbackground=C["border"],
                highlightcolor=C["accent"],
            )

            def _show_hint():
                e.config(fg=C["muted"])
                e.delete(0, tk.END)
                e.insert(0, hint)

            def _on_focus_in(_ev):
                if e.get() == hint:
                    e.config(fg=C["text"])
                    e.delete(0, tk.END)

            def _on_focus_out(_ev):
                raw = e.get().strip()
                if not raw or raw == hint:
                    var.set("")
                    _show_hint()
                else:
                    var.set(raw)
                update_cb(field)

            e.bind("<FocusIn>",  _on_focus_in)
            e.bind("<FocusOut>", _on_focus_out)
            e.bind("<Return>",   lambda _ev: _on_focus_out(_ev))

            real = var.get().strip()
            if real:
                e.insert(0, real)
                e.config(fg=C["text"])
            else:
                _show_hint()

            return e

        def _refresh_toggle(*_):
            active = bool(col_var.get().strip())
            toggle_btn.config(
                text="\u2713 if..." if active else "if...",
                bg=C["accent"]    if active else C["btn_idle"],
                fg=C["text_inv"]  if active else C["subtext"],
            )

        col_var.trace_add("write", _refresh_toggle)

        tk.Label(
            entry_row, text="col",
            font=(FONT_FAMILY_UI, 7), fg=C["subtext"], bg=bg,
        ).pack(side="left")
        _make_hint_entry(entry_row, col_var, HINT_COL).pack(side="left", padx=(3, 4))
        tk.Label(
            entry_row, text="=",
            font=(FONT_FAMILY_UI, 8, "bold"), fg=C["subtext"], bg=bg,
        ).pack(side="left")
        _make_hint_entry(entry_row, val_var, HINT_VAL).pack(side="left", padx=(4, 0))

        _shown = [has_condition]

        def _toggle_detail():
            if _shown[0]:
                detail.pack_forget()
                _shown[0] = False
            else:
                detail.pack(fill="x")
                _shown[0] = True

        if has_condition:
            detail.pack(fill="x")

        toggle_btn.config(command=_toggle_detail)

    # ------------------------------------------------------------------
    def _build_text_controls(self, parent, field, s,
                             available_fonts, update_cb, color_cb, bg):
        # Row 2: size + font
        r2 = tk.Frame(parent, bg=bg)
        r2.pack(fill="x", pady=(0, 4))
        tk.Label(
            r2, text="Sz",
            font=(FONT_FAMILY_UI, 7), fg=C["subtext"], bg=bg,
        ).pack(side="left")
        spin = tk.Spinbox(
            r2, from_=6, to=300, width=4,
            textvariable=s["size"],
            font=(FONT_FAMILY_UI, 8),
            bg=C["surface3"], fg=C["text"],
            buttonbackground=C["surface3"],
            insertbackground=C["text"],
            relief="flat", bd=0,
            highlightthickness=1, highlightbackground=C["border"],
            highlightcolor=C["accent"],
            command=lambda f=field: update_cb(f),
        )
        spin.bind("<Return>", lambda e, f=field: update_cb(f))
        spin.pack(side="left", padx=(3, 8))
        tk.Label(
            r2, text="Font",
            font=(FONT_FAMILY_UI, 7), fg=C["subtext"], bg=bg,
        ).pack(side="left")
        cb = ttk.Combobox(
            r2, values=available_fonts,
            textvariable=s["font_name"],
            width=11, state="readonly", style="Flat.TCombobox",
        )
        cb.bind("<<ComboboxSelected>>", lambda e, f=field: update_cb(f))
        cb.pack(side="left", padx=(3, 0))

        # Row 3: colour swatch + alignment pills
        r3 = tk.Frame(parent, bg=bg)
        r3.pack(fill="x", pady=(0, 4))
        swatch = tk.Button(
            r3, width=3, height=1,
            bg=s["color"].get(),
            relief="flat", bd=0, cursor="hand2",
            highlightthickness=1, highlightbackground=C["border"],
            command=lambda f=field: color_cb(f),
        )
        swatch.pack(side="left", padx=(0, 5))
        s["_swatch"] = swatch
        tk.Label(
            r3, text="Color",
            font=(FONT_FAMILY_UI, 7), fg=C["subtext"], bg=bg,
        ).pack(side="left", padx=(0, 8))

        tk.Label(
            r3, text="Align",
            font=(FONT_FAMILY_UI, 7), fg=C["subtext"], bg=bg,
        ).pack(side="left", padx=(0, 3))
        align_var  = s["align"]
        pill_refs  = {}

        def _set_align(val, f=field):
            align_var.set(val)
            for v, b in pill_refs.items():
                b.config(
                    bg=C["accent"]    if v == val else C["btn_idle"],
                    fg=C["text_inv"]  if v == val else C["subtext"],
                )
            update_cb(f)

        for sym, val in _ALIGN_OPTIONS:
            active = align_var.get() == val
            b = tk.Button(
                r3, text=sym,
                command=lambda v=val: _set_align(v),
                bg=C["accent"]    if active else C["btn_idle"],
                fg=C["text_inv"]  if active else C["subtext"],
                font=(FONT_FAMILY_UI, 8, "bold"),
                relief="flat", bd=0, cursor="hand2",
                activebackground=C["accent2"],
                activeforeground=C["text_inv"],
                width=2, pady=1,
            )
            b.pack(side="left", padx=(0, 2))
            pill_refs[val] = b

        # Row 4: opacity
        self._build_opacity_row(parent, field, s, update_cb, bg)

        # Row 5: shadow + outline toggles
        r5 = tk.Frame(parent, bg=bg)
        r5.pack(fill="x")

        def _toggle_btn(p, lbl_text, var, f):
            def _toggle():
                var.set(not var.get())
                b.config(
                    bg=C["accent"]    if var.get() else C["btn_idle"],
                    fg=C["text_inv"]  if var.get() else C["subtext"],
                )
                update_cb(f)
            b = tk.Button(
                p, text=lbl_text, command=_toggle,
                bg=C["accent"]    if var.get() else C["btn_idle"],
                fg=C["text_inv"]  if var.get() else C["subtext"],
                font=(FONT_FAMILY_UI, 7),
                relief="flat", bd=0, cursor="hand2",
                activebackground=C["accent2"],
                activeforeground=C["text_inv"],
                padx=6, pady=2,
            )
            b.pack(side="left", padx=(0, 4))
            return b

        _toggle_btn(r5, "Shadow",  s["shadow"],  field)
        _toggle_btn(r5, "Outline", s["outline"], field)

    # ------------------------------------------------------------------
    def _build_size_controls(self, parent, field, s, key, label_text,
                             min_val, max_val, update_cb, bg):
        row = tk.Frame(parent, bg=bg)
        row.pack(fill="x", pady=(2, 2))
        tk.Label(
            row, text=label_text,
            font=(FONT_FAMILY_UI, 7), fg=C["subtext"], bg=bg,
        ).pack(side="left")
        spin = tk.Spinbox(
            row, from_=min_val, to=max_val, width=5,
            textvariable=s.get(key),
            font=(FONT_FAMILY_UI, 8),
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
            parent, text="Value taken from data column at runtime.",
            font=(FONT_FAMILY_UI, 6), fg=C["muted"], bg=bg,
            wraplength=240, justify="left",
        ).pack(anchor="w", pady=(0, 4))

    def _build_opacity_row(self, parent, field, s, update_cb, bg):
        r = tk.Frame(parent, bg=bg)
        r.pack(fill="x", pady=(0, 4))
        tk.Label(
            r, text="Opacity",
            font=(FONT_FAMILY_UI, 7), fg=C["subtext"], bg=bg,
        ).pack(side="left")
        lbl = tk.Label(
            r, text="100%",
            font=(FONT_FAMILY_UI, 7), fg=C["text"], bg=bg, width=4,
        )
        lbl.pack(side="right")

        def _changed(val, f=field):
            lbl.config(text=f"{int(float(val))}%")
            update_cb(f)

        tk.Scale(
            r, from_=0, to=100, orient="horizontal",
            variable=s["opacity"],
            command=_changed,
            bg=bg, fg=C["text"],
            troughcolor=C["surface3"],
            activebackground=C["accent_dim"],
            highlightthickness=0, relief="flat",
            showvalue=False, length=140,
        ).pack(side="left", padx=(4, 0), fill="x", expand=True)


# ---------------------------------------------------------------------------
class _ToggleSwitch(tk.Canvas):
    """Minimal pill toggle switch."""
    W, H, R = 32, 16, 8

    def __init__(self, parent, var, command, bg=None):
        super().__init__(
            parent, width=self.W, height=self.H,
            bg=bg or C["surface"], highlightthickness=0, cursor="hand2",
        )
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
        self.create_oval(
            kx - 5, self.H // 2 - 5,
            kx + 5, self.H // 2 + 5,
            fill=C["white"], outline="",
        )

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
