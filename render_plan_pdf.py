from pathlib import Path
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import ListFlowable, ListItem, PageBreak, Paragraph, SimpleDocTemplate, Spacer
from pypdf import PdfReader

ROOT = Path(__file__).parent
source = (ROOT / "CW1_Plan_Submission.md").read_text(encoding="utf-8")
out = ROOT / "CW1_Plan_Submission.pdf"

styles = getSampleStyleSheet()
styles.add(ParagraphStyle(name="PlanTitle", parent=styles["Title"], fontName="Helvetica-Bold", fontSize=14, leading=17, alignment=TA_CENTER, textColor=colors.HexColor("#2c5591"), spaceAfter=3))
styles.add(ParagraphStyle(name="PlanSub", parent=styles["Heading2"], fontName="Helvetica-Bold", fontSize=11, leading=13, alignment=TA_CENTER, textColor=colors.HexColor("#2c5591"), spaceAfter=6))
styles.add(ParagraphStyle(name="PlanH", parent=styles["Heading2"], fontName="Helvetica-Bold", fontSize=10.2, leading=12, textColor=colors.HexColor("#2c5591"), spaceBefore=5, spaceAfter=2))
styles.add(ParagraphStyle(name="PlanBody", parent=styles["BodyText"], fontName="Helvetica", fontSize=7.8, leading=9.1, spaceAfter=2))
styles.add(ParagraphStyle(name="PlanBullet", parent=styles["BodyText"], fontName="Helvetica", fontSize=7.4, leading=8.4, spaceAfter=0.5))


def rich(text):
    text = escape(text)
    import re
    text = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", text)
    text = re.sub(r"\*(.+?)\*", r"<i>\1</i>", text)
    text = re.sub(r"\[([^]]+)\]\(([^)]+)\)", r'<link href="\2" color="#0563c1">\1</link>', text)
    return text


story = []
for line in source.splitlines():
    line = line.strip()
    if not line:
        continue
    if line.startswith("# "):
        story.append(Paragraph(rich(line[2:]), styles["PlanTitle"]))
    elif line.startswith("## "):
        story.append(Paragraph(rich(line[3:]), styles["PlanSub"]))
    elif line.startswith("### "):
        story.append(Paragraph(rich(line[4:]), styles["PlanH"]))
    elif line.startswith("- "):
        story.append(Paragraph("&#8226;&nbsp;&nbsp;" + rich(line[2:]), styles["PlanBullet"]))
    else:
        story.append(Paragraph(rich(line), styles["PlanBody"]))

doc = SimpleDocTemplate(str(out), pagesize=A4, rightMargin=19*mm, leftMargin=19*mm, topMargin=11*mm, bottomMargin=11*mm, title="COM661 CW1 Application Plan", author="[Your name]")
doc.build(story)
print(f"Created {out}; pages={len(PdfReader(str(out)).pages)}")
