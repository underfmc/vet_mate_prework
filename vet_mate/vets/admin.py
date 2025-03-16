from django.contrib import admin
from .models import Veterinarian, VetVisit, Clinic


admin.site.register(Veterinarian)
admin.site.register(VetVisit)
admin.site.register(Clinic)
