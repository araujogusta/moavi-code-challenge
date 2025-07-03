from http import HTTPStatus

from django.http import HttpRequest, JsonResponse

from pharmacy.core.services.csv_importer import import_markings_from_csv


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
