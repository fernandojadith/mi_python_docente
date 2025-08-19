from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from .models import FormacionDocente
from reportlab.lib.pagesizes import landscape, portrait, letter, A4
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
import os
import qrcode
from io import BytesIO


@receiver(post_save, sender=FormacionDocente)
def generar_certificado_pdf(sender, instance, created, **kwargs):
    if instance.aprobado and not instance.pdf_certificado and instance.id_usuario and instance.id_formacion:
        usuario = instance.id_usuario
        formacion = instance.id_formacion
        tipo_formacion = formacion.id_tipo_formacion.formaciones.lower() if formacion.id_tipo_formacion else "generico"

        # Construir nombre del archivo
        nombre_archivo = f"certificado_{usuario.nombre.replace(' ', '_')}_{instance.id_formaciondocente}.pdf"
        ruta_carpeta = os.path.join(settings.MEDIA_ROOT, 'certificados')
        os.makedirs(ruta_carpeta, exist_ok=True)
        ruta_pdf = os.path.join(ruta_carpeta, nombre_archivo)

        # =======================
        # PLANTILLA PARA CADA TIPO
        # =======================

        if tipo_formacion == "curso":
            c = canvas.Canvas(ruta_pdf, pagesize=landscape(letter))
            width, height = landscape(letter)
            fondo = os.path.join(settings.BASE_DIR, "static/fondo_certificado.jpg")
            if os.path.exists(fondo):
                c.drawImage(fondo, 0, 0, width=width, height=height)

            c.setFont("Helvetica-Bold", 22)
            c.drawCentredString(width/2, height - 200, f"Certificado de Curso")
            c.setFont("Times-Roman", 14)
            c.drawCentredString(width/2, height - 250, f"Otorgado a: {usuario.nombre}")
            c.drawCentredString(width/2, height - 280, f"Documento: {usuario.numero_de_documento}")
            c.drawCentredString(width/2, height - 320, f"Por aprobar el curso: {formacion.formacion}")
            c.drawCentredString(width/2, height - 350, f"Duración: {formacion.incertidumbre_horaria} horas")

        elif tipo_formacion == "taller":
            c = canvas.Canvas(ruta_pdf, pagesize=portrait(A4))
            width, height = portrait(A4)
            fondo = os.path.join(settings.BASE_DIR, "static/fondos_certificados/taller.jpg")
            if os.path.exists(fondo):
                c.drawImage(fondo, 0, 0, width=width, height=height)

            c.setFont("Courier-Bold", 24)
            c.drawCentredString(width/2, height - 150, "Constancia de Participación en Taller")
            c.setFont("Courier", 14)
            c.drawCentredString(width/2, height - 220, f"Se certifica que {usuario.nombre}")
            c.drawCentredString(width/2, height - 250, f"Ha participado activamente en el taller:")
            c.drawCentredString(width/2, height - 280, f"{formacion.formacion}")
            c.drawCentredString(width/2, height - 320, f"Con una duración total de {formacion.incertidumbre_horaria} horas")

        elif tipo_formacion == "foro":
            c = canvas.Canvas(ruta_pdf, pagesize=A4)  # 👈 Vertical
            width, height = A4  # 👈 Ancho y alto en orientación normal

            fondo = os.path.join(settings.BASE_DIR, "static/fondos_certificados/foro.jpg")
            if os.path.exists(fondo):
                c.drawImage(fondo, 0, 0, width=width, height=height)

            c.setFont("Helvetica-Oblique", 20)
            c.drawCentredString(width/2, height - 180, "Reconocimiento de Participación en Foro")
            c.setFont("Times-Italic", 16)
            c.drawCentredString(width/2, height - 240, f"{usuario.nombre}")
            c.setFont("Times-Roman", 12)
            c.drawCentredString(width/2, height - 270, f"Documento: {usuario.numero_de_documento}")
            c.drawCentredString(width/2, height - 300, f"Por su aporte en el foro: {formacion.formacion}")

        elif tipo_formacion == "diplomado":
            c = canvas.Canvas(ruta_pdf, pagesize=landscape(letter))
            width, height = landscape(letter)
            fondo = os.path.join(settings.BASE_DIR, "static/fondos_certificados/seminario.jpg")
            if os.path.exists(fondo):
                c.drawImage(fondo, 0, 0, width=width, height=height)

            c.setFont("Helvetica-Bold", 26)
            c.drawCentredString(width/2, height - 220, "Certificado de Asistencia a Seminario")
            c.setFont("Helvetica", 14)
            c.drawCentredString(width/2, height - 270, f"Se otorga a {usuario.nombre}")
            c.drawCentredString(width/2, height - 300, f"Por asistir y aprobar el seminario:")
            c.setFont("Times-BoldItalic", 16)
            c.drawCentredString(width/2, height - 330, f"{formacion.formacion}")
            c.setFont("Times-Roman", 12)
            c.drawCentredString(width/2, height - 360, f"Duración: {formacion.incertidumbre_horaria} horas")

        else:  # genérico
            c = canvas.Canvas(ruta_pdf, pagesize=landscape(letter))
            width, height = landscape(letter)
            fondo = os.path.join(settings.BASE_DIR, "static/fondos_certificados/default.jpg")
            if os.path.exists(fondo):
                c.drawImage(fondo, 0, 0, width=width, height=height)

            c.setFont("Times-Roman", 14)
            c.drawCentredString(width/2, height - 200, f"Se certifica que {usuario.nombre}")
            c.drawCentredString(width/2, height - 230, f"Ha aprobado la formación: {formacion.formacion}")

        # ========== QR (común a todos) ==========
        url_verificacion = f"http://127.0.0.1:8000/media/certificados/{nombre_archivo}"
        qr = qrcode.QRCode(version=1, box_size=10, border=2)
        qr.add_data(url_verificacion)
        qr.make(fit=True)

        img_qr = qr.make_image(fill_color="black", back_color="white")
        buffer = BytesIO()
        img_qr.save(buffer, format="PNG")
        buffer.seek(0)
        qr_reader = ImageReader(buffer)

        c.drawImage(qr_reader, width - 180, 100, width=100, height=100)
        c.setFont("Times-Bold", 10)
        c.drawCentredString(width - 130, 90, f"ID: {instance.id_formaciondocente}")

        # ========== Firma (común a todos, pero puedes cambiarla por tipo también) ==========
        firma_path = os.path.join(settings.BASE_DIR, 'static', 'firma_director.png')
        if os.path.exists(firma_path):
            c.drawImage(firma_path, width/2 - 50, 120, width=100, height=50)

        c.drawCentredString(width/2, 100, "Dr. Hernán Guzmán Murillo")
        c.drawCentredString(width/2, 85, "Director CENAPED")

        # Guardar PDF
        c.save()

        # Guardar ruta en el modelo
        relative_path = f"certificados/{nombre_archivo}"
        instance.pdf_certificado.name = relative_path
        instance.save(update_fields=['pdf_certificado'])
