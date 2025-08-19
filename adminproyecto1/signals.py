from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from .models import FormacionDocente
<<<<<<< HEAD
from reportlab.lib.pagesizes import landscape, portrait, letter, A4
=======
from reportlab.lib.pagesizes import landscape, letter
>>>>>>> b0021ce30dfd751496c6528ecf6ed53640ac85e7
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
import os
import qrcode
from io import BytesIO

<<<<<<< HEAD

=======
>>>>>>> b0021ce30dfd751496c6528ecf6ed53640ac85e7
@receiver(post_save, sender=FormacionDocente)
def generar_certificado_pdf(sender, instance, created, **kwargs):
    if instance.aprobado and not instance.pdf_certificado and instance.id_usuario and instance.id_formacion:
        usuario = instance.id_usuario
        formacion = instance.id_formacion
<<<<<<< HEAD
        tipo_formacion = formacion.id_tipo_formacion.formaciones.lower() if formacion.id_tipo_formacion else "generico"
=======
>>>>>>> b0021ce30dfd751496c6528ecf6ed53640ac85e7

        # Construir nombre del archivo
        nombre_archivo = f"certificado_{usuario.nombre.replace(' ', '_')}_{instance.id_formaciondocente}.pdf"
        ruta_carpeta = os.path.join(settings.MEDIA_ROOT, 'certificados')
        os.makedirs(ruta_carpeta, exist_ok=True)
        ruta_pdf = os.path.join(ruta_carpeta, nombre_archivo)

<<<<<<< HEAD
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
=======
        # Crear PDF
        c = canvas.Canvas(ruta_pdf, pagesize=landscape(letter))
        width, height = landscape(letter)

        # Fondo
        fondo_path = os.path.join(settings.BASE_DIR, 'static', 'fondo_certificado.jpg')
        if os.path.exists(fondo_path):
            c.drawImage(fondo_path, 0, 0, width=width, height=height)

        # Texto del certificado
        c.setFont("Times-Roman", 14)
        c.drawCentredString(width/2, 400, "La Universidad del Sinú y el CENAPED certifican que:")
        c.setFont("Times-Bold", 18)
        c.drawCentredString(width/2, 370, usuario.nombre)
        c.setFont("Times-Roman", 12)
        c.drawCentredString(width/2, 350, f"Identificado con documento No. {usuario.numero_de_documento}")
        c.drawCentredString(width/2, 330, f"Docente de {usuario.lugar_de_residencia} cursó y aprobó:")
        c.setFont("Times-Italic", 14)
        c.drawCentredString(width/2, 310, f"“{formacion.formacion}”")
        c.setFont("Times-Roman", 12)
        c.drawCentredString(width/2, 290, f"Con intensidad horaria de {formacion.incertidumbre_horaria} horas.")

        # ======= GENERAR Y DIBUJAR QR =======
        url_verificacion = f"http://127.0.0.1:8000/media/certificados/{nombre_archivo}"
        qr = qrcode.QRCode(
            version=1,
            box_size=10,
            border=2
        )
>>>>>>> b0021ce30dfd751496c6528ecf6ed53640ac85e7
        qr.add_data(url_verificacion)
        qr.make(fit=True)

        img_qr = qr.make_image(fill_color="black", back_color="white")
        buffer = BytesIO()
        img_qr.save(buffer, format="PNG")
        buffer.seek(0)
<<<<<<< HEAD
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
=======

        qr_reader = ImageReader(buffer)
        qr_x = width - 200
        qr_y = 80
        c.drawImage(qr_reader, qr_x, qr_y, width=100, height=100)

        # ID debajo del QR
        c.setFont("Times-Bold", 10)
        c.drawCentredString(qr_x + 50, qr_y - 15, f"ID: {instance.id_formaciondocente}")

        # Firma
        firma_path = os.path.join(settings.BASE_DIR, 'static', 'firma_director.png')
        if os.path.exists(firma_path):
            c.drawImage(firma_path, width/2 - 50, 180, width=100, height=50)

        c.drawCentredString(width/2, 170, "Dr. Hernán Guzmán Murillo")
        c.drawCentredString(width/2, 155, "Director CENAPED")
>>>>>>> b0021ce30dfd751496c6528ecf6ed53640ac85e7

        # Guardar PDF
        c.save()

        # Guardar ruta en el modelo
        relative_path = f"certificados/{nombre_archivo}"
        instance.pdf_certificado.name = relative_path
        instance.save(update_fields=['pdf_certificado'])
