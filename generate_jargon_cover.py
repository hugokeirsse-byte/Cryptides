"""
The Jargon Breaker Protocol — KDP Full Wrap Cover
Back cover + Spine + Front cover — print-ready PDF with bleed
Trim size : 6 × 9 inches | 120 pages | White 60# paper
Spine     : 120 × 0.002252" = 0.2702" ≈ 0.270"
Canvas    : 12.520 × 9.25 inches (bleed 0.125" all sides)

Set guides=False before final KDP upload.
"""

from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor, black, white
from reportlab.lib.units import inch as IN
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import math
import random

# ── KDP-compliant font embedding ─────────────────────────────────────────────
_LIB = "/usr/share/fonts/truetype/liberation"
pdfmetrics.registerFont(TTFont("Helvetica",           f"{_LIB}/LiberationSans-Regular.ttf"))
pdfmetrics.registerFont(TTFont("Helvetica-Bold",      f"{_LIB}/LiberationSans-Bold.ttf"))
pdfmetrics.registerFont(TTFont("Helvetica-Oblique",   f"{_LIB}/LiberationSans-Italic.ttf"))
pdfmetrics.registerFont(TTFont("Helvetica-BoldOblique", f"{_LIB}/LiberationSans-BoldItalic.ttf"))
pdfmetrics.registerFont(TTFont("Mono",                f"{_LIB}/LiberationMono-Regular.ttf"))
pdfmetrics.registerFont(TTFont("MonoB",               f"{_LIB}/LiberationMono-Bold.ttf"))
pdfmetrics.registerFontFamily("Helvetica",
    normal="Helvetica", bold="Helvetica-Bold",
    italic="Helvetica-Oblique", boldItalic="Helvetica-BoldOblique")

# ── Dimensions ────────────────────────────────────────────────────────────────
BLEED    = 0.125 * IN
PAGE_W   = 6.0   * IN
PAGE_H   = 9.0   * IN
SPINE_W  = 0.270 * IN   # 120 pages × 0.002252"

TOTAL_W  = BLEED + PAGE_W + SPINE_W + PAGE_W + BLEED
TOTAL_H  = BLEED + PAGE_H + BLEED

# Panel absolute X positions
X_BACK_L  = 0
X_BACK_R  = BLEED + PAGE_W
X_SPINE_L = X_BACK_R
X_SPINE_R = X_SPINE_L + SPINE_W
X_FRONT_L = X_SPINE_R
X_FRONT_R = TOTAL_W

# Content bounds (inside bleed)
BK_X = BLEED
BK_W = PAGE_W
FR_X = X_FRONT_L
FR_W = PAGE_W
CT_Y = BLEED
CT_H = PAGE_H

# ── Blueprint palette ─────────────────────────────────────────────────────────
NAVY      = HexColor("#0A1628")
NAVY_DARK = HexColor("#060E1C")
CYAN      = HexColor("#00B4D8")
CYAN_DIM  = HexColor("#0077A8")
CYAN_PALE = HexColor("#48CAE4")
WHITE     = HexColor("#FFFFFF")
WHITE_DIM = HexColor("#CBD5E1")
WHITE_MID = HexColor("#8899AA")


# ── Blueprint helpers ────────────────────────────────────────────────────────

def bp_grid(c, x, y, w, h, spacing=18, r=0.5, alpha=0.08):
    """Subtle dot grid — mirrors the interior blueprint aesthetic."""
    c.saveState()
    cols = int(w / spacing) + 1
    rows = int(h / spacing) + 1
    for i in range(cols):
        for j in range(rows):
            px = x + i * spacing
            py = y + j * spacing
            if x <= px <= x + w and y <= py <= y + h:
                c.setFillColorRGB(0.28, 0.70, 0.85, alpha)
                c.circle(px, py, r, fill=1, stroke=0)
    c.restoreState()


def corner_marks(c, x, y, w, h, size=10, lw=0.6, color=CYAN_DIM):
    """L-shaped corner brackets matching the interior style."""
    c.saveState()
    c.setStrokeColor(color)
    c.setLineWidth(lw)
    for bx, by, sx, sy in [
        (x,     y + h, 1,  -1),
        (x + w, y + h, -1, -1),
        (x,     y,     1,   1),
        (x + w, y,     -1,  1),
    ]:
        c.line(bx, by, bx + sx * size, by)
        c.line(bx, by, bx, by + sy * size)
    c.restoreState()


def bp_circuit_line(c, x1, y1, x2, y2, lw=0.4, alpha=0.20):
    """A thin cyan circuit trace."""
    c.saveState()
    c.setStrokeColorRGB(0.28, 0.70, 0.85, alpha)
    c.setLineWidth(lw)
    c.line(x1, y1, x2, y2)
    c.restoreState()


def crosshair(c, cx, cy, size=16, lw=0.5, alpha=0.35):
    """Small blueprint crosshair target."""
    c.saveState()
    c.setStrokeColorRGB(0.28, 0.70, 0.85, alpha)
    c.setLineWidth(lw)
    c.circle(cx, cy, size * 0.55, fill=0, stroke=1)
    c.circle(cx, cy, 2, fill=0, stroke=1)
    hs = size * 0.9
    c.line(cx - hs, cy, cx - size * 0.3, cy)
    c.line(cx + size * 0.3, cy, cx + hs, cy)
    c.line(cx, cy - hs, cx, cy - size * 0.3)
    c.line(cx, cy + size * 0.3, cx, cy + hs)
    c.restoreState()


# ── Panels ────────────────────────────────────────────────────────────────────

def draw_front(c, x0, y0, w, h, img_path=None):
    """Place the front-cover PNG scaled to fill the panel + outer bleed."""
    if img_path:
        c.drawImage(img_path,
                    x0, y0 - BLEED,
                    width=w + BLEED, height=h + 2 * BLEED,
                    preserveAspectRatio=False, mask="auto")
    else:
        c.setFillColor(NAVY)
        c.rect(x0, y0, w, h, fill=1, stroke=0)


def draw_back(c, x0, y0, w, h, img_path=None):
    """Place the back-cover PNG scaled to fill the panel + outer bleed."""
    if img_path:
        c.drawImage(img_path,
                    x0 - BLEED, y0 - BLEED,
                    width=w + BLEED, height=h + 2 * BLEED,
                    preserveAspectRatio=False, mask="auto")
    else:
        c.setFillColor(NAVY)
        c.rect(x0, y0, w, h, fill=1, stroke=0)


def draw_spine(c, x0, y0, w, h):
    """Blueprint-style spine matching the cover aesthetic."""
    # Background — same navy as the covers
    c.setFillColor(NAVY_DARK)
    c.rect(x0, y0, w, h, fill=1, stroke=0)

    # Very subtle dot grid
    bp_grid(c, x0, y0, w, h, spacing=10, r=0.4, alpha=0.12)

    # Thin cyan edge rules (matching interior section borders)
    c.saveState()
    c.setStrokeColorRGB(0.28, 0.70, 0.85, 0.45)
    c.setLineWidth(0.4)
    c.line(x0 + 1.2, y0, x0 + 1.2, y0 + h)
    c.line(x0 + w - 1.2, y0, x0 + w - 1.2, y0 + h)
    c.restoreState()

    # Small crosshair at the vertical centre
    crosshair(c, x0 + w / 2, y0 + h * 0.5, size=8, lw=0.4, alpha=0.28)

    # ── Spine text (rotated, reads bottom → top) ──────────────────────────
    c.saveState()
    c.translate(x0 + w / 2, y0 + h / 2)
    c.rotate(90)

    # Main title
    c.setFont("Helvetica-Bold", 6.5)
    c.setFillColor(WHITE)
    c.drawCentredString(22, 2, "THE JARGON BREAKER PROTOCOL")

    # Publisher at the bottom end of the spine
    c.setFont("MonoB", 5)
    c.setFillColor(CYAN_DIM)
    c.drawCentredString(-h / 2 + 22, 2, "ENGINEERED FOR IMPACT")

    c.restoreState()

    # Tiny circuit-node dot at centre
    c.saveState()
    c.setFillColorRGB(0.28, 0.70, 0.85, 0.55)
    c.circle(x0 + w / 2, y0 + h * 0.72, 2.5, fill=1, stroke=0)
    c.setFillColorRGB(1, 1, 1, 0.9)
    c.circle(x0 + w / 2, y0 + h * 0.72, 1.0, fill=1, stroke=0)
    c.restoreState()


# ── Trim guides ───────────────────────────────────────────────────────────────

def trim_guides(c):
    c.saveState()
    c.setStrokeColorRGB(1, 0, 0, 0.55)
    c.setLineWidth(0.3)
    c.setDash(5, 5)
    for xv in [BLEED, BLEED + PAGE_W,
               BLEED + PAGE_W + SPINE_W,
               BLEED + PAGE_W + SPINE_W + PAGE_W]:
        c.line(xv, 0, xv, TOTAL_H)
    for yh in [BLEED, BLEED + PAGE_H]:
        c.line(0, yh, TOTAL_W, yh)
    c.setFont("Helvetica", 5)
    c.setFillColorRGB(1, 0, 0, 0.7)
    c.drawString(2,               BLEED + PAGE_H / 2, "BACK")
    c.drawString(X_FRONT_L + 2,  BLEED + PAGE_H / 2, "FRONT")
    c.drawString(X_SPINE_L + 2,  BLEED + PAGE_H / 2, "SPINE")
    c.restoreState()


# ── Main generator ────────────────────────────────────────────────────────────

def generate_cover(filename="Cover_Jargon_Breaker.pdf",
                   front_image=None,
                   back_image=None,
                   guides=True):
    cv = canvas.Canvas(filename, pagesize=(TOTAL_W, TOTAL_H))
    cv.setTitle("The Jargon Breaker Protocol — Full Paperback Cover")
    cv.setAuthor("Engineered For Impact Press")

    # Full-bleed navy base (fills any sub-pixel seams between panels)
    cv.setFillColor(NAVY_DARK)
    cv.rect(0, 0, TOTAL_W, TOTAL_H, fill=1, stroke=0)

    draw_back( cv, BK_X,      CT_Y, BK_W,    CT_H, img_path=back_image)
    draw_spine(cv, X_SPINE_L, CT_Y, SPINE_W, CT_H)
    draw_front(cv, FR_X,      CT_Y, FR_W,    CT_H, img_path=front_image)

    if guides:
        trim_guides(cv)

    cv.save()
    print(f"Generated : {filename}")
    print(f"Canvas    : {TOTAL_W/IN:.4f}\" × {TOTAL_H/IN:.4f}\"")
    print(f"Spine     : {SPINE_W/IN:.4f}\" ({SPINE_W:.2f} pt)")
    print(f"Guides    : {'YES — remove before KDP upload' if guides else 'OFF'}")


FRONT_COVER_IMAGE = (
    "/root/.claude/uploads/309e5a74-f5a0-472a-9a28-03ea08fe2d0d/"
    "98b8c162-1000012233.png"
)
BACK_COVER_IMAGE = (
    "/root/.claude/uploads/309e5a74-f5a0-472a-9a28-03ea08fe2d0d/"
    "4e973991-1000012234.png"
)

if __name__ == "__main__":
    generate_cover(
        front_image=FRONT_COVER_IMAGE,
        back_image=BACK_COVER_IMAGE,
        guides=True,
    )
