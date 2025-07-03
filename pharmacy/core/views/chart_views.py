from datetime import datetime
from http import HTTPStatus

from django.http import HttpRequest, JsonResponse

from pharmacy.core.services.chart_data import compute_interval_presence


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
