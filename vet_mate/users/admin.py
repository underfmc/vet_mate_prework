from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import MyUser, Subscription

UserAdmin.readonly_fields += ('birth_date',)
UserAdmin.fieldsets += (
    ('Extra Fields', {'fields': ('middle_name',
                                 'phone_number', 'country', 'city',
                                 'bio', 'photo', 'subscription',
                                 'subscription_start_date')}),
)
admin.site.register(MyUser, UserAdmin)

admin.site.register(Subscription)
