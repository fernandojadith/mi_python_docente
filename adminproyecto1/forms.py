from django import forms
from .models import Formacion, Usuario, FormacionDocente

class FormacionDocenteAdminForm(forms.ModelForm):
    class Meta:
        model = FormacionDocente
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(FormacionDocenteAdminForm, self).__init__(*args, **kwargs)
        self.fields['id_usuario'].queryset = Usuario.objects.filter(id_rol=1)


class FormacionAdminForm(forms.ModelForm):
    class Meta:
        model = Formacion
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(FormacionAdminForm, self).__init__(*args, **kwargs)
        self.fields['id_usuario'].queryset = Usuario.objects.filter(id_rol=2)
