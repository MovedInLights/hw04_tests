import datetime as dt
current_year = int(dt.datetime.now().year)


def year(request):
    """Добавляет переменную с текущим годом."""
    return {
        'year': current_year
    }
