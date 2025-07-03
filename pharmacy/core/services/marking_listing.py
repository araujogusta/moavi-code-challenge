from typing import Tuple

from django.core.paginator import Paginator

from pharmacy.core.models import Marking


def get_paginated_markings(page_number: str, per_page: int = 50) -> Tuple[list, bool]:
    markings = Marking.objects.all().order_by('-date', '-hour')
    paginator = Paginator(markings, per_page)
    page = paginator.get_page(page_number)

    return list(page), page.has_next()
