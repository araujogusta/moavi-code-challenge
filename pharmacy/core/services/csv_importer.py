import csv

from django.core.files.uploadedfile import UploadedFile

from pharmacy.core.models import Marking, MarkingImport


def import_markings_from_csv(file: UploadedFile) -> MarkingImport:
    raw_file_content = file.read().decode('utf-8')
    reader = csv.reader(raw_file_content.splitlines(), delimiter=';')
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

    return markings_import
