from django.urls import path
from . import views

urlpatterns = [
    
    path('certificado_entidad/<int:id_entidad>/', views.generar_certificado, name='certificado_entidad'),
    path('certificado_formacion/<int:id_formacion_docente>/', views.generar_certificado_pdf, name='certificado_formacion'),
]
