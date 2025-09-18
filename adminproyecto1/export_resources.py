from import_export import resources, fields
from import_export.widgets import ForeignKeyWidget, BooleanWidget
from import_export.results import RowResult
from .models import Usuario, Formacion, FormacionDocente, Programa
from .models import Usuario, Rol, Programa

# 👇 Widget booleano flexible (acepta 1/0, Sí/No, True/False)
class FlexibleBooleanWidget(BooleanWidget):
    def clean(self, value, row=None, *args, **kwargs):
        if value in [True, "True", "true", "1", 1, "SI", "Si", "sí", "si", "aprobado", "Aprobado"]:
            return True
        if value in [False, "False", "false", "0", 0, "NO", "No", "no", "no aprobado", "No Aprobado"]:
            return False
        return super().clean(value, row=row, *args, **kwargs)

    def render(self, value, obj=None, *args, **kwargs):  
        if value in [True, 1]:
            return "Aprobado"
        if value in [False, 0]:
            return "No Aprobado"
        return ""



from import_export import resources, fields
from import_export.widgets import ForeignKeyWidget
from .models import Usuario, Rol, Programa


from import_export import resources, fields
from import_export.widgets import ForeignKeyWidget
from .models import Usuario, Programa, Rol


class CaseInsensitiveFKWidget(ForeignKeyWidget):
    def clean(self, value, row=None, *args, **kwargs):
        if value:
            return self.get_queryset(value, row, *args, **kwargs).get(
                **{f"{self.field}__iexact": value.strip()}
            )
        return None


class UsuarioResource(resources.ModelResource):
    # ✅ Nombre del Rol en vez de ID (con widget tolerante)
    nombre_rol = fields.Field(
        attribute="id_rol",
        column_name="Rol",
        widget=CaseInsensitiveFKWidget(Rol, "tipos_de_rol")
    )

    # ✅ Nombre del Programa en vez de ID
    nombre_programa = fields.Field(
        attribute="id_programa",
        column_name="Programa",
        widget=CaseInsensitiveFKWidget(Programa, "Programa")
    )

    class Meta:
        model = Usuario
        import_id_fields = ["id_usuario"]
        fields = (
            "id_usuario",
            "nombre",
            "fecha_de_nacimiento",
            "telefono",
            "tipo_de_documento",
            "numero_de_documento",
            "lugar_de_residencia",
            "nombre_programa",
            "titulo_de_pregrado",
            "titulo_de_nivel_maximo",
            "tipo_de_vinculo",
            "fecha_de_ingreso",
            "nombre_rol",
        )
        export_order = fields

    # 👇 Este método se ejecuta al exportar para obtener el valor de facultad
    def dehydrate_facultad(self, obj):
        return obj.id_programa.id_facultad.facultad if obj.id_programa and obj.id_programa.id_facultad else ""



class FormacionDocenteResource(resources.ModelResource):
    nombre_usuario = fields.Field(
        attribute='id_usuario',
        column_name='Nombre del Usuario',
        widget=ForeignKeyWidget(Usuario, 'nombre')
    )

    nombre_formacion = fields.Field(
        attribute='id_formacion',
        column_name='Nombre de la Formación',
        widget=ForeignKeyWidget(Formacion, 'formacion')
    )

    nombre_programa = fields.Field(
        attribute='id_programa',
        column_name='Programa',
        widget=ForeignKeyWidget(Programa, 'Programa')
    )

    aprobado = fields.Field(
        attribute='aprobado',
        column_name='aprobado',
        widget=FlexibleBooleanWidget()
    )

    # ✅ Campo calculado: Periodo
    periodo = fields.Field(
        column_name="Periodo"
    )

    class Meta:
        model = FormacionDocente
        import_id_fields = ('serial',)  # usamos serial como identificador único
        skip_unchanged = True
        report_skipped = True
        fields = (
            'id_formaciondocente',
            'serial',
            'nombre_usuario',
            'nombre_formacion',
            'nombre_programa',
            'estado',
            'observacion',
            'aprobado',
            'fecha_aprobacion',
            "evaluacion_de_conocimiento",
            "nivel_de_satisfaccion",
            "desempeño_laboral",
            "efectividad",
            'pdf_certificado',
            'periodo',  # 👈 agregado
        )
        export_order = fields
        def dehydrate_efectividad(self, obj):
            return obj.efectividad
    # ✅ Sobrescribimos get_instance para actualizar si serial existe
    def get_instance(self, instance_loader, row):
        serial = row.get('serial')
        if serial:
            try:
                return FormacionDocente.objects.get(serial=serial)
            except FormacionDocente.DoesNotExist:
                return None
        return None

    # ✅ Evita duplicados de usuario + formación + programa
    def skip_row(self, instance, original, row, import_validation_errors=None):
        usuario_nombre = row.get("Nombre del Usuario")
        formacion_nombre = row.get("Nombre de la Formación")
        programa_nombre = row.get("Programa")
        serial = row.get("serial")

        usuario = Usuario.objects.filter(nombre=usuario_nombre).first()
        formacion = Formacion.objects.filter(formacion=formacion_nombre).first()
        programa = Programa.objects.filter(Programa=programa_nombre).first()

        if usuario and formacion and programa:
            existe = FormacionDocente.objects.filter(
                id_usuario=usuario,
                id_formacion=formacion,
                id_programa=programa
            ).exclude(serial=serial).exists()
            if existe:
                return True  # Saltar fila si hay duplicado

        return False

    def get_skip_row_result(self, row, import_validation_errors=None):
        return RowResult.IMPORT_TYPE_SKIP, ["Ya existe registro con mismo usuario, formación y periodo."]

    # ✅ Método para calcular el periodo (igual que en el admin)
    def dehydrate_periodo(self, obj):
        if obj.id_formacion and obj.id_formacion.fecha_fin:
            fecha = obj.id_formacion.fecha_fin
            return f"{fecha.year}-1" if fecha.month < 8 else f"{fecha.year}-2"
        return "Sin fecha"
