import os
from django.conf import settings
from django.template.loader import render_to_string
from weasyprint import HTML
from django.http import HttpResponse
from django.shortcuts import render
from .models import FormacionDocente, Entidad

from reportlab.platypus import Paragraph, Frame, PageTemplate, BaseDocTemplate
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import letter


# ✅ Clase personalizada para PDF con fondo usando ReportLab
class PDFCertificado(BaseDocTemplate):
    def __init__(self, filename, fondo_path=None, **kwargs):
        super().__init__(filename, pagesize=letter, **kwargs)
        self.fondo_path = fondo_path

        frame = Frame(50, 50, self.pagesize[0]-100, self.pagesize[1]-100, id='normal')
        template = PageTemplate(id='Certificado', frames=[frame], onPage=self._draw_fondo)
        self.addPageTemplates([template])

    def _draw_fondo(self, canvas, doc):
        if self.fondo_path and os.path.exists(self.fondo_path):
            canvas.drawImage(self.fondo_path, 0, 0, width=self.pagesize[0], height=self.pagesize[1])

# ✅ Vista que genera el certificado PDF con ReportLab
def generar_certificado(request, id_entidad):
    entidad = Entidad.objects.get(pk=id_entidad)

    certificados_dir = os.path.join(settings.MEDIA_ROOT, 'certificados')
    os.makedirs(certificados_dir, exist_ok=True)

    fondo_path = os.path.join(settings.MEDIA_ROOT, 'fondo_certificado.jpg')
    file_path = os.path.join(certificados_dir, f'certificado_{entidad.nombre}.pdf')

    doc = PDFCertificado(file_path, fondo_path=fondo_path)
    styles = getSampleStyleSheet()

    elementos = []
    texto = f"Certificamos que la entidad {entidad.nombre} ubicada en {entidad.ciudad}, {entidad.pais} ha sido registrada correctamente."
    elementos.append(Paragraph(texto, styles['Title']))

    doc.build(elementos)

    with open(file_path, 'rb') as f:
        response = HttpResponse(f.read(), content_type='application/pdf')
        response['Content-Disposition'] = f'inline; filename=certificado_{entidad.nombre}.pdf'
        return response

# ✅ Vista que genera el certificado PDF con WeasyPrint
def generar_certificado_pdf(request, id_formacion_docente):
    formacion_docente = FormacionDocente.objects.get(id=id_formacion_docente)

    fondo_path = 'file:///' + os.path.join(settings.MEDIA_ROOT, 'fondo_certificado.jpg').replace('\\', '/')
    firma_path = 'file:///' + os.path.join(settings.MEDIA_ROOT, 'firma_director.png').replace('\\', '/')

    fondo_absoluto = fondo_path[7:]
    firma_absoluto = firma_path[7:]

    print("➡️ Ruta fondo:", fondo_absoluto)
    print("✅ ¿Existe fondo?", os.path.exists(fondo_absoluto))
    print("➡️ Ruta firma:", firma_absoluto)
    print("✅ ¿Existe firma?", os.path.exists(firma_absoluto))

    html_string = render_to_string('certificados/plantilla_certificado.html', {
        'formacion_docente': formacion_docente,
        'fondo_path': fondo_path,
        'firma_path': firma_path,
    })

    pdf_file = HTML(string=html_string).write_pdf()

    response = HttpResponse(pdf_file, content_type='application/pdf')
    response['Content-Disposition'] = f'filename="certificado_{formacion_docente.id_usuario.nombre}.pdf"'
    return response
