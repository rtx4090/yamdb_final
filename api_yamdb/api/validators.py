from datetime import datetime

from rest_framework.exceptions import ValidationError


def year_validator(value):
    if value < 1 or value > datetime.now().year:
        raise ValidationError(f'{value} - is not a correct year!')
