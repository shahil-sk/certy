"""
CertificateApp  -- the top-level controller.
"""
import os
import platform
import threading

import tkinter as tk
from tkinter import filedialog, messagebox

from PIL import Image, ImageTk

from app.constants import (
    C, APP_TITLE, DEFAULT_FONT_SIZE,
    FONT_FAMILY_UI, FONT_SZ_MD, FONT_SZ_SM,
    PAD_SM, PAD_MD, PAD_LG, SIDEBAR_W,
)
from app.helpers import resource_path, cmyk_to_hex
from app.font_manager import load_available_fonts
from app import excel_loader, generator, project_io
from app.ui.widgets import setup_ttk_styles
from app.ui.navbar import NavBar
from app.ui.status_bar import StatusBar
from app.ui.control_panel import ControlPanel
from app.ui.field_row import FieldList
from app.ui.canvas_area import CanvasArea
from app.ui.dialogs import show_preview, pick_color_rgb, pick_color_cmyk

_DEFAULT_ALIGN = "center"


def _make_field_settings(default_font: str) -> dict:
    """Return a fresh font_settings sub-dict for one field."""
    return {
        "size":           tk.IntVar(value=DEFAULT_FONT_SIZE),
        "color":          tk.StringVar(value="#000000"),
        "font_name":      tk.StringVar(value=default_font),
        "align":          tk.StringVar(value=_DEFAULT_ALIGN),
        "opacity":        tk.IntVar(value=100),
        "shadow":         tk.BooleanVar(value=False),
        "shadow_offset":  tk.IntVar(value=4),
        "outline":        tk.BooleanVar(value=False),
        "outline_width":  tk.IntVar(value=2),
    }


class CertificateApp:

    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title(APP_TITLE)
        self.root.minsize(1020, 680)
        self.root.configure(bg=C["bg"])

        # Centre on first launch at a comfortable default size
        sw, sh = root.winfo_screenwidth(), root.winfo_screenheight()
        win_w, win_h = min(1400, sw - 80), min(880, sh - 80)
        x = (sw - win_w) // 2
        y = (sh - win_h) // 2
        root.geometry(f"{win_w}x{win_h}+{x}+{y}")

        self.original_image  = None
        self.template_path   = None
        self.excel_path      = None
        self.excel_data:     list = []
        self.fields:         list = []
        self.field_vars:     dict = {}
        self.font_settings:  dict = {}
        self.color_space     = tk.StringVar(value="RGB")
        self._gen_lock       = threading.Lock()

        self.available_fonts = load_available_fonts()

        setup_ttk_styles()
        self._build_ui()
        self._set_icon()

    def _build_ui(self):
        NavBar(
            self.root,
            save_cmd=self.save_project,
            load_cmd=self.load_project,
            load_template_cmd=self.load_template,
            load_excel_cmd=self.load_excel,
        )
        # 1 px shadow line beneath the navbar for depth
        tk.Frame(self.root, bg=C["shadow"], height=1).pack(fill="x")

        self._status_bar = StatusBar(self.root)
        body = tk.Frame(self.root, bg=C["bg"])
        body.pack(fill="both", expand=True, padx=PAD_MD, pady=(PAD_SM, PAD_SM))
        self._panel = ControlPanel(
            body,
            preview_cmd=self.preview_certificate,
            generate_cmd=self.generate_certificates,
        )
        self._field_list  = FieldList(self._panel.fields_frame)
        self._canvas_area = CanvasArea(body)

    def _set_icon(self):
        # on Windows use the .ico; everywhere else fall back to the .png
        candidates = ("icon.ico", "icon.png")
        for p in map(resource_path, candidates):
            if not os.path.exists(p):
                continue
            try:
                if platform.system() == "Windows" and p.endswith(".ico"):
                    self.root.iconbitmap(p)
                    return
                photo = ImageTk.PhotoImage(Image.open(p))
                self.root.iconphoto(True, photo)
                self._icon_ref = photo
                return
            except Exception:
                pass

    def _status(self, msg: str, ok: bool = True) -> None:
        self._status_bar.set(msg, ok)
        self.root.update_idletasks()

    def _log(self, msg, clear=False):
        self.root.after(0, lambda m=msg, c=clear: self._panel.append_log(m, c))

    # ------------------------------------------------------------------
    def load_template(self, file_path=None):
        if not file_path:
            file_path = filedialog.askopenfilename(
                title="Select certificate template",
                filetypes=[("Images", "*.png *.jpg *.jpeg")])
        if not file_path: return
        try:
            self.template_path  = file_path
            self.original_image = Image.open(file_path).convert("RGBA")
            w, h = self.original_image.size
            self._canvas_area.load_image(self.original_image)
            for f in self.fields:
                self._canvas_area.create_placeholder(f)
            self._status(
                f"Template loaded  ·  {os.path.basename(file_path)}  ·  {w}×{h} px")
        except Exception as exc:
            messagebox.showerror("Error", f"Cannot load template:\n{exc}")

    def load_excel(self, file_path=None):
        if not file_path:
            file_path = filedialog.askopenfilename(
                title="Select data file",
                filetypes=[("Excel / CSV", "*.xlsx *.csv")])
        if not file_path: return
        try:
            header, rows = excel_loader.read(file_path)
        except Exception as exc:
            messagebox.showerror("Error", str(exc))
            return

        self.excel_path  = file_path
        self.fields      = header
        self.excel_data  = rows

        default_font = next(iter(self.available_fonts))
        self.field_vars    = {f: tk.BooleanVar(value=True) for f in header}
        self.font_settings = {f: _make_field_settings(default_font) for f in header}

        self._canvas_area.font_settings   = self.font_settings
        self._canvas_area.available_fonts = self.available_fonts
        self._canvas_area.excel_data      = self.excel_data
        self._canvas_area.fields          = self.fields

        self._field_list.rebuild(
            self.fields, self.field_vars, self.font_settings,
            list(self.available_fonts.keys()),
            update_cb=self._on_field_update,
            color_cb=self._on_pick_color,
        )
        if self.original_image:
            for f in self.fields:
                self._canvas_area.create_placeholder(f)

        ext = os.path.splitext(file_path)[1].upper()
        fname = os.path.basename(file_path)
        self._status(
            f"{ext} loaded  ·  {fname}  ·  {len(rows)} records  ·  {len(header)} fields")

    def _on_field_update(self, field):
        self._canvas_area.update_placeholder(field)
        self._status(f"Field updated  ·  {field}")

    def _on_pick_color(self, field):
        if self.color_space.get() == "RGB":
            pick_color_rgb(self.root, field, self.font_settings)
        else:
            pick_color_cmyk(self.root, field, self.font_settings)
        self._canvas_area.update_placeholder(field)
        swatch = self.font_settings[field].get("_swatch")
        if swatch:
            col = self.font_settings[field]["color"].get()
            if col.startswith("cmyk("):
                col = cmyk_to_hex(col)
            try:
                swatch.config(bg=col)
            except Exception:
                pass

    def preview_certificate(self):
        if not self.original_image:
            messagebox.showwarning("Certy", "Load a template first."); return
        if not self.excel_data:
            messagebox.showwarning("Certy", "Load student data first."); return
        from app.image_renderer import draw_text_on_image
        img = draw_text_on_image(
            self.original_image.copy(),
            self.fields, self.field_vars, self.font_settings,
            self.available_fonts, self.excel_data[0],
            self._canvas_area.get_scaled_positions(),
        )
        show_preview(self.root, img)

    def generate_certificates(self):
        if not self.excel_data:
            messagebox.showwarning("Certy", "Load student data first."); return
        if not self.original_image:
            messagebox.showwarning("Certy", "Load a template first."); return
        if not self._gen_lock.acquire(blocking=False):
            messagebox.showwarning("Certy", "Generation already in progress.\nPlease wait for the current batch to finish."); return

        use_cmyk = messagebox.askyesno(
            "Output colour mode",
            "Generate certificates in CMYK colour mode?\n\n"
            "  Yes  →  CMYK  (recommended for professional printing)\n"
            "  No   →  RGB   (recommended for screen / digital use)")
        self.color_space.set("CMYK" if use_cmyk else "RGB")
        out_dir = filedialog.askdirectory(title="Select output folder")
        if not out_dir:
            self._gen_lock.release(); return

        self._status("Generating certificates…", ok=True)
        generator.run(
            excel_data=self.excel_data,
            fields=self.fields,
            field_vars=self.field_vars,
            font_settings=self.font_settings,
            available_fonts=self.available_fonts,
            original_image=self.original_image,
            positions=self._canvas_area.get_scaled_positions(),
            out_dir=out_dir,
            color_mode="CMYK" if use_cmyk else "RGB",
            filename_pattern=self._panel.filename_pattern.get(),
            on_progress=lambda pct: self.root.after(
                0, lambda v=pct: self._panel.set_progress(v)),
            on_log=lambda msg, clr: self.root.after(
                0, lambda m=msg, c=clr: self._panel.append_log(m, c)),
            on_done=lambda cnt, tot: self.root.after(
                0, lambda: (
                    self._status(f"Done  ·  {cnt} certificate(s) saved to {os.path.basename(out_dir)}/"),
                    messagebox.showinfo(
                        "Certy — Done",
                        f"✓  {cnt} certificate(s) generated successfully!\n\nSaved to:\n{out_dir}")
                )),
            lock=self._gen_lock,
        )

    # ------------------------------------------------------------------
    def save_project(self):
        if not self.original_image:
            messagebox.showwarning("Warning", "No template loaded."); return
        try:
            data = project_io.serialise(
                template_path=self.template_path,
                excel_path=self.excel_path,
                color_space=self.color_space.get(),
                positions=self._canvas_area.get_scaled_positions(),
                fields=self.fields,
                font_settings=self.font_settings,
                field_vars=self.field_vars,
                filename_pattern=self._panel.filename_pattern.get(),
            )
            path = filedialog.asksaveasfilename(
                defaultextension=".certy",
                filetypes=[("Certy Project", "*.certy")])
            if path:
                project_io.save(path, data)
                self._status(f"Project saved  ·  {os.path.basename(path)}")
                messagebox.showinfo("Saved", f"Project saved successfully.\n\n{path}")
        except Exception as exc:
            messagebox.showerror("Error", f"Save failed:\n{exc}")

    def load_project(self):
        path = filedialog.askopenfilename(
            filetypes=[("Certy Project", "*.certy")])
        if not path: return
        try:
            data = project_io.load(path)
            self.load_template(data.get("template_path"))
            self.load_excel(data.get("excel_path"))
            self.color_space.set(data.get("color_space", "RGB"))
            self._panel.filename_pattern.set(
                data.get("filename_pattern", ""))
            pos = data.get("positions", {})
            self._canvas_area.set_scaled_positions(pos)
            fs = data.get("field_settings", {})
            for f, settings in fs.items():
                if f not in self.font_settings: continue
                self.font_settings[f]["size"].set(settings.get("size", 32))
                self.font_settings[f]["color"].set(settings.get("color", "#000000"))
                self.field_vars[f].set(settings.get("visible", True))
                self.font_settings[f]["font_name"].set(settings.get("font_name", ""))
                self.font_settings[f]["align"].set(settings.get("align", "center"))
                if "opacity" in self.font_settings[f]:
                    self.font_settings[f]["opacity"].set(settings.get("opacity", 100))
                if "shadow" in self.font_settings[f]:
                    self.font_settings[f]["shadow"].set(settings.get("shadow", False))
                if "shadow_offset" in self.font_settings[f]:
                    self.font_settings[f]["shadow_offset"].set(settings.get("shadow_offset", 4))
                if "outline" in self.font_settings[f]:
                    self.font_settings[f]["outline"].set(settings.get("outline", False))
                if "outline_width" in self.font_settings[f]:
                    self.font_settings[f]["outline_width"].set(settings.get("outline_width", 2))
            self._field_list.rebuild(
                self.fields, self.field_vars, self.font_settings,
                list(self.available_fonts.keys()),
                update_cb=self._on_field_update,
                color_cb=self._on_pick_color,
            )
            for f in self.fields:
                self._canvas_area.update_placeholder(f)
            self._status(f"Project loaded  ·  {os.path.basename(path)}")
        except Exception as exc:
            messagebox.showerror("Error", f"Load failed:\n{exc}")
