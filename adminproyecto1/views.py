import os
from django.conf import settings
<<<<<<< HEAD
from django.http import HttpResponse
from django.shortcuts import render, redirect
from .models import FormacionDocente, Entidad, Usuario, Formacion
=======
from django.template.loader import render_to_string
from weasyprint import HTML
from django.http import HttpResponse
from django.shortcuts import render
from .models import FormacionDocente, Entidad
>>>>>>> b0021ce30dfd751496c6528ecf6ed53640ac85e7

from reportlab.platypus import Paragraph, Frame, PageTemplate, BaseDocTemplate
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import letter
<<<<<<< HEAD


=======
from django.shortcuts import render, redirect
from .models import Usuario


from django.shortcuts import render
from .models import Formacion

>>>>>>> b0021ce30dfd751496c6528ecf6ed53640ac85e7
def oferta_formacion(request):
    # Obtener todas las formaciones
    formaciones = Formacion.objects.all()
    # Pasar las formaciones al contexto para que se muestren en la plantilla
    context = {
        'formaciones': formaciones,
    }
    return render(request, 'adminproyecto1/oferta_formacion.html', context)
<<<<<<< HEAD


=======
>>>>>>> b0021ce30dfd751496c6528ecf6ed53640ac85e7
def historial_docente(request):
    usuario_id = request.session.get('usuario_id')
    usuario_nombre = request.session.get('usuario_nombre', '')  # Obtener nombre desde sesión

    if not usuario_id:
        return redirect('login')

    # Obtener las formaciones del usuario
    formaciones = FormacionDocente.objects.filter(id_usuario=usuario_id)

    # Calcular el periodo y agregarlo a cada formación
    for f in formaciones:
        if f.id_formacion and f.id_formacion.fecha_fin:
            fecha = f.id_formacion.fecha_fin
            f.periodo = f"{fecha.year}-1" if fecha.month < 8 else f"{fecha.year}-2"
        else:
            f.periodo = "Sin fecha"

    context = {
        'formaciones': formaciones,
        'usuario_nombre': usuario_nombre,  # Enviar nombre al template
    }
    return render(request, 'adminproyecto1/historial_docente.html', context)

<<<<<<< HEAD

def logout_view(request):
    request.session.flush()  # Elimina toda la sesión
    return redirect('login')  # Redirige al login

=======
def logout_view(request):
    request.session.flush()  # Elimina toda la sesión
    return redirect('login')  # Redirige al login
from django.shortcuts import render, redirect
from .models import Usuario
>>>>>>> b0021ce30dfd751496c6528ecf6ed53640ac85e7

def login_view(request):
    if request.method == "POST":
        nombre = request.POST.get('nombre')
        numero_de_documento = request.POST.get('numero_de_documento')

        try:
            usuario = Usuario.objects.get(nombre=nombre, numero_de_documento=numero_de_documento)
            # Guardar info de usuario en sesión
            request.session['usuario_id'] = usuario.id_usuario
            request.session['usuario_nombre'] = usuario.nombre

            # Redirigir a dashboard o página principal
            return redirect('dashboard')  # Asegúrate que esta URL exista
        except Usuario.DoesNotExist:
            # Usuario no encontrado, mostrar error
            context = {'error': 'Nombre o número de documento incorrectos'}
            return render(request, 'adminproyecto1/login.html', context)

    # GET muestra el formulario de login
    return render(request, 'adminproyecto1/login.html')


<<<<<<< HEAD
=======

>>>>>>> b0021ce30dfd751496c6528ecf6ed53640ac85e7
def index(request):
    usuario_nombre = request.session.get('usuario_nombre', '')  # igual que antes
    return render(request, "adminproyecto1/index.html", {
        'usuario_nombre': usuario_nombre
    })

<<<<<<< HEAD

=======
    
>>>>>>> b0021ce30dfd751496c6528ecf6ed53640ac85e7
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

<<<<<<< HEAD

=======
>>>>>>> b0021ce30dfd751496c6528ecf6ed53640ac85e7
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
<<<<<<< HEAD
        return response
=======
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
>>>>>>> b0021ce30dfd751496c6528ecf6ed53640ac85e7
