from collections import defaultdict
from datetime import datetime, timedelta
from http import HTTPStatus

from django.core.paginator import Paginator
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import render

from pharmacy.core.models import Marking, MarkingImport
from pharmacy.core.services.csv_importer import import_markings_from_csv


def root(request: HttpRequest) -> HttpResponse:
    return render(request, 'index.html')


def markings(request: HttpRequest) -> HttpResponse:
    return render(request, 'markings.html')


def chart(request: HttpRequest) -> HttpResponse:
    return render(request, 'chart.html')


def upload_csv_file(request: HttpRequest) -> JsonResponse:
    if request.method != 'POST':
        return JsonResponse({'error': 'Method now allowed'}, status=HTTPStatus.METHOD_NOT_ALLOWED)

    file = request.FILES.get('file')
    if not file:
        return JsonResponse({'error': 'No files provided'}, status=HTTPStatus.BAD_REQUEST)

    if not file.name.endswith('.csv'):
        return JsonResponse({'error': 'Only CSV files are allowed'}, status=HTTPStatus.BAD_REQUEST)

    try:
        markings_import = import_markings_from_csv(file)
    except Exception as e:
        return JsonResponse({'error': f'Failed to import CSV: {str(e)}'}, status=HTTPStatus.INTERNAL_SERVER_ERROR)

    return JsonResponse({'markings_import': markings_import.to_dict()}, status=HTTPStatus.CREATED)


def get_markings_import(request: HttpRequest) -> JsonResponse:
    markings_imports = MarkingImport.objects.all().order_by('-id')
    return JsonResponse(
        {'markings_imports': [mi.to_dict() for mi in markings_imports]},
        status=HTTPStatus.OK,
    )


def get_markings(request: HttpRequest) -> JsonResponse:
    markings = Marking.objects.all().order_by('-date', '-hour')
    paginator = Paginator(markings, 50)

    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return JsonResponse(
        {'markings': [m.to_dict() for m in page], 'has_next': page.has_next()},
        status=HTTPStatus.OK,
    )


def get_chart_data(request: HttpRequest) -> JsonResponse:
    try:
        raw_date = request.GET.get('date')
        date = datetime.strptime(raw_date, '%Y-%m-%d').date()
    except ValueError:
        return JsonResponse({'error': 'Invalid date format'}, status=HTTPStatus.BAD_REQUEST)

    try:
        interval_presence = compute_interval_presence(date)
    except Exception as e:
        return JsonResponse(
            {'error': f'Failed to compute chart data: {str(e)}'}, status=HTTPStatus.INTERNAL_SERVER_ERROR
        )

    return JsonResponse(
        {'employee_interval_count': interval_presence},
        status=HTTPStatus.OK,
    )
