from datetime import date, time

from django.test import TestCase

from pharmacy.core.models import Marking, MarkingImport
from pharmacy.core.services.chart_data import compute_interval_presence


class ComputeIntervalPresenceTest(TestCase):
    def setUp(self):
        self.target_date = date(2025, 7, 1)
        self.marking_import = MarkingImport.objects.create(
            filename='test.csv', uploaded_at=self.target_date, markings_count=0
        )

    def test_compute_interval_presence_basic_flow(self):
        Marking.objects.create(
            employee_id=1, date=self.target_date, hour=time(9, 3), marking_import=self.marking_import
        )  # entra
        Marking.objects.create(
            employee_id=2, date=self.target_date, hour=time(9, 7), marking_import=self.marking_import
        )  # entra
        Marking.objects.create(
            employee_id=1, date=self.target_date, hour=time(9, 21), marking_import=self.marking_import
        )  # sai
        Marking.objects.create(
            employee_id=2, date=self.target_date, hour=time(9, 35), marking_import=self.marking_import
        )  # sai

        result = compute_interval_presence(self.target_date)

        self.assertEqual(result['09:00'], 2)
        self.assertEqual(result['09:10'], 2)
        self.assertEqual(result['09:20'], 1)
        self.assertEqual(result['09:30'], 0)

        self.assertEqual(result['08:50'], 0)
        self.assertEqual(result['10:00'], 0)

    def test_empty_markings_returns_all_zeros(self):
        result = compute_interval_presence(self.target_date)

        total_intervals = 24 * 6
        zeros = [v for v in result.values() if v == 0]
        self.assertEqual(len(zeros), total_intervals)

    def test_unmatched_entries(self):
        Marking.objects.create(
            employee_id=1, date=self.target_date, hour=time(14, 5), marking_import=self.marking_import
        )

        result = compute_interval_presence(self.target_date)

        self.assertEqual(result['14:00'], 1)
        self.assertEqual(result['14:10'], 1)
        self.assertEqual(result['15:00'], 1)
        self.assertEqual(result['23:50'], 1)
