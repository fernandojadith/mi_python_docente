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
from adminproyecto1 import views  # importa tus vistas
urlpatterns = [
   
    # 1️⃣  Ruta del panel de administración
    path('admin/', admin.site.urls),
    path('', include('adminproyecto1.urls')),  # 👉 conecta tu plantilla
    path("dashboard/", views.dashboard, name="admin-dashboard"),  # 👈 mismo name
    
    # path('', include('adminproyecto1.urls')),
]

# 3️⃣  Solo para DESARROLLO: servir archivos MEDIA y STATIC
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)