from http import HTTPStatus

from django.http import HttpRequest, JsonResponse

from pharmacy.core.models import MarkingImport
from pharmacy.core.services.marking_listing import get_paginated_markings


def get_markings_import(request: HttpRequest) -> JsonResponse:
    markings_imports = MarkingImport.objects.all().order_by('-id')
    return JsonResponse(
        {'markings_imports': [mi.to_dict() for mi in markings_imports]},
        status=HTTPStatus.OK,
    )


def get_markings(request: HttpRequest) -> JsonResponse:
    page_number = request.GET.get('page')
    markings, has_next = get_paginated_markings(page_number)

    return JsonResponse(
        {'markings': [m.to_dict() for m in markings], 'has_next': has_next},
        status=HTTPStatus.OK,
    )
