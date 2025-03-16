from django import forms

from .models import Veterinarian, VetVisit


class VeterinarianForm(forms.ModelForm):
    class Meta:
        model = Veterinarian
        fields = '__all__'


class VetVisitForm(forms.ModelForm):
    class Meta:
        model = VetVisit
        fields = ['pet', 'veterinarian', 'date', 'reason']
        exclude = ('user', 'is_active')
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'})
        }
