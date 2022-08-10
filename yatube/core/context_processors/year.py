from datetime import datetime


def year(request):
    """Выводит текущий год"""
    return {
        'year': datetime.now().year
        }