"""
URL configuration for proyecto1 project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from . import views
urlpatterns = [
    path('', views.login_view, name='login'),   # ⬅️ ahora la raíz muestra el login
    path('index/', views.index, name='index'),  # ⬅️ dashboard lo pones en /index/
    path('logout/', views.logout_view, name='logout'),
    path("mis-formaciones/", views.mis_formaciones, name="mis_formaciones"),
    path('historial/', views.historial_docente, name='historial_docente'),
    path('oferta/', views.oferta_formacion, name='oferta_formacion'),
    # 1️⃣  Ruta del panel de administración
    
    path('admin/', admin.site.urls),
      # aquí le pones el nombre 'dashboard'
    # 2️⃣  (Opcional) rutas de tu app principal
    # path('', include('adminproyecto1.urls')),
]

# 3️⃣  Solo para DESARROLLO: servir archivos MEDIA y STATIC
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)