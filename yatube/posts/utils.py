from django.conf import settings
from django.core.paginator import Paginator
from django.db.models import QuerySet as QS
from django.http import HttpRequest


def create_paginator(request: HttpRequest,
                     object_list: QS,
                     count_posts: int = settings.COUNT_OF_VISIBLE_POSTS) -> QS:
    """Возвращает пагинатор с заданным количеством постов"""
    paginator = Paginator(object_list, count_posts)

    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return page_obj
