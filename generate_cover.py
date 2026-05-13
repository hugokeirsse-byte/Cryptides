"""
KDP Paperback Full Wrap Cover Generator
Back cover + Spine + Front cover — print-ready PDF with bleed
Trim size: 6 × 9 inches | 110 pages | White 60# paper
Spine:  110 × 0.002252" = 0.2477" ≈ 0.248"
Canvas: 12.498 × 9.25 inches (bleed 0.125" all sides)
"""

import math
import random
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor, black, white
from reportlab.lib.utils import ImageReader
from reportlab.lib.units import inch as IN

# ── Dimensions (all in points, 1in = 72pt) ───────────────────────────────────
BLEED      = 0.125 * IN
PAGE_W     = 6.0   * IN
PAGE_H     = 9.0   * IN
SPINE_W    = 0.248 * IN   # KDP formula: 110 pages × 0.002252"

TOTAL_W = BLEED + PAGE_W + SPINE_W + PAGE_W + BLEED   # ≈ 900 pt
TOTAL_H = BLEED + PAGE_H + BLEED                       # ≈ 666 pt

# Absolute X positions
X_BACK_L   = 0
X_BACK_R   = BLEED + PAGE_W
X_SPINE_L  = X_BACK_R
X_SPINE_R  = X_SPINE_L + SPINE_W
X_FRONT_L  = X_SPINE_R
X_FRONT_R  = TOTAL_W
Y_BOT      = 0
Y_TOP      = TOTAL_H

# Content bounds (inside bleed)
BK_X  = BLEED              # back cover content left
BK_W  = PAGE_W             # back cover content width
FR_X  = X_FRONT_L          # front cover content left
FR_W  = PAGE_W             # front cover content width
CT_Y  = BLEED              # content bottom
CT_H  = PAGE_H             # content height

# ── Palette ───────────────────────────────────────────────────────────────────
NAVY       = HexColor("#0A1628")
NAVY_DARK  = HexColor("#060E1C")
NAVY_MID   = HexColor("#0F1E38")
GOLD       = HexColor("#D4AF37")
GOLD_LIGHT = HexColor("#EDD060")
BLUE_E     = HexColor("#4FC3F7")
W_PURE     = HexColor("#FFFFFF")
W_DIM      = HexColor("#CBD5E1")
W_FADE     = HexColor("#8899AA")


# ── Helpers ───────────────────────────────────────────────────────────────────

def stars(c, x0, y0, w, h, seed=42, n=180):
    rng = random.Random(seed)
    c.saveState()
    for _ in range(n):
        sx = x0 + rng.random() * w
        sy = y0 + rng.random() * h
        sz = rng.choice([0.4, 0.4, 0.7, 0.7, 1.1, 1.5])
        al = rng.uniform(0.25, 1.0)
        c.setFillColorRGB(0.85 + 0.1 * al, 0.9 + 0.05 * al, 1.0, al)
        c.circle(sx, sy, sz, fill=1, stroke=0)
    c.restoreState()


def neural_net(c, cx, cy, rx, ry, seed=77):
    """Approximate neural brain network with nodes & glowing edges."""
    rng = random.Random(seed)

    # Generate scattered node positions inside an ellipse
    raw = []
    while len(raw) < 40:
        tx = rng.uniform(-1, 1)
        ty = rng.uniform(-1, 1)
        if tx**2 + ty**2 <= 1:
            # Slightly flatten top/bottom for brain silhouette
            nx = cx + rx * tx * (1 - 0.25 * abs(ty))
            ny = cy + ry * ty * 0.72
            raw.append((nx, ny, rng.uniform(0.35, 0.85)))

    # Three bright SRS nodes
    srs = [
        (cx - rx * 0.12, cy + ry * 0.30, "1 DAY",   1.0),
        (cx + rx * 0.48, cy + ry * 0.08, "7 DAYS",  1.0),
        (cx - rx * 0.28, cy - ry * 0.32, "30 DAYS", 1.0),
    ]
    srs_pts = [(s[0], s[1]) for s in srs]

    all_nodes = raw + [(s[0], s[1], s[3]) for s in srs]

    # Draw edges
    c.saveState()
    for i in range(len(all_nodes)):
        for j in range(i + 1, len(all_nodes)):
            x1, y1, _ = all_nodes[i]
            x2, y2, _ = all_nodes[j]
            d = math.hypot(x2 - x1, y2 - y1)
            thresh = rx * 0.62
            if d < thresh:
                al = (1 - d / thresh) * 0.55
                is_srs = (i >= len(raw)) or (j >= len(raw))
                if is_srs:
                    c.setStrokeColorRGB(0.83, 0.69, 0.22, al * 1.0)
                    c.setLineWidth(0.5)
                else:
                    c.setStrokeColorRGB(0.31, 0.76, 0.97, al * 0.55)
                    c.setLineWidth(0.35)
                c.line(x1, y1, x2, y2)
    c.restoreState()

    # Regular nodes
    c.saveState()
    for nx, ny, br in raw:
        sz = 1.2 + br * 1.6
        c.setFillColorRGB(0.31, 0.76, 0.97, 0.12)
        c.circle(nx, ny, sz * 3.5, fill=1, stroke=0)
        c.setFillColorRGB(0.45, 0.82, 1.0, br * 0.75)
        c.circle(nx, ny, sz, fill=1, stroke=0)
    c.restoreState()

    # SRS bright nodes (gold glow)
    c.saveState()
    for lx, ly, label, _ in srs:
        for glow_r, glow_a in [(22, 0.08), (14, 0.15), (8, 0.25)]:
            c.setFillColorRGB(0.83, 0.69, 0.22, glow_a)
            c.circle(lx, ly, glow_r, fill=1, stroke=0)
        c.setFillColorRGB(0.94, 0.88, 0.38, 1.0)
        c.circle(lx, ly, 4.5, fill=1, stroke=0)
        c.setFillColorRGB(1, 1, 1, 1)
        c.circle(lx, ly, 1.8, fill=1, stroke=0)
    c.restoreState()

    # SRS labels
    c.saveState()
    c.setFont("Helvetica-BoldOblique", 6.5)
    offsets = {
        "1 DAY":   (0,  12),
        "7 DAYS":  (18,  8),
        "30 DAYS": (-4, -14),
    }
    for lx, ly, label, _ in srs:
        ox, oy = offsets[label]
        c.setFillColor(GOLD_LIGHT)
        c.drawCentredString(lx + ox, ly + oy, label)
    c.restoreState()


def icon_book(c, cx, cy, sz):
    hw = sz * 0.42
    c.setLineWidth(0.8)
    c.rect(cx - hw, cy - sz * 0.5, hw, sz, fill=0, stroke=1)
    c.rect(cx,       cy - sz * 0.5, hw, sz, fill=0, stroke=1)
    c.line(cx - 0.5, cy - sz * 0.5, cx - 0.5, cy + sz * 0.5)


def icon_clock(c, cx, cy, sz):
    c.setLineWidth(0.8)
    c.circle(cx, cy, sz * 0.5, fill=0, stroke=1)
    c.line(cx, cy, cx, cy + sz * 0.35)
    c.line(cx, cy, cx + sz * 0.28, cy)


def icon_calendar(c, cx, cy, sz):
    c.setLineWidth(0.8)
    c.rect(cx - sz * 0.5, cy - sz * 0.38, sz, sz * 0.76, fill=0, stroke=1)
    c.line(cx - sz * 0.5, cy + sz * 0.15, cx + sz * 0.5, cy + sz * 0.15)
    c.line(cx - sz * 0.18, cy + sz * 0.18, cx - sz * 0.18, cy + sz * 0.38)
    c.line(cx + sz * 0.18, cy + sz * 0.18, cx + sz * 0.18, cy + sz * 0.38)


def icon_target(c, cx, cy, sz):
    c.setLineWidth(0.8)
    c.circle(cx, cy, sz * 0.5, fill=0, stroke=1)
    c.circle(cx, cy, sz * 0.3, fill=0, stroke=1)
    c.setFillColor(GOLD)
    c.circle(cx, cy, sz * 0.13, fill=1, stroke=0)


ICONS = [icon_book, icon_clock, icon_calendar, icon_target]


def wordwrap(c, text, x, y, max_w, font, size, color, leading=11):
    """Simple word-wrap text draw. Returns final y."""
    c.setFont(font, size)
    c.setFillColor(color)
    words = text.split()
    line = ""
    avg_char_w = size * 0.52  # rough Helvetica char width
    max_chars = int(max_w / avg_char_w)
    for word in words:
        candidate = (line + " " + word).strip()
        if len(candidate) <= max_chars:
            line = candidate
        else:
            c.drawString(x, y, line)
            y -= leading
            line = word
    if line:
        c.drawString(x, y, line)
        y -= leading
    return y


# ── Panels ────────────────────────────────────────────────────────────────────

def draw_back(c, x0, y0, w, h):
    # Background
    c.setFillColor(NAVY)
    c.rect(x0, y0, w, h, fill=1, stroke=0)
    stars(c, x0, y0, w, h, seed=17, n=140)

    # Subtle dark vignette top
    c.saveState()
    for i in range(30):
        a = 0.18 * (1 - i / 30)
        c.setFillColorRGB(0.02, 0.05, 0.10, a)
        c.rect(x0, y0 + h - (i + 1) * 16, w, 16, fill=1, stroke=0)
    c.restoreState()

    PAD   = 30
    cx    = x0 + PAD
    cw    = w - 2 * PAD
    mid_x = x0 + w / 2
    y     = y0 + h - PAD

    # ── Headline (borrowed from Image 2) ──────────────────────────────────
    y -= 14
    c.setFont("Helvetica-BoldOblique", 8)
    c.setFillColor(GOLD)
    c.drawCentredString(mid_x, y, "BUILT FOR INTELLIGENT LEARNERS.")
    y -= 12
    c.drawCentredString(mid_x, y, "ENGINEERED FOR LASTING RESULTS.")
    y -= 10

    # Gold rule
    c.setStrokeColor(GOLD)
    c.setLineWidth(0.5)
    c.line(cx, y, cx + cw, y)
    y -= 4

    # Diamond ornament
    c.saveState()
    c.setFillColor(GOLD)
    dm = 4
    c.translate(mid_x, y + 2)
    c.rotate(45)
    c.rect(-dm / 2, -dm / 2, dm, dm, fill=1, stroke=0)
    c.restoreState()
    y -= 14

    # ── HOW IT WORKS ──────────────────────────────────────────────────────
    c.setFont("Helvetica-Bold", 10.5)
    c.setFillColor(W_PURE)
    c.drawString(cx, y, "HOW IT WORKS")
    y -= 4

    c.setStrokeColor(GOLD)
    c.setLineWidth(0.4)
    c.line(cx, y, cx + cw, y)
    y -= 16

    steps = [
        ("01", "NEW WORDS",
         "Learn 5 carefully selected high-level words each day with "
         "clear definitions and contextual examples."),
        ("02", "24H RECALL",
         "Fill-in-the-blank exercises from yesterday reinforce "
         "short-term memory at the critical 24-hour mark."),
        ("03", "7-DAY REVIEW",
         "A matching exercise revisits words from one week ago, "
         "consolidating them into long-term storage."),
        ("04", "30-DAY MASTERY",
         "A final synonym challenge locks words from 30 days ago "
         "into permanent, effortless recall."),
    ]

    for idx, (num, title, desc) in enumerate(steps):
        icon_fn = ICONS[idx]
        icon_cx = cx + 11
        icon_cy = y - 9

        # Icon circle glow
        c.saveState()
        c.setFillColorRGB(0.83, 0.69, 0.22, 0.12)
        c.circle(icon_cx, icon_cy, 14, fill=1, stroke=0)
        c.setStrokeColor(GOLD)
        c.setFillColor(GOLD)
        icon_fn(c, icon_cx, icon_cy, 13)
        c.restoreState()

        tx = cx + 30

        # Number + title on same line
        c.setFont("Helvetica-Bold", 8.5)
        c.setFillColor(GOLD)
        c.drawString(tx, y, num + "  ")

        c.setFont("Helvetica-Bold", 8.5)
        c.setFillColor(W_PURE)
        c.drawString(tx + 18, y, title)
        y -= 13

        # Description
        c.setFont("Helvetica", 7.5)
        c.setFillColor(W_DIM)
        avg = 7.5 * 0.52
        max_c = int((cw - 30) / avg)
        words_q = desc.split()
        line = ""
        for word in words_q:
            cand = (line + " " + word).strip()
            if len(cand) <= max_c:
                line = cand
            else:
                c.drawString(tx, y, line)
                y -= 10
                line = word
        if line:
            c.drawString(tx, y, line)
            y -= 10

        y -= 8  # gap between steps

    # ── SCIENCE OF MEMORY ──────────────────────────────────────────────
    y -= 4
    c.setStrokeColor(GOLD)
    c.setLineWidth(0.4)
    c.line(cx, y, cx + cw, y)
    y -= 14

    c.setFont("Helvetica-Bold", 10)
    c.setFillColor(W_PURE)
    c.drawString(cx, y, "THE SCIENCE OF MEMORY")
    y -= 13

    science = (
        "Spaced Repetition is a scientifically proven learning technique that "
        "optimises recall by reviewing information at precisely the moment your "
        "brain is about to forget it. This method strengthens neural connections "
        "and dramatically improves long-term retention — helping you remember "
        "more, for longer, with less effort."
    )
    y = wordwrap(c, science, cx, y, cw, "Helvetica", 7.5, W_DIM, leading=10.5)

    # ── BOTTOM ──────────────────────────────────────────────────────────
    bot = y0 + PAD

    # ISBN barcode box
    bc_w, bc_h = 96, 60
    bc_x = x0 + w - PAD - bc_w
    bc_y = bot
    c.setFillColor(W_PURE)
    c.rect(bc_x, bc_y, bc_w, bc_h, fill=1, stroke=0)
    # Barcode line simulation
    c.saveState()
    rng2 = random.Random(99)
    bx2 = bc_x + 6
    while bx2 < bc_x + bc_w - 6:
        bw2 = rng2.choice([0.8, 0.8, 1.2, 1.8])
        c.setFillColor(black)
        c.rect(bx2, bc_y + 18, bw2, bc_h - 26, fill=1, stroke=0)
        bx2 += bw2 + rng2.choice([0.8, 1.2, 2.0])
    c.restoreState()
    c.setFont("Helvetica", 5.5)
    c.setFillColor(black)
    c.drawCentredString(bc_x + bc_w / 2, bc_y + 6, "9 780000 000000")

    # Publisher block
    c.saveState()
    c.setFont("Helvetica-Bold", 9.5)
    c.setFillColor(GOLD)
    c.drawString(cx, bot + 36, "LEXIQUENT PRESS")
    c.setFont("Helvetica", 7)
    c.setFillColor(W_FADE)
    c.drawString(cx, bot + 24, "WORDS TODAY. MASTERY FOREVER.")

    # Minimal L-pillar logo mark
    c.setStrokeColor(GOLD)
    c.setLineWidth(1.8)
    lx, ly = cx - 20, bot + 26
    c.line(lx, ly + 14, lx, ly)
    c.line(lx, ly, lx + 11, ly)
    c.restoreState()

    # Price tag
    c.setFont("Helvetica", 7.5)
    c.setFillColor(W_FADE)
    c.drawString(cx, bot + 8, "USD $13.99")

    # KDP category
    c.setFont("Helvetica", 6)
    c.setFillColor(W_FADE)
    cat = "Education / Test Preparation / SAT & GRE / Vocabulary"
    c.drawString(cx, bot - 2, cat)


def draw_spine(c, x0, y0, w, h):
    c.setFillColor(NAVY_DARK)
    c.rect(x0, y0, w, h, fill=1, stroke=0)

    # Edge rules
    c.setStrokeColor(GOLD)
    c.setLineWidth(0.35)
    c.line(x0 + 1,     y0, x0 + 1,     y0 + h)
    c.line(x0 + w - 1, y0, x0 + w - 1, y0 + h)

    # Spine text — rotated 90° counter-clockwise (reads bottom → top)
    c.saveState()
    c.translate(x0 + w / 2, y0 + h / 2)
    c.rotate(90)

    # Title
    c.setFont("Helvetica-Bold", 6.5)
    c.setFillColor(W_PURE)
    c.drawCentredString(40, 2, "ADVANCED SAT/GRE VOCABULARY WORKBOOK")

    # Publisher at far end
    c.setFont("Helvetica-Bold", 5)
    c.setFillColor(GOLD)
    c.drawCentredString(-h / 2 + 22, 2, "LEXIQUENT")

    c.restoreState()

    # Small gold diamond ornament, centered on spine
    c.saveState()
    c.setFillColor(GOLD)
    c.translate(x0 + w / 2, y0 + h * 0.72)
    c.rotate(45)
    dm = 3.5
    c.rect(-dm / 2, -dm / 2, dm, dm, fill=1, stroke=0)
    c.restoreState()


def draw_front(c, x0, y0, w, h, img_path=None):
    """Place the actual front-cover PNG, scaled to fill the panel + bleed."""
    if img_path:
        # Extend the image into the bleed on the 3 outer sides (right, top, bottom).
        # The spine side (left edge = x0) is already flush with the spine panel.
        draw_x = x0
        draw_y = y0 - BLEED          # bleed below trim
        draw_w = w + BLEED           # bleed beyond right trim
        draw_h = h + 2 * BLEED      # bleed above + below trim
        c.drawImage(img_path, draw_x, draw_y, width=draw_w, height=draw_h,
                    preserveAspectRatio=False, mask='auto')
    else:
        # Fallback: solid navy if no image provided
        c.setFillColor(NAVY)
        c.rect(x0, y0, w, h, fill=1, stroke=0)


# ── Trim / bleed guide lines ──────────────────────────────────────────────────

def trim_guides(c):
    c.saveState()
    c.setStrokeColorRGB(1, 0, 0, 0.55)
    c.setLineWidth(0.3)
    c.setDash(5, 5)
    # Vertical trims
    for xv in [BLEED, BLEED + PAGE_W, BLEED + PAGE_W + SPINE_W,
                BLEED + PAGE_W + SPINE_W + PAGE_W]:
        c.line(xv, 0, xv, TOTAL_H)
    # Horizontal trims
    for yh in [BLEED, BLEED + PAGE_H]:
        c.line(0, yh, TOTAL_W, yh)

    # Labels
    c.setFont("Helvetica", 5)
    c.setFillColorRGB(1, 0, 0, 0.7)
    c.drawString(2, BLEED + PAGE_H / 2, "BACK")
    c.drawString(BLEED + PAGE_W + SPINE_W + 2, BLEED + PAGE_H / 2, "FRONT")
    c.drawString(BLEED + PAGE_W + 2, BLEED + PAGE_H / 2, "SPINE")
    c.restoreState()


# ── Main ──────────────────────────────────────────────────────────────────────

def generate_cover(filename="Cover_SAT_GRE_Workbook.pdf",
                   front_image=None,
                   guides=True):
    cv = canvas.Canvas(filename, pagesize=(TOTAL_W, TOTAL_H))
    cv.setTitle("Advanced SAT/GRE Vocabulary Workbook — Full Paperback Cover")
    cv.setAuthor("Lexiquent Press")

    # Full bleed background (navy fills any gaps at edges)
    cv.setFillColor(NAVY)
    cv.rect(0, 0, TOTAL_W, TOTAL_H, fill=1, stroke=0)

    # Panels
    draw_back( cv, BK_X,      CT_Y, BK_W,   CT_H)
    draw_spine(cv, X_SPINE_L, CT_Y, SPINE_W, CT_H)
    draw_front(cv, FR_X,      CT_Y, FR_W,   CT_H, img_path=front_image)

    if guides:
        trim_guides(cv)

    cv.save()

    print(f"Generated : {filename}")
    print(f"Canvas    : {TOTAL_W/IN:.4f}\" × {TOTAL_H/IN:.4f}\"")
    print(f"Spine     : {SPINE_W/IN:.4f}\" ({SPINE_W:.2f} pt)")
    print(f"Front img : {front_image or 'none (fallback navy)'}")
    print(f"Guides    : {'YES — remove before KDP upload' if guides else 'OFF'}")


FRONT_COVER_IMAGE = (
    "/root/.claude/uploads/e38dc713-bbc2-44cb-9057-6a670caf3951/"
    "e5a597dd-1000010432.png"
)

if __name__ == "__main__":
    generate_cover(front_image=FRONT_COVER_IMAGE, guides=True)
