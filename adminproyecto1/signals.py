from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from .models import FormacionDocente
from reportlab.lib.pagesizes import landscape, letter
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

        # Construir nombre del archivo
        nombre_archivo = f"certificado_{usuario.nombre.replace(' ', '_')}_{instance.id_formaciondocente}.pdf"
        ruta_carpeta = os.path.join(settings.MEDIA_ROOT, 'certificados')
        os.makedirs(ruta_carpeta, exist_ok=True)
        ruta_pdf = os.path.join(ruta_carpeta, nombre_archivo)

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
        qr.add_data(url_verificacion)
        qr.make(fit=True)

        img_qr = qr.make_image(fill_color="black", back_color="white")
        buffer = BytesIO()
        img_qr.save(buffer, format="PNG")
        buffer.seek(0)

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

        # Guardar PDF
        c.save()

        # Guardar ruta en el modelo
        relative_path = f"certificados/{nombre_archivo}"
        instance.pdf_certificado.name = relative_path
        instance.save(update_fields=['pdf_certificado'])
