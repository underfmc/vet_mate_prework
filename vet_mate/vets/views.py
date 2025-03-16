from django.shortcuts import render, redirect
import requests
from django.conf import settings
from django.contrib.auth.decorators import login_required
from vets.models import Veterinarian
from django.views.decorators.http import require_GET
from geopy.distance import geodesic
from vets.models import Clinic
from django.http import JsonResponse
from vets.forms import VetVisitForm
from vets.models import VetVisit

YANDEX_API_KEY = settings.YANDEX_API_KEY


@require_GET
def vets_list(request):
    template_name = 'vets/vets_list.html'
    title = 'VetMate | Ветеринары рядом'
    user_location = request.GET.get('location', None)
    clinics = []
    veterinarians = []

    if user_location:
        try:
            lat, lon = map(float, user_location.split(','))
            user_coords = (lat, lon)

            # Поиск ближайших клиник из базы данных
            all_clinics = Clinic.objects.filter(latitude__isnull=False,
                                                longitude__isnull=False)
            clinics = sorted(
                all_clinics,
                key=lambda clinic: geodesic(user_coords, (clinic.latitude,
                                                          clinic.longitude)).km
            )[:10]

            # Поиск ближайших ветеринаров из базы данных
            veterinarians = Veterinarian.objects.filter(
                latitude__isnull=False, longitude__isnull=False
            )
            veterinarians = sorted(
                veterinarians,
                key=lambda vet: geodesic(user_coords, (vet.latitude,
                                                       vet.longitude)).km
            )[:10]
        except (ValueError, requests.RequestException):
            pass

    context = {
        'title': title,
        'clinics': clinics,
        'veterinarians': veterinarians,
        'location': user_location,
    }
    return render(request, template_name, context)


@require_GET
def clinic_detail(request, pk):
    try:
        clinic = Clinic.objects.get(id=pk)
        veterinarians = clinic.get_veterinarians()
        data = {
            'name': clinic.name,
            'address': clinic.address,
            'veterinarians': [{'name': vet.name} for vet in veterinarians],
            'clinic_id': clinic.id,
        }
        return JsonResponse(data)
    except Clinic.DoesNotExist:
        return JsonResponse({'error': 'Clinic not found'}, status=404)


@require_GET
def vet_detail(request, pk):
    try:
        vet = Veterinarian.objects.get(id=pk)
        data = {
            'name': vet.name,
            'address': vet.address,
            'clinic_name': vet.clinic.name if vet.clinic else ('Клиника'
                                                               ' не указана'),
            'photo_url': vet.photo.url if vet.photo else None,
        }
        return JsonResponse(data)
    except Veterinarian.DoesNotExist:
        return JsonResponse({'error': 'Veterinarian not found'}, status=404)


@login_required
def vet_visits(request):
    template_name = 'vets/vet_visits.html'
    title = 'VetMate | Записи на прием'
    user = request.user
    visits = VetVisit.objects.filter(user=user)

    # Фильтрация по животному или ветеринару
    pet_id = request.GET.get('pet')
    vet_id = request.GET.get('veterinarian')
    if pet_id:
        visits = visits.filter(pet_id=pet_id)
    if vet_id:
        visits = visits.filter(veterinarian_id=vet_id)

    # Обработка добавления новой записи
    if request.method == 'POST':
        form = VetVisitForm(request.POST)
        if form.is_valid():
            new_visit = form.save(commit=False)
            new_visit.user = user
            new_visit.save()
            return redirect('vets:vet_visits')
    else:
        form = VetVisitForm()

    # Обработка удаления записи
    if 'delete_visit' in request.POST:
        visit_id = request.POST.get('delete_visit')
        VetVisit.objects.filter(id=visit_id, user=user).delete()
        return redirect('vets:vet_visits')

    context = {
        'title': title,
        'visits': visits,
        'form': form,
    }
    return render(request, template_name, context)
