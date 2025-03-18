from django.shortcuts import render
from shop.models import Product
from vets.models import Veterinarian


def index(request):
    template_name = 'homepage/index.html'
    title = 'VetMate | Главная'

    products = Product.objects.all()[:3]
    veterinarians = Veterinarian.objects.all()[:3]

    context = {
        'title': title,
        'products': products,
        'veterinarians': veterinarians,
    }
    return render(request, template_name, context)
