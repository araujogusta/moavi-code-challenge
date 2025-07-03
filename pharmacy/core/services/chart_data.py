from collections import defaultdict
from datetime import date, datetime, timedelta

from pharmacy.core.models import Marking


def compute_interval_presence(date: date) -> dict[str, int]:
    markings = Marking.objects.filter(date=date).order_by('hour')

    grouped_markings = defaultdict(set)
    for employee in markings:
        rounded_minute = (employee.hour.minute // 10) * 10
        rounded_time = employee.hour.replace(minute=rounded_minute, second=0, microsecond=0)
        time_key = rounded_time.strftime('%H:%M')
        grouped_markings[time_key].add(employee.employee_id)

    interval_start = datetime.combine(date, datetime.min.time())
    interval_end = datetime.combine(date, datetime.max.time())

    active_employees = set()
    interval_presence = {}
    while interval_start < interval_end:
        key = interval_start.strftime('%H:%M')

        for employees in grouped_markings[key]:
            if employees in active_employees:
                active_employees.remove(employees)
            else:
                active_employees.add(employees)

        interval_presence[key] = len(active_employees)
        interval_start += timedelta(minutes=10)

    return interval_presence
