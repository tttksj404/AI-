"""Render PDF pages to PNG for visual review."""
from pathlib import Path
import pypdfium2 as pdfium

ROOT = Path(r"C:\Users\SSAFY\Desktop\AI해커톤")
PDF = ROOT / "기획서_Sentinel30_v2_3.pdf"
OUT = ROOT / "_review"
OUT.mkdir(exist_ok=True)

doc = pdfium.PdfDocument(str(PDF))
print(f"pages: {len(doc)}")
for i, page in enumerate(doc):
    pil = page.render(scale=1.5).to_pil()
    p = OUT / f"page_{i+1:02d}.png"
    pil.save(p)
    print(f"[{i+1}] {pil.size} -> {p.name}")
