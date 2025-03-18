from django.shortcuts import render, get_object_or_404
from .models import Product
from pets.models import PetSpecies


def product_list(request):
    products = Product.objects.select_related('sponsor').all()

    # Получаем уникальные значения для фильтрации
    animal_types = PetSpecies.objects.values_list('name', 'id').distinct()
    product_types = Product.objects.values_list(
        'product_type', flat=True).distinct()
    brands = Product.objects.values_list('brand', flat=True).distinct()
    materials = Product.objects.values_list('material', flat=True).distinct()

    # Получаем параметры фильтрации из GET-запроса
    animal_type = request.GET.get('animal_type')
    product_type = request.GET.get('product_type')
    brand = request.GET.get('brand')
    rating = request.GET.get('rating')
    material = request.GET.get('material')

    # Фильтрация товаров
    if animal_type:
        products = products.filter(animal_type=animal_type)
    if product_type:
        products = products.filter(product_type=product_type)
    if brand:
        products = products.filter(brand=brand)
    if rating:
        products = products.filter(rating__gte=rating)
    if material:
        products = products.filter(material=material)

    context = {
        'products': products,
        'animal_types': animal_types,
        'product_types': product_types,
        'brands': brands,
        'materials': materials,
    }

    return render(request, 'shop/product_list.html', context)


def product_detail(request, id):
    product = get_object_or_404(Product.objects.select_related('sponsor'),
                                id=id)
    return render(request, 'shop/product_detail.html', {'product': product})
