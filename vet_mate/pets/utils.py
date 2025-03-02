import datetime
from django.utils.timezone import now
from .models import Vaccine


def get_vaccines_for_next_year(pet):
    pet_age_weeks = (now().date() - pet.birth_date).days // 7
    max_age_weeks = pet_age_weeks + 52

    done_vaccination_ids = set(
        pet.vaccinations.values_list('vaccine_id', flat=True)
    )
    vaccines = Vaccine.objects.filter(
        breeds=pet.breed,
        age_in_weeks__range=(pet_age_weeks, max_age_weeks)
    ).exclude(id__in=done_vaccination_ids).order_by('age_in_weeks')

    return vaccines


def generate_health_report(pet, diseases, sponsored_medicines,
                           vaccination_schedule):
    report = []

    # 1. Возраст питомца
    age_weeks = (now().date() - pet.birth_date).days // 7
    report.append(f"📅 Возраст: {age_weeks // 52} лет, "
                  f"{age_weeks % 52} недель.")

    # 2. Заболевания и лекарства (1 SQL-запрос вместо нескольких)
    if diseases:
        disease_names = ", ".join(d.get('name') for d in diseases)
        report.append(f"❌ Обнаружены болезни: {disease_names}.")

        if sponsored_medicines:
            report.append(f"💊 Рекомендуемые лекарства: "
                          f"{', '.join(str(m) for m in sponsored_medicines)}.")
        else:
            report.append("⚠️ Рекомендуем обратиться к ветеринару.")
    else:
        report.append("✅ Питомец здоров!")

    # 3. Анализ корма (используем select_related)
    if pet.food:
        recommended_food = pet.breed.food.filter(sponsored=True).only(
            "id", "name").first()
        if recommended_food and pet.food_id != recommended_food.id:
            report.append(f"🍽️ Рекомендуем корм "
                          f"'{recommended_food.name}' вместо текущего "
                          f"'{pet.food.name}'.")
        else:
            report.append("✅ Корм подходит.")

    # 4. Вакцинация (используем select_related)
    if vaccination_schedule and vaccination_schedule.next_vaccination_date:
        report.append(
            f"💉 Следующая прививка: "
            f"{vaccination_schedule.next_vaccination_date} "
            f"({vaccination_schedule.recommended_vaccine.name})."
        )
    else:
        report.append("✅ Все прививки актуальны.")

    return "<br>".join(report)


class SexChoices:
    CHOICES = (
        ('Самец', 'Самец'),
        ('Самка', 'Самка'),
    )


def calculate_age(birthday):
    today = datetime.date.today()
    age = today.year - birthday.year - ((today.month, today.day) <
                                        (birthday.month, birthday.day))
    if age % 10 == 1 and age % 100 != 11:
        return f'{age} год'
    elif 2 <= age % 10 <= 4 and (age % 100 < 10 or age % 100 >= 20):
        return f'{age} года'
    else:
        return f'{age} лет'
