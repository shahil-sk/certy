# ---------------------------------------------------------------------------
# Theme palette  —  single source of truth for every colour in the app
# ---------------------------------------------------------------------------
#
# Design language: "Obsidian Studio"
# Deep neutral blacks with warm-tinted surfaces, crisp violet-indigo accent,
# and tight contrast ratios for legibility. Inspired by high-end creative tools.
# ---------------------------------------------------------------------------
C = {
    # ── backgrounds ─────────────────────────────────────────────────────────
    "bg":         "#0a0b0f",   # root window — near-black with cool tint
    "surface":    "#111318",   # panel / card — one step up
    "surface2":   "#181b22",   # field rows / inner cards
    "surface3":   "#1f2330",   # inputs, comboboxes, text fields
    "nav":        "#0d0e13",   # topbar — deepest surface
    "canvas_bg":  "#0c0d12",   # canvas background

    # ── accents ──────────────────────────────────────────────────────────────
    "accent":     "#6c74ff",   # primary — vivid violet-indigo
    "accent2":    "#5560f0",   # hover / pressed state
    "accent3":    "#818cff",   # lighter accent for highlights
    "accent_dim": "#1e2250",   # subtle accent-tinted bg (badges, chips)
    "accent_glow":"#6c74ff28", # translucent glow for focus rings

    "success":    "#2dd4a0",   # teal-green
    "success2":   "#1ab888",   # green hover
    "success_dim":"#0d2e24",   # subtle green bg

    "danger":     "#ff6b6b",   # warm red
    "danger2":    "#e85555",   # red hover
    "danger_dim": "#2e1414",   # subtle red bg

    "warning":    "#f5c542",   # golden amber
    "warning_dim":"#2b2110",   # subtle amber bg

    # ── text ─────────────────────────────────────────────────────────────────
    "text":       "#edf0f7",   # primary — soft cool white
    "subtext":    "#8b93a8",   # secondary / labels
    "muted":      "#3d4455",   # placeholder / disabled
    "text_inv":   "#0a0b0f",   # inverse text (on accent buttons)

    # ── borders & structural ──────────────────────────────────────────────────
    "border":     "#232738",   # default divider
    "border2":    "#2d3347",   # slightly lighter border (hover / focus)
    "row_alt":    "#141720",   # alternating row tint
    "log_bg":     "#080910",   # log / terminal area
    "white":      "#ffffff",

    # ── interactive states ────────────────────────────────────────────────────
    "btn_idle":   "#1a1d2c",   # toolbar / toggle idle
    "btn_hover":  "#22263a",   # toolbar / toggle hover
    "btn_active": "#6c74ff",   # toolbar / toggle active
    "btn_press":  "#5560f0",   # pressed

    # ── elevation shadows (use as .configure() bg on separator frames) ────────
    "shadow":     "#05060a",   # deepest shadow tone for layered depth
}

APP_TITLE         = "Certy"
APP_VERSION       = "3.2.0"

CANVAS_MAX_W      = 1100
CANVAS_MAX_H      = 750
PX_TO_MM          = 0.264583
DEFAULT_FONT_SIZE  = 32
SIDEBAR_W         = 330       # slightly wider for breathing room

# ── Spacing & radius tokens (use in widget padding/relief configs) ────────────
PAD_XS   = 2
PAD_SM   = 6
PAD_MD   = 12
PAD_LG   = 20
PAD_XL   = 32

RADIUS_SM = 4    # subtle rounding (entries, small chips)
RADIUS_MD = 8    # cards, panels
RADIUS_LG = 12   # dialogs, large surfaces

# ── Typography scale (points) ─────────────────────────────────────────────────
FONT_FAMILY_UI   = "Segoe UI"          # Windows; falls back gracefully on macOS/Linux
FONT_FAMILY_MONO = "Cascadia Code"     # log / code areas; fallback: Consolas
FONT_SZ_XS  = 9
FONT_SZ_SM  = 10
FONT_SZ_MD  = 11
FONT_SZ_LG  = 13
FONT_SZ_XL  = 15
FONT_SZ_H1  = 18
