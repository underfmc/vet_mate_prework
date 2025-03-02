from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import MyUser

UserAdmin.readonly_fields += ('birth_date',)
UserAdmin.fieldsets += (
    ('Extra Fields', {'fields': ('middle_name',
                                 'phone_number', 'country', 'city',
                                 'bio', 'photo')}),
)
admin.site.register(MyUser, UserAdmin)
