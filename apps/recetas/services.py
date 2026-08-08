from io import BytesIO
from html import escape

import qrcode
from django.core.files.base import ContentFile
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import Image, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle


def generar_pdf_receta(receta, verification_url):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=18 * mm, leftMargin=18 * mm, topMargin=16 * mm, bottomMargin=16 * mm)
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name="ClinicTitle", parent=styles["Title"], textColor=colors.HexColor("#075a98"), fontSize=19, leading=23, alignment=TA_CENTER))
    styles.add(ParagraphStyle(name="Section", parent=styles["Heading2"], textColor=colors.HexColor("#075a98"), fontSize=11, leading=14, spaceBefore=10, spaceAfter=6))
    styles.add(ParagraphStyle(name="SmallClinic", parent=styles["BodyText"], textColor=colors.HexColor("#627d98"), fontSize=8, leading=11, alignment=TA_CENTER))
    story = [Paragraph("CLÍNICA REINA", styles["ClinicTitle"]), Paragraph("Atención médica profesional y humana<br/>Loja, Ecuador | contacto@clinicareina.com", styles["SmallClinic"]), Spacer(1, 8 * mm)]
    paciente = receta.paciente.get_full_name() or receta.paciente.username
    datos = [["Paciente", paciente], ["Médico", str(receta.medico)], ["Especialidad", receta.medico.especialidad.nombre], ["Registro profesional", receta.medico.registro_profesional], ["Fecha de emisión", receta.emitida_en.strftime("%d/%m/%Y %H:%M")], ["Código", str(receta.codigo_verificacion)]]
    tabla = Table(datos, colWidths=[42 * mm, 120 * mm])
    tabla.setStyle(TableStyle([("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#e9f5fd")), ("TEXTCOLOR", (0, 0), (0, -1), colors.HexColor("#075a98")), ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"), ("FONTNAME", (1, 0), (1, -1), "Helvetica"), ("FONTSIZE", (0, 0), (-1, -1), 9), ("GRID", (0, 0), (-1, -1), .35, colors.HexColor("#d9e2ec")), ("VALIGN", (0, 0), (-1, -1), "TOP"), ("TOPPADDING", (0, 0), (-1, -1), 6), ("BOTTOMPADDING", (0, 0), (-1, -1), 6)]))
    story.extend([tabla, Paragraph("Diagnóstico", styles["Section"]), Paragraph(escape(receta.diagnostico).replace("\n", "<br/>"), styles["BodyText"]), Paragraph("Medicamentos prescritos", styles["Section"])])
    prescripcion = [["Medicamentos", receta.medicamentos], ["Dosis", receta.dosis], ["Frecuencia", receta.frecuencia], ["Duración", receta.duracion], ["Indicaciones", receta.indicaciones]]
    if receta.observaciones:
        prescripcion.append(["Observaciones", receta.observaciones])
    tabla_rx = Table([[Paragraph(escape(str(a)), styles["BodyText"]), Paragraph(escape(str(b)).replace("\n", "<br/>"), styles["BodyText"])] for a, b in prescripcion], colWidths=[38 * mm, 124 * mm])
    tabla_rx.setStyle(TableStyle([("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#f6f9fc")), ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"), ("GRID", (0, 0), (-1, -1), .35, colors.HexColor("#d9e2ec")), ("VALIGN", (0, 0), (-1, -1), "TOP"), ("TOPPADDING", (0, 0), (-1, -1), 7), ("BOTTOMPADDING", (0, 0), (-1, -1), 7)]))
    qr_buffer = BytesIO(); qrcode.make(verification_url).save(qr_buffer, format="PNG"); qr_buffer.seek(0)
    firma = Paragraph(f"<b>Firma digital</b><br/>{receta.firma_digital}<br/><font size='7'>Documento verificable electrónicamente</font>", styles["BodyText"])
    verificacion = Table([[firma, Image(qr_buffer, width=28 * mm, height=28 * mm)]], colWidths=[130 * mm, 32 * mm])
    verificacion.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "MIDDLE"), ("LINEABOVE", (0, 0), (-1, 0), .7, colors.HexColor("#0877c9")), ("TOPPADDING", (0, 0), (-1, -1), 10)]))
    story.extend([tabla_rx, Spacer(1, 10 * mm), verificacion, Spacer(1, 4 * mm), Paragraph(f"Verificación: {verification_url}", styles["SmallClinic"])])
    doc.build(story)
    receta.pdf.save(f"receta-{receta.pk}.pdf", ContentFile(buffer.getvalue()), save=True)
    return receta.pdf
