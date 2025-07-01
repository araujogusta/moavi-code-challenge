import csv
from http import HTTPStatus

from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import render

from pharmacy.core.models import Marking, MarkingImport


def root(request: HttpRequest) -> HttpResponse:
    return render(request, "index.html")


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
