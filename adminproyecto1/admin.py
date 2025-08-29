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
from .models import Programa, Facultad,Areas
from django.contrib import admin, messages
from django.db.models import ProtectedError
from django.urls import reverse
from django.utils.html import format_html
from import_export.admin import ImportExportModelAdmin
from .models import Usuario, Formacion



@admin.register(Areas)
class AreasAdmin(admin.ModelAdmin):
    list_display = ('id_areas', 'areas')


@admin.register(Programa)
class ProgramaAdmin(admin.ModelAdmin):
    list_display = ('id_programa', 'Programa', 'id_facultad')  # columnas visibles en el panel

@admin.register(Facultad)
class FacultadAdmin(admin.ModelAdmin):
    list_display = ('id_facultad', 'facultad')  # cambia según tu modelo

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
    """
    Clase de administración para el modelo Usuario en el panel de Django Admin.
    Permite importar/exportar datos y personalizar la interfaz de gestión.
    """
    resource_class = UsuarioResource
    list_display = (
        "id_usuario",
        "nombre",
        "numero_de_documento",
        "telefono",
        "facultad",
        "id_programa",
        "fecha_de_nacimiento",
        "lugar_de_residencia",
        "titulo_de_pregrado",
        "titulo_de_nivel_maximo",
        "tipo_de_vinculo",
        "fecha_de_ingreso",
        "id_rol",
        "editar_link",
    )
    list_per_page = 10
    list_display_links = None
    list_max_show_all = 0
    search_fields = ("nombre", "numero_de_documento", "id_programa__Programa", "id_programa__id_facultad__facultad",)

    def facultad(self, obj):
        """
        Muestra la facultad del usuario a través de su programa.
        """
        return obj.id_programa.id_facultad.facultad if obj.id_programa and obj.id_programa.id_facultad else None
    facultad.admin_order_field = 'id_programa__id_facultad'
    facultad.short_description = 'Facultad'

    def editar_link(self, obj):
        """
        Crea un botón de "Editar" que redirige a la página de cambio de objeto.
        """
        url = reverse('admin:adminproyecto1_usuario_change', args=[obj.pk])
        return format_html('<a class="button" href="{}">Editar</a>', url)
    
    editar_link.short_description = 'Acciones'
    editar_link.allow_tags = True
    
    def delete_model(self, request, obj):
        """
        Sobreescribe el método para manejar la eliminación de un solo objeto.
        Evita la eliminación si el usuario tiene formaciones asociadas.
        """
        if obj.formacion_set.exists():
            mensaje = f"No se puede eliminar el usuario '{obj.nombre}' porque tiene formaciones asociadas."
            self.message_user(request, mensaje, level=messages.ERROR)
            return
        
        try:
            obj.delete()
            mensaje = f"El usuario '{obj.nombre}' se ha eliminado correctamente."
            self.message_user(request, mensaje, level=messages.SUCCESS)
        except ProtectedError as e:
            error_message = f"No se pudo eliminar el usuario '{obj.nombre}'. Error: {e}"
            self.message_user(request, error_message, level=messages.ERROR)

    def delete_queryset(self, request, queryset):
        """
        Sobreescribe el método para manejar la eliminación masiva (acciones de la lista).
        Filtra los usuarios que no se pueden eliminar y muestra un mensaje de error.
        """
        undeletable_users = []
        deletable_users = []
        
        for user in queryset:
            # Revisa si el usuario tiene formaciones asociadas.
            # 'formacion_set' es el nombre por defecto del ManyToManyField inverso
            # o de la relación ForeignKey en el modelo Formacion.
            if user.formacion_set.exists():
                undeletable_users.append(user.nombre)
            else:
                deletable_users.append(user)

        if undeletable_users:
            names = ', '.join(undeletable_users)
            self.message_user(
                request, 
                f"No se pudieron eliminar los siguientes usuarios porque tienen formaciones asociadas: {names}", 
                level=messages.ERROR
            )

        if deletable_users:
            try:
                # Si hay usuarios que se pueden eliminar, se realiza la acción.
                super().delete_queryset(request, Usuario.objects.filter(pk__in=[u.pk for u in deletable_users]))
                self.message_user(
                    request,
                    f"Se eliminaron {len(deletable_users)} usuarios correctamente.",
                    level=messages.SUCCESS
                )
            except ProtectedError as e:
                # Este try-except es una salvaguarda adicional.
                error_message = f"Ocurrió un error al intentar eliminar algunos usuarios. Detalles: {e}"
                self.message_user(request, error_message, level=messages.ERROR)


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
            opciones.append((f'1-{año.year}', f'{año.year}-1'))
            opciones.append((f'2-{año.year}', f'{año.year}-2'))
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
  
    list_filter = ['id_formacion', PeriodoFilter, 'estado',]
    list_display = (
        'id_formaciondocente',
        'serial',
        'id_programa',
        'get_usuario_nombre',
        'get_formacion_nombre',
        'estado',
        'aprobado',
        'fecha_aprobacion',
        "evaluacion_de_conocimiento",
        "nivel_de_satisfaccion",
        "desempeño_laboral",
        "efectividad",
        "get_momento",
        'periodo',
        'editar_formaciondocente_link',
        'pdf_certificado',
    )
    list_per_page = 5
    list_display_links = None
    list_max_show_all = 0  # 👈 quita el botón "Mostrar todo"
    # 🔍 Buscador: campos reales + ID exacto
    search_fields = (
        'serial',
        'estado',
        'observacion',
        'id_usuario__nombre',
        'id_programa__Programa',
        'id_formacion__formacion',  # nombre real del curso
        'pdf_certificado',
    )
    
    def evaluacion_conocimiento_format(self, obj):
        return f"{obj.evaluacion_de_conocimiento:.1f}" if obj.evaluacion_de_conocimiento is not None else "-"
    evaluacion_conocimiento_format.short_description = "Evaluación Conocimiento"

    def nivel_satisfaccion_format(self, obj):
        return f"{obj.nivel_de_satisfaccion:.1f}" if obj.nivel_de_satisfaccion is not None else "-"
    nivel_satisfaccion_format.short_description = "Nivel Satisfacción"

    def desempeno_laboral_format(self, obj):
        return f"{obj.desempeño_laboral:.1f}" if obj.desempeño_laboral is not None else "-"
    desempeno_laboral_format.short_description = "Desempeño Laboral"

    def efectividad(self, obj):
        return obj.efectividad
    efectividad.short_description = "efectividadd"

    def get_momento(self, obj):
        return obj.id_formacion.momento
    get_momento.short_description = "Momento"



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
    
#tabla formacion ------------------------------------------------------------------------------------------------------------

class formacionAdmin(admin.ModelAdmin):
    form = FormacionAdminForm

    list_display = (
        "id_formacion", 
        "formacion", 
        "descripcion", 
        "fecha_de_inicio", 
        "fecha_fin",
        "momento",
        "mostrar_modalidad", 
        "mostrar_entidad", 
        "mostrar_tipo_formacion", 
        "mostrar_usuario", 
        "num_aprobados",# Docente
        "editar_link",
    )

    list_display_links = None
   

     # método para contar los aprobados de cada formación
    def num_aprobados(self, obj):
        return FormacionDocente.objects.filter(
            id_formacion=obj,
            aprobado=True
        ).count()
    num_aprobados.short_description = "Aprobados"



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
