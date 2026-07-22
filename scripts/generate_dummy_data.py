#!/usr/bin/env python3
"""Generate dummy PDFs and images for testing the full pipeline.

Usage:
    python scripts/generate_dummy_data.py
"""

import os
from pathlib import Path

from fpdf import FPDF
from PIL import Image, ImageDraw, ImageFont

BASE = Path("data")
PDFS = BASE / "pdfs"
IMAGES = BASE / "images"


def _soap_image(path: Path, label: str, color: tuple[int, int, int]) -> None:
    img = Image.new("RGB", (200, 200), color)
    draw = ImageDraw.Draw(img)
    draw.ellipse([20, 40, 180, 180], fill=(255, 255, 220), outline=(180, 140, 80))
    draw.text((60, 90), label, fill=(60, 40, 20))
    img.save(path)


def main() -> None:
    PDFS.mkdir(parents=True, exist_ok=True)
    IMAGES.mkdir(parents=True, exist_ok=True)

    # ── PDF 1: Product Catalog ──────────────────────────────────
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 16)
    pdf.cell(0, 10, "Artisan Soap Co. - Product Catalog", new_x="LMARGIN", new_y="NEXT", align="C")
    pdf.ln(5)
    pdf.set_font("Helvetica", "", 12)
    catalog_text = (
        "Welcome to Artisan Soap Co.! We make small-batch, handcrafted "
        "oatmeal soaps using natural ingredients.\n\n"
        "Our product line:\n"
        "- Classic Oatmeal: R$ 19,90 - gentle exfoliation, unscented\n"
        "- Lavender Oatmeal: R$ 24,90 - calming lavender essential oil\n"
        "- Honey & Oatmeal: R$ 24,90 - moisturising honey blend\n"
        "- Citrus Burst: R$ 22,90 - orange & lemon essential oils\n"
        "- Tea Tree & Oatmeal: R$ 26,90 - antibacterial tea tree oil\n\n"
        "All soaps weigh approx. 100 g and are cured for 4 weeks.\n"
        "Free shipping on orders over R$ 100,00."
    )
    pdf.multi_cell(0, 8, catalog_text)
    pdf.output(str(PDFS / "catalogo.pdf"))
    print(f"Created {PDFS / 'catalogo.pdf'}")

    # ── PDF 2: Oatmeal soap details ─────────────────────────────
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 16)
    pdf.cell(0, 10, "Classic Oatmeal Soap - Detail", new_x="LMARGIN", new_y="NEXT", align="C")
    pdf.ln(5)
    pdf.set_font("Helvetica", "", 12)
    detail_text = (
        "Our flagship product.\n\n"
        "Ingredients: olive oil, coconut oil, distilled water, sodium hydroxide, "
        "finely ground oatmeal, shea butter.\n\n"
        "Benefits:\n"
        "- Gently exfoliates dead skin cells\n"
        "- Soothes dry and sensitive skin\n"
        "- Lathers richly without stripping natural oils\n\n"
        "Price: R$ 19,90 (100 g bar)\n"
        "Available in single bars or gift packs of 3 (R$ 49,90)."
    )
    pdf.multi_cell(0, 8, detail_text)
    pdf.output(str(PDFS / "aveia_classico.pdf"))
    print(f"Created {PDFS / 'aveia_classico.pdf'}")

    # ── PDF 3: Fragrance Collection ─────────────────────────────
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 16)
    pdf.cell(0, 10, "Fragrance Collection", new_x="LMARGIN", new_y="NEXT", align="C")
    pdf.ln(5)
    pdf.set_font("Helvetica", "", 12)
    fragrance_text = (
        "Choose your scent:\n\n"
        "1. Lavender - Relaxing floral with hints of herbaceous sweetness.\n"
        "   Price: R$ 24,90\n\n"
        "2. Honey & Oatmeal - Warm, comforting, lightly sweet.\n"
        "   Price: R$ 24,90\n\n"
        "3. Citrus Burst - Bright orange and lemon, energising.\n"
        "   Price: R$ 22,90\n\n"
        "4. Tea Tree & Oatmeal - Fresh, medicinal, purifying.\n"
        "   Price: R$ 26,90\n\n"
        "5. Unscented (Classic) - Pure oatmeal, no added fragrance.\n"
        "   Price: R$ 19,90\n\n"
        "All scents use natural essential oils. No synthetic fragrances."
    )
    pdf.multi_cell(0, 8, fragrance_text)
    pdf.output(str(PDFS / "fragrancias.pdf"))
    print(f"Created {PDFS / 'fragrancias.pdf'}")

    # ── Dummy product images ────────────────────────────────────
    soaps = [
        ("classic.png", "Classic", (210, 180, 140)),
        ("lavender.png", "Lavender", (200, 180, 220)),
        ("honey.png", "Honey", (220, 200, 150)),
        ("citrus.png", "Citrus", (230, 200, 100)),
        ("tea_tree.png", "Tea Tree", (180, 210, 170)),
    ]
    for fname, label, color in soaps:
        path = IMAGES / fname
        _soap_image(path, label, color)
        print(f"Created {path}")


if __name__ == "__main__":
    main()
