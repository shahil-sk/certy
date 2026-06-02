"""
Right-side canvas frame: template + draggable text placeholders.
Features:
  - Scroll (mousewheel + scrollbars)
  - Row preview switcher in toolbar
  - Ctrl+Scroll zoom (30% - 200%)
  - Zoom in / out buttons in toolbar
  - Undo / Redo for placeholder positions (Ctrl+Z / Ctrl+Y or Ctrl+Shift+Z)

Coordinate convention
---------------------
  _placeholders[field]["x"] / ["y"]
      Base-display space: the position at zoom=1.0.
      This is the only coordinate we store and persist.

  canvas_x = base_x * zoom
  canvas_y = base_y * zoom

  original_image_x = base_x * scale_x
  original_image_y = base_y * scale_y
"""
import platform
import tkinter as tk
from tkinter import ttk
from collections import deque

from PIL import Image, ImageTk

from app.constants import C, CANVAS_MAX_W, CANVAS_MAX_H, FONT_FAMILY_UI
from app.image_renderer import render_placeholder

_LANCZOS   = Image.Resampling.LANCZOS
_MAX_UNDO  = 50
_ZOOM_MIN  = 0.3
_ZOOM_MAX  = 2.0
_ZOOM_STEP = 0.1

_TB_BG = C["surface"]


class CanvasArea(tk.Frame):

    def __init__(self, parent):
        super().__init__(
            parent, bg=C["surface"],
            highlightthickness=1, highlightbackground=C["border"],
        )
        self.pack(side="left", fill="both", expand=True, pady=6)

        self._scale_x = self._scale_y = 1.0
        self._zoom    = 1.0
        self._pil_image     = None
        self._display_image = None
        self._ph_images:    dict = {}
        # _placeholders[field] = {"item": canvas_item_id, "x": base_x, "y": base_y}
        # x/y are in base-display space (zoom=1.0). Apply zoom at draw time.
        self._placeholders: dict = {}
        self._drag:         dict = {}
        self._preview_idx   = 0

        self._undo_stack: deque = deque(maxlen=_MAX_UNDO)
        self._redo_stack: deque = deque(maxlen=_MAX_UNDO)

        # injected by App after construction
        self.font_settings:   dict = {}
        self.available_fonts: dict = {}
        self.excel_data:      list = []
        self.fields:          list = []

        self._build_toolbar()
        self._build_canvas()

    # ------------------------------------------------------------------
    # Toolbar
    # ------------------------------------------------------------------
    def _build_toolbar(self) -> None:
        tb = tk.Frame(self, bg=_TB_BG, height=32)
        tb.pack(fill="x")
        tb.pack_propagate(False)

        tk.Frame(self, bg=C["border"], height=1).pack(fill="x")

        def _tbtn(parent, text, cmd):
            return tk.Button(
                parent, text=text, command=cmd,
                bg=_TB_BG, fg=C["subtext"],
                relief="flat", bd=0, cursor="hand2",
                font=(FONT_FAMILY_UI, 10),
                activebackground=C["btn_idle"],
                activeforeground=C["text"],
                padx=6, pady=2,
            )

        # zoom controls
        zoom_grp = tk.Frame(tb, bg=_TB_BG)
        zoom_grp.pack(side="left", padx=(8, 0))

        _tbtn(zoom_grp, "\u2212", self._zoom_out).pack(side="left")

        self._zoom_label = tk.Label(
            zoom_grp, text="100%", width=5,
            font=(FONT_FAMILY_UI, 8), fg=C["subtext"], bg=_TB_BG,
            cursor="hand2",
        )
        self._zoom_label.pack(side="left", padx=2)
        self._zoom_label.bind("<Button-1>", lambda _e: self._zoom_reset())

        _tbtn(zoom_grp, "+", self._zoom_in).pack(side="left")

        tk.Frame(tb, bg=C["border"], width=1).pack(
            side="left", fill="y", padx=6, pady=4)

        # undo / redo
        undo_grp = tk.Frame(tb, bg=_TB_BG)
        undo_grp.pack(side="left")
        for txt, cmd in (("\u21b6", self.undo), ("\u21b7", self.redo)):
            _tbtn(undo_grp, txt, cmd).pack(side="left", padx=(0, 2))

        tk.Frame(tb, bg=C["border"], width=1).pack(
            side="left", fill="y", padx=6, pady=4)

        # row navigator
        nav = tk.Frame(tb, bg=_TB_BG)
        nav.pack(side="left")
        _tbtn(nav, "\u25c4", self._prev_row).pack(side="left")
        self._row_label = tk.Label(
            nav, text="row \u2014",
            font=(FONT_FAMILY_UI, 8), fg=C["text"], bg=_TB_BG, width=12,
        )
        self._row_label.pack(side="left", padx=4)
        _tbtn(nav, "\u25ba", self._next_row).pack(side="left")

        tk.Label(
            tb,
            text="Ctrl+scroll to zoom  \u00b7  Ctrl+Z to undo",
            font=(FONT_FAMILY_UI, 7), fg=C["muted"], bg=_TB_BG,
        ).pack(side="right", padx=10)

    # ------------------------------------------------------------------
    # Canvas
    # ------------------------------------------------------------------
    def _build_canvas(self) -> None:
        self._h_scroll = ttk.Scrollbar(
            self, orient="horizontal", style="Dark.Horizontal.TScrollbar")
        self._v_scroll = ttk.Scrollbar(
            self, orient="vertical",   style="Dark.Vertical.TScrollbar")

        self._canvas = tk.Canvas(
            self, bg=C["canvas_bg"], highlightthickness=0,
            xscrollcommand=self._h_scroll.set,
            yscrollcommand=self._v_scroll.set,
        )
        self._h_scroll.config(command=self._canvas.xview)
        self._v_scroll.config(command=self._canvas.yview)

        self._h_scroll.pack(side="bottom", fill="x")
        self._v_scroll.pack(side="right",  fill="y")
        self._canvas.pack(fill="both", expand=True, padx=1, pady=1)

        self._canvas.bind("<Enter>", self._bind_scroll)
        self._canvas.bind("<Leave>", self._unbind_scroll)

        self._canvas.bind_all("<Control-z>",       lambda e: self.undo())
        self._canvas.bind_all("<Control-Z>",       lambda e: self.undo())
        self._canvas.bind_all("<Control-y>",       lambda e: self.redo())
        self._canvas.bind_all("<Control-Y>",       lambda e: self.redo())
        self._canvas.bind_all("<Control-Shift-z>", lambda e: self.redo())
        self._canvas.bind_all("<Control-equal>",   lambda e: self._zoom_in())
        self._canvas.bind_all("<Control-plus>",    lambda e: self._zoom_in())
        self._canvas.bind_all("<Control-minus>",   lambda e: self._zoom_out())
        self._canvas.bind_all("<Control-0>",       lambda e: self._zoom_reset())

    # ------------------------------------------------------------------
    @property
    def scale_x(self): return self._scale_x

    @property
    def scale_y(self): return self._scale_y

    # ------------------------------------------------------------------
    # Image loading
    # ------------------------------------------------------------------
    def load_image(self, pil_image) -> None:
        self._pil_image   = pil_image
        self._preview_idx = 0
        self._redraw_image()

    def _redraw_image(self) -> None:
        if not self._pil_image:
            return
        ow, oh     = self._pil_image.size
        base_ratio = min(CANVAS_MAX_W / ow, CANVAS_MAX_H / oh)
        base_nw    = max(int(ow * base_ratio), 1)
        base_nh    = max(int(oh * base_ratio), 1)

        # scale_x/scale_y: original → base-display (zoom-independent)
        self._scale_x = ow / base_nw
        self._scale_y = oh / base_nh

        nw = max(int(base_nw * self._zoom), 1)
        nh = max(int(base_nh * self._zoom), 1)

        self._display_image = ImageTk.PhotoImage(
            self._pil_image.resize((nw, nh), _LANCZOS))
        self._canvas.config(
            width=min(nw, CANVAS_MAX_W),
            height=min(nh, CANVAS_MAX_H),
            scrollregion=(0, 0, nw, nh),
        )
        self._canvas.delete("all")
        self._canvas.create_image(0, 0, image=self._display_image, anchor="nw")
        self._zoom_label.config(text=f"{int(self._zoom * 100)}%")

        # Redraw all placeholders using stored base coords.
        # draw_placeholder converts base → canvas with current zoom.
        for field, data in list(self._placeholders.items()):
            self._draw_at_base(field, data["x"], data["y"])

    # ------------------------------------------------------------------
    # Row switcher
    # ------------------------------------------------------------------
    def _update_row_label(self) -> None:
        total = len(self.excel_data)
        self._row_label.config(
            text=f"row {self._preview_idx + 1} / {total}" if total
            else "row \u2014")

    def _prev_row(self) -> None:
        if not self.excel_data:
            return
        self._preview_idx = (self._preview_idx - 1) % len(self.excel_data)
        self._update_row_label()
        self._refresh_all_placeholders()

    def _next_row(self) -> None:
        if not self.excel_data:
            return
        self._preview_idx = (self._preview_idx + 1) % len(self.excel_data)
        self._update_row_label()
        self._refresh_all_placeholders()

    def _refresh_all_placeholders(self) -> None:
        for field, data in list(self._placeholders.items()):
            self._draw_at_base(field, data["x"], data["y"])

    def _current_row(self) -> dict:
        return self.excel_data[self._preview_idx] if self.excel_data else {}

    # ------------------------------------------------------------------
    # Undo / Redo  (snapshots in base space)
    # ------------------------------------------------------------------
    def _snapshot(self) -> dict:
        return {f: (d["x"], d["y"]) for f, d in self._placeholders.items()}

    def _push_undo(self) -> None:
        self._undo_stack.append(self._snapshot())
        self._redo_stack.clear()

    def undo(self) -> None:
        if not self._undo_stack:
            return
        self._redo_stack.append(self._snapshot())
        self._apply_snapshot(self._undo_stack.pop())

    def redo(self) -> None:
        if not self._redo_stack:
            return
        self._undo_stack.append(self._snapshot())
        self._apply_snapshot(self._redo_stack.pop())

    def _apply_snapshot(self, state: dict) -> None:
        for field, (x, y) in state.items():
            if field in self._placeholders:
                self._placeholders[field]["x"] = x
                self._placeholders[field]["y"] = y
        self._redraw_image()

    # ------------------------------------------------------------------
    # Placeholder management
    # ------------------------------------------------------------------
    def _draw_at_base(self, field: str, base_x: float, base_y: float) -> None:
        """
        Internal: render the placeholder image and place it on the canvas
        at the zoomed canvas position derived from base-display coords.

        canvas_x = base_x * zoom
        canvas_y = base_y * zoom
        """
        if field in self._placeholders:
            old_item = self._placeholders[field].get("item")
            if old_item is not None:
                self._canvas.delete(old_item)

        saved = self.excel_data
        row   = self._current_row()
        self.excel_data = [row] if row else saved

        ph_img = render_placeholder(
            field, self.font_settings, self.available_fonts,
            self.excel_data, self._scale_x, self._scale_y, self._zoom,
        )
        self.excel_data = saved

        photo = ImageTk.PhotoImage(ph_img)
        self._ph_images[field] = photo

        # apply zoom to get actual canvas pixel position
        cx = base_x * self._zoom
        cy = base_y * self._zoom

        item = self._canvas.create_image(cx, cy, image=photo, anchor="center")
        self._canvas.tag_bind(
            item, "<Button-1>",
            lambda e, f=field: self._drag_start(e, f))
        self._canvas.tag_bind(
            item, "<B1-Motion>",
            lambda e, f=field: self._drag_move(e, f))
        self._canvas.tag_bind(
            item, "<ButtonRelease-1>",
            lambda e, f=field: self._drag_end(e, f))

        # always write back base coords, not canvas coords
        self._placeholders[field] = {"item": item, "x": base_x, "y": base_y}
        self._update_row_label()

    # public surface -- accepts base-space coords
    def draw_placeholder(self, field: str, base_x: float, base_y: float) -> None:
        self._draw_at_base(field, base_x, base_y)

    def create_placeholder(self, field: str, x=None, y=None) -> None:
        """x, y are base-display coords (zoom=1.0). None → centre of visible canvas."""
        if field not in self.fields:
            return
        if x is None or y is None:
            cw  = self._canvas.winfo_width() or 800
            idx = self.fields.index(field)
            # divide by zoom so stored value is in base space
            x = (cw // 2) / self._zoom
            y = (50 + idx * 60) / self._zoom
        self._draw_at_base(field, x, y)

    def update_placeholder(self, field: str) -> None:
        if field in self._placeholders:
            p = self._placeholders[field]
            self._draw_at_base(field, p["x"], p["y"])

    def get_scaled_positions(self) -> dict:
        """
        Convert base-display coords to original-image pixel coords.

        original_x = base_x * scale_x
        original_y = base_y * scale_y
        """
        return {
            f: (d["x"] * self._scale_x, d["y"] * self._scale_y)
            for f, d in self._placeholders.items()
        }

    def set_scaled_positions(self, positions: dict) -> None:
        """
        Restore placeholder positions from original-image pixel coords.

        base_x = original_x / scale_x
        base_y = original_y / scale_y

        Must be called after load_image so scale_x/scale_y are valid.
        """
        for field, (ox, oy) in positions.items():
            bx = ox / self._scale_x
            by = oy / self._scale_y
            self._placeholders[field] = {"item": None, "x": bx, "y": by}
        self._redraw_image()

    def clear(self) -> None:
        self._canvas.delete("all")
        self._placeholders.clear()
        self._ph_images.clear()
        self._undo_stack.clear()
        self._redo_stack.clear()
        self._preview_idx = 0
        self._update_row_label()

    # ------------------------------------------------------------------
    # Drag  -- all math in base space
    # ------------------------------------------------------------------
    def _drag_start(self, event, field: str) -> None:
        self._push_undo()
        # record canvas-space start position; convert to base at end
        self._drag = {
            "field": field,
            "cx":    self._canvas.canvasx(event.x),
            "cy":    self._canvas.canvasy(event.y),
        }

    def _drag_move(self, event, field: str) -> None:
        if not self._drag or self._drag.get("field") != field:
            return
        cx = self._canvas.canvasx(event.x)
        cy = self._canvas.canvasy(event.y)
        dx = cx - self._drag["cx"]
        dy = cy - self._drag["cy"]
        self._drag["cx"] = cx
        self._drag["cy"] = cy

        if field not in self._placeholders:
            return

        # move stored base coords by delta / zoom
        self._placeholders[field]["x"] += dx / self._zoom
        self._placeholders[field]["y"] += dy / self._zoom

        item = self._placeholders[field]["item"]
        if item is not None:
            self._canvas.move(item, dx, dy)

    def _drag_end(self, event, field: str) -> None:
        self._drag = {}

    # ------------------------------------------------------------------
    # Scroll + Zoom
    # ------------------------------------------------------------------
    def _bind_scroll(self, _event=None) -> None:
        system = platform.system()
        if system == "Windows":
            self._canvas.bind_all("<MouseWheel>",       self._on_mousewheel)
            self._canvas.bind_all("<Shift-MouseWheel>", self._scroll_x)
        elif system == "Darwin":
            self._canvas.bind_all("<MouseWheel>",       self._on_mousewheel_mac)
            self._canvas.bind_all("<Shift-MouseWheel>", self._scroll_x_mac)
        else:
            self._canvas.bind_all("<Button-4>",         self._scroll_up)
            self._canvas.bind_all("<Button-5>",         self._scroll_down)
            self._canvas.bind_all("<Shift-Button-4>",   self._scroll_left)
            self._canvas.bind_all("<Shift-Button-5>",   self._scroll_right)
            self._canvas.bind_all("<Control-Button-4>", self._zoom_in)
            self._canvas.bind_all("<Control-Button-5>", self._zoom_out)

    def _unbind_scroll(self, _event=None) -> None:
        for seq in ("<MouseWheel>", "<Shift-MouseWheel>",
                    "<Button-4>", "<Button-5>",
                    "<Shift-Button-4>", "<Shift-Button-5>",
                    "<Control-Button-4>", "<Control-Button-5>"):
            try:
                self._canvas.unbind_all(seq)
            except Exception:
                pass

    def _on_mousewheel(self, event):
        if event.state & 0x0004:
            self._zoom_in() if event.delta > 0 else self._zoom_out()
        else:
            self._canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def _on_mousewheel_mac(self, event):
        if event.state & 0x0004:
            self._zoom_in() if event.delta > 0 else self._zoom_out()
        else:
            self._canvas.yview_scroll(int(-1 * event.delta), "units")

    def _scroll_x(self, event):
        self._canvas.xview_scroll(int(-1 * (event.delta / 120)), "units")

    def _scroll_x_mac(self, event):
        self._canvas.xview_scroll(int(-1 * event.delta), "units")

    def _scroll_up(self,    _e): self._canvas.yview_scroll(-1, "units")
    def _scroll_down(self,  _e): self._canvas.yview_scroll( 1, "units")
    def _scroll_left(self,  _e): self._canvas.xview_scroll(-1, "units")
    def _scroll_right(self, _e): self._canvas.xview_scroll( 1, "units")

    def _zoom_in(self, _e=None):
        if self._zoom < _ZOOM_MAX:
            self._zoom = round(min(self._zoom + _ZOOM_STEP, _ZOOM_MAX), 1)
            self._redraw_image()

    def _zoom_out(self, _e=None):
        if self._zoom > _ZOOM_MIN:
            self._zoom = round(max(self._zoom - _ZOOM_STEP, _ZOOM_MIN), 1)
            self._redraw_image()

    def _zoom_reset(self, _e=None):
        self._zoom = 1.0
        self._redraw_image()
