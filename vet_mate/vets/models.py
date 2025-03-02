from django.contrib.auth import get_user_model
from django.db import models
from pets.models import Pet


User = get_user_model()


class Veterinarian(models.Model):
    name = models.CharField(max_length=100, verbose_name='Имя')
    address = models.CharField(max_length=255, verbose_name='Адрес')
    phone = models.CharField(max_length=20, verbose_name='Телефон')

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
            if self.date >= self.date.today():
                self.is_active = True
        super(VetVisit, self).save(*args, **kwargs)

    class Meta:
        verbose_name = 'Посещение ветеринара'
        verbose_name_plural = 'Посещения ветеринара'
        ordering = ['-date']
