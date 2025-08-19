from django.shortcuts import render

def saludo(request):
    nombre = "juan"
    apellido = "lopez"
    tema = ["plantillas", "modelos", "vistas", "formulario"]

    return render(request, "index.html", {
        "nombre_persona": nombre,
        "apellido_persona": apellido,
        "tema": tema
    })
