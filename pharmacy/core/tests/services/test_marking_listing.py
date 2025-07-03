from datetime import date, time, timedelta

from django.test import TestCase

from pharmacy.core.models import Marking, MarkingImport
from pharmacy.core.services.marking_listing import get_paginated_markings


class GetPaginatedMarkingsTest(TestCase):
    def setUp(self):
        self.today = date(2025, 7, 1)
        self.marking_import = MarkingImport.objects.create(
            filename='test.csv', uploaded_at=self.today, markings_count=0
        )

    def create_markings(self, count):
        for i in range(count):
            Marking.objects.create(
                employee_id=i % 5,
                date=self.today - timedelta(days=i),
                hour=time(8, i % 60),
                marking_import=self.marking_import,
            )

    def test_returns_paginated_results_with_has_next(self):
        self.create_markings(55)

        results, has_next = get_paginated_markings(page_number='1')

        self.assertEqual(len(results), 50)
        self.assertTrue(has_next)

    def test_returns_last_page_without_next(self):
        self.create_markings(55)

        results, has_next = get_paginated_markings(page_number='2')

        self.assertEqual(len(results), 5)
        self.assertFalse(has_next)

    def test_empty_result_returns_empty_list(self):
        results, has_next = get_paginated_markings(page_number='1')

        self.assertEqual(results, [])
        self.assertFalse(has_next)

    def test_custom_per_page(self):
        self.create_markings(30)

        results, has_next = get_paginated_markings(page_number='1', per_page=10)

        self.assertEqual(len(results), 10)
        self.assertTrue(has_next)
