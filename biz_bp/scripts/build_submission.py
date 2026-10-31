# -*- coding: utf-8 -*-
"""Build CW1 submission artefacts (no external deps beyond openpyxl)."""
import json, os, zipfile, datetime
from pathlib import Path
import openpyxl
from openpyxl.styles import Font, Alignment, PatternFill

ROOT = Path(r"G:\FullStack")
BIZ = ROOT / "biz_bp"
OUT = ROOT / "需提交内容"
PDF_DIR = OUT / "4_PDFs"
PDF_DIR.mkdir(parents=True, exist_ok=True)

# ---------------------------------------------------------------- PDF writer
MAP = {"\u2014": "-", "\u2013": "-", "\u2018": "'", "\u2019": "'", "\u201c": '"',
       "\u201d": '"', "\u2022": "*", "\u2026": "...", "\u2192": "->", "\u2265": ">=",
       "\u2264": "<=", "\u00d7": "x", "\u00a0": " ", "\u200b": ""}

def ascii_text(s):
    for k, v in MAP.items():
        s = s.replace(k, v)
    return s.encode("ascii", "replace").decode("ascii")

def esc(s):
    return s.replace("\\", r"\\").replace("(", r"\(").replace(")", r"\)")

def wrap(line, width):
    if len(line) <= width:
        return [line]
    out = []
    while len(line) > width:
        cut = line.rfind(" ", 0, width + 1)
        if cut < width * 0.6:
            cut = width
        out.append(line[:cut])
        line = line[cut:].lstrip()
    out.append(line)
    return out

def make_pdf(pdf_path, title, pages):
    """pages: list of dict(font='F1'|'F2', size=int, leading=int, lines=[str])"""
    objs = []
    def add(data):
        objs.append(data)
        return len(objs)

    font1 = add(b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>")
    font2 = add(b"<< /Type /Font /Subtype /Type1 /BaseFont /Courier >>")
    pages_id = add(b"")  # placeholder
    kids = []
    for pg in pages:
        font = "F2" if pg["font"] == "F2" else "F1"
        size, lead = pg["size"], pg["leading"]
        body = ["BT", "/%s %d Tf" % (font, size), "%d TL" % lead, "50 805 Td"]
        for ln in pg["lines"]:
            body.append("(%s) Tj T*" % esc(ascii_text(ln)))
        body.append("ET")
        stream = "\n".join(body).encode("latin-1", "replace")
        cid = add(b"<< /Length %d >>\nstream\n" % len(stream) + stream + b"\nendstream")
        pid = add(("<< /Type /Page /Parent %d 0 R /MediaBox [0 0 595 842] "
                   "/Resources << /Font << /F1 %d 0 R /F2 %d 0 R >> >> /Contents %d 0 R >>"
                   % (pages_id, font1, font2, cid)).encode())
        kids.append(pid)

    objs[pages_id - 1] = ("<< /Type /Pages /Kids [%s] /Count %d >>"
                          % (" ".join("%d 0 R" % k for k in kids), len(kids))).encode()
    objs[0] = b"<< /Type /Catalog /Pages %d 0 R >>" % pages_id
    info = add(("<< /Title (%s) /Producer (LocalLens submission builder) /CreationDate (D:%s) >>"
                % (esc(ascii_text(title)), datetime.datetime.now().strftime("%Y%m%d%H%M%S"))).encode())

    buf = bytearray(b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n")
    offsets = [0]
    for i, data in enumerate(objs, 1):
        offsets.append(len(buf))
        buf += b"%d 0 obj\n" % i + data + b"\nendobj\n"
    xref = len(buf)
    buf += b"xref\n0 %d\n" % (len(objs) + 1)
    buf += b"0000000000 65535 f \n"
    for off in offsets[1:]:
        buf += b"%010d 00000 n \n" % off
    buf += (b"trailer\n<< /Size %d /Root 1 0 R /Info %d 0 R >>\nstartxref\n%d\n%%%%EOF\n"
            % (len(objs) + 1, info, xref))
    Path(pdf_path).write_bytes(bytes(buf))

def text_pages(text, font="F1", size=9, leading=12, width=None):
    width = width or (85 if font == "F1" else 105)
    lines = []
    for raw in ascii_text(text).splitlines():
        lines.extend(wrap(raw.rstrip(), width))
    per = int((805 - 50) / leading)
    return [{"font": font, "size": size, "leading": leading,
             "lines": lines[i:i + per]} for i in range(0, len(lines), per)] or \
           [{"font": font, "size": size, "leading": leading, "lines": [""]}]

def read(p):
    return Path(p).read_text(encoding="utf-8", errors="replace")

# --------------------------------------------------------------- 1. code zip
CODE_EXCLUDE_DIRS = {"venv", "__pycache__", ".git", "tmp", "node_modules", ".pytest_cache"}
CODE_EXCLUDE_FILES = {".env.local"}

def code_files():
    for dirpath, dirnames, filenames in os.walk(BIZ):
        dirnames[:] = [d for d in dirnames if d not in CODE_EXCLUDE_DIRS]
        for fn in filenames:
            if fn in CODE_EXCLUDE_FILES or fn.endswith(".pyc"):
                continue
            p = Path(dirpath) / fn
            yield p, p.relative_to(ROOT)

zip1 = OUT / "1_Backend_API_Code.zip"
if zip1.exists():
    zip1.unlink()
with zipfile.ZipFile(zip1, "w", zipfile.ZIP_DEFLATED) as z:
    for p, rel in code_files():
        z.write(p, Path("biz_bp") / p.relative_to(BIZ))

# --------------------------------------------------------------- 2. data zip
export_dir = BIZ / "data" / "export"
zip2 = OUT / "2_Database_Collections_JSON.zip"
if zip2.exists():
    zip2.unlink()
with zipfile.ZipFile(zip2, "w", zipfile.ZIP_DEFLATED) as z:
    for p in sorted(export_dir.glob("*.json")):
        z.write(p, p.name)

# --------------------------------------------------------------- 3. PDFs
code_order = ["app.py", "globals.py", "decorators.py", "utils.py",
              "blueprints/__init__.py", "blueprints/auth/auth.py",
              "blueprints/businesses/businesses.py", "blueprints/reviews/reviews.py",
              "create_users.py", "scripts/import_seed_data.py", "scripts/export_data.py",
              "scripts/make_seed_data.py", "requirements.txt", ".env.example"]
listing = []
for rel in code_order:
    p = BIZ / rel
    if not p.exists():
        continue
    listing.append("=" * 100)
    listing.append("FILE: biz_bp/%s" % rel.replace("\\", "/"))
    listing.append("=" * 100)
    for i, line in enumerate(read(p).splitlines(), 1):
        listing.append("%4d | %s" % (i, line))
    listing.append("")
make_pdf(PDF_DIR / "Backend_API_Code_Listing.pdf", "LocalLens Backend API Code Listing",
         text_pages("\n".join(listing), "F2", 7, 9, 112))

make_pdf(PDF_DIR / "API_Endpoints_Summary.pdf", "LocalLens API Endpoints Summary",
         text_pages(read(BIZ / "docs" / "API_ENDPOINTS.md")))

evidence = read(BIZ / "docs" / "TEST_EVIDENCE.md")
evidence += ("\n\nNote: this printout combines the automated Flask test run with the Postman\n"
             "collection status. A live Postman Desktop run must still be executed and\n"
             "its Collection Runner output/export attached as evidence.\n")
make_pdf(PDF_DIR / "Postman_Test_Results.pdf", "LocalLens Automated Test Results",
         text_pages(evidence, "F2", 8, 10, 100))

coll = json.loads(read(BIZ / "postman" / "LocalLens.postman_collection.json"))
doc = ["LocalLens API Documentation", "=" * 70,
       "Base URL: http://127.0.0.1:5000",
       "Auth: Authorization: Bearer <jwt> for protected routes", ""]

def walk(items, depth=0):
    for it in items:
        if "item" in it:
            doc.append("")
            doc.append("#" * min(depth + 2, 6) + " " + it.get("name", ""))
            walk(it["item"], depth + 1)
            continue
        req = it.get("request", {})
        method = req.get("method", "GET")
        url = req.get("url", {})
        raw = url.get("raw") if isinstance(url, dict) else str(url)
        doc.append("")
        doc.append("[%s] %s" % (method, raw))
        doc.append("Name: %s" % it.get("name", ""))
        desc = (req.get("description") or it.get("description") or "").strip()
        if desc:
            for line in desc.splitlines():
                doc.append("  " + line)
        if isinstance(url, dict) and url.get("query"):
            q = ", ".join("%s=%s" % (x.get("key"), x.get("value")) for x in url["query"] if not x.get("disabled"))
            if q:
                doc.append("  Query: " + q)
        for h in req.get("header", []) or []:
            if h.get("key") and h.get("key").lower() not in ("content-type",):
                doc.append("  Header: %s: %s" % (h["key"], h.get("value", "")))
        body = req.get("body", {})
        if body.get("raw"):
            doc.append("  Body: " + body["raw"].replace("\n", " ")[:300])
        for ex in it.get("response", []) or []:
            doc.append("  Example response: %s" % (ex.get("name") or ex.get("code")))

walk(coll.get("item", []))
doc.append("")
doc.append("Generated from postman/LocalLens.postman_collection.json.")
doc.append("Postman can also publish these docs directly (View in Postman -> Publish).")
make_pdf(PDF_DIR / "Postman_API_Documentation.pdf", "LocalLens API Documentation",
         text_pages("\n".join(doc)))

# ------------------------------------------------- 4. self-evaluation workbook
src = ROOT / "CW" / "CW1 Assessment Grid.xlsx"
wb = openpyxl.load_workbook(src)
ws = wb["Sheet1"]
ws["B2"] = "Name:   [Your Name]"
ws["D2"] = "Student ID:   [Your ID]"
try:
    ws["B15"] = "Self-score (indicative):"
    ws["C15"] = 72
    ws["D15"] = "70-79 band: strong implementation beyond the Biz Directory, with automation, aggregation and geospatial query."
except Exception:
    pass

if "Self-Evaluation" in wb.sheetnames:
    del wb["Self-Evaluation"]
se = wb.create_sheet("Self-Evaluation")
se["A1"] = "COM661 CW1 Self-Evaluation (LocalLens)"
se["A1"].font = Font(bold=True, size=14)
headers = ["Criterion", "Weight", "Self score / band", "Justification", "Evidence"]
for c, h in enumerate(headers, 1):
    cell = se.cell(row=3, column=c, value=h)
    cell.font = Font(bold=True, color="FFFFFF")
    cell.fill = PatternFill("solid", fgColor="305496")
    cell.alignment = Alignment(vertical="center", wrap_text=True)

rows = [
    ("Choice of Dataset", "15%", 70,
     "120 businesses and 600 reviews across 4 collections; GeoJSON location, dates, booleans, nested address/hours and derived rating fields. Synthetic but realistic and no Yelp data.",
     "docs/SCHEMA.md; data/export/*.json"),
    ("Database Functionality", "25%", 72,
     "Full CRUD for businesses and reviews, multi-value category filtering, seven-stage aggregation pipeline, $geoNear proximity query, rating recomputation and TTL-backed JWT blacklist.",
     "tests/test_api_smoke.py; docs/TEST_EVIDENCE.md"),
    ("API Structure / Design", "25%", 72,
     "Flask Blueprints per resource, RESTful paths and verbs, correct 200/201/204/400/401/403/404/409 codes, role and ownership decorators.",
     "app.py; blueprints/*; docs/API_ENDPOINTS.md"),
    ("Usability", "25%", 68,
     "Input validation, consistent JSON errors, pagination, sort controls, CORS for the Angular client, Postman collection. Live Postman run still to be captured.",
     "utils.py; docs/TEST_EVIDENCE.md; postman/"),
    ("Submission Package", "10%", 60,
     "Code zip, mongoexport JSON zip, code-listing PDF, endpoint summary PDF, test evidence PDF, API documentation PDF and this grid are assembled. Video and live Postman output remain human tasks.",
     "需提交内容/ folder"),
]
for r, row in enumerate(rows, 4):
    for c, val in enumerate(row, 1):
        cell = se.cell(row=r, column=c, value=val)
        cell.alignment = Alignment(vertical="top", wrap_text=True)
se["A10"] = "Weighted self-score"
se["A10"].font = Font(bold=True)
se["B10"] = 69.2
se["A11"] = ("Weights: 70*.15 + 72*.25 + 72*.25 + 68*.25 + 60*.10 = 69.2 (2:1 band). "
             "Self-assessment is indicative only and does not contribute marks.")
se["A11"].alignment = Alignment(wrap_text=True, vertical="top")
se.merge_cells("A11:E11")
se["A12"] = ("To finish: enter your name/student ID above, run the Postman collection with "
             "Collection Runner, export the run results, and record the <=5 minute narrated video.")
se["A12"].alignment = Alignment(wrap_text=True, vertical="top")
se.merge_cells("A12:E12")
widths = {"A": 28, "B": 10, "C": 18, "D": 70, "E": 46}
for k, v in widths.items():
    se.column_dimensions[k].width = v
for r in range(4, 9):
    se.row_dimensions[r].height = 62

xlsx_out = OUT / "5_Self_Evaluation_Sheet.xlsx"
wb.save(xlsx_out)

print("ZIP1", zip1.stat().st_size)
print("ZIP2", zip2.stat().st_size)
for p in sorted(PDF_DIR.glob("*.pdf")):
    print("PDF", p.name, p.stat().st_size)
print("XLSX", xlsx_out.stat().st_size)
