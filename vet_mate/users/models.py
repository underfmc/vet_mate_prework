from core.validators import (validate_name_or_country_city,
                             validate_email,
                             validate_phone_number)
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.shortcuts import get_object_or_404


class MyUser(AbstractUser):
    CHOICES = (('Мужской', 'Мужской'), ('Женский', 'Женский'))
    last_name = models.CharField(max_length=100, verbose_name='Фамилия',
                                 validators=[validate_name_or_country_city])
    first_name = models.CharField(max_length=100, verbose_name='Имя',
                                  validators=[validate_name_or_country_city])
    middle_name = models.CharField(max_length=100, verbose_name='Отчество',
                                   blank=True,
                                   validators=[validate_name_or_country_city],
                                   default='Не указано')
    birth_date = models.DateField(verbose_name='Дата рождения', blank=True,
                                  null=True)
    gender = models.CharField(max_length=7, verbose_name='Пол',
                              choices=CHOICES, default='Мужской')
    email = models.EmailField(verbose_name='Почта',
                              validators=[validate_email],
                              unique=True)
    phone_number = models.CharField(max_length=20,
                                    verbose_name='Номер телефона',
                                    validators=[validate_phone_number],
                                    unique=True)
    country = models.CharField(max_length=100, verbose_name='Страна',
                               validators=[validate_name_or_country_city])
    city = models.CharField(max_length=100, verbose_name='Город',
                            validators=[validate_name_or_country_city])
    bio = models.TextField('О себе', blank=True)
    photo = models.ImageField(upload_to='users/', verbose_name='Фото',
                              blank=True, default='cat_profile.webp')

    def get_object(self, queryset=None):
        if self.kwargs.get('pk'):
            return get_object_or_404(MyUser, pk=self.kwargs['pk'])
        elif self.kwargs.get('slug'):
            return get_object_or_404(MyUser, username=self.kwargs['slug'])
