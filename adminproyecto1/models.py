# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models
from datetime import date

class Entidad(models.Model):
    id_entidad = models.BigIntegerField(primary_key=True)
    nombre = models.TextField(blank=True, null=True)
    tipo_de_entidad = models.CharField(blank=True, null=True)
    pais = models.CharField(blank=True, null=True)
    ciudad = models.CharField(blank=True, null=True)
    telefono = models.BigIntegerField(blank=True, null=True)
    correo = models.CharField(blank=True, null=True)

    def __str__(self): 
     return self.nombre  
 

    class Meta:
        db_table = 'entidad'


class Areas(models.Model):
    id_areas = models.BigAutoField(db_column='id_areas', primary_key=True)
    areas = models.CharField(max_length=200, blank=True, null=True)

    def __str__(self):
        return self.areas



    class Meta:
        db_table = "Areas"


class Formacion(models.Model):
    id_formacion = models.BigIntegerField(primary_key=True)
    id_areas = models.ForeignKey(Areas,on_delete=models.CASCADE,db_column='id_areas',related_name='formacion',blank=True, null=True)
    MOMENTO_CHOICES = [
        ("semestre", "Semestre"),
        ("intersemestral", "Intersemestral"),
    ]
   
    formacion = models.TextField(blank=True, null=True)
    descripcion = models.TextField(blank=True, null=True)
    fecha_de_inicio = models.DateField(blank=True, null=True)
    fecha_fin = models.DateField(blank=True, null=True)
    momento = models.CharField(
        max_length=20,
        choices=MOMENTO_CHOICES,
        default="semestre"
    )
    
    id_modalidad = models.ForeignKey('Modalidad', models.DO_NOTHING, db_column='id_modalidad', blank=True, null=True)
    id_entidad = models.ForeignKey('Entidad', models.DO_NOTHING, db_column='id_entidad', blank=True, null=True)
    id_tipo_formacion = models.ForeignKey('TipoFormacion', models.DO_NOTHING, db_column='id_tipo_formacion', blank=True, null=True)
    id_usuario = models.ForeignKey('Usuario', models.DO_NOTHING, db_column='id_usuario', blank=True, null=True)
    incertidumbre_horaria = models.CharField(max_length=100, blank=True, null=True)
    activo = models.BooleanField(default=True) # Nuevo campo para activar/desactivar la formación

    def __str__(self):
        return self.formacion

    @property
    def periodo(self):
        """
        Determina el periodo de la formación usando sus fechas de finalización y de inicio.
        """
        # Preferimos la fecha de fin para el cálculo del periodo
        ref_date = None
        if self.fecha_fin:
            ref_date = self.fecha_fin
        elif self.fecha_de_inicio:
            ref_date = self.fecha_de_inicio

        if ref_date is None:
            return "Sin periodo"

        inicio_p2 = date(ref_date.year, 7, 22)

        if ref_date < inicio_p2:
            return f"{ref_date.year}-1"
        else:
            return f"{ref_date.year}-2"

    class Meta:
        db_table = 'formacion'

        
class FormacionDocente(models.Model):
    id_formaciondocente = models.BigAutoField(db_column='id_FormacionDocente', primary_key=True)
    serial = models.CharField(max_length=50, unique=True)

    

    ESTADOS = [
        ("cursando", "Cursando"),
        ("finalizado", "Finalizado"),
       
    ]

    id_usuario = models.ForeignKey('Usuario', models.DO_NOTHING, db_column='id_usuario', blank=True, null=True)
    id_programa = models.ForeignKey('Programa', models.DO_NOTHING, db_column='id_programa', blank=True, null=True)
    estado = models.CharField(max_length=30, choices=ESTADOS, default="cursando")
    observacion = models.CharField(max_length=200, blank=True, null=True)
    id_formacion = models.ForeignKey('Formacion', models.DO_NOTHING, db_column='id_formacion', blank=True, null=True)
    aprobado = models.BooleanField(default=False)
    evaluacion_de_conocimiento = models.DecimalField(max_digits=5, decimal_places=1, null=True, blank=True)
    nivel_de_satisfaccion = models.DecimalField(max_digits=5, decimal_places=1, null=True, blank=True)
    desempeño_laboral = models.DecimalField(max_digits=5, decimal_places=1, null=True, blank=True)
    fecha_aprobacion = models.DateField(blank=True, null=True)
    pdf_certificado = models.FileField(upload_to='certificados/', blank=True, null=True)

    @property
    def efectividad(self):
        if (
            self.evaluacion_de_conocimiento is not None and
            self.nivel_de_satisfaccion is not None and
            self.desempeño_laboral is not None
    ):
            promedio = (self.evaluacion_de_conocimiento + self.nivel_de_satisfaccion + self.desempeño_laboral) / 3
            return f"{promedio:.1f}"  # 🔹 siempre 1 decimal
        return None
    def __str__(self):
        return f"{self.id_formaciondocente} - {self.id_usuario}"

class Modalidad(models.Model):
    id_modalidad = models.BigIntegerField(primary_key=True)
    modalidad = models.CharField(blank=True, null=True)
    descripcion = models.CharField(blank=True, null=True)

    def __str__(self):
     return self.modalidad 


    class Meta:
        db_table = 'modalidad'


class Rol(models.Model):
    id_rol = models.BigIntegerField(primary_key=True)
    tipos_de_rol = models.CharField(blank=True, null=True)

    def __str__(self):
     return self.tipos_de_rol  


    class Meta:
        db_table = 'rol'


class TipoFormacion(models.Model):
    id_tipo_formacion = models.BigIntegerField(primary_key=True)
    formaciones = models.CharField(blank=True, null=True)

    def __str__(self):
     return self.formaciones 


    class Meta:
        db_table = 'tipo_formacion'


class Facultad(models.Model):
    id_facultad = models.BigAutoField(db_column='id_facultad', primary_key=True)
    facultad = models.CharField(max_length=200, blank=True, null=True)




    def __str__(self):
     return self.facultad 
 

    class Meta:
        db_table = 'facultad'


class Programa(models.Model):
    id_programa = models.BigAutoField(db_column='id_programa', primary_key=True)
    Programa= models.CharField(max_length=200, blank=True, null=True)
    id_facultad = models.ForeignKey(Facultad,on_delete=models.CASCADE,db_column='id_facultad',related_name='programas',blank=True, null=True)




    def __str__(self):
     return self.Programa


    class Meta:
        db_table = 'programa'

class Usuario(models.Model):
    id_usuario = models.BigIntegerField(primary_key=True)
    nombre = models.TextField()
    fecha_de_nacimiento = models.DateField(blank=True, null=True)
    telefono = models.BigIntegerField(blank=True, null=True)
    tipo_de_documento = models.CharField(blank=True, null=True)
    numero_de_documento = models.BigIntegerField()
    lugar_de_residencia = models.CharField(blank=True, null=True)
    titulo_de_pregrado = models.CharField(blank=True, null=True)
    titulo_de_nivel_maximo = models.CharField(blank=True, null=True)
    tipo_de_vinculo = models.CharField(blank=True, null=True)
    fecha_de_ingreso = models.DateField(blank=True, null=True)
    id_rol = models.ForeignKey(Rol, models.DO_NOTHING, db_column='id_rol', blank=True, null=True)
    id_programa = models.ForeignKey(Programa, models.DO_NOTHING, db_column='id_PROGRAMA', blank=True, null=True)
    
    
    def __str__(self):
     return self.nombre  
 


    class Meta:
        db_table = 'usuario'



