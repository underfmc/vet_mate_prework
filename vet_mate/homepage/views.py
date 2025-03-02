from django.shortcuts import render


def index(request):
    tempate_name = 'homepage/index.html'
    title = 'VetMate | Главная'
    context = {
        'title': title,
    }
    return render(request, tempate_name, context)
