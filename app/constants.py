# ---------------------------------------------------------------------------
# Theme palette  --  "Warm Neutral"
# Clean, crisp, modern. Warm beige surfaces, single teal accent.
# Inspired by Notion / Linear light mode. No glassmorphism, no thick borders.
# ---------------------------------------------------------------------------

C = {
    # -- backgrounds ---------------------------------------------------------
    "bg":         "#f7f6f3",   # warm off-white page background
    "surface":    "#ffffff",   # primary card / panel surface
    "surface2":   "#f3f2ef",   # slightly recessed surface (sidebar, rows)
    "surface3":   "#eceae5",   # deeper recess (inputs, code blocks)
    "nav":        "#ffffff",   # top nav bar
    "canvas_bg":  "#e8e6e0",   # canvas workspace background

    # -- accent (single teal) ------------------------------------------------
    "accent":     "#0f7b6c",   # primary teal CTA
    "accent2":    "#0d6b5d",   # hover
    "accent3":    "#3da899",   # softer teal for badges / highlights
    "accent_dim": "#d4ede9",   # teal-tinted surface (selected rows, etc.)
    "accent_glow":"#0f7b6c18", # very faint teal wash

    "success":    "#2d8a4e",
    "success2":   "#247a42",
    "success_dim":"#dff3e7",

    "danger":     "#c0392b",
    "danger2":    "#a93226",
    "danger_dim": "#fae5e3",

    "warning":    "#b7670a",
    "warning_dim":"#fdf0dc",

    # -- text ----------------------------------------------------------------
    "text":       "#1a1916",   # near-black, warm tint
    "subtext":    "#6b6860",   # secondary labels
    "muted":      "#b0aca3",   # placeholder, disabled
    "text_inv":   "#ffffff",   # text on dark/accent backgrounds

    # -- borders & dividers --------------------------------------------------
    # single-pixel dividers only; no thick borders
    "border":     "#e0ddd7",   # standard divider
    "border2":    "#cbc8c1",   # slightly stronger (focus rings, etc.)
    "row_alt":    "#f9f8f5",   # alternating table row tint
    "log_bg":     "#f3f2ef",
    "white":      "#ffffff",

    # -- interactive states --------------------------------------------------
    "btn_idle":   "#f0efe9",   # secondary button default
    "btn_hover":  "#e6e4de",   # secondary button hover
    "btn_active": "#0f7b6c",   # primary button (accent)
    "btn_press":  "#0d6b5d",   # primary button pressed

    # -- shadows (soft, warm-tinted) -----------------------------------------
    "shadow":     "#c8c5bc",
}

APP_TITLE          = "Certy"
APP_VERSION        = "4.0.1"

CANVAS_MAX_W       = 1100
CANVAS_MAX_H       = 750
PX_TO_MM           = 0.264583
DEFAULT_FONT_SIZE  = 32
SIDEBAR_W          = 340

# -- spacing -----------------------------------------------------------------
PAD_XS   = 2
PAD_SM   = 6
PAD_MD   = 12
PAD_LG   = 20
PAD_XL   = 32

# -- radius ------------------------------------------------------------------
RADIUS_SM = 4
RADIUS_MD = 6
RADIUS_LG = 10

# -- typography --------------------------------------------------------------
FONT_FAMILY_UI   = "Segoe UI"
FONT_FAMILY_MONO = "Cascadia Code"

FONT_SZ_XS  = 9
FONT_SZ_SM  = 10
FONT_SZ_MD  = 11
FONT_SZ_LG  = 13
FONT_SZ_XL  = 15
FONT_SZ_H1  = 18
