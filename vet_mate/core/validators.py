from datetime import date
from django.core.exceptions import ValidationError
from django.core.validators import (MinLengthValidator,
                                    MaxLengthValidator,
                                    RegexValidator)


def validate_name_or_country_city(value):
    return MinLengthValidator(value, 2) and MaxLengthValidator(value, 100)


validate_email = RegexValidator(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$',
                                'Введите корректную почту.')

validate_phone_number = RegexValidator(r'^\+?1?\d{9,15}$',
                                       'Введите корректный номер телефона.')


def real_age(value: date) -> None:
    age = (date.today() - value).days / 365
    if age < 0 or age > 600:
        raise ValidationError(
            'Ожидается возраст от 0 до 600 лет'
        )
