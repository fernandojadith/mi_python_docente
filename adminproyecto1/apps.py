# adminproyecto1/apps.py
from django.apps import AppConfig

class Adminproyecto1Config(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'adminproyecto1'

    def ready(self):
        import adminproyecto1.signals  # ← Asegúrate de importar aquí
