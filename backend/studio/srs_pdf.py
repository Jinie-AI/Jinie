"""Paginated SRS export using the same content as the website."""
import io
from xml.sax.saxutils import escape
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from .srs_document import build_srs

def generate_srs_pdf(project):
    data = build_srs(project)
    buffer = io.BytesIO()
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name="Entry", fontName="Helvetica", fontSize=10,
                              leading=15, spaceAfter=10, splitLongWords=True))
    styles["Heading2"].textColor = colors.HexColor("#65449b")
    styles["Heading2"].spaceBefore = 18
    styles["Heading2"].keepWithNext = True
    def para(text, style):
        return Paragraph(escape(str(text)).replace("\n", "<br/>"), style)
    story = [para(data["name"], styles["Title"]),
             para("Software Requirements Specification", styles["Heading1"]),
             para(f"Jinie | Saved revision {data['revision']}", styles["Normal"]),
             Spacer(1, 16)]
    for section in data["sections"]:
        story.append(para(section["title"], styles["Heading2"]))
        story.append(para(section["note"], styles["Entry"]))
        for entry in section["entries"]:
            story.append(para(entry, styles["Entry"]))
    def footer(canvas, doc):
        canvas.saveState()
        canvas.setFont("Helvetica", 8)
        canvas.setFillColor(colors.HexColor("#6e667d"))
        canvas.drawString(48, 28, "Jinie | Software Requirements Specification")
        canvas.drawRightString(564, 28, f"Page {doc.page}")
        canvas.restoreState()
    SimpleDocTemplate(buffer, leftMargin=48, rightMargin=48, topMargin=42,
                      bottomMargin=48, title=data["name"] + " - SRS",
                      author="Jinie").build(story, onFirstPage=footer, onLaterPages=footer)
    return buffer.getvalue()
