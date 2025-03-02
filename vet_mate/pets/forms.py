from django import forms

from .models import (Breed, Pet, Vaccination,
                     FeedingSchedule, HealthAnalysis)


class PetForm(forms.ModelForm):
    class Meta:
        model = Pet
        fields = '__all__'
        exclude = ('slug', 'user', 'food')
        widgets = {
            'birth_date': forms.DateInput(attrs={'type': 'date'})
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['breed'].queryset = Breed.objects.none()

        if 'species' in self.data:
            try:
                animal_type_id = int(self.data.get('species'))
                self.fields['breed'].queryset = Breed.objects.filter(
                    animal_type_id=animal_type_id).order_by('name')
            except (ValueError, TypeError):
                pass
        elif self.instance.pk:
            self.fields[
                'breed'
                ].queryset = self.instance.species.breed.order_by('name')


class VaccinationForm(forms.ModelForm):
    class Meta:
        model = Vaccination
        fields = '__all__'


class FeedingScheduleForm(forms.ModelForm):
    class Meta:
        model = FeedingSchedule
        fields = '__all__'


class HealthAnalysisForm(forms.ModelForm):
    class Meta:
        model = HealthAnalysis
        fields = '__all__'
