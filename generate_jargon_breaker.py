"""
The Jargon Breaker Protocol — Premium Workbook Generator
120-page, 6x9-inch KDP-ready interior PDF.
Output: Jargon_Breaker_Interior_Final.pdf

Structure:
  5  front matter pages  (title, copyright, manifesto, how-to, progress tracker)
  95 session pages       (5 per weekly block)
  19 weekly debrief pages (after every 5 sessions)
  1  conclusion page
= 120 pages total

Run:  python generate_jargon_breaker.py
"""

import math
import random
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch as IN
from reportlab.lib.colors import black, white, HexColor
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# ── Unicode-capable fonts ──────────────────────────────────────────────────────
_LIB = "/usr/share/fonts/truetype/liberation"
pdfmetrics.registerFont(TTFont("Helv",    f"{_LIB}/LiberationSans-Regular.ttf"))
pdfmetrics.registerFont(TTFont("HelvB",   f"{_LIB}/LiberationSans-Bold.ttf"))
pdfmetrics.registerFont(TTFont("HelvI",   f"{_LIB}/LiberationSans-Italic.ttf"))
pdfmetrics.registerFont(TTFont("HelvBI",  f"{_LIB}/LiberationSans-BoldItalic.ttf"))
pdfmetrics.registerFont(TTFont("Mono",    f"{_LIB}/LiberationMono-Regular.ttf"))
pdfmetrics.registerFont(TTFont("MonoB",   f"{_LIB}/LiberationMono-Bold.ttf"))

# ── Page geometry ──────────────────────────────────────────────────────────────
PAGE_W  = 6.125 * IN   # includes 0.125" bleed
PAGE_H  = 9.25  * IN
ML      = 0.85  * IN   # gutter (left)
MR      = 0.6   * IN   # outside
MT      = 0.6   * IN   # top
MB      = 0.6   * IN   # bottom

# Content rectangle
CX = ML
CY = MB
CW = PAGE_W - ML - MR
CH = PAGE_H - MT - MB

# Accent colours (for B&W print — use only black tints)
C_BLACK  = black
C_MID    = HexColor("#444444")
C_LIGHT  = HexColor("#888888")
C_PALE   = HexColor("#CCCCCC")
C_RULE   = HexColor("#AAAAAA")
C_DOT    = HexColor("#DDDDDD")

TOTAL_SESSIONS = 95
DEBRIEF_EVERY  = 5


# ── Primitive helpers ─────────────────────────────────────────────────────────

def corner_brackets(c, x, y, w, h, size=8, lw=0.5):
    """Draw L-shaped corner brackets (blueprint/circuit aesthetic)."""
    c.saveState()
    c.setStrokeColor(C_BLACK)
    c.setLineWidth(lw)
    for bx, by, sx, sy in [
        (x,     y + h, 1,  -1),  # top-left
        (x + w, y + h, -1, -1),  # top-right
        (x,     y,     1,   1),  # bottom-left
        (x + w, y,     -1,  1),  # bottom-right
    ]:
        c.line(bx, by, bx + sx * size, by)
        c.line(bx, by, bx, by + sy * size)
    c.restoreState()


def dot_grid(c, x, y, w, h, spacing=10, r=0.6):
    """Subtle dot grid — blueprint background texture."""
    c.saveState()
    c.setFillColor(C_DOT)
    cols = int(w / spacing) + 1
    rows = int(h / spacing) + 1
    for i in range(cols):
        for j in range(rows):
            px = x + i * spacing
            py = y + j * spacing
            if x <= px <= x + w and y <= py <= y + h:
                c.circle(px, py, r, fill=1, stroke=0)
    c.restoreState()


def section_box(c, x, y, w, h, label, label_size=7.5, fill_dots=False,
                lw=0.5, tag=None):
    """Draw a labelled section box with optional dot-grid fill."""
    c.saveState()
    c.setStrokeColor(C_BLACK)
    c.setLineWidth(lw)
    c.rect(x, y, w, h, fill=0, stroke=1)
    if fill_dots:
        dot_grid(c, x + 3, y + 3, w - 6, h - 6)
    # Label tab (top-left)
    tab_w = len(label) * label_size * 0.62 + 10
    tab_h = label_size + 5
    c.setFillColor(C_BLACK)
    c.rect(x, y + h, tab_w, tab_h, fill=1, stroke=0)
    c.setFillColor(white)
    c.setFont("MonoB", label_size)
    c.drawString(x + 5, y + h + 3, label)
    # Optional right-side tag
    if tag:
        tag_w = len(tag) * 6 + 8
        c.setFillColor(C_BLACK)
        c.rect(x + w - tag_w, y + h, tag_w, tab_h, fill=1, stroke=0)
        c.setFillColor(white)
        c.setFont("Mono", 6)
        c.drawString(x + w - tag_w + 4, y + h + 3, tag)
    c.restoreState()
    corner_brackets(c, x, y, w, h)


def ruled_lines(c, x, y, w, h, n, dash=None, lw=0.5, color=C_RULE):
    """Draw n evenly-spaced horizontal rules inside a box."""
    c.saveState()
    c.setStrokeColor(color)
    c.setLineWidth(lw)
    if dash:
        c.setDash(*dash)
    gap = h / (n + 1)
    for i in range(1, n + 1):
        ly = y + h - i * gap
        c.line(x + 4, ly, x + w - 4, ly)
    c.restoreState()


def checkbox_line(c, x, y, w, box_size=9, lw=0.5):
    """One checkbox followed by a ruled line."""
    c.saveState()
    c.setStrokeColor(C_BLACK)
    c.setLineWidth(lw)
    c.rect(x, y - box_size * 0.3, box_size, box_size, fill=0, stroke=1)
    c.setStrokeColor(C_RULE)
    c.line(x + box_size + 6, y + box_size * 0.3,
           x + w - 4,        y + box_size * 0.3)
    c.restoreState()


def dotted_lines(c, x, y, w, h, n, lw=0.4):
    """Draw n dotted horizontal rules (friction log style)."""
    c.saveState()
    c.setStrokeColor(C_MID)
    c.setLineWidth(lw)
    c.setDash(1.5, 4)
    gap = h / (n + 1)
    for i in range(1, n + 1):
        ly = y + h - i * gap
        c.line(x + 4, ly, x + w - 4, ly)
    c.restoreState()


def progress_dots(c, cx, y, total, current, r=3.5, gap=10):
    """Compact progress indicator: filled dots = done, outline = remaining."""
    c.saveState()
    n = min(total, 20)  # cap at 20 dots
    filled = min(current, n)
    start_x = cx - (n - 1) * gap / 2
    for i in range(n):
        px = start_x + i * gap
        c.setLineWidth(0.4)
        c.setStrokeColor(C_MID)
        if i < filled:
            c.setFillColor(C_MID)
            c.circle(px, y, r, fill=1, stroke=0)
        else:
            c.setFillColor(white)
            c.circle(px, y, r, fill=1, stroke=1)
    # Progress fraction
    c.setFont("Mono", 6.5)
    c.setFillColor(C_LIGHT)
    c.drawCentredString(cx, y - r - 7, f"SESSION {current} / {total}")
    c.restoreState()


def complexity_gauge(c, x, y, level):
    """Five-segment battery-style complexity indicator."""
    seg_w, seg_h, gap = 12, 8, 2
    c.saveState()
    for i in range(5):
        sx = x + i * (seg_w + gap)
        c.setLineWidth(0.4)
        c.setStrokeColor(C_BLACK)
        if i < level:
            c.setFillColor(C_BLACK)
        else:
            c.setFillColor(white)
        c.rect(sx, y, seg_w, seg_h, fill=1, stroke=1)
    # Terminal nub
    nub_x = x + 5 * (seg_w + gap)
    c.setFillColor(C_BLACK)
    c.rect(nub_x, y + 2, 4, 4, fill=1, stroke=0)
    c.restoreState()


def page_footer(c, page_num, total_pages=120):
    """Minimal footer: page number + thin rule."""
    c.saveState()
    c.setStrokeColor(C_PALE)
    c.setLineWidth(0.4)
    fy = MB * 0.45
    c.line(ML, fy, PAGE_W - MR, fy)
    c.setFont("Mono", 6.5)
    c.setFillColor(C_LIGHT)
    c.drawRightString(PAGE_W - MR, fy - 9, f"{page_num} / {total_pages}")
    c.restoreState()


# ── Front matter pages ────────────────────────────────────────────────────────

def draw_title_page(c):
    c.saveState()

    # Full-bleed grid background
    dot_grid(c, 0, 0, PAGE_W, PAGE_H, spacing=18, r=0.7)

    # Top border bar
    c.setFillColor(C_BLACK)
    c.rect(0, PAGE_H - 28, PAGE_W, 28, fill=1, stroke=0)
    c.setFillColor(white)
    c.setFont("Mono", 8)
    c.drawCentredString(PAGE_W / 2, PAGE_H - 18,
                        "[ COGNITIVE DECONSTRUCTION WORKBOOK — SERIES 01 ]")

    # Main title block
    ty = PAGE_H * 0.68
    c.setFont("HelvB", 32)
    c.setFillColor(C_BLACK)
    c.drawCentredString(PAGE_W / 2, ty, "THE JARGON")
    c.drawCentredString(PAGE_W / 2, ty - 38, "BREAKER")

    # Accent underline
    c.setLineWidth(2)
    c.setStrokeColor(C_BLACK)
    uw = CW * 0.55
    c.line(PAGE_W / 2 - uw / 2, ty - 50, PAGE_W / 2 + uw / 2, ty - 50)

    # Subtitle
    c.setFont("Mono", 10)
    c.setFillColor(C_MID)
    c.drawCentredString(PAGE_W / 2, ty - 68, "PROTOCOL")
    c.setFont("HelvI", 9)
    c.drawCentredString(PAGE_W / 2, ty - 84,
                        "Deconstruct Any Concept. Master It.")

    # Central instruction box
    bx = ML + CW * 0.08
    bw = CW * 0.84
    bh = 66
    by = PAGE_H * 0.33
    c.setLineWidth(0.5)
    c.setStrokeColor(C_BLACK)
    c.rect(bx, by, bw, bh, fill=0, stroke=1)
    corner_brackets(c, bx, by, bw, bh)
    lines = [
        "Ban the jargon. Explain simply.",
        "Build an analogy. Log the friction.",
        "Understand it — or admit you don't.",
    ]
    c.setFont("Mono", 8.5)
    c.setFillColor(C_MID)
    for i, line in enumerate(lines):
        c.drawCentredString(PAGE_W / 2, by + bh - 18 - i * 16, line)

    # Stats strip
    sy = PAGE_H * 0.20
    c.setFont("MonoB", 8)
    c.setFillColor(C_BLACK)
    stats = ["95 SESSIONS", "|", "19 WEEKLY DEBRIEFS", "|", "6 × 9 IN"]
    full = "  ".join(stats)
    c.drawCentredString(PAGE_W / 2, sy, full)

    # Bottom border bar
    c.setFillColor(C_BLACK)
    c.rect(0, 0, PAGE_W, 20, fill=1, stroke=0)
    c.setFillColor(white)
    c.setFont("Mono", 6.5)
    c.drawCentredString(PAGE_W / 2, 6, "SIMPLICITY IS THE ULTIMATE SOPHISTICATION")

    c.restoreState()


def draw_copyright_page(c, page_num):
    c.saveState()
    c.setFont("Helv", 8.5)
    c.setFillColor(C_MID)
    texts = [
        "© All Rights Reserved.",
        "No part of this publication may be reproduced, distributed,",
        "or transmitted in any form without prior written permission.",
        "",
        "First Edition.",
        "Printed in the United States of America.",
        "",
        "The Jargon Breaker Protocol is a registered workbook concept.",
        "Use of this workbook is strictly for personal learning.",
    ]
    y = PAGE_H * 0.5 + len(texts) * 10
    for line in texts:
        c.drawCentredString(PAGE_W / 2, y, line)
        y -= 14
    page_footer(c, page_num)
    c.restoreState()


def draw_manifesto_page(c, page_num):
    """The Anti-Jargon Manifesto — emotional buy-in page."""
    c.saveState()
    dot_grid(c, ML, MB, CW, CH, spacing=14, r=0.55)

    # Header
    c.setFillColor(C_BLACK)
    c.rect(ML, CH + MB - 2, CW, 22, fill=1, stroke=0)
    c.setFillColor(white)
    c.setFont("MonoB", 9)
    c.drawCentredString(PAGE_W / 2, CH + MB + 6, "[ THE ANTI-JARGON MANIFESTO ]")

    manifesto = [
        ("I DECLARE", 14, "HelvB"),
        ("", 0, ""),
        ("that I will not hide behind complex vocabulary.", 9, "Mono"),
        ("that if I cannot explain it simply, I do not understand it.", 9, "Mono"),
        ("that technical jargon is a tool — not a shield.", 9, "Mono"),
        ("", 0, ""),
        ("I COMMIT", 14, "HelvB"),
        ("", 0, ""),
        ("to banning my crutch words before I begin.", 9, "Mono"),
        ("to finding the analogy before I claim mastery.", 9, "Mono"),
        ("to logging my confusion honestly.", 9, "Mono"),
        ("to choosing clarity over the appearance of intelligence.", 9, "Mono"),
        ("", 0, ""),
        ("I UNDERSTAND", 14, "HelvB"),
        ("", 0, ""),
        ('that "I know it, I just can\'t explain it" means', 9, "Mono"),
        ("I do not know it.", 9, "MonoB"),
        ("", 0, ""),
        ("Signed: _______________________________", 9, "HelvI"),
        ("Date:   _______________", 9, "HelvI"),
    ]

    y = CH + MB - 32
    for text, size, font in manifesto:
        if not text:
            y -= 6
            continue
        c.setFont(font, size)
        c.setFillColor(C_BLACK if font in ("HelvB", "MonoB") else C_MID)
        indent = ML + 20 if not font.endswith("B") else ML + 10
        c.drawString(indent, y, text)
        y -= size + 6

    # Bottom rule
    c.setStrokeColor(C_BLACK)
    c.setLineWidth(1.5)
    c.line(ML, MB + 20, PAGE_W - MR, MB + 20)
    c.setFont("Mono", 7)
    c.setFillColor(C_MID)
    c.drawCentredString(PAGE_W / 2, MB + 8,
                        "[ TEAR OUT AND POST WHERE YOU WORK ]")
    page_footer(c, page_num)
    c.restoreState()


def draw_how_to_use_page(c, page_num):
    c.saveState()
    # Title
    c.setFont("HelvB", 14)
    c.setFillColor(C_BLACK)
    c.drawCentredString(PAGE_W / 2, CH + MB - 16, "HOW TO USE THIS WORKBOOK")
    c.setLineWidth(0.5)
    c.setStrokeColor(C_BLACK)
    c.line(ML, CH + MB - 22, PAGE_W - MR, CH + MB - 22)

    steps = [
        ("STEP 1", "BAN THE JARGON",
         "Write 3-4 terms you are FORBIDDEN to use. This forces\n"
         "you to find simpler language before you start."),
        ("STEP 2", "ELI5 — EXPLAIN LIKE I'M FIVE",
         "Use only everyday words. Imagine you are explaining\n"
         "to a curious 10-year-old with no background."),
        ("STEP 3", "BUILD THE ANALOGY BRIDGE",
         "Link the abstract concept to something physical.\n"
         "Sketch it or write: 'It works like a ...'"),
        ("STEP 4", "LOG THE FRICTION",
         "Be ruthlessly honest. Which part of your explanation\n"
         "still feels forced or unclear? Name it."),
        ("BONUS", "THE GOLDEN SENTENCE + 5-WORD CHALLENGE",
         "Compress your entire explanation to 15 words,\n"
         "then to 5 words. Constraints reveal mastery."),
    ]

    y = CH + MB - 50
    for tag, title, desc in steps:
        # Tag badge
        c.setFillColor(C_BLACK)
        tw = 52
        c.rect(ML, y - 2, tw, 20, fill=1, stroke=0)
        c.setFillColor(white)
        c.setFont("MonoB", 7.5)
        c.drawCentredString(ML + tw / 2, y + 5, tag)

        # Title
        c.setFont("HelvB", 9.5)
        c.setFillColor(C_BLACK)
        c.drawString(ML + tw + 8, y + 6, title)

        # Description
        c.setFont("Mono", 8)
        c.setFillColor(C_MID)
        for i, line in enumerate(desc.split('\n')):
            c.drawString(ML + tw + 8, y - 5 - i * 11, line)

        y -= 58

    # Weekly Debrief note
    y -= 10
    c.setFillColor(C_BLACK)
    c.rect(ML, y - 2, CW, 18, fill=0, stroke=1)
    c.setFont("Mono", 8)
    c.setFillColor(C_MID)
    c.drawString(ML + 8, y + 5,
                 "Every 5 sessions → WEEKLY DEBRIEF page. "
                 "Identify patterns in your friction points.")

    page_footer(c, page_num)
    c.restoreState()


def draw_progress_tracker_page(c, page_num):
    """Grid dashboard — one cell per session + debrief markers."""
    c.saveState()
    c.setFont("HelvB", 13)
    c.setFillColor(C_BLACK)
    c.drawCentredString(PAGE_W / 2, CH + MB - 16, "PROGRESS TRACKER")
    c.setFont("Mono", 7.5)
    c.setFillColor(C_MID)
    c.drawCentredString(PAGE_W / 2, CH + MB - 28,
                        "Shade each cell when you complete a session.")

    # Grid: 5 columns × 19 rows  + debrief rows
    cols = 5
    rows = 19
    cell_w = CW / (cols + 0.5)
    cell_h = (CH - 55) / (rows + 1)
    gx = ML + cell_w * 0.25
    gy_start = CH + MB - 45

    for row in range(rows):
        gy = gy_start - row * (cell_h + 2)
        for col in range(cols):
            session = row * cols + col + 1
            if session > TOTAL_SESSIONS:
                break
            cx_ = gx + col * (cell_w + 2)
            c.setLineWidth(0.4)
            c.setStrokeColor(C_MID)
            c.rect(cx_, gy - cell_h, cell_w, cell_h, fill=0, stroke=1)
            c.setFont("Mono", 6)
            c.setFillColor(C_LIGHT)
            c.drawCentredString(cx_ + cell_w / 2, gy - cell_h + 3,
                                f"S{session:02d}")
        # Debrief marker after each row of 5
        db_x = gx + cols * (cell_w + 2) + 3
        db_y = gy - cell_h
        c.setFillColor(C_BLACK)
        c.rect(db_x, db_y, cell_w * 0.8, cell_h, fill=0, stroke=1)
        c.setFont("Mono", 5.5)
        c.setFillColor(C_MID)
        c.drawCentredString(db_x + cell_w * 0.4, db_y + 3, f"D{row+1:02d}")

    # Legend
    ly = MB + 14
    c.setFont("Mono", 6.5)
    c.setFillColor(C_MID)
    c.drawString(ML, ly, "S## = Session   D## = Weekly Debrief   "
                 "[ shade when complete ]")

    page_footer(c, page_num)
    c.restoreState()


# ── Session page ──────────────────────────────────────────────────────────────

def draw_session_page(c, session_num, page_num):
    c.saveState()
    total_h = CH
    x0, y_bot = CX, CY
    w = CW

    # Section heights (% of content height)
    h_head   = total_h * 0.095
    h_s1     = total_h * 0.145
    h_s2     = total_h * 0.330
    h_s3     = total_h * 0.235
    h_s4     = total_h * 0.105
    h_bonus  = total_h * 0.090
    # Total = 1.000

    # Y positions (bottom up)
    y_bonus = y_bot
    y_s4    = y_bonus + h_bonus
    y_s3    = y_s4    + h_s4
    y_s2    = y_s3    + h_s3
    y_s1    = y_s2    + h_s2
    y_head  = y_s1    + h_s1

    # ── HEADER ───────────────────────────────────────────────────────────────
    # Outer border
    c.setLineWidth(0.5)
    c.setStrokeColor(C_BLACK)
    c.rect(x0, y_head, w, h_head, fill=0, stroke=1)
    corner_brackets(c, x0, y_head, w, h_head, size=7)

    # Session badge (top-left)
    badge_w = 70
    c.setFillColor(C_BLACK)
    c.rect(x0, y_head + h_head - 16, badge_w, 16, fill=1, stroke=0)
    c.setFillColor(white)
    c.setFont("MonoB", 8)
    c.drawString(x0 + 5, y_head + h_head - 11,
                 f"SESSION {session_num:02d}/{TOTAL_SESSIONS:02d}")

    # Week indicator
    week = math.ceil(session_num / DEBRIEF_EVERY)
    c.setFillColor(C_MID)
    c.setFont("Mono", 6.5)
    c.drawString(x0 + badge_w + 5, y_head + h_head - 11, f"WK {week:02d}")

    # Field + Topic fields
    pad = 6
    mid = x0 + w / 2
    row1_y = y_head + h_head - 28
    c.setFont("MonoB", 7.5)
    c.setFillColor(C_BLACK)
    c.drawString(x0 + pad, row1_y, "FIELD:")
    c.setStrokeColor(C_RULE)
    c.setLineWidth(0.4)
    c.line(x0 + 38, row1_y + 2, mid - 6, row1_y + 2)
    c.drawString(mid, row1_y, "TOPIC:")
    c.line(mid + 36, row1_y + 2, x0 + w - pad, row1_y + 2)

    # Complexity + Date
    row2_y = y_head + h_head - 44
    c.setFont("MonoB", 7.5)
    c.setFillColor(C_BLACK)
    c.drawString(x0 + pad, row2_y, "COMPLEXITY:")
    complexity_gauge(c, x0 + 72, row2_y - 1, level=0)
    c.drawString(mid, row2_y, "DATE:")
    c.setStrokeColor(C_RULE)
    c.setLineWidth(0.4)
    c.line(mid + 32, row2_y + 2, x0 + w - pad, row2_y + 2)

    # Progress dots
    progress_dots(c, x0 + w - 70, y_head + h_head - 50,
                  total=TOTAL_SESSIONS, current=session_num)

    # ── STEP 1: JARGON BAN ───────────────────────────────────────────────────
    section_box(c, x0, y_s1, w, h_s1,
                label="[STEP 1]  THE JARGON BAN",
                tag="BAN 3-4 TERMS",
                lw=0.5)

    instr_y = y_s1 + h_s1 - 14
    c.setFont("Mono", 7.5)
    c.setFillColor(C_MID)
    c.drawString(x0 + 8, instr_y,
                 'Terms you are FORBIDDEN to use in your explanation:')

    cb_start = y_s1 + h_s1 - 28
    cb_gap   = (h_s1 - 34) / 4
    for i in range(4):
        checkbox_line(c, x0 + 10, cb_start - i * cb_gap, w - 20)

    # ── STEP 2: ELI5 ZONE ────────────────────────────────────────────────────
    section_box(c, x0, y_s2, w, h_s2,
                label="[STEP 2]  ELI5 ZONE — EXPLAIN LIKE I'M FIVE",
                tag="NO JARGON",
                lw=0.5, fill_dots=True)

    c.setFont("Mono", 7.5)
    c.setFillColor(C_MID)
    c.drawString(x0 + 8, y_s2 + h_s2 - 14,
                 "Use only simple, everyday language. No crutch words allowed.")

    # Wide-ruled lines (kid-style = fewer, taller lines)
    ruled_lines(c, x0 + 6, y_s2 + 4, w - 12, h_s2 - 22,
                n=8, lw=0.5, color=C_RULE)

    # Rubber Duck icon (SVG-style with canvas)
    duck_x = x0 + w - 28
    duck_y = y_s2 + 12
    c.saveState()
    c.setStrokeColor(C_PALE)
    c.setFillColor(white)
    c.setLineWidth(0.6)
    c.ellipse(duck_x - 8, duck_y, duck_x + 8, duck_y + 11, stroke=1, fill=1)
    c.ellipse(duck_x - 5, duck_y + 9, duck_x + 5, duck_y + 17, stroke=1, fill=1)
    c.setFillColor(C_PALE)
    c.wedge(duck_x + 3, duck_y + 12, duck_x + 10, duck_y + 15,
            0, 40, stroke=0, fill=1)
    c.setFont("Mono", 5)
    c.setFillColor(C_PALE)
    c.drawCentredString(duck_x, duck_y - 6, "RUBBER")
    c.drawCentredString(duck_x, duck_y - 12, "DUCK TEST")
    c.restoreState()

    # ── STEP 3: ANALOGY BRIDGE ───────────────────────────────────────────────
    section_box(c, x0, y_s3, w, h_s3,
                label="[STEP 3]  THE ANALOGY BRIDGE",
                tag="SKETCH OR WRITE",
                lw=0.5)

    c.setFont("Mono", 7.5)
    c.setFillColor(C_MID)
    c.drawString(x0 + 8, y_s3 + h_s3 - 14,
                 "Connect this concept to a physical object or real-world situation.")

    # Sketch frame (left 45%)
    sk_w = w * 0.42
    sk_h = h_s3 - 28
    c.setStrokeColor(C_MID)
    c.setLineWidth(0.4)
    c.setDash(3, 3)
    c.rect(x0 + 6, y_s3 + 6, sk_w, sk_h, fill=0, stroke=1)
    c.setDash()
    c.setFont("Helv", 6.5)
    c.setFillColor(C_PALE)
    c.drawCentredString(x0 + 6 + sk_w / 2, y_s3 + 6 + sk_h / 2, "[ SKETCH ]")

    # Text side (right 50%)
    tx = x0 + sk_w + 14
    tw = w - sk_w - 20
    c.setFont("MonoB", 8)
    c.setFillColor(C_MID)
    c.drawString(tx, y_s3 + h_s3 - 26, "It's like a ...")
    ruled_lines(c, tx - 4, y_s3 + 6, tw + 4, h_s3 - 38,
                n=4, lw=0.5, color=C_RULE)

    # ── STEP 4: FRICTION LOG ─────────────────────────────────────────────────
    section_box(c, x0, y_s4, w, h_s4,
                label="[STEP 4]  FRICTION LOG",
                tag="BE HONEST",
                lw=0.5)

    c.setFont("Mono", 7.5)
    c.setFillColor(C_MID)
    c.drawString(x0 + 8, y_s4 + h_s4 - 14,
                 "Which part still feels blurry or forced?")
    dotted_lines(c, x0 + 6, y_s4 + 4, w - 12, h_s4 - 22, n=2)

    # ── BONUS: GOLDEN SENTENCE + 5-WORD CHALLENGE ────────────────────────────
    section_box(c, x0, y_bonus, w, h_bonus,
                label="[BONUS]  THE GOLDEN SENTENCE",
                tag="MAX 15 WORDS",
                lw=0.5)

    bpad = 8
    half_w = w / 2 - bpad
    bline_y = y_bonus + h_bonus * 0.45

    c.setFont("MonoB", 7)
    c.setFillColor(C_BLACK)
    c.drawString(x0 + bpad, y_bonus + h_bonus - 14,
                 "In 15 words or fewer:")
    c.setStrokeColor(C_RULE)
    c.setLineWidth(0.5)
    c.line(x0 + bpad, bline_y, x0 + half_w + bpad, bline_y)
    c.line(x0 + bpad, bline_y - 14, x0 + half_w + bpad, bline_y - 14)

    # 5-word box
    fw_x = x0 + w / 2 + bpad / 2
    fw_w = w / 2 - bpad * 1.5
    c.setFont("MonoB", 7)
    c.setFillColor(C_BLACK)
    c.drawString(fw_x, y_bonus + h_bonus - 14, "5-WORD CHALLENGE:")
    c.setFillColor(C_BLACK)
    c.setLineWidth(0.5)
    c.rect(fw_x, y_bonus + 4, fw_w, h_bonus - 22, fill=0, stroke=1)
    c.setFont("Mono", 6)
    c.setFillColor(C_PALE)
    c.drawCentredString(fw_x + fw_w / 2,
                        y_bonus + 4 + (h_bonus - 22) / 2 - 3,
                        "__ __ __ __ __")

    page_footer(c, page_num)
    c.restoreState()


# ── Weekly Debrief page ───────────────────────────────────────────────────────

def draw_debrief_page(c, debrief_num, s_start, s_end, page_num):
    c.saveState()
    dot_grid(c, ML, MB, CW, CH, spacing=14, r=0.55)

    # Header bar
    c.setFillColor(C_BLACK)
    c.rect(ML, CH + MB - 22, CW, 22, fill=1, stroke=0)
    c.setFillColor(white)
    c.setFont("MonoB", 9)
    c.drawString(ML + 8, CH + MB - 14,
                 f"[ WEEKLY DEBRIEF #{debrief_num:02d} ]")
    c.setFont("Mono", 8)
    c.drawRightString(ML + CW - 8, CH + MB - 14,
                      f"Sessions {s_start}–{s_end}")

    y = CH + MB - 44

    # Session rating grid
    c.setFont("MonoB", 8)
    c.setFillColor(C_BLACK)
    c.drawString(ML, y, "SESSION MASTERY RATINGS")
    y -= 16
    for s in range(s_start, s_end + 1):
        c.setFont("Mono", 8)
        c.setFillColor(C_BLACK)
        c.drawString(ML, y, f"S{s:02d}:")
        # 5 star boxes
        for i in range(5):
            bx = ML + 30 + i * 18
            c.setLineWidth(0.4)
            c.setStrokeColor(C_MID)
            c.rect(bx, y - 2, 14, 12, fill=0, stroke=1)
        c.setFont("Mono", 7)
        c.setFillColor(C_LIGHT)
        c.drawString(ML + 130, y + 2, "(1 = still fuzzy  5 = crystal clear)")
        y -= 18

    y -= 6
    c.setStrokeColor(C_MID)
    c.setLineWidth(0.4)
    c.line(ML, y, ML + CW, y)
    y -= 14

    debriefs = [
        ("WHICH CONCEPT WAS HARDEST TO SIMPLIFY?", 3),
        ("WHAT ANALOGY WORKED BEST — AND WHY?", 3),
        ("WHAT RECURRING FRICTION PATTERN DO YOU NOTICE?", 3),
        ("ONE REAL-WORLD SITUATION WHERE THIS MATTERS:", 2),
    ]

    for question, n_lines in debriefs:
        c.setFont("MonoB", 8)
        c.setFillColor(C_BLACK)
        c.drawString(ML, y, question)
        y -= 14
        dotted_lines(c, ML, y - n_lines * 14, CW, n_lines * 14, n=n_lines)
        y -= n_lines * 14 + 10

    # Weekly insight banner
    c.setLineWidth(0.5)
    c.setStrokeColor(C_BLACK)
    bh = 32
    c.rect(ML, MB + 22, CW, bh, fill=0, stroke=1)
    corner_brackets(c, ML, MB + 22, CW, bh, size=6)
    c.setFont("MonoB", 8)
    c.setFillColor(C_BLACK)
    c.drawCentredString(PAGE_W / 2, MB + 22 + bh - 12,
                        "THIS WEEK'S BREAKTHROUGH INSIGHT:")
    c.setStrokeColor(C_RULE)
    c.setLineWidth(0.4)
    c.line(ML + 8, MB + 30, ML + CW - 8, MB + 30)

    page_footer(c, page_num)
    c.restoreState()


# ── Conclusion page ───────────────────────────────────────────────────────────

def draw_conclusion_page(c, page_num):
    c.saveState()
    dot_grid(c, 0, 0, PAGE_W, PAGE_H, spacing=16, r=0.6)

    # Top bar
    c.setFillColor(C_BLACK)
    c.rect(0, PAGE_H - 28, PAGE_W, 28, fill=1, stroke=0)
    c.setFillColor(white)
    c.setFont("MonoB", 9)
    c.drawCentredString(PAGE_W / 2, PAGE_H - 16,
                        "[ PROTOCOL COMPLETE ]")

    # Main message
    ty = PAGE_H * 0.65
    c.setFont("HelvB", 18)
    c.setFillColor(C_BLACK)
    c.drawCentredString(PAGE_W / 2, ty, "YOU HAVE BROKEN")
    c.drawCentredString(PAGE_W / 2, ty - 24, "THE JARGON.")

    c.setFont("Mono", 9.5)
    c.setFillColor(C_MID)
    c.drawCentredString(PAGE_W / 2, ty - 50,
                        "95 concepts. Explained simply.")
    c.drawCentredString(PAGE_W / 2, ty - 64,
                        "No hiding. No crutches. Real understanding.")

    # Certificate box
    bx = ML + CW * 0.06
    bw = CW * 0.88
    bh = 90
    by = PAGE_H * 0.28
    c.setLineWidth(1)
    c.setStrokeColor(C_BLACK)
    c.rect(bx, by, bw, bh, fill=0, stroke=1)
    corner_brackets(c, bx, by, bw, bh, size=10, lw=1)
    c.setFont("MonoB", 8)
    c.setFillColor(C_BLACK)
    c.drawCentredString(PAGE_W / 2, by + bh - 18,
                        "THIS CERTIFIES THAT")
    c.setStrokeColor(C_RULE)
    c.setLineWidth(0.5)
    c.line(bx + 16, by + bh - 32, bx + bw - 16, by + bh - 32)
    c.setFont("Mono", 8)
    c.setFillColor(C_MID)
    c.drawCentredString(PAGE_W / 2, by + bh - 44,
                        "has completed The Jargon Breaker Protocol")
    c.drawCentredString(PAGE_W / 2, by + bh - 56, "and achieved clarity over complexity.")
    c.setFont("HelvI", 7.5)
    c.drawCentredString(PAGE_W / 2, by + 14, "Date: ___________________")
    c.drawCentredString(PAGE_W / 2, by + 28, "Signed: _______________________________")

    # Bottom
    c.setFillColor(C_BLACK)
    c.rect(0, 0, PAGE_W, 22, fill=1, stroke=0)
    c.setFillColor(white)
    c.setFont("Mono", 7)
    c.drawCentredString(PAGE_W / 2, 7,
                        "SIMPLICITY IS THE ULTIMATE SOPHISTICATION — REVISIT. REFINE. REPEAT.")

    page_footer(c, page_num)
    c.restoreState()


# ── Main generator ────────────────────────────────────────────────────────────

def generate(filename="Jargon_Breaker_Interior_Final.pdf"):
    c = canvas.Canvas(filename, pagesize=(PAGE_W, PAGE_H))
    c.setTitle("The Jargon Breaker Protocol — Premium Workbook")
    c.setAuthor("Cognitive Deconstruction Series")

    page = 1

    # Front matter (5 pages)
    draw_title_page(c);    c.showPage(); page += 1
    draw_copyright_page(c, page); c.showPage(); page += 1
    draw_manifesto_page(c, page); c.showPage(); page += 1
    draw_how_to_use_page(c, page); c.showPage(); page += 1
    draw_progress_tracker_page(c, page); c.showPage(); page += 1

    # Session + debrief blocks
    session = 1
    debrief = 1
    while session <= TOTAL_SESSIONS:
        # 5 session pages
        for _ in range(DEBRIEF_EVERY):
            if session > TOTAL_SESSIONS:
                break
            draw_session_page(c, session, page)
            c.showPage()
            page += 1
            session += 1
        # 1 debrief page
        s_start = (debrief - 1) * DEBRIEF_EVERY + 1
        s_end   = min(debrief * DEBRIEF_EVERY, TOTAL_SESSIONS)
        draw_debrief_page(c, debrief, s_start, s_end, page)
        c.showPage()
        page += 1
        debrief += 1

    # Conclusion (1 page)
    draw_conclusion_page(c, page)
    c.showPage()
    page += 1

    c.save()
    print(f"Generated : {filename}")
    print(f"Pages     : {page - 1}")


if __name__ == "__main__":
    generate()
