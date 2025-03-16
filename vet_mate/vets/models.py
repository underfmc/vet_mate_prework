import datetime as dt
import requests
from django.contrib.auth import get_user_model
from django.db import models
from pets.models import Pet
from vet_mate.settings import YANDEX_API_KEY


User = get_user_model()


class Veterinarian(models.Model):
    name = models.CharField(max_length=100, verbose_name='Имя')
    latitude = models.FloatField(verbose_name='Широта', null=True, blank=True)
    longitude = models.FloatField(verbose_name='Долгота', null=True,
                                  blank=True)
    address = models.CharField(max_length=255, verbose_name='Адрес')
    photo = models.ImageField(upload_to='vets/veterinarians/photos/',
                              verbose_name='Фото', null=True, blank=True)
    contact_phone = models.CharField(max_length=20,
                                     verbose_name='Телефон для связи',
                                     null=True, blank=True)
    clinic = models.ForeignKey('Clinic', on_delete=models.SET_NULL, null=True,
                               blank=True, verbose_name='Клиника',
                               related_name='veterinarians')

    def save(self, *args, **kwargs):
        if self.address and (self.latitude is None or self.longitude is None):
            try:
                response = requests.get(
                    'https://geocode-maps.yandex.ru/1.x/',
                    params={
                        'apikey': YANDEX_API_KEY,
                        'geocode': self.address,
                        'format': 'json'
                    }
                )
                if response.status_code == 200:
                    geo_object = (response.json(

                    )['response']['GeoObjectCollection']
                     ['featureMember'][0]['GeoObject'])
                    coordinates = geo_object['Point']['pos'].split()
                    self.longitude, self.latitude = map(float, coordinates)
            except (IndexError, KeyError, requests.RequestException):
                pass  # Обработка ошибок, можно добавить логирование
        super(Veterinarian, self).save(*args, **kwargs)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Ветеринар'
        verbose_name_plural = 'Ветеринары'
        ordering = ['name']


class VetVisit(models.Model):
    pet = models.ForeignKey(Pet, on_delete=models.CASCADE,
                            verbose_name='Домашнее животное',
                            related_name='vet_visit')
    veterinarian = models.ForeignKey(Veterinarian, on_delete=models.CASCADE,
                                     verbose_name='Ветеринар',
                                     related_name='vet_visit',
                                     blank=True, null=True)
    date = models.DateField(verbose_name='Дата')
    reason = models.TextField(verbose_name='Причина')
    user = models.ForeignKey(User, on_delete=models.CASCADE,
                             verbose_name='Пользователь',
                             related_name='vet_visit')
    is_active = models.BooleanField(verbose_name='Предстоящий')

    def save(self, *args, **kwargs):
        if not self.is_active:
            self.date = dt.datetime.strptime(self.date, '%Y-%m-%d').date()
            if self.date >= self.date.today():
                self.is_active = True
            else:
                self.is_active = False
        super(VetVisit, self).save(*args, **kwargs)

    def __str__(self):
        return f"{self.pet.name} - {self.veterinarian.name} - {self.date}"

    class Meta:
        verbose_name = 'Посещение ветеринара'
        verbose_name_plural = 'Посещения ветеринара'
        ordering = ['-date']


class Clinic(models.Model):
    name = models.CharField(max_length=100, verbose_name='Название клиники')
    latitude = models.FloatField(verbose_name='Широта', null=True, blank=True)
    longitude = models.FloatField(verbose_name='Долгота', null=True,
                                  blank=True)
    address = models.CharField(max_length=255, verbose_name='Адрес')
    phone = models.CharField(max_length=20, verbose_name='Телефон')

    def save(self, *args, **kwargs):
        if self.address and (self.latitude is None or self.longitude is None):
            try:
                response = requests.get(
                    'https://geocode-maps.yandex.ru/1.x/',
                    params={
                        'apikey': YANDEX_API_KEY,
                        'geocode': self.address,
                        'format': 'json'
                    }
                )
                if response.status_code == 200:
                    geo_object = (
                        response.json()['response']['GeoObjectCollection']
                        ['featureMember'][0]['GeoObject']
                    )
                    coordinates = geo_object['Point']['pos'].split()
                    self.longitude, self.latitude = map(float, coordinates)
            except (IndexError, KeyError, requests.RequestException):
                pass  # Обработка ошибок, можно добавить логирование
        super(Clinic, self).save(*args, **kwargs)

    def get_veterinarians(self):
        return self.veterinarians.all()

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Клиника'
        verbose_name_plural = 'Клиники'
        ordering = ['name']
