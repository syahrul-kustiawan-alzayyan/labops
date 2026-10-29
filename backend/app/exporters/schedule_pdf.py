"""Generate A4 landscape PDF jadwal lab (siap tanda tangan)."""
from io import BytesIO
from reportlab.lib.pagesizes import landscape, A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.units import cm

DAY_NAMES = ["Senin", "Selasa", "Rabu", "Kamis", "Jumat", "Sabtu"]

def generate_schedule_pdf(sessions, labs, courses, classes, title="Jadwal Penggunaan Laboratorium", subtitle=""):
    buf = BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=landscape(A4), leftMargin=1*cm, rightMargin=1*cm,
                            topMargin=1.5*cm, bottomMargin=1.5*cm)
    styles = getSampleStyleSheet()
    h1 = ParagraphStyle("h1", parent=styles["Heading1"], fontSize=14, alignment=1, spaceAfter=4)
    sub = ParagraphStyle("sub", parent=styles["Normal"], fontSize=9, alignment=1, spaceAfter=12)
    story = []
    story.append(Paragraph(title, h1))
    if subtitle:
        story.append(Paragraph(subtitle, sub))
    story.append(Spacer(1, 6))

    # map
    lab_map = {str(l.id): l.canonical_name for l in labs}
    course_map = {str(c.id): c.code for c in courses}
    class_map = {str(c.id): c.code for c in classes}

    # header
    data = [["Hari", "Jam", "Ruang", "Mata Kuliah", "Kelas", "Mahasiswa", "Status"]]
    for s in sorted(sessions, key=lambda x: (x.day_of_week, str(x.start_time))):
        data.append([
            DAY_NAMES[s.day_of_week],
            f"{str(s.start_time)[:5]}-{str(s.end_time)[:5]}",
            lab_map.get(str(s.lab_id), str(s.lab_id)[:8]),
            course_map.get(str(s.course_id), "-") if s.course_id else "-",
            class_map.get(str(s.class_id), "-") if s.class_id else "-",
            str(s.student_count),
            s.status,
        ])

    t = Table(data, colWidths=[2.2*cm, 2.6*cm, 3*cm, 4*cm, 3*cm, 2*cm, 2.2*cm], repeatRows=1)
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1d4ed8")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 8),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f1f5f9")]),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
    ]))
    story.append(t)
    story.append(Spacer(1, 16))

    # signature block
    sig = Table([
        ["Mengetahui,", "", "Dibuat oleh,"],
        ["", "", ""],
        ["", "", ""],
        ["(____________________)", "", "(____________________)"],
        ["Ketua Jurusan", "", "Koordinator Laboratorium"],
    ], colWidths=[6*cm, 6*cm, 6*cm])
    sig.setStyle(TableStyle([
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("TOPPADDING", (0, 0), (-1, -1), 2),
    ]))
    story.append(sig)

    doc.build(story)
    buf.seek(0)
    return buf.getvalue()