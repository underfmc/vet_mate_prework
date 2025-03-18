from django.db import models
from pets.models import PetSpecies


class Sponsor(models.Model):
    name = models.CharField(max_length=255)
    website = models.URLField()

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    image = models.ImageField(upload_to='products/')
    sponsor = models.ForeignKey(Sponsor, on_delete=models.CASCADE)
    sponsor_link = models.URLField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    animal_type = models.ForeignKey(PetSpecies, on_delete=models.CASCADE)
    product_type = models.CharField(max_length=100)  # Тип товара
    brand = models.CharField(max_length=100)  # Бренд товара
    rating = models.DecimalField(max_digits=3, decimal_places=2, null=True,
                                 blank=True)  # Рейтинг товара
    material = models.CharField(max_length=100, null=True,
                                blank=True)  # Материал товара

    def __str__(self):
        return f'{self.name} - {self.price}'
