# -----------------------------------------------------------------------------------------------------------------------------------------------
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from .models import FormacionDocente
from reportlab.lib.pagesizes import landscape, portrait, letter, A4
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from reportlab.lib.units import cm
import os
import qrcode
from io import BytesIO
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from django.utils import timezone
from datetime import date
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone



from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.timezone import now




# import locale # <- Eliminado, ya no es necesario

# Ruta a la carpeta de fuentes
fonts_path = os.path.join(settings.BASE_DIR, "static", "fonts")

# Registrar las variantes de Georgia
pdfmetrics.registerFont(TTFont("Georgia", os.path.join(fonts_path, "GEORGIA.TTF")))
pdfmetrics.registerFont(TTFont("Georgia-Bold", os.path.join(fonts_path, "GEORGIAB.TTF")))
pdfmetrics.registerFont(TTFont("Georgia-Italic", os.path.join(fonts_path, "GEORGIAI.TTF")))
pdfmetrics.registerFont(TTFont("Georgia-BoldItalic", os.path.join(fonts_path, "GEORGIAZ.TTF")))

# Lista de meses en español para un formato robusto
meses_es = [
    "enero", "febrero", "marzo", "abril", "mayo", "junio",
    "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"
]


@receiver(post_save, sender=FormacionDocente)
def generar_certificado_pdf(sender, instance, created, **kwargs):
    if instance.aprobado and not instance.pdf_certificado and instance.id_usuario and instance.id_formacion:
        usuario = instance.id_usuario
        formacion = instance.id_formacion
        tipo_formacion = formacion.id_tipo_formacion.formaciones if formacion.id_tipo_formacion else "generico"

        # Construir nombre del archivo
        nombre_archivo = f"certificado_{usuario.nombre.replace(' ', '_')}_{instance.id_formaciondocente}.pdf"
        ruta_carpeta = os.path.join(settings.MEDIA_ROOT, 'certificados')
        os.makedirs(ruta_carpeta, exist_ok=True)
        ruta_pdf = os.path.join(ruta_carpeta, nombre_archivo)

        # =======================
        # PLANTILLAS POR TIPO
        # =======================
        if tipo_formacion == "curso":
            c = canvas.Canvas(ruta_pdf, pagesize=landscape(letter))
            width, height = landscape(letter)

            # Fondo
            fondo = os.path.join(settings.BASE_DIR, "static/Membrete certificados (1).jpg")
            if os.path.exists(fondo):
                c.drawImage(fondo, 0, 0, width=width, height=height)

            y = height - 145

            # Encabezado
            c.setFont("Georgia-Bold", 16)
            c.drawCentredString(width / 2, y, "El Centro de Actualización y Perfeccionamiento Docente")
            y -= 17

            c.setFont("Georgia", 15)
            c.drawCentredString(width / 2, y, "de la Universidad del Sinú – Elías Bechara Zainúm")
            y -= 40

            # Texto: "Certifican que"
            c.setFont("Georgia", 14)
            c.drawCentredString(width / 2, y, "Certifican que")
            y -= 40

            nombre_usuario = None
            if usuario and hasattr(usuario, "nombre"):
                nombre_usuario = usuario.nombre.title()

            # ========= Dibujar en el PDF =========
            if nombre_usuario:
                c.setFont("Georgia-Bold", 26)
                c.drawCentredString(width / 2, y, nombre_usuario)
                y -= 18
            # Documento
            c.setFont("Georgia", 12)
            c.drawCentredString(width / 2, y, f"Identificado(a) con el documento de identidad No. {usuario.numero_de_documento}")
            y -= 40

            # Programa
            programa = None
            if usuario.id_programa:
                programa_nombre = getattr(usuario.id_programa, "Programa", None)
                if programa_nombre:
                    programa = programa_nombre.title()

            if programa:
                c.drawCentredString(width / 2, y, f"Docente adscrito(a) al {programa} cursó y aprobó el curso")
            else:
                c.drawCentredString(width / 2, y, "Docente sin programa asignado cursó y aprobó el curso")
            y -= 25

            # Nombre del curso en negrilla
            nombre_formacion = None
            if formacion and hasattr(formacion, "formacion"):
                nombre_formacion = formacion.formacion.title()

            if nombre_formacion:
                texto_formacion = f"“{nombre_formacion}”"
                c.setFont("Georgia-Bold", 20)
                c.drawCentredString(width / 2, y, texto_formacion)
            y -= 40

            # Periodo y horas
            periodo = "N/A"
            if formacion.fecha_fin:
                año = formacion.fecha_fin.year
                mes = formacion.fecha_fin.month
                if 1 <= mes <= 7:
                    periodo = f"1-{año}"
                else:
                    periodo = f"2-{año}"

            horas = formacion.incertidumbre_horaria or 0

            c.setFont("Georgia", 12)
            c.drawCentredString(
                width / 2,
                y,
                f"Desarrollado durante el periodo académico {periodo}, con una intensidad horaria de {horas} horas."
            )
            y -= 30

            # ** INICIO CORRECCIÓN FECHA **
            fecha_texto = "" # Inicialización para evitar UnboundLocalError
            if instance.fecha_aprobacion:
                dia = instance.fecha_aprobacion.day
                mes_num = instance.fecha_aprobacion.month
                anio = instance.fecha_aprobacion.year
                mes_nombre = meses_es[mes_num - 1]
                fecha_texto = f"Para constancia se firma el presente certificado el día {dia} del mes de {mes_nombre} de {anio}."
            
            c.setFont("Georgia", 12)
            c.drawCentredString(width / 2, y, fecha_texto)
            
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

            c.drawImage(qr_reader, width - 160, 100, width=70, height=70)

            if instance.serial:
                serial_texto = instance.serial.upper()
                c.setFont("Times-Bold", 10)
                c.drawCentredString(width - 130, 90, serial_texto)
                
            # ========== Firma ==========
            firma_path = os.path.join(settings.BASE_DIR, 'static', 'firma_director.png')
            if os.path.exists(firma_path):
                c.drawImage(firma_path, width / 2 - 75, 130, width=150, height=75, mask='auto')

            # Nombre en negrilla, tamaño 16
            c.setFont("Georgia-Bold", 16)
            c.drawCentredString(width / 2, 150, "______________________")
            c.drawCentredString(width / 2, 135, "Dr. Hernán Guzmán Murillo")

            # Cargo en normal, tamaño 12
            c.setFont("Georgia", 12)
            c.drawCentredString(width / 2, 120, "Director del Centro de Actualización y")
            c.drawCentredString(width / 2, 105, "Perfeccionamiento Docente")
            c.drawCentredString(width / 2, 90, "CENAPED")

            c.showPage()
            c.save()

            # Guardar ruta en el modelo
            relative_path = f"certificados/{nombre_archivo}"
            instance.pdf_certificado.name = relative_path
            instance.save(update_fields=['pdf_certificado'])
            
# ---------------------------------------------------------------------------------------------------------------------------------------------------------------------
        elif tipo_formacion == "talleres":
            
            c = canvas.Canvas(ruta_pdf, pagesize=landscape(letter))
            width, height = landscape(letter)

            # Fondo
            fondo = os.path.join(settings.BASE_DIR, "static/Membrete certificados (1).jpg")
            if os.path.exists(fondo):
                c.drawImage(fondo, 0, 0, width=width, height=height)

            y = height - 160

            # Encabezado
            c.setFont("Georgia", 15)
            c.drawCentredString(width / 2, y, "La Universidad del Sinú y el Centro de Actualización y Perfeccionamiento")
            y -= 17

            c.setFont("Georgia", 15)
            c.drawCentredString(width / 2, y, "Docente – CENAPED certifican que ")
            y -= 40

            # ========= Nombre del usuario =========
            nombre_usuario = None
            if usuario and hasattr(usuario, "nombre"):
                nombre_usuario = usuario.nombre.title()

            # ========= Dibujar en el PDF =========
            if nombre_usuario:
                c.setFont("Georgia-Bold", 26)
                c.drawCentredString(width / 2, y, nombre_usuario)
                y -= 18

            # Documento
            c.setFont("Georgia", 12)
            c.drawCentredString(width / 2, y, f"Identificado(a) con el documento de identidad No. {usuario.numero_de_documento}")
            y -= 30

            # Programa
            programa = None
            if usuario.id_programa:
                programa_nombre = getattr(usuario.id_programa, "Programa", None)
                if programa_nombre:
                    programa = programa_nombre.title()

            if programa:
                c.drawCentredString(width / 2, y, f"Docente adscrito(a) al {programa} participó en el")
            else:
                c.drawCentredString(width / 2, y, "Docente sin programa asignado cursó y aprobó el curso")
            y -= 25

            # Nombre del curso en negrilla
            nombre_formacion = None
            if formacion and hasattr(formacion, "formacion"):
                nombre_formacion = formacion.formacion.title()

            if nombre_formacion:
                texto_formacion = f"“Taller: {nombre_formacion}”"
                c.setFont("Georgia-Bold", 20)
                c.drawCentredString(width / 2, y, texto_formacion)
                y -= 30
            
            # ** INICIO CORRECCIÓN FECHA **
            # Eliminadas las llamadas a locale.setlocale
            texto_periodo = ""
            if formacion.fecha_de_inicio:
                dia = formacion.fecha_de_inicio.day
                mes_num = formacion.fecha_de_inicio.month
                anio = formacion.fecha_de_inicio.year
                mes_nombre = meses_es[mes_num - 1]
                texto_periodo = f"Desarrollado el día {dia} de {mes_nombre} de {anio}."

            c.setFont("Georgia", 12)
            c.drawCentredString(width / 2, y, texto_periodo)
            y -= 40
            
            fecha_texto = "" # Inicialización para evitar UnboundLocalError
            if instance.fecha_aprobacion:
                dia = instance.fecha_aprobacion.day
                mes_num = instance.fecha_aprobacion.month
                anio = instance.fecha_aprobacion.year
                mes_nombre = meses_es[mes_num - 1]
                fecha_texto = f"Para constancia se firma el presente certificado el día {dia} del mes de {mes_nombre} de {anio}."

            c.setFont("Georgia", 12)
            c.drawCentredString(width / 2, y, fecha_texto)

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

            c.drawImage(qr_reader, width - 160, 100, width=70, height=70)

            c.setFont("Times-Bold", 10)
            c.drawCentredString(width - 130, 90, f"ID: {instance.id_formaciondocente}")

            # ========== Firma ==========
            firma_path = os.path.join(settings.BASE_DIR, 'static', 'firma_director.png')
            if os.path.exists(firma_path):
                c.drawImage(firma_path, width / 2 - 75, 130, width=150, height=75, mask='auto')

            # Nombre en negrilla, tamaño 16
            c.setFont("Georgia-Bold", 16)
            c.drawCentredString(width / 2, 150, "______________________")
            c.drawCentredString(width / 2, 135, "Dr. Hernán Guzmán Murillo")

            # Cargo en normal, tamaño 12
            c.setFont("Georgia", 12)
            c.drawCentredString(width / 2, 120, "Director del Centro de Actualización y")
            c.drawCentredString(width / 2, 105, "Perfeccionamiento Docente")
            c.drawCentredString(width / 2, 90, "CENAPED")

            c.showPage()
            c.save()

            # Guardar ruta en el modelo
            relative_path = f"certificados/{nombre_archivo}"
            instance.pdf_certificado.name = relative_path
            instance.save(update_fields=['pdf_certificado'])
            
# ---------------------------------------------------------------------------------------------------------------------------------------------------------------------
        elif tipo_formacion == "diplomado" and formacion.formacion == "Diplomado En Docencia Universitaria Con Énfasis en Investigación en el Aula":
            c = canvas.Canvas(ruta_pdf, pagesize=portrait((25 * cm, 35 * cm)))
            width, height = portrait((25 * cm, 35 * cm))

            fondo = os.path.join(settings.BASE_DIR, "static/Diseño certificado.jpg")
            if os.path.exists(fondo):
                c.drawImage(fondo, 0, 0, width=width, height=height)

            y = height - 8 * cm
            
            c.setFont("Georgia", 18)
            c.drawCentredString(width / 2, y, "El Centro De Actualización y Perfeccionamiento Docente")
            y -= 20

            c.setFont("Georgia", 18)
            c.drawCentredString(width / 2, y, "de la Universidad del Sinú - Elías Bechara Zainúm")
            y -= 2 * cm
            
            c.setFont("Georgia", 14)
            c.drawCentredString(width / 2, y, "Certifica que:")
            y -= 2 * cm
            
            c.setFont("Georgia-Bold", 26)
            c.drawCentredString(width / 2, y, usuario.nombre.title())
            y -= 20

            c.setFont("Georgia", 16)
            c.drawCentredString(width / 2, y, f"Identificado(a) con el documento de identidad No. {usuario.numero_de_documento}")
            y -= 2 * cm
            
            c.setFont("Georgia", 14)
            c.drawCentredString(width / 2, y, "Cursó y aprobó el")
            y -= 2 * cm

            line1 = "Diplomado En Docencia Universitaria"
            line2 = "Con Énfasis en Investigación en el Aula"

            c.setFont("Georgia-Bold", 24)
            c.drawCentredString(width / 2, y, f"{line1}")
            y -= 1 * cm
            c.drawCentredString(width / 2, y, f"{line2}")
            y -= 2 * cm
            
            periodo = "N/A"
            if formacion.fecha_fin:
                año = formacion.fecha_fin.year
                mes = formacion.fecha_fin.month
                if 1 <= mes <= 7:
                    periodo = f"1-{año}"
                else:
                    periodo = f"2-{año}"

            horas = formacion.incertidumbre_horaria or 0

            line1_periodo = f"Desarrollado en el periodo académico {periodo},"
            line2_periodo = f"con una intensidad horaria de {horas} horas."
            
            c.setFont("Georgia", 16)
            c.drawCentredString(width / 2, y, line1_periodo)
            y -= 20
            c.drawCentredString(width / 2, y, line2_periodo)

            y -= 2 * cm
            
            # ** INICIO CORRECCIÓN FECHA **
            # Eliminadas las llamadas a locale.setlocale
            fecha_texto_line1 = ""
            fecha_texto_line2 = ""

            if instance.fecha_aprobacion:
                dia = instance.fecha_aprobacion.day
                mes_num = instance.fecha_aprobacion.month
                anio = instance.fecha_aprobacion.year
                mes_nombre = meses_es[mes_num - 1]
                fecha_texto_line1 = "Para constancia, se expide el presente certificado"
                fecha_texto_line2 = f"a los {dia} días del mes de {mes_nombre} de {anio}."
            
            c.setFont("Georgia", 16)
            c.drawCentredString(width / 2, y, fecha_texto_line1)
            y -= 0.7 * cm
            c.drawCentredString(width / 2, y, fecha_texto_line2)
            y -= 40
                
            # ========= Lógica de QR y Firma para el certificado especial (vertical) =========
            url_verificacion = f"http://127.0.0.1:8000/media/certificados/{nombre_archivo}"
            qr = qrcode.QRCode(version=1, box_size=10, border=2)
            qr.add_data(url_verificacion)
            qr.make(fit=True)

            img_qr = qr.make_image(fill_color="black", back_color="white")
            buffer = BytesIO()
            img_qr.save(buffer, format="PNG")
            buffer.seek(0)
            qr_reader = ImageReader(buffer)

            c.drawImage(qr_reader, width - 120, 150, width=70, height=70)
             

            if instance.serial:
                serial_texto = instance.serial.upper()
                c.setFont("Times-Bold", 10)
                c.drawCentredString(width - 90, 140, serial_texto)
            
            firma_path = os.path.join(settings.BASE_DIR, 'static', 'firma_director.png')
            if os.path.exists(firma_path):
                c.drawImage(firma_path, width / 2 - 75, 200, width=150, height=75, mask='auto')

            # Nuevo diseño de la firma
            c.setFont("Georgia-Bold", 16)
            c.drawCentredString(width / 2, 220, "______________________")
            c.drawCentredString(width / 2, 205, "Dr. Hernán Guzmán Murillo")

            c.setFont("Georgia", 12)
            c.drawCentredString(width / 2, 190, "Director del Centro de Actualización y")
            c.drawCentredString(width / 2, 175, "Perfeccionamiento Docente CENAPED")
                
            c.showPage()
            c.save()

            # Guardar ruta en el modelo
            relative_path = f"certificados/{nombre_archivo}"
            instance.pdf_certificado.name = relative_path
            instance.save(update_fields=['pdf_certificado'])
            
# -----------------------------------------------------------------------------------------------------------------------------------------------------
        elif tipo_formacion == "diplomado":
            c = canvas.Canvas(ruta_pdf, pagesize=landscape(letter))
            width, height = landscape(letter)

            # Fondo
            fondo = os.path.join(settings.BASE_DIR, "static/Membrete certificados (1).jpg")
            if os.path.exists(fondo):
                c.drawImage(fondo, 0, 0, width=width, height=height)

            y = height - 145

            # Encabezado
            c.setFont("Georgia-Bold", 16)
            c.drawCentredString(width / 2, y, "El Centro de Actualización y Perfeccionamiento Docente")
            y -= 17

            c.setFont("Georgia", 15)
            c.drawCentredString(width / 2, y, "de la Universidad del Sinú – Elías Bechara Zainúm")
            y -= 40

            # Texto: "Certifican que"
            c.setFont("Georgia", 14)
            c.drawCentredString(width / 2, y, "Certifican que")
            y -= 40

            nombre_usuario = None
            if usuario and hasattr(usuario, "nombre"):
                nombre_usuario = usuario.nombre.title()

            # ========= Dibujar en el PDF =========
            if nombre_usuario:
                c.setFont("Georgia-Bold", 26)
                c.drawCentredString(width / 2, y, nombre_usuario)
                y -= 18
            # Documento
            c.setFont("Georgia", 12)
            c.drawCentredString(width / 2, y, f"Identificado(a) con el documento de identidad No. {usuario.numero_de_documento}")
            y -= 40

            # Programa
            programa = None
            if usuario.id_programa:
                programa_nombre = getattr(usuario.id_programa, "Programa", None)
                if programa_nombre:
                    programa = programa_nombre.title()

            if programa:
                c.drawCentredString(width / 2, y, f"Docente adscrito(a) al {programa} cursó y aprobó el ")
            else:
                c.drawCentredString(width / 2, y, "Docente sin programa asignado cursó y aprobó el ")
            y -= 25

            # Nombre del curso en negrilla
            nombre_formacion = None
            if formacion and hasattr(formacion, "formacion"):
                nombre_formacion = formacion.formacion.title()

            if nombre_formacion:
                texto_formacion = f"{nombre_formacion}"
                c.setFont("Georgia-Bold", 20)
                c.drawCentredString(width / 2, y, texto_formacion)
            y -= 40

            # Periodo y horas
            periodo = "N/A"
            if formacion.fecha_fin:
                año = formacion.fecha_fin.year
                mes = formacion.fecha_fin.month
                if 1 <= mes <= 7:
                    periodo = f"1-{año}"
                else:
                    periodo = f"2-{año}"

            horas = formacion.incertidumbre_horaria or 0

            c.setFont("Georgia", 12)
            c.drawCentredString(
                width / 2,
                y,
                f"Desarrollado durante el periodo académico {periodo}, con una intensidad horaria de {horas} horas."
            )
            y -= 40

            # ** INICIO CORRECCIÓN FECHA **
            # Eliminadas las llamadas a locale.setlocale
            fecha_texto = "" # Inicialización para evitar UnboundLocalError
            if instance.fecha_aprobacion:
                dia = instance.fecha_aprobacion.day
                mes_num = instance.fecha_aprobacion.month
                anio = instance.fecha_aprobacion.year
                mes_nombre = meses_es[mes_num - 1]
                fecha_texto = f"Para constancia se firma el presente certificado el día {dia} del mes de {mes_nombre} de {anio}."
            
            c.setFont("Georgia", 12)
            c.drawCentredString(width / 2, y, fecha_texto)
            
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

            c.drawImage(qr_reader, width - 160, 100, width=70, height=70)

            c.setFont("Times-Bold", 10)
            c.drawCentredString(width - 130, 90, f"ID: {instance.id_formaciondocente}")

            # ========== Firma ==========
            firma_path = os.path.join(settings.BASE_DIR, 'static', 'firma_director.png')
            if os.path.exists(firma_path):
                c.drawImage(firma_path, width / 2 - 75, 130, width=150, height=75, mask='auto')

            # Nombre en negrilla, tamaño 16
            c.setFont("Georgia-Bold", 16)
            c.drawCentredString(width / 2, 150, "______________________")
            c.drawCentredString(width / 2, 135, "Dr. Hernán Guzmán Murillo")

            # Cargo en normal, tamaño 12
            c.setFont("Georgia", 12)
            c.drawCentredString(width / 2, 120, "Director del Centro de Actualización y")
            c.drawCentredString(width / 2, 105, "Perfeccionamiento Docente")
            c.drawCentredString(width / 2, 90, "CENAPED")

            c.showPage()
            c.save()

            # Guardar ruta en el modelo
            relative_path = f"certificados/{nombre_archivo}"
            instance.pdf_certificado.name = relative_path
            instance.save(update_fields=['pdf_certificado'])
            
        elif tipo_formacion == "foro":
            c = canvas.Canvas(ruta_pdf, pagesize=landscape(A4))
            width, height = landscape(A4)

            fondo = os.path.join(settings.BASE_DIR, "static/fondos_certificados/foro.jpg")
            if os.path.exists(fondo):
                c.drawImage(fondo, 0, 0, width=width, height=height)

            c.setFont("Helvetica-Oblique", 20)
            c.drawCentredString(width / 2, height - 180, "Reconocimiento de Participación en Foro")

            c.setFont("Times-Italic", 16)
            c.drawCentredString(width / 2, height - 240, f"{usuario.nombre}")

            c.setFont("Times-Roman", 12)
            c.drawCentredString(width / 2, height - 270, f"Documento: {usuario.numero_de_documento}")
            c.drawCentredString(width / 2, height - 300, f"Por su aporte en el foro: {formacion.formacion}")

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

            c.drawImage(qr_reader, width - 160, 100, width=70, height=70)

            if instance.serial:
                serial_texto = instance.serial.upper()
                c.setFont("Times-Bold", 10)
                c.drawCentredString(width - 90, 140, serial_texto)

            # ========== Firma ==========
            firma_path = os.path.join(settings.BASE_DIR, 'static', 'firma_director.png')
            if os.path.exists(firma_path):
                c.drawImage(firma_path, width / 2 - 75, 130, width=150, height=75, mask='auto')

            # Nombre en negrilla, tamaño 16
            c.setFont("Georgia-Bold", 16)
            c.drawCentredString(width / 2, 150, "______________________")
            c.drawCentredString(width / 2, 135, "Dr. Hernán Guzmán Murillo")

            # Cargo en normal, tamaño 12
            c.setFont("Georgia", 12)
            c.drawCentredString(width / 2, 120, "Director del Centro de Actualización y")
            c.drawCentredString(width / 2, 105, "Perfeccionamiento Docente")
            c.drawCentredString(width / 2, 90, "CENAPED")
        
            c.showPage()
            c.save()

            # Guardar ruta en el modelo
            relative_path = f"certificados/{nombre_archivo}"
            instance.pdf_certificado.name = relative_path
            instance.save(update_fields=['pdf_certificado'])