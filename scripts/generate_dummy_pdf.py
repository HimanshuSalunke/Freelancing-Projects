"""Generate a dummy 50-page PDF for testing summarization.
Usage:
  python scripts/generate_dummy_pdf.py output.pdf
"""
import sys
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4


def main(path: str) -> None:
    c = canvas.Canvas(path, pagesize=A4)
    width, height = A4
    for i in range(1, 51):
        c.setFont("Helvetica-Bold", 14)
        c.drawString(72, height - 72, f"Dummy Document - Page {i}")
        c.setFont("Helvetica", 11)
        text = (
            "This is a placeholder paragraph describing organizational policies and procedures. "
            "Employees must follow the IT security policies including strong password use, device "
            "encryption, and phishing awareness. HR processes include leave applications, appraisals, "
            "and onboarding rules. This page is repeated to make a long document for testing. "
        )
        y = height - 120
        for _ in range(40):
            c.drawString(72, y, text)
            y -= 14
        c.showPage()
    c.save()


if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else "dummy_50_pages.pdf"
    main(out)


