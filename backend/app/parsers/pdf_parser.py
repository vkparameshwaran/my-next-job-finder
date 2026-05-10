from __future__ import annotations

from io import BytesIO

import pdfplumber


def extract_text_from_pdf(data: bytes) -> str:
    pages: list[str] = []
    with pdfplumber.open(BytesIO(data)) as pdf:
        for page in pdf.pages:
            text = page.extract_text(x_tolerance=2, y_tolerance=2) or ""
            pages.append(text)
    return "\n\n".join(p.strip() for p in pages if p.strip())
