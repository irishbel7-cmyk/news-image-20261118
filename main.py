#!/usr/bin/env python3
"""news-image-20261118 entry: writes a deterministic PNG summing up 18 Nov 2026 world news.

The simplest valid make.fun news-image program copies a held image to /output/entry.png.
This variant regenerates the image from fixed layout constants so it is fully deterministic
(two runs write byte-identical PNGs) and self-contained in the repository.
Requirements: whole PNG, <= 1 MiB, <= 1024x1024 px, no network, deterministic.
"""
import os
import hashlib
import datetime

from PIL import Image, ImageDraw, ImageFont

WIDTH, HEIGHT = 1024, 1024
DAY = "2026-11-18"


def _font(size, bold=False):
    candidates = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold
        else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ]
    for path in candidates:
        if os.path.exists(path):
            try:
                return ImageFont.truetype(path, size)
            except OSError:
                pass
    return ImageFont.load_default()


def build_image() -> Image.Image:
    # Fixed seed derived from the day string (deterministic across runs/machines).
    seed = hashlib.sha256(f"news-image-{DAY}".encode()).digest()

    def tint(idx, base):
        return (
            max(0, min(255, base[0] + (seed[idx] % 40) - 20)),
            max(0, min(255, base[1] + (seed[idx + 1] % 40) - 20)),
            max(0, min(255, base[2] + (seed[idx + 2] % 40) - 20)),
        )

    img = Image.new("RGB", (WIDTH, HEIGHT), color=(18, 20, 28))
    draw = ImageDraw.Draw(img)

    title_font = _font(46, bold=True)
    head_font = _font(27, bold=True)
    body_font = _font(19)

    # Masthead
    draw.rectangle((0, 0, WIDTH, 96), fill=(30, 34, 48))
    draw.text((32, 26), "WORLD NEWS  -  18 NOVEMBER 2026", fill=(245, 245, 250), font=title_font)

    stories = [
        ("XI & PUTIN MEET IN SHENZHEN", "Xi & Putin huddle in Shenzhen on eve of APEC; historic three-way summit set for Thursday; trade, Iran war, Ukraine, nuclear on agenda", tint(0, (70, 90, 130))),
        ("KERCH BRIDGE CRIPPLED", "Crimea link road arch downed days before Shenzhen summit; US warns deep strikes counterproductive; Europe balks at Washington's line", tint(4, (120, 80, 120))),
        ("US-IRAN WAR ESCALATES", "US strikes IRGC site on Qeshm Island; Iran eyes Hormuz fees after midterm defeat; dirty-bomb report denied, Rubio: no imminent threat; Brent ~$93", tint(12, (130, 70, 60))),
        ("QUAD MEETS IN MANILA", "Trump, Modi, Takaichi, Albanese: first Quad since Jan 2025; AI accelerator, rare-earths pact; 2,000 protesters on the streets", tint(16, (60, 110, 90))),
        ("OPTIMIZELY HACK: 178 SITES", "BBC, IKEA, Zoom, HSBC UAE, Air France-KLM, CNN: card skimmer + crypto clipper; Apple-device exploits; contained Nov 16-17", tint(20, (120, 60, 60))),
        ("US LOSES MEASLES STATUS", "PAHO: 26-year elimination over; 5,400+ cases, 10 deaths in 2026; Canada, Spain, UK, Mexico, Bolivia also lost it", tint(24, (60, 70, 110))),
    ]

    cols, gap = 2, 24
    card_w = (WIDTH - 3 * gap) // cols
    y = 136
    for i, (head, body, color) in enumerate(stories):
        col = i % cols
        row = i // cols
        x = gap + col * (card_w + gap)
        cy = y + row * 258
        draw.rounded_rectangle((x, cy, x + card_w, cy + 238), radius=14, fill=color)
        # wrap headline to at most 2 lines
        hwords = head.split()
        hline, hlines = "", []
        for w in hwords:
            test = (hline + " " + w).strip()
            if draw.textlength(test, font=head_font) > card_w - 36:
                hlines.append(hline)
                hline = w
            else:
                hline = test
        if hline:
            hlines.append(hline)
        ty = cy + 16
        for hl in hlines[:2]:
            draw.text((x + 18, ty), hl, fill=(250, 250, 250), font=head_font)
            ty += 30
        ty += 6
        body_top = ty
        # wrap body text
        words = body.split()
        line, lines = "", []
        for w in words:
            test = (line + " " + w).strip()
            if draw.textlength(test, font=body_font) > card_w - 36:
                lines.append(line)
                line = w
            else:
                line = test
        if line:
            lines.append(line)
        ty = body_top + 4
        for ln in lines[:4]:
            draw.text((x + 18, ty), ln, fill=(225, 225, 235), font=body_font)
            ty += 24

    # Footer
    draw.text((32, HEIGHT - 44), "AS REPORTED 18 NOVEMBER 2026 - REUTERS / AP / AFP / NYT / GUARDIAN", fill=(150, 155, 175), font=body_font)
    return img


def main():
    out_dir = "/output"
    try:
        os.makedirs(out_dir, exist_ok=True)
    except (PermissionError, OSError):
        out_dir = os.environ.get("OUTPUT_DIR", ".")
    os.makedirs(out_dir, exist_ok=True)
    img = build_image()
    # optimize + no timestamp args => deterministic bytes
    img.save(os.path.join(out_dir, "entry.png"), format="PNG", optimize=True)


if __name__ == "__main__":
    main()
