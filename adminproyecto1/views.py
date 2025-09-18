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
from django.shortcuts import render
from .models import Formacion
from django.contrib.admin.views.decorators import staff_member_required
from django.http import JsonResponse
from django.db.models import Count, Q
import datetime, json
from datetime import date
from django.utils.timezone import now
from .models import Formacion, FormacionDocente, Programa, Facultad, Usuario, Areas


def calcular_periodo(fecha):
    """Devuelve el periodo en formato 'YYYY-1' o 'YYYY-2' según la fecha."""
    if fecha.month <= 7:
        return f"{fecha.year}-1"
    else:
        return f"{fecha.year}-2"


# 🔑 Mapeo de opciones del select a los valores reales en la BD
MAPA_MOMENTOS = {
    "SEMESTRAL1": "semestre_1",
    "SEMESTRAL2": "semestre_2",
    "INTERSEMESTRAL1": "intersemestral_1",
    "INTERSEMESTRAL2": "intersemestral_2",
}


@staff_member_required
def dashboard(request):
    hoy = now().date()
    periodo_actual = calcular_periodo(hoy)

    # === Rango del periodo actual ===
    año, semestre = periodo_actual.split("-")
    año = int(año)
    if semestre == "1":
        inicio = datetime.date(año, 1, 1)
        fin = datetime.date(año, 7, 31)
    else:
        inicio = datetime.date(año, 8, 1)
        fin = datetime.date(año, 12, 31)

    # ==========================================================
    # 📊 GRÁFICO 1: Aprobados por formación (periodo actual)
    # ==========================================================
    formaciones_qs = (
        Formacion.objects
        .filter(fecha_de_inicio__lte=fin, fecha_fin__gte=inicio)
        .annotate(aprobados=Count("formaciondocente", filter=Q(formaciondocente__aprobado=True)))
        .order_by("-aprobados")
    )

    chart_labels_formacion = [f.formacion for f in formaciones_qs]
    chart_values_formacion = [f.aprobados for f in formaciones_qs]
    total_aprobados_formacion = sum(chart_values_formacion)

    # ==========================================================
    # 📊 GRÁFICO 2: Histórico (Año + Momento)
    # ==========================================================
    año_filtro = request.GET.get("año")
    opcion_filtro = request.GET.get("opcion")

    formaciones_historico = Formacion.objects.none()
    if año_filtro:
        año_filtro = int(año_filtro)
        formaciones_historico = Formacion.objects.filter(fecha_de_inicio__year=año_filtro)

        if opcion_filtro == "TODO":
            pass
        elif opcion_filtro == "PERIODO1":
            formaciones_historico = formaciones_historico.filter(fecha_de_inicio__month__lte=7)
        elif opcion_filtro == "PERIODO2":
            formaciones_historico = formaciones_historico.filter(fecha_de_inicio__month__gte=8)
        elif opcion_filtro in MAPA_MOMENTOS:
            formaciones_historico = formaciones_historico.filter(momento=MAPA_MOMENTOS[opcion_filtro])

        formaciones_historico = (
            formaciones_historico
            .annotate(aprobados=Count("formaciondocente", filter=Q(formaciondocente__aprobado=True)))
            .order_by("-aprobados")
        )

    chart_labels_formacion_hist = [f.formacion for f in formaciones_historico]
    chart_values_formacion_hist = [f.aprobados for f in formaciones_historico]
    total_aprobados_formacion_hist = sum(chart_values_formacion_hist)

    # Lista de años disponibles
    años_opciones = sorted([d.year for d in Formacion.objects.dates("fecha_de_inicio", "year")])

    opciones_filtro = [
        {"value": "TODO", "label": "Todo"},
        {"value": "PERIODO1", "label": "Periodo 1"},
        {"value": "PERIODO2", "label": "Periodo 2"},
        {"value": "SEMESTRAL1", "label": "Semestral 1"},
        {"value": "SEMESTRAL2", "label": "Semestral 2"},
        {"value": "INTERSEMESTRAL1", "label": "Intersemestral 1"},
        {"value": "INTERSEMESTRAL2", "label": "Intersemestral 2"},
    ]

    # ==========================================================
    # 📊 GRÁFICO 3: Aprobados por área (con filtros)
    # ==========================================================
    programa_id = request.GET.get("programa")
    año_area = request.GET.get("año_area")
    momento_area = request.GET.get("momento_area")

    programas = Programa.objects.all()
    qs = FormacionDocente.objects.filter(aprobado=True)

    if programa_id:
        qs = qs.filter(id_programa=programa_id)
    if año_area:
        qs = qs.filter(id_formacion__fecha_de_inicio__year=año_area)
    if momento_area and momento_area in MAPA_MOMENTOS:
        qs = qs.filter(id_formacion__momento=MAPA_MOMENTOS[momento_area])

    areas_data = (
        qs.values("id_formacion__id_areas__areas")
        .annotate(total=Count("id_usuario", distinct=True))
        .order_by("-total")
    )

    chart_labels_area = [a["id_formacion__id_areas__areas"] or "Sin área" for a in areas_data]
    chart_values_area = [a["total"] for a in areas_data]
    total_aprobados_area = sum(chart_values_area)

    # ==========================================================
    # 📊 GRÁFICO 4: Aprobados por formación (con filtros)
    # ==========================================================
    programa_formacion_id = request.GET.get("programa_formacion")
    año_formacion = request.GET.get("año_formacion")
    momento_formacion = request.GET.get("momento_formacion")

    qs_formacion_filtro = FormacionDocente.objects.filter(aprobado=True)

    if programa_formacion_id:
        qs_formacion_filtro = qs_formacion_filtro.filter(id_programa=programa_formacion_id)
    if año_formacion:
        qs_formacion_filtro = qs_formacion_filtro.filter(id_formacion__fecha_de_inicio__year=año_formacion)
    if momento_formacion and momento_formacion in MAPA_MOMENTOS:
        qs_formacion_filtro = qs_formacion_filtro.filter(id_formacion__momento=MAPA_MOMENTOS[momento_formacion])

    formacion_filtro_data = (
        qs_formacion_filtro
        .values("id_formacion__formacion")
        .annotate(total=Count("id_usuario", distinct=True))
        .order_by("-total")
    )

    chart_labels_formacion_filtro = [f["id_formacion__formacion"] or "Sin nombre" for f in formacion_filtro_data]
    chart_values_formacion_filtro = [f["total"] for f in formacion_filtro_data]
    total_aprobados_formacion_filtro = sum(chart_values_formacion_filtro)

    # ==========================================================
    # 📊 GRÁFICO 5: Docentes (total vs aprobados) por facultad
    # ==========================================================
    facultad_id = request.GET.get("facultad")
    año_facultad = request.GET.get("año_facultad")
    momento_facultad = request.GET.get("momento_facultad")

    facultades = Facultad.objects.all()
    total_docentes_facultad = 0
    docentes_con_formacion = 0

    if facultad_id:
        facultad_id = int(facultad_id)
        docentes_facultad = Usuario.objects.filter(id_programa__id_facultad=facultad_id)
        total_docentes_facultad = docentes_facultad.count()

        qs_facultad = FormacionDocente.objects.filter(aprobado=True, id_usuario__in=docentes_facultad)
        if año_facultad:
            qs_facultad = qs_facultad.filter(id_formacion__fecha_de_inicio__year=año_facultad)
        if momento_facultad and momento_facultad in MAPA_MOMENTOS:
            qs_facultad = qs_facultad.filter(id_formacion__momento=momento_facultad)

        docentes_ids_aprobados = qs_facultad.values_list("id_usuario", flat=True).distinct()
        docentes_con_formacion = docentes_ids_aprobados.count()

    chart_labels_facultad = ["Total docentes", "Docentes aprobados"]
    chart_values_facultad = [total_docentes_facultad, docentes_con_formacion]

    # ==========================================================
    # 📊 GRÁFICO NUEVO: Áreas por Facultad
    # ==========================================================
    facultad_filtro = request.GET.get("facultad_area")
    año_area_fac = request.GET.get("año_area_fac")
    momento_area_fac = request.GET.get("momento_area_fac")

    # Base: docentes aprobados
    qs_areas_fac = FormacionDocente.objects.filter(aprobado=True)

    # 🔹 Filtrar por facultad
    if facultad_filtro:
        qs_areas_fac = qs_areas_fac.filter(id_usuario__id_programa__id_facultad=facultad_filtro)

    # 🔹 Filtrar por año
    if año_area_fac:
        qs_areas_fac = qs_areas_fac.filter(id_formacion__fecha_de_inicio__year=año_area_fac)

    # 🔹 Filtrar por momento
    if momento_area_fac and momento_area_fac in MAPA_MOMENTOS:
        qs_areas_fac = qs_areas_fac.filter(id_formacion__momento=MAPA_MOMENTOS[momento_area_fac])

    # Agrupar por área de la formación
    areas_fac_data = (
        qs_areas_fac.values("id_formacion__id_areas__areas")
        .annotate(total=Count("id_usuario", distinct=True))
        .order_by("-total")
    )

    chart_labels_area_fac = [a["id_formacion__id_areas__areas"] or "Sin área" for a in areas_fac_data]
    chart_values_area_fac = [a["total"] for a in areas_fac_data]
    total_aprobados_area_fac = sum(chart_values_area_fac)

    # ==========================================================
    # 📊 GRÁFICO 7: Programas por Facultad
    # ==========================================================
    facultad_programa = request.GET.get("facultad_programa")
    año_programa_fac = request.GET.get("año_programa_fac")
    momento_programa_fac = request.GET.get("momento_programa_fac")

    if año_programa_fac:
        inicio = date(int(año_programa_fac), 1, 1)
        fin = date(int(año_programa_fac), 12, 31)
    else:
        inicio = date.today().replace(month=1, day=1)
        fin = date.today()

    programas_qs = Programa.objects.all()

    if facultad_programa:
        programas_qs = programas_qs.filter(id_facultad=facultad_programa)

    programas_qs = (
        programas_qs.annotate(
            aprobados=Count(
                "formaciondocente",
                filter=Q(
                    formaciondocente__aprobado=True,
                    formaciondocente__id_formacion__fecha_de_inicio__lte=fin,
                    formaciondocente__id_formacion__fecha_fin__gte=inicio,
                ),
                distinct=True
            )
        )
        .order_by("-aprobados")
    )

    chart_labels_programa_fac = [p.Programa for p in programas_qs]
    chart_values_programa_fac = [p.aprobados for p in programas_qs]
    total_aprobados_programa_fac = sum(chart_values_programa_fac)

     # ==========================================================
    # 📊 GRÁFICO 8: Formaciones por Facultad
    # ==========================================================
    facultad_formacion = request.GET.get("facultad_formacion")
    año_formacion_fac = request.GET.get("año_formacion_fac")
    momento_formacion_fac = request.GET.get("momento_formacion_fac")

    # Base: docentes aprobados
    qs_formacion_fac = FormacionDocente.objects.filter(aprobado=True)

    # 🔹 Filtrar por facultad → solo docentes de esa facultad
    if facultad_formacion:
        qs_formacion_fac = qs_formacion_fac.filter(
            id_usuario__id_programa__id_facultad=facultad_formacion
        )

    # 🔹 Filtrar por año
    if año_formacion_fac:
        qs_formacion_fac = qs_formacion_fac.filter(
            id_formacion__fecha_de_inicio__year=año_formacion_fac
        )

    # 🔹 Filtrar por momento
    if momento_formacion_fac and momento_formacion_fac in MAPA_MOMENTOS:
        qs_formacion_fac = qs_formacion_fac.filter(
            id_formacion__momento=MAPA_MOMENTOS[momento_formacion_fac]
        )

    # Agrupar por formación
    formaciones_fac_data = (
        qs_formacion_fac.values("id_formacion__formacion")
        .annotate(total=Count("id_usuario", distinct=True))
        .order_by("-total")
    )

    chart_labels_formacion_fac = [
        f["id_formacion__formacion"] or "Sin nombre" for f in formaciones_fac_data
    ]
    chart_values_formacion_fac = [f["total"] for f in formaciones_fac_data]
    total_aprobados_formacion_fac = sum(chart_values_formacion_fac)






     

    # ==========================================================
    # Contexto final
    # ==========================================================
    context = {
        "periodo": periodo_actual,

        # Gráfico 1
        "chart_labels_formacion": json.dumps(chart_labels_formacion),
        "chart_values_formacion": json.dumps(chart_values_formacion),
        "total_aprobados_formacion": total_aprobados_formacion,

        # Gráfico 2
        "chart_labels_formacion_hist": json.dumps(chart_labels_formacion_hist),
        "chart_values_formacion_hist": json.dumps(chart_values_formacion_hist),
        "total_aprobados_formacion_hist": total_aprobados_formacion_hist,
        "años_opciones": años_opciones,
        "opciones_filtro": opciones_filtro,
        "año_filtro": año_filtro,
        "opcion_filtro": opcion_filtro,

        # Gráfico 3
        "programas": programas,
        "programa_id": int(programa_id) if programa_id else None,
        "chart_labels_area": json.dumps(chart_labels_area),
        "chart_values_area": json.dumps(chart_values_area),
        "total_aprobados_area": total_aprobados_area,
        "año_area": año_area,
        "momento_area": momento_area,

        # Gráfico 4
        "programa_formacion_id": int(programa_formacion_id) if programa_formacion_id else None,
        "chart_labels_formacion_filtro": json.dumps(chart_labels_formacion_filtro),
        "chart_values_formacion_filtro": json.dumps(chart_values_formacion_filtro),
        "total_aprobados_formacion_filtro": total_aprobados_formacion_filtro,
        "año_formacion": año_formacion,
        "momento_formacion": momento_formacion,

        # Gráfico 5
        "facultades": facultades,
        "facultad_id": facultad_id,
        "año_facultad": año_facultad,
        "momento_facultad": momento_facultad,
        "chart_labels_facultad": json.dumps(chart_labels_facultad),
        "chart_values_facultad": json.dumps(chart_values_facultad),

        # Gráfico 6
         "chart_labels_area_fac": json.dumps(chart_labels_area_fac),
        "chart_values_area_fac": json.dumps(chart_values_area_fac),
        "total_aprobados_area_fac": total_aprobados_area_fac,
        "facultad_area": facultad_filtro,
        "año_area_fac": año_area_fac,
        "momento_area_fac": momento_area_fac,
        "facultades": facultades,  # Para el select de facultades
        # Gráfico 7
        "chart_labels_programa_fac": json.dumps(chart_labels_programa_fac),
        "chart_values_programa_fac": json.dumps(chart_values_programa_fac),
        "total_aprobados_programa_fac": total_aprobados_programa_fac,
        "facultad_programa": facultad_programa,
        "año_programa_fac": año_programa_fac,
        "momento_programa_fac": momento_programa_fac,

        # Gráfico 8
        "chart_labels_formacion_fac": json.dumps(chart_labels_formacion_fac),
        "chart_values_formacion_fac": json.dumps(chart_values_formacion_fac),
        "total_aprobados_formacion_fac": total_aprobados_formacion_fac,
        "facultad_formacion": facultad_formacion,
        "año_formacion_fac": año_formacion_fac,
        "momento_formacion_fac": momento_formacion_fac,
        "facultades": facultades,  # Para el select de facultades




    }

    return render(request, "dashboard.html", context)














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
