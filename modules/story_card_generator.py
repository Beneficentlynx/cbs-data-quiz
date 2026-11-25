"""
Generates an authentic, high-resolution Spotify-Wrapped style 9:16 mobile story card (1080x1920)
for Instagram Stories, WhatsApp Status, and social sharing.
"""

import io
from typing import Dict, Any
from PIL import Image, ImageDraw, ImageFont


def generate_spotify_wrapped_story_card(wrapped: Dict[str, Any]) -> bytes:
    """
    Renders a stunning 1080 x 1920 (9:16 vertical story) image inspired by Spotify Wrapped,
    infused with official CBS Design System colors (#271D6C Corporate Blue, #00A1CD Aqua Light,
    electric accents and high-contrast typography).
    """
    width = 1080
    height = 1920

    img = Image.new("RGB", (width, height), color=(20, 13, 50))
    draw = ImageDraw.Draw(img)

    # 1. Vibrant Spotify-Wrapped Gradient Background
    # Deep CBS Corporate Blue (#130B34) -> (#271D6C) -> (#0A3C6E)
    for y in range(height):
        ratio = y / height
        if ratio < 0.45:
            r = int(19 + (ratio / 0.45) * (39 - 19))
            g = int(11 + (ratio / 0.45) * (29 - 11))
            b = int(52 + (ratio / 0.45) * (108 - 52))
        else:
            sub = (ratio - 0.45) / 0.55
            r = int(39 - sub * (39 - 10))
            g = int(29 + sub * (60 - 29))
            b = int(108 + sub * (120 - 108))
        draw.line([(0, y), (width, y)], fill=(r, g, b))

    # Decorative geometric background curves (Spotify Wrapped graphic language)
    draw.arc([-200, -200, 600, 600], start=0, end=360, fill=(0, 161, 205), width=8)
    draw.arc([600, 1300, 1400, 2100], start=0, end=360, fill=(0, 212, 255), width=6)
    draw.arc([750, 200, 1250, 700], start=0, end=360, fill=(255, 255, 255), width=2)

    # 2. Font Loader Helper with robust fallbacks
    def get_font(size: int, bold: bool = False):
        font_names = [
            "arialbd.ttf" if bold else "arial.ttf",
            "segoeuib.ttf" if bold else "segoeui.ttf",
            "calibrib.ttf" if bold else "calibri.ttf",
        ]
        for name in font_names:
            try:
                return ImageFont.truetype(name, size)
            except Exception:
                continue
        return ImageFont.load_default()

    font_badge = get_font(30, bold=True)
    font_hero_title = get_font(60, bold=True)
    font_score_huge = get_font(130, bold=True)
    font_score_lbl = get_font(28, bold=True)
    font_archetype = get_font(46, bold=True)
    font_desc = get_font(30, bold=False)
    font_chip_title = get_font(30, bold=True)
    font_chip_val = get_font(46, bold=True)
    font_list_rank = get_font(36, bold=True)
    font_list_title = get_font(30, bold=True)
    font_list_meta = get_font(24, bold=False)
    font_footer = get_font(24, bold=False)

    # 3. Top Header: Spotify Wrapped style pill & title
    # Header Tag Pill
    draw.rounded_rectangle([340, 70, 740, 128], radius=28, fill=(0, 212, 255))
    draw.text((540, 99), "#CBSWRAPPED 2026", font=font_badge, fill=(20, 13, 50), anchor="mm")

    draw.text((540, 185), "STATISTISCHE FEITENCHECK", font=font_hero_title, fill=(255, 255, 255), anchor="mm")

    # 4. Hero Score Graphic: Radial glowing ring + Giant Score
    cx, cy, radius = 540, 390, 140
    # Outer neon ring
    draw.ellipse([cx - radius - 14, cy - radius - 14, cx + radius + 14, cy + radius + 14], fill=None, outline=(0, 212, 255), width=5)
    # Inner background circle
    draw.ellipse([cx - radius, cy - radius, cx + radius, cy + radius], fill=(39, 29, 108), outline=(255, 255, 255), width=4)

    score_val = f"{wrapped['total_score']:.0f}%"
    draw.text((cx, cy - 12), score_val, font=font_score_huge, fill=(255, 255, 255), anchor="mm")
    draw.text((cx, cy + 80), "NAUWKEURIGHEID", font=font_score_lbl, fill=(0, 212, 255), anchor="mm")

    # 5. Personality Archetype Card (Spotify "Your Audio Aura" style)
    draw.rounded_rectangle([80, 580, 1000, 770], radius=24, fill=(255, 255, 255, 25), outline=(0, 212, 255), width=3)
    draw.text((540, 630), wrapped["archetype"], font=font_archetype, fill=(0, 212, 255), anchor="mm")

    # Wrapped description text
    desc = wrapped["archetype_desc"]
    if len(desc) > 65:
        desc = desc[:62] + "..."
    draw.text((540, 685), desc, font=font_desc, fill=(230, 240, 255), anchor="mm")

    # Bias tag
    bias_tag = f"Neiging: {wrapped['bias_label']}"
    draw.rounded_rectangle([320, 715, 760, 755], radius=20, fill=(0, 161, 205))
    draw.text((540, 735), bias_tag, font=get_font(22, bold=True), fill=(20, 13, 50), anchor="mm")

    # 6. Spotify Wrapped Category Cards (Side by Side)
    best_cat = wrapped["best_category"]
    worst_cat = wrapped["worst_category"]

    # Best Category Card (Neon Mint Green)
    draw.rounded_rectangle([80, 810, 520, 1010], radius=20, fill=(255, 255, 255), outline=(16, 231, 157), width=4)
    draw.text((115, 845), "🌟 TOP THEMA", font=font_chip_title, fill=(16, 231, 157))
    draw.text((115, 895), f"{best_cat[1]:.0f}%", font=font_chip_val, fill=(39, 29, 108))
    b_name = best_cat[0][:18] + "..." if len(best_cat[0]) > 18 else best_cat[0]
    draw.text((115, 955), b_name, font=font_desc, fill=(70, 85, 105))

    # Worst Category Card (Neon Coral)
    draw.rounded_rectangle([560, 810, 1000, 1010], radius=20, fill=(255, 255, 255), outline=(255, 68, 102), width=4)
    draw.text((595, 845), "⚠️ BLINDE VLEK", font=font_chip_title, fill=(255, 68, 102))
    draw.text((595, 895), f"{worst_cat[1]:.0f}%", font=font_chip_val, fill=(39, 29, 108))
    w_name = worst_cat[0][:18] + "..." if len(worst_cat[0]) > 18 else worst_cat[0]
    draw.text((595, 955), w_name, font=font_desc, fill=(70, 85, 105))

    # 7. Spotify Top Tracks style: "JOUW TOP 3 BESTE SCHATTINGEN"
    draw.rounded_rectangle([80, 1045, 1000, 1750], radius=24, fill=(255, 255, 255), outline=(217, 226, 236), width=2)

    draw.text((120, 1090), "🏆 JOUW TOP SCHATTINGEN", font=get_font(34, bold=True), fill=(39, 29, 108))

    medals_colors = [(255, 184, 0), (148, 163, 184), (217, 119, 6)]
    y_entry = 1150
    for i, q in enumerate(wrapped["best_3_questions"][:3]):
        # Rank badge
        rank_bg = medals_colors[i] if i < len(medals_colors) else (0, 161, 205)
        draw.ellipse([120, y_entry, 175, y_entry + 55], fill=rank_bg)
        draw.text((147, y_entry + 27), str(i + 1), font=font_list_rank, fill=(255, 255, 255), anchor="mm")

        # Question title
        q_title = q["title"][:32] + "..." if len(q["title"]) > 32 else q["title"]
        draw.text((195, y_entry + 2), q_title, font=font_list_title, fill=(30, 41, 59))

        # Sub line
        draw.text(
            (195, y_entry + 36),
            f"Schatting: {q['guess_pct']:+.1f}% | Werkelijk: {q['actual_pct']:+.1f}%",
            font=font_list_meta,
            fill=(100, 116, 139),
        )
        # Score on right
        draw.text((960, y_entry + 15), f"{q['score']:.0f} pt", font=get_font(28, bold=True), fill=(0, 161, 205), anchor="ra")

        y_entry += 95

    # Divider line
    draw.line([(120, y_entry + 10), (960, y_entry + 10)], fill=(226, 232, 240), width=2)
    y_entry += 35

    # Biggest Surprise / Blind Spot
    draw.text((120, y_entry), "🔍 GROOTSTE MISVATTING", font=get_font(32, bold=True), fill=(225, 29, 72))
    y_entry += 50
    worst_q = wrapped["worst_3_questions"][0]
    draw.ellipse([120, y_entry, 175, y_entry + 55], fill=(225, 29, 72))
    draw.text((147, y_entry + 27), "!", font=font_list_rank, fill=(255, 255, 255), anchor="mm")

    w_title = worst_q["title"][:32] + "..." if len(worst_q["title"]) > 32 else worst_q["title"]
    draw.text((195, y_entry + 2), w_title, font=font_list_title, fill=(30, 41, 59))
    draw.text(
        (195, y_entry + 36),
        f"Schatting: {worst_q['guess_pct']:+.1f}% | Werkelijk: {worst_q['actual_pct']:+.1f}% (Afwijking: {worst_q['error']:.1f}% punt)",
        font=font_list_meta,
        fill=(225, 29, 72),
    )

    # 8. Spotify Wrapped Brand Footer
    draw.text(
        (540, 1810),
        "Centraal Bureau voor de Statistiek — Voor wat er feitelijk gebeurt",
        font=font_footer,
        fill=(0, 212, 255),
        anchor="mm",
    )
    draw.text((540, 1845), "Doe ook de test op cbs-quiz.nl", font=font_footer, fill=(200, 215, 240), anchor="mm")

    # Output as PNG bytes
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()
