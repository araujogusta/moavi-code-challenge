import csv
from collections import defaultdict
from datetime import datetime, timedelta
from http import HTTPStatus

from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import render

from pharmacy.core.models import Marking, MarkingImport


def root(request: HttpRequest) -> HttpResponse:
    return render(request, "index.html")


def markings(request: HttpRequest) -> HttpResponse:
    return render(request, "markings.html")


def chart(request: HttpRequest) -> HttpResponse:
    return render(request, "chart.html")


def upload_csv_file(request: HttpRequest) -> JsonResponse:
    if request.method != "POST":
        return JsonResponse(
            {"error": "Method now allowed"}, status=HTTPStatus.METHOD_NOT_ALLOWED
        )

    file = request.FILES.get("file")
    if not file:
        return JsonResponse(
            {"error": "No files provided"}, status=HTTPStatus.BAD_REQUEST
        )

    if not file.name.endswith(".csv"):
        return JsonResponse(
            {"error": "Only CSV files are allowed"}, status=HTTPStatus.BAD_REQUEST
        )

    raw_file_content = file.read().decode("utf-8")
    reader = csv.reader(raw_file_content.splitlines(), delimiter=";")
    file_content = list(reader)

    markings_import = MarkingImport(filename=file.name, markings_count=0)

    markings = []
    for row in file_content[1::]:
        employee_id, marking_date, marking_hour = row
        marking = Marking(
            employee_id=employee_id,
            date=marking_date,
            hour=marking_hour,
            marking_import=markings_import,
        )
        markings.append(marking)

    markings_import.markings_count = len(markings)
    markings_import.save()
    Marking.objects.bulk_create(markings)

    return JsonResponse(
        {"markings_import": markings_import.to_dict()}, status=HTTPStatus.CREATED
    )


def get_markings_import(request: HttpRequest) -> JsonResponse:
    markings_imports = MarkingImport.objects.all().order_by("-id")
    return JsonResponse(
        {"markings_imports": [mi.to_dict() for mi in markings_imports]},
        status=HTTPStatus.OK,
    )


def get_markings(request: HttpRequest) -> JsonResponse:
    markings = Marking.objects.all().order_by("-date", "-hour")
    return JsonResponse(
        {"markings": [m.to_dict() for m in markings]},
        status=HTTPStatus.OK,
    )


def get_chart_data(request: HttpRequest) -> JsonResponse:
    try:
        raw_date = request.GET.get("date")
        date = datetime.strptime(raw_date, "%Y-%m-%d").date()
    except ValueError:
        return JsonResponse(
            {"error": "Invalid date format"}, status=HTTPStatus.BAD_REQUEST
        )

    markings = Marking.objects.filter(date=date).order_by("hour")

    grouped_markings = defaultdict(set)
    for employee in markings:
        rounded_minute = (employee.hour.minute // 10) * 10
        rounded_time = employee.hour.replace(
            minute=rounded_minute, second=0, microsecond=0
        )
        time_key = rounded_time.strftime("%H:%M")
        grouped_markings[time_key].add(employee.employee_id)

    interval_start = datetime.combine(date, datetime.min.time())
    interval_end = datetime.combine(date, datetime.max.time())

    active_employees = set()
    interval_presence = {}
    while interval_start < interval_end:
        key = interval_start.strftime("%H:%M")

        for employees in grouped_markings[key]:
            if employees in active_employees:
                active_employees.remove(employees)
            else:
                active_employees.add(employees)

        interval_presence[key] = len(active_employees)
        interval_start += timedelta(minutes=10)

    return JsonResponse(
        {"employee_interval_count": interval_presence},
        status=HTTPStatus.OK,
    )
