from django.db import models
from django.contrib.auth import get_user_model
from django.utils.text import slugify
from django.urls import reverse
from core.validators import real_age
from django.utils.timezone import now, timedelta


User = get_user_model()


class PetSpecies(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Breed(models.Model):
    SIZE_CATEGORIES = [
        ('small', 'Мелкая'),
        ('medium', 'Средняя'),
        ('large', 'Крупная')
    ]
    animal_type = models.ForeignKey(PetSpecies, on_delete=models.CASCADE,
                                    related_name='breed')
    name = models.CharField(max_length=100)
    size_category = models.CharField(
        max_length=10, choices=SIZE_CATEGORIES, default='medium'
    )
    food = models.ManyToManyField('Food', blank=True,
                                  related_name='food_for_breed')

    def __str__(self):
        return self.name


class Food(models.Model):
    name = models.CharField(max_length=100, default='Не указано')
    sponsored = models.BooleanField(default=False,
                                    verbose_name='Спонсорский корм')

    def __str__(self):
        return self.name


class Vaccine(models.Model):
    name = models.CharField(max_length=100,
                            verbose_name="Название вакцины", unique=True)
    age_in_weeks = models.PositiveIntegerField(
        verbose_name="Возраст для прививки (в неделях)")
    breeds = models.ManyToManyField('Breed', related_name="required_vaccines",
                                    verbose_name="Подходящие породы")
    sponsored = models.BooleanField(default=False,
                                    verbose_name="Спонсорская вакцина")

    class Meta:
        verbose_name = "Вакцина"
        verbose_name_plural = "Вакцины"
        ordering = ["age_in_weeks"]

    def __str__(self):
        sponsor_tag = " (Спонс.)" if self.sponsored else ""
        return f"{self.name} ({self.age_in_weeks} недель){sponsor_tag}"


class Disease(models.Model):
    name = models.CharField(max_length=255, verbose_name="Название болезни")
    species = models.ManyToManyField(PetSpecies, related_name="diseases",
                                     verbose_name="Вид животного")
    common_for_breeds = models.ManyToManyField(
        Breed,
        blank=True,
        verbose_name="Часто встречается у пород"
    )

    def __str__(self):
        return self.name


class Medicine(models.Model):
    name = models.CharField(max_length=255, verbose_name="Название лекарства")
    diseases = models.ManyToManyField(Disease, related_name="medicines",
                                      verbose_name="Лечит болезни")
    sponsored = models.BooleanField(default=False,
                                    verbose_name="Спонсорское лекарство")

    def __str__(self):
        return self.name


class Vaccination(models.Model):
    pet = models.ForeignKey(
        'Pet', on_delete=models.CASCADE,
        verbose_name='Домашнее животное',
        related_name='vaccinations'
    )
    vaccine = models.ForeignKey(
        Vaccine, on_delete=models.CASCADE,
        verbose_name='Вакцина', related_name='vaccinations',
        default=0
    )
    date = models.DateField(verbose_name='Дата прививки')
    completed = models.BooleanField(default=False,
                                    verbose_name="Сделана ли прививка")

    class Meta:
        verbose_name = 'Прививка'
        verbose_name_plural = 'Прививки'
        ordering = ('-date',)

    def __str__(self):
        status = "✅" if self.completed else "❌"
        return (f"{self.vaccine.name} для {self.pet.name} "
                f"({self.date}) {status}")


class VaccinationSchedule(models.Model):
    pet = models.ForeignKey(
        'Pet', on_delete=models.CASCADE, verbose_name='Домашнее животное',
        related_name='vaccination_schedule'
    )
    next_vaccination_date = models.DateField(
        verbose_name="Ближайшая дата вакцинации", null=True, blank=True
    )
    recommended_vaccine = models.ForeignKey(
        Vaccine, on_delete=models.SET_NULL, null=True, blank=True,
        verbose_name="Рекомендуемая вакцина", related_name="recommended_for"
    )

    class Meta:
        verbose_name = 'График вакцинации'
        verbose_name_plural = 'Графики вакцинации'

    def calculate_schedule(self, pet):
        pet_age_weeks = (now().date() - pet.birth_date).days // 7
        max_age_weeks = pet_age_weeks + 52
        recommended = None

        done_vaccination_ids = (
            pet.vaccinations.values_list('vaccine_id', flat=True)
        )

        vaccines = Vaccine.objects.filter(
            breeds=pet.breed,
            age_in_weeks__range=(pet_age_weeks, max_age_weeks)
        ).exclude(id__in=done_vaccination_ids).order_by('age_in_weeks')

        recommended = vaccines.filter(sponsored=True).first(
        ) or vaccines.first()

        if recommended:
            next_vaccination_date = max(
                pet.birth_date + timedelta(weeks=recommended.age_in_weeks),
                now().date() + timedelta(days=1)
            )
        else:
            next_vaccination_date = None

        # Сохраняем изменения в объекте
        self.recommended_vaccine = recommended
        self.next_vaccination_date = next_vaccination_date
        self.save(update_fields=['recommended_vaccine',
                                 'next_vaccination_date'])

        return vaccines, [recommended, next_vaccination_date]


class Pet(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, verbose_name='Пользователь',
        related_name='pets'
    )
    name = models.CharField(max_length=100, verbose_name='Имя')
    species = models.ForeignKey(
        'PetSpecies', on_delete=models.CASCADE, verbose_name='Вид',
        related_name='species'
    )
    breed = models.ForeignKey(
        'Breed', on_delete=models.CASCADE, verbose_name='Порода',
        related_name='breeds'
    )
    birth_date = models.DateField(verbose_name='Дата рождения',
                                  validators=[real_age,])
    sex = models.CharField(max_length=20,
                           choices=[('М', 'Мальчик'), ('Ж', 'Девочка')],
                           default='М', verbose_name='Пол')
    weight = models.IntegerField(verbose_name='Вес', default=10)
    height = models.IntegerField(verbose_name='Размер', default=10)
    is_neutered = models.BooleanField(default=False,
                                      verbose_name='Стерилизовано')
    diseases = models.ManyToManyField(Disease, blank=True, related_name='pets',
                                      verbose_name='Болезни')
    medications = models.ManyToManyField(Medicine, blank=True,
                                         related_name='pets',
                                         verbose_name='Принимаемые лекарства')
    image = models.ImageField(
        upload_to='pets/profile_photo', verbose_name='Картинка',
        default='pets/cat_profile.webp', blank=True
    )
    characteristic = models.TextField(verbose_name='Особенности',
                                      blank=True, null=True)
    slug = models.SlugField(max_length=255, unique=True, blank=True)
    food = models.ForeignKey(Food, on_delete=models.SET_NULL, null=True,
                             blank=True, verbose_name="Используемый корм",
                             related_name='pets')

    class Meta:
        verbose_name = 'Домашнее животное'
        verbose_name_plural = 'Домашние животные'
        ordering = ('id',)

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        if not self.slug:
            self.slug = slugify(f"{self.name}-{Pet.objects.count() + 1}")
        super().save(*args, **kwargs)
        if is_new:
            VaccinationSchedule.objects.create(pet=self)
            FeedingSchedule.objects.create(pet=self)

    def get_absolute_url(self):
        return reverse('pets:pet_detail', kwargs={'slug': self.slug})

    def __str__(self):
        return f'{self.name} - {self.breed.name} - {self.species.name}'


class FeedingSchedule(models.Model):
    pet = models.OneToOneField(
        Pet, on_delete=models.CASCADE, verbose_name='Домашнее животное',
        related_name='feeding_schedule'
    )
    food = models.ForeignKey(
        Food, on_delete=models.SET_NULL, null=True, blank=True,
        verbose_name='Название корма', related_name='food'
    )
    recommended_food = models.ForeignKey(
        Food, on_delete=models.SET_NULL, null=True, blank=True,
        verbose_name='Рекомендуемый корм', related_name='recommended_food'
    )
    next_meal_time = models.TimeField(verbose_name='Ближайшее время кормления',
                                      null=True, blank=True)

    class Meta:
        verbose_name = 'График кормления'
        verbose_name_plural = 'Графики кормления'

    def calculate_schedule(self):
        size_category = self.pet.breed.size_category
        weight = self.pet.weight
        meals_per_day = None

        if size_category == 'small':
            meals_per_day = 4 if weight < 5 else 3
        elif size_category == 'medium':
            meals_per_day = 3
        else:
            meals_per_day = 2 if weight > 20 else 3

        meal_times = []
        start_time = now().replace(hour=8, minute=0, second=0, microsecond=0)

        for i in range(meals_per_day):
            meal_times.append(start_time + timedelta(hours=i *
                                                     (14 // meals_per_day)))

        self.next_meal_time = meal_times[0].time()
        return meal_times

    def save(self, *args, **kwargs):
        if not self.recommended_food:
            self.recommended_food = Food.objects.filter(sponsored=True).first()
        meal_times = self.calculate_schedule()
        super().save(*args, **kwargs)
        self.daily_feeding_schedule.all().delete()
        for time in meal_times:
            DailyFeedingSchedule.objects.create(schedule=self,
                                                time=time.time())


class DailyFeedingSchedule(models.Model):
    schedule = models.ForeignKey(
        FeedingSchedule, on_delete=models.CASCADE,
        related_name='daily_feeding_schedule'
    )
    time = models.TimeField()

    class Meta:
        verbose_name = 'Ежедневное кормление'
        verbose_name_plural = 'Ежедневные кормления'


class HealthAnalysis(models.Model):
    pet = models.OneToOneField(Pet, on_delete=models.CASCADE,
                               verbose_name='Домашнее животное',
                               related_name='health')
    result = models.TextField(verbose_name='Результат')

    class Meta:
        verbose_name = 'Анализ здоровья'
        verbose_name_plural = 'Анализы здоровья'
