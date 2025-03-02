from django.shortcuts import render


def vets_list(request):
    tempate_name = 'vets/vets_list.html'
    title = 'VetMate | Ветеринары рядом'
    context = {
        'title': title,
    }
    return render(request, tempate_name, context)


def vet_detail(request, id):
    tempate_name = 'vets/vet.html'
    title = 'VetMate | О ветеринаре'
    context = {
        'title': title,
        'id': id,
    }
    return render(request, tempate_name, context)
