from import_export import resources, fields
from import_export.widgets import ForeignKeyWidget
from import_export.results import RowResult
from .models import Usuario, Formacion, FormacionDocente

class UsuarioResource(resources.ModelResource):
    class Meta:
        model = Usuario
        import_id_fields = ['id_usuario']
        fields = (
            'id_usuario', 'nombre', 'fecha_de_nacimiento', 'telefono',
            'tipo_de_documento', 'numero_de_documento', 'lugar_de_residencia',
            'titulo_de_pregrado', 'titulo_de_nivel_maximo',
            'tipo_de_vinculo', 'fecha_de_ingreso', 'id_rol',
        )

class FormacionDocenteResource(resources.ModelResource):
    nombre_usuario = fields.Field(
        attribute='id_usuario',
        column_name='Nombre del Usuario',
        widget=ForeignKeyWidget(Usuario, 'nombre')
    )
    nombre_formacion = fields.Field(
        attribute='id_formacion',
        column_name='Nombre del Curso',
        widget=ForeignKeyWidget(Formacion, 'formacion')  # CORREGIDO
    )

    class Meta:
        model = FormacionDocente
        import_id_fields = ('id_formaciondocente',)
        skip_unchanged = True
        report_skipped = True
        fields = (
            'id_formaciondocente',
            'id_usuario',
            'id_formacion',
            'nombre_usuario',
            'nombre_formacion',
            'estado',
            'certificado',
            'fecha',
            'periodo1',
            'periodo2',
        )

    def skip_row(self, instance, original, row, import_validation_errors=None):
        try:
            id_usuario = row.get('id_usuario')
            id_formacion = row.get('id_formacion')
            periodo = row.get('periodo1') or row.get('periodo2')

            if not (id_usuario and id_formacion and periodo):
                return False

            ya_existe = FormacionDocente.objects.filter(
                id_usuario=id_usuario,
                id_formacion=id_formacion
            ).filter(
                periodo1=periodo
            ).exists() or FormacionDocente.objects.filter(
                id_usuario=id_usuario,
                id_formacion=id_formacion
            ).filter(
                periodo2=periodo
            ).exists()

            return ya_existe

        except Exception:
            return False

    def get_skip_row_result(self, row, import_validation_errors=None):
        return RowResult.IMPORT_TYPE_SKIP, ["Ya existe una formación igual con el mismo usuario y periodo."]
