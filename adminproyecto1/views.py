import os
from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import render, redirect
from .models import FormacionDocente, Entidad, Usuario, Formacion
from datetime import date
from reportlab.platypus import Paragraph, Frame, PageTemplate, BaseDocTemplate
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import letter
from django.shortcuts import render, get_object_or_404

from django.shortcuts import render
from django.db.models import Count
from .models import Formacion







def oferta_formacion(request):
    # Solo formaciones activas
    formaciones = Formacion.objects.filter(activo=True)

    context = {
        "formaciones": formaciones,
    }
    return render(request, "adminproyecto1/oferta_formacion.html", context)

def mis_formaciones(request):
    """
    Vista que muestra las formaciones de un usuario, filtradas por el periodo actual.
    """
    usuario_id = request.session.get("usuario_id")
    usuario = get_object_or_404(Usuario, id_usuario=usuario_id)

    # 1. Obtenemos el periodo actual
    hoy = date.today()
    año_actual = hoy.year
    corte = date(año_actual, 7, 22)
    if hoy < corte:
        periodo_actual = f"{año_actual}-1"
    else:
        periodo_actual = f"{año_actual}-2"
        
    # 2. Filtramos las formaciones del docente por el periodo actual
    formaciones_del_periodo = []
    
    # Traemos todas las formaciones del usuario y las filtramos en el código
    todas_las_formaciones_del_usuario = FormacionDocente.objects.filter(id_usuario=usuario)
    
    for formacion_docente in todas_las_formaciones_del_usuario:
        # Usamos la propiedad 'periodo' del modelo Formacion
        if formacion_docente.id_formacion.periodo == periodo_actual:
            formaciones_del_periodo.append(formacion_docente)

    context = {
        "formaciones": formaciones_del_periodo,
    }

    return render(request, "adminproyecto1/mis_formaciones.html", context)

 





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


def logout_view(request):
    request.session.flush()  # Elimina toda la sesión
    return redirect('login')  # Redirige al login


def login_view(request):
    if request.method == "POST":
        nombre = request.POST.get('nombre')
        numero_de_documento = request.POST.get('numero_de_documento')

        try:
            usuario = Usuario.objects.get(nombre=nombre, numero_de_documento=numero_de_documento)
            # Guardar info de usuario en sesión
            request.session['usuario_id'] = usuario.id_usuario
            request.session['usuario_nombre'] = usuario.nombre

            # Redirigir al dashboard (index)
            return redirect('index')   # ⬅️ aquí estaba el error
        except Usuario.DoesNotExist:
            # Usuario no encontrado, mostrar error
            context = {'error': 'Nombre o número de documento incorrectos'}
            return render(request, 'adminproyecto1/login.html', context)

    # GET muestra el formulario de login
    return render(request, 'adminproyecto1/login.html')



def index(request):
    usuario_nombre = request.session.get('usuario_nombre', '')  # igual que antes
    return render(request, "adminproyecto1/index.html", {
        'usuario_nombre': usuario_nombre
    })

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
