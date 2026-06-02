# ---------------------------------------------------------------------------
# Theme palette  —  "Warm Neutral"
# Clean, visible, crisp light theme. No glassmorphism. No thick borders.
# One teal accent. Warm off-white surfaces. Dark sidebar nav.
# ---------------------------------------------------------------------------

C = {
    # ── backgrounds ─────────────────────────────────────────────────────────
    "bg":         "#f4f3f0",   # warm off-white page background
    "surface":    "#faf9f7",   # card / panel surface
    "surface2":   "#f0efe9",   # slightly recessed input bg
    "surface3":   "#e8e6df",   # hover trough / slider track
    "nav":        "#1c1b18",   # dark sidebar
    "canvas_bg":  "#e9e7e0",   # canvas working area

    # ── accents ──────────────────────────────────────────────────────────────
    "accent":     "#1a7a5e",   # teal primary
    "accent2":    "#0f6249",   # teal darker hover
    "accent3":    "#5ecba1",   # teal lighter (nav active text)
    "accent_dim": "#d3ece6",   # teal tinted surface (selected card)

    "success":    "#1e7a45",
    "success2":   "#16603a",
    "success_dim":"#ddf0e6",

    "danger":     "#c0392b",
    "danger2":    "#a12f23",
    "danger_dim": "#fae5e3",

    "warning":    "#b45309",
    "warning_dim":"#fef3cd",

    # ── text ─────────────────────────────────────────────────────────────────
    "text":       "#1a1917",   # near-black
    "subtext":    "#6b6860",   # secondary
    "muted":      "#a8a5a0",   # placeholders / labels
    "text_inv":   "#ffffff",   # text on dark/accent surfaces

    # ── borders & structure ──────────────────────────────────────────────────
    # alpha-blended: adapts cleanly, never harsh
    "border":     "#1a191914",  # rgba 8 %  — dividers, card edges
    "border2":    "#1a191922",  # rgba 13 % — stronger separators
    "row_alt":    "#f6f5f1",    # alternate row tint
    "log_bg":     "#f0efe9",
    "white":      "#ffffff",

    # ── interactive states ───────────────────────────────────────────────────
    "btn_idle":   "#eeece7",   # default button fill
    "btn_hover":  "#e4e2db",   # hovered button
    "btn_active": "#1a7a5e",   # active / selected (same as accent)
    "btn_press":  "#0f6249",

    # ── shadows ──────────────────────────────────────────────────────────────
    "shadow":     "#00000014",  # subtle, warm-neutral
}

APP_TITLE          = "Certy"
APP_VERSION        = "4.0.1"

CANVAS_MAX_W       = 1100
CANVAS_MAX_H       = 750
PX_TO_MM           = 0.264583
DEFAULT_FONT_SIZE  = 32
SIDEBAR_W          = 330

# ── spacing ────────────────────────────────────────────────────────────────
PAD_XS   = 2
PAD_SM   = 6
PAD_MD   = 12
PAD_LG   = 20
PAD_XL   = 32

# ── radius ─────────────────────────────────────────────────────────────────
RADIUS_SM = 4
RADIUS_MD = 6
RADIUS_LG = 10

# ── typography ─────────────────────────────────────────────────────────────
FONT_FAMILY_UI   = "Segoe UI"
FONT_FAMILY_MONO = "Cascadia Code"

FONT_SZ_XS  = 9
FONT_SZ_SM  = 10
FONT_SZ_MD  = 11
FONT_SZ_LG  = 13
FONT_SZ_XL  = 15
FONT_SZ_H1  = 18
