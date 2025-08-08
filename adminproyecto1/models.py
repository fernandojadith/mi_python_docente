# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


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


class Formacion(models.Model):
    id_formacion = models.BigIntegerField(primary_key=True)
    formacion = models.TextField(blank=True, null=True)
    descripcion = models.TextField(blank=True, null=True)
    fecha_de_inicio = models.DateField(blank=True, null=True)
    fecha_fin = models.DateField(blank=True, null=True)
    id_modalidad = models.ForeignKey('Modalidad', models.DO_NOTHING, db_column='id_modalidad', blank=True, null=True)
    id_entidad = models.ForeignKey(Entidad, models.DO_NOTHING, db_column='id_entidad', blank=True, null=True)
    id_tipo_formacion = models.ForeignKey('TipoFormacion', models.DO_NOTHING, db_column='id_tipo_formacion', blank=True, null=True)
    id_usuario = models.ForeignKey('Usuario', models.DO_NOTHING, db_column='id_usuario', blank=True, null=True)
    incertidumbre_horaria = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
     return self.formacion  
 


    class Meta:
        db_table = 'formacion'


class FormacionDocente(models.Model):
    id_formaciondocente = models.BigIntegerField(db_column='id_FormacionDocente', primary_key=True)  # Field name made lowercase.
    id_usuario = models.ForeignKey('Usuario', models.DO_NOTHING, db_column='id_usuario', blank=True, null=True)
    estado = models.CharField(max_length=50, blank=True, null=True)
    observacion = models.CharField(max_length=200, blank=True, null=True)
    id_formacion = models.ForeignKey(Formacion, models.DO_NOTHING, db_column='id_formacion', blank=True, null=True)
    aprobado              = models.BooleanField(default=False)
    fecha_aprobacion      = models.DateField(blank=True, null=True)
    pdf_certificado = models.FileField(upload_to='certificados/', blank=True, null=True)


    class Meta:
        db_table = 'formacion_docente'


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

    def __str__(self):
     return self.nombre  
 


    class Meta:
        db_table = 'usuario'
