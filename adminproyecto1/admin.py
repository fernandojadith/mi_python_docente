from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.contrib.admin.models import LogEntry
from import_export.admin import ImportExportModelAdmin 
from .export_resources import UsuarioResource
from .export_resources import FormacionDocenteResource 
from django.contrib.admin import SimpleListFilter
import datetime
from .forms import FormacionAdminForm, FormacionDocenteAdminForm
from .models import Entidad, Formacion, FormacionDocente, Modalidad, Rol, TipoFormacion, Usuario




@admin.register(LogEntry)
class LogEntryAdmin(admin.ModelAdmin):
    list_display = ['user', 'action_time', 'content_type', 'object_repr', 'action_flag']
    readonly_fields = [f.name for f in LogEntry._meta.fields]
    search_fields = ['object_repr', 'change_message']
    list_filter = ['action_flag', 'content_type']
    
class modalidadAdmin(admin.ModelAdmin):
    list_display = ("modalidad", "descripcion")
   #tabla usuario -------------------------------------------------------------------------------------------------- 
@admin.register(Usuario)
class usuarioAdmin(ImportExportModelAdmin):
    resource_class = UsuarioResource
    list_display = (
        "id_usuario",
        "nombre",
        "fecha_de_nacimiento",
        "telefono",
        "numero_de_documento",
        "lugar_de_residencia",
        "titulo_de_pregrado",
        "titulo_de_nivel_maximo",
        "tipo_de_vinculo",
        "fecha_de_ingreso",
        "id_rol",
        "editar_link",  # Columna con el botón de editar
    )
    list_display_links = None  # Desactiva el enlace predeterminado para que el botón sea el principal
    search_fields = ("nombre", "numero_de_documento",) # Habilita la búsqueda por estos campos

    def editar_link(self, obj):
        # Genera la URL para la página de edición de un objeto Usuario
        url = reverse('admin:adminproyecto1_usuario_change', args=[obj.pk])
        return format_html('<a class="button" href="{}">Editar</a>', url)

    editar_link.short_description = 'Acciones' # Encabezado de la columna en el Admin
    editar_link.allow_tags = True # Permite que Django renderice HTML en esta columna
    from django.contrib.admin import SimpleListFilter
import datetime

class PeriodoFilter(SimpleListFilter):
    title = 'Periodo'
    parameter_name = 'periodo'

    def lookups(self, request, model_admin):
        años = (
            Formacion.objects
            .filter(fecha_fin__isnull=False)
            .dates('fecha_fin', 'year')
            .distinct()
        )
        opciones = []
        for año in años:
            opciones.append((f'1-{año.year}', f'1 - {año.year}'))
            opciones.append((f'2-{año.year}', f'2 - {año.year}'))
        return opciones

    def queryset(self, request, queryset):
        value = self.value()
        if value:
            try:
                semestre, año = value.split('-')
                año = int(año)
                if semestre == '1':
                    inicio = datetime.date(año, 1, 1)
                    fin = datetime.date(año, 7, 31)
                elif semestre == '2':
                    inicio = datetime.date(año, 8, 1)
                    fin = datetime.date(año, 12, 31)
                else:
                    return queryset.none()
                return queryset.filter(id_formacion__fecha_fin__range=(inicio, fin))
            except:
                return queryset.none()
        return queryset

#tabla formaciondocente ---------------------------------------------------------------------------------------------------------------

@admin.register(FormacionDocente)
class formaciondocenteAdmin(ImportExportModelAdmin):
    form = FormacionDocenteAdminForm
    resource_class = FormacionDocenteResource
  
    list_filter = ['id_formacion', PeriodoFilter]
    list_display = (
        'id_formaciondocente',
        'get_usuario_nombre',
        'get_formacion_nombre',
        'estado',
        'aprobado',
        'fecha_aprobacion',
        'periodo',
        'editar_formaciondocente_link',
        'pdf_certificado',
    )
    list_display_links = None

    # 🔍 Buscador: campos reales + ID exacto
    search_fields = (
        'estado',
        'observacion',
        'id_usuario__nombre',
        'id_formacion__formacion',  # nombre real del curso
        'pdf_certificado',
    )

    def get_search_results(self, request, queryset, search_term):
        # Primero busca normalmente
        queryset, use_distinct = super().get_search_results(request, queryset, search_term)
        # Si el término es numérico, buscar exacto por ID
        if search_term.isdigit():
            queryset |= self.model.objects.filter(id_formaciondocente=int(search_term))
        return queryset, use_distinct

    def get_usuario_nombre(self, obj):
        return obj.id_usuario.nombre if obj.id_usuario else "N/A"
    get_usuario_nombre.short_description = 'Nombre de Usuario'
    get_usuario_nombre.admin_order_field = 'id_usuario__nombre'

    def get_formacion_nombre(self, obj):
        return obj.id_formacion.formacion if obj.id_formacion else "N/A"
    get_formacion_nombre.short_description = 'Nombre de Formación'
    get_formacion_nombre.admin_order_field = 'id_formacion__formacion'

    def editar_formaciondocente_link(self, obj):
        url = reverse('admin:adminproyecto1_formaciondocente_change', args=[obj.pk])
        return format_html('<a class="button" href="{}">Editar</a>', url)
    editar_formaciondocente_link.short_description = 'Acciones'
    editar_formaciondocente_link.allow_tags = True

    def periodo(self, obj):
        if obj.id_formacion and obj.id_formacion.fecha_fin:
            fecha = obj.id_formacion.fecha_fin
            return f"{fecha.year}-1" if fecha.month < 8 else f"{fecha.year}-2"
        return "Sin fecha"
    periodo.short_description = 'Periodo'

#tabla formacion ------------------------------------------------------------------------------------------------------------

class formacionAdmin(admin.ModelAdmin):
    form = FormacionAdminForm

    list_display = (
        "id_formacion", 
        "formacion", 
        "descripcion", 
        "fecha_de_inicio", 
        "fecha_fin", 
        "mostrar_modalidad", 
        "mostrar_entidad", 
        "mostrar_tipo_formacion", 
        "mostrar_usuario",  # Docente
        "editar_link",
    )

    list_display_links = None

    def mostrar_modalidad(self, obj):
        return obj.id_modalidad
    mostrar_modalidad.short_description = "Modalidad"

    def mostrar_entidad(self, obj):
        return obj.id_entidad
    mostrar_entidad.short_description = "Entidad"

    def mostrar_tipo_formacion(self, obj):
        return obj.id_tipo_formacion
    mostrar_tipo_formacion.short_description = "Tipo de Formación"

    def mostrar_usuario(self, obj):
        return obj.id_usuario
    mostrar_usuario.short_description = "Docente"

    def editar_link(self, obj):
        url = reverse("admin:adminproyecto1_formacion_change", args=[obj.pk])
        return format_html(f'<a class="button" href="{url}">Editar</a>')
    editar_link.short_description = "Editar"

#tabla entidad ------------------------------------------------------------------------------------------------------------

class entidadAdmin(admin.ModelAdmin):
      list_display = ("nombre", "tipo_de_entidad", "pais", "ciudad", "telefono", "correo",)
      
#tabla rol -------------------------------------------------------------------------------------------------------------------
            
class roldadAdmin(admin.ModelAdmin):       
    list_display = ("id_rol","tipos_de_rol",)   
    
#tabla modalidad -------------------------------------------------------------------------------------------------------------------

class modalidadAdmin(admin.ModelAdmin):     
    list_display = ("id_modalidad","modalidad","descripcion",)     
    
    
class TipoFormacionAdmin(admin.ModelAdmin):  
    list_display = ("id_tipo_formacion","formaciones",)      
# Registra los modelos con sus clases Admin personalizadas.
# Los modelos registrados con @admin.register (como Usuario y FormacionDocente)
# NO necesitan un admin.site.register() aquí.
admin.site.register(Entidad, entidadAdmin)
admin.site.register(Formacion, formacionAdmin)
admin.site.register(Modalidad, modalidadAdmin)
admin.site.register(Rol,roldadAdmin) # Asumo que Rol no necesita una clase Admin personalizada por ahora
admin.site.register(TipoFormacion,TipoFormacionAdmin) # Asumo que TipoFormacion tampoco necesita una clase Admin personalizada por ahora
      
# para cambiar el nombre del panel de django
admin.site.site_header = "ADMIN "
admin.site.site_title = "CENAPED Admin"
admin.site.index_title = "Panel de Administración  CENAPED"
