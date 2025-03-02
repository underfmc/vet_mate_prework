from django import forms

from .models import Veterinarian, VetVisit


class VeterinarianForm(forms.ModelForm):
    class Meta:
        model = Veterinarian
        fields = '__all__'


class VetVisitForm(forms.ModelForm):
    class Meta:
        model = VetVisit
        fields = '__all__'
