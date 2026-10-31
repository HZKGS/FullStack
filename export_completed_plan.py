from pathlib import Path
from xml.sax.saxutils import escape
import re

from docx import Document
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import Paragraph, SimpleDocTemplate
from pypdf import PdfReader


root = Path(__file__).parent
source = Document(root / "CW1_Plan_Submission.docx")
pdf_path = root / "CW1_Plan_Submission_Completed.pdf"
styles = getSampleStyleSheet()
styles.add(ParagraphStyle(name="MainTitle", parent=styles["Title"], fontName="Helvetica-Bold", fontSize=13.2, leading=15, alignment=TA_CENTER, textColor=colors.HexColor("#2c5591"), spaceAfter=2))
styles.add(ParagraphStyle(name="SubTitle", parent=styles["Heading2"], fontName="Helvetica-Bold", fontSize=10.8, leading=12, alignment=TA_CENTER, textColor=colors.HexColor("#2c5591"), spaceAfter=3))
styles.add(ParagraphStyle(name="Section", parent=styles["Heading2"], fontName="Helvetica-Bold", fontSize=9.5, leading=10.5, textColor=colors.HexColor("#2c5591"), spaceBefore=3, spaceAfter=1))
styles.add(ParagraphStyle(name="BodyTight", parent=styles["BodyText"], fontName="Helvetica", fontSize=7.1, leading=8.0, spaceAfter=1))
styles.add(ParagraphStyle(name="BulletTight", parent=styles["BodyText"], fontName="Helvetica", fontSize=6.9, leading=7.7, leftIndent=8, firstLineIndent=-6, spaceAfter=0.5))


def convert(text):
    text = escape(text)
    text = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", text)
    text = re.sub(r"\*(.+?)\*", r"<i>\1</i>", text)
    text = re.sub(r"(https?://[^\s)]+)", r'<link href="\1" color="#0563c1">\1</link>', text)
    return text


story = []
for i, paragraph in enumerate(source.paragraphs):
    text = paragraph.text.strip()
    if not text:
        continue
    if i == 0:
        style = styles["MainTitle"]
    elif i == 1:
        style = styles["SubTitle"]
    elif text in {"Application", "Dataset", "Functionality", "Initial implementation sequence"}:
        style = styles["Section"]
    elif text.startswith("• ") or text.startswith("- "):
        style = styles["BulletTight"]
        text = "•  " + text[2:]
    else:
        style = styles["BodyTight"]
    story.append(Paragraph(convert(text), style))

doc = SimpleDocTemplate(
    str(pdf_path), pagesize=A4, rightMargin=15*mm, leftMargin=15*mm,
    topMargin=8*mm, bottomMargin=8*mm,
    title="COM661 CW1 Application Plan", author="YuTong Li",
)
doc.build(story)
print(f"PDF: {pdf_path}; pages: {len(PdfReader(str(pdf_path)).pages)}")
