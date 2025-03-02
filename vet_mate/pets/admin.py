from django.contrib import admin
from .models import (PetSpecies, Breed, Pet, Vaccination,
                     FeedingSchedule, HealthAnalysis, Food,
                     Disease, Medicine, Vaccine, VaccinationSchedule)


admin.site.register(VaccinationSchedule)
admin.site.register(Vaccine)
admin.site.register(Disease)
admin.site.register(Medicine)
admin.site.register(Food)
admin.site.register(PetSpecies)
admin.site.register(Breed)
admin.site.register(Pet)
admin.site.register(Vaccination)
admin.site.register(FeedingSchedule)
admin.site.register(HealthAnalysis)
