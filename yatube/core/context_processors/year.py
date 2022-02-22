from django.utils import timezone

now = timezone.datetime.now()


def year(requests):
    """Добавляет переменную с текущим годом."""
    return {
        'year': int(now.year)
    }
