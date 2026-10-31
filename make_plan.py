from pathlib import Path

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Inches, Pt, RGBColor


ROOT = Path(__file__).parent
SOURCE = ROOT / "CW1_Plan_Submission.md"
OUTPUT = ROOT / "CW1_Plan_Submission.docx"


def add_rich_text(paragraph, text):
    """Render the small Markdown subset used in this plan."""
    import re

    parts = re.split(r"(\*\*.*?\*\*|\*.*?\*|\[[^\]]+\]\([^)]+\))", text)
    for part in parts:
        if not part:
            continue
        if part.startswith("**") and part.endswith("**"):
            run = paragraph.add_run(part[2:-2])
            run.bold = True
        elif part.startswith("*") and part.endswith("*"):
            run = paragraph.add_run(part[1:-1])
            run.italic = True
        elif part.startswith("["):
            label, url = part[1:].split("](", 1)
            url = url[:-1]
            run = paragraph.add_run(f"{label} ({url})")
            run.font.color.rgb = RGBColor(5, 99, 193)
        else:
            paragraph.add_run(part)


def main():
    doc = Document()
    section = doc.sections[0]
    section.top_margin = Inches(0.55)
    section.bottom_margin = Inches(0.55)
    section.left_margin = Inches(0.72)
    section.right_margin = Inches(0.72)
    normal = doc.styles["Normal"]
    normal.font.name = "Arial"
    normal.font.size = Pt(9)
    normal.paragraph_format.space_after = Pt(4)
    normal.paragraph_format.line_spacing = 1.02
    for style_name, size in (("Title", 15), ("Heading 1", 12), ("Heading 2", 10)):
        style = doc.styles[style_name]
        style.font.name = "Arial"
        style.font.size = Pt(size)
        style.font.color.rgb = RGBColor(44, 85, 145)
        style.font.bold = True
        style.paragraph_format.space_before = Pt(5)
        style.paragraph_format.space_after = Pt(3)

    for raw in SOURCE.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line:
            continue
        if line.startswith("# "):
            p = doc.add_paragraph(style="Title")
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            add_rich_text(p, line[2:])
        elif line.startswith("## "):
            p = doc.add_paragraph(style="Heading 1")
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            add_rich_text(p, line[3:])
        elif line.startswith("### "):
            p = doc.add_paragraph(style="Heading 2")
            add_rich_text(p, line[4:])
        elif line.startswith("- "):
            p = doc.add_paragraph(style="List Bullet")
            p.paragraph_format.left_indent = Inches(0.2)
            p.paragraph_format.first_line_indent = Inches(-0.12)
            p.paragraph_format.space_after = Pt(2)
            add_rich_text(p, line[2:])
        else:
            p = doc.add_paragraph()
            add_rich_text(p, line)

    doc.core_properties.title = "COM661 CW1 Application Plan"
    doc.core_properties.subject = "LocalLens Flask and MongoDB API plan"
    doc.save(OUTPUT)
    print(OUTPUT)


if __name__ == "__main__":
    main()
