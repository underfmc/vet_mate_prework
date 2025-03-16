from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Prefetch
from django.http import Http404, JsonResponse
from django.views.generic import (CreateView, DeleteView,
                                  ListView, UpdateView)
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from .models import (Pet, Breed, Disease, Medicine, Food,
                     VaccinationSchedule, Vaccine, Vaccination,
                     FeedingSchedule)
from vets.models import Veterinarian, VetVisit
from .forms import PetForm
from .utils import (calculate_age, generate_health_report)


User = get_user_model()


def load_breeds(request):
    animal_type_id = request.GET.get('species')
    breeds = Breed.objects.filter(
        animal_type_id=animal_type_id).order_by('name')
    return JsonResponse(list(breeds.values()), safe=False)


@login_required
def pet_detail(request, slug):
    pet = get_object_or_404(
        Pet.objects.select_related(
            "breed", "species",
        ).prefetch_related(
            Prefetch("vaccinations", queryset=Vaccination.objects.only(
                "id", "vaccine__name", "date")),
            Prefetch("diseases", queryset=Disease.objects.only("id", "name")),
            Prefetch("medications", queryset=Medicine.objects.only(
                "id", "name")),
            Prefetch("breed__food", queryset=Food.objects.only("id", "name")),
        ),
        slug=slug, user=request.user
    )

    vaccination_schedule, _ = VaccinationSchedule.objects.get_or_create(
        pet=pet)

    rec_and_date = vaccination_schedule.calculate_schedule(pet)
    available_vaccines = rec_and_date[0] if rec_and_date else []
    recommended_vaccine, next_vaccination_date = (
        rec_and_date[1] if rec_and_date else (None, None))

    feeding = FeedingSchedule.objects.filter(pet=pet).first()
    recommended_food = feeding.food if feeding else None
    next_meal_time = feeding.next_meal_time if feeding else None

    pet_disease_ids = {d["id"] for d in pet.diseases.values("id")}
    pet_medication_ids = {m["id"] for m in pet.medications.values("id")}

    available_diseases = Disease.objects.exclude(id__in=pet_disease_ids).only(
        "id", "name").order_by("name")
    available_medications = Medicine.objects.exclude(
        id__in=pet_medication_ids).only("id", "name").order_by("name")

    if request.method == "POST":
        post_data = request.POST

        if disease_id := post_data.get("remove_disease"):
            if pet.diseases.filter(id=disease_id).exists():
                pet.diseases.remove(disease_id)

        elif medication_id := post_data.get("remove_medication"):
            if pet.medications.filter(id=medication_id).exists():
                pet.medications.remove(medication_id)

        elif vet_visit_id := post_data.get("remove_visit"):
            if pet.vet_visit.filter(id=vet_visit_id).exists():
                VetVisit.objects.filter(id=vet_visit_id).delete()

        elif vaccination_id := post_data.get("remove_vaccination"):
            if pet.vaccinations.filter(id=vaccination_id).exists():
                Vaccination.objects.filter(id=vaccination_id).delete()

        elif post_data.get("add_vaccine"):
            vaccine_id = post_data.get("vaccine_id")
            if Vaccine.objects.filter(id=vaccine_id).exists():
                Vaccination.objects.create(
                    pet=pet,
                    vaccine_id=vaccine_id,
                    date=post_data.get("vaccination_date"),
                    completed=True
                )
                vaccination_schedule.calculate_schedule(pet)

        elif post_data.get("add_visit"):
            veterinarian_id = post_data.get("veterinarian_id")
            visit_date = post_data.get("visit_date")
            reason = post_data.get("reason")
            if Veterinarian.objects.filter(id=veterinarian_id).exists():
                VetVisit.objects.create(
                    pet=pet, veterinarian_id=veterinarian_id, date=visit_date,
                    reason=reason, user=request.user)

        else:
            if disease_id := post_data.get("disease_id"):
                pet.diseases.add(disease_id)

            if medication_id := post_data.get("medication_id"):
                pet.medications.add(medication_id)

            if food_brand := post_data.get("food_brand"):
                food_chosen = Food.objects.filter(id=food_brand).only(
                    "id").first()
                if food_chosen:
                    if feeding:
                        feeding.food = food_chosen
                        feeding.save(update_fields=["food"])
                    else:
                        FeedingSchedule.objects.create(
                            pet=pet, food=food_chosen)

        return redirect("pets:pet_detail", slug=pet.slug)
    diseases = pet.diseases.values("id", "name")
    medications = pet.medications.values("id", "name")
    health_report = generate_health_report(
            pet, diseases, available_medications,
            vaccination_schedule)
    veterinarians = list(Veterinarian.objects.all().only('id', 'name'))
    visits = VetVisit.objects.filter(pet=pet).select_related(
        "veterinarian").only("id", "veterinarian__name", "date", "reason")

    context = {
        "pet": pet,
        "age": calculate_age(pet.birth_date),
        "done_vaccinations": list(pet.vaccinations.values(
            "id", "vaccine__name", "date")),
        "vaccination_schedule": vaccination_schedule,
        "next_vaccination_date": next_vaccination_date,
        "recommended_vaccine": recommended_vaccine,
        "available_vaccines": available_vaccines,
        "diseases": diseases,
        "medications": list(medications),
        "foods": list(pet.breed.food.values("id", "name")),
        "feeding": feeding,
        "all_diseases": available_diseases,
        "all_medications": available_medications,
        "health_report": health_report,
        "veterinarians": veterinarians,
        "visits": visits,
        "recommended_food": recommended_food,
        "next_meal_time": next_meal_time,
    }

    return render(request, "pets/pet_detail.html", context)


class PetListView(LoginRequiredMixin, ListView):
    model = Pet
    template_name = 'pets/animals.html'
    ordering = 'id'
    paginate_by = 8

    def get_queryset(self):
        return Pet.objects.filter(user=self.request.user).select_related(
            'species')


class PetCreateView(LoginRequiredMixin, CreateView):
    model = Pet
    form_class = PetForm

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)


class PetUpdateView(LoginRequiredMixin, UpdateView):
    model = Pet
    form_class = PetForm

    def get_object(self, queryset=None):
        if queryset is None:
            queryset = self.get_queryset()
        try:
            pet = queryset.get(slug=self.kwargs['slug'],
                               user=self.request.user)
        except Pet.DoesNotExist:
            raise Http404()
        return pet


class PetDeleteView(LoginRequiredMixin, DeleteView):
    model = Pet
    success_url = reverse_lazy('pets:pets_list')

    def get_object(self, queryset=None):
        if queryset is None:
            queryset = self.get_queryset()
        try:
            pet = queryset.get(slug=self.kwargs['slug'],
                               user=self.request.user)
        except Pet.DoesNotExist:
            raise Http404()
        return pet
