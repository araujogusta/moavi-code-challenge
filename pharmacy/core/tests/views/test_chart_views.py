from datetime import time
from http import HTTPStatus

from django.test import Client, TestCase
from django.utils import timezone

from pharmacy.core.models import Marking, MarkingImport


class GetChartDataTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.marking_import = MarkingImport.objects.create(filename='dummy.csv', markings_count=0)
        self.date = timezone.now().date()

    def create_marking(self, employee_id, hour):
        return Marking.objects.create(
            employee_id=employee_id,
            date=self.date,
            hour=hour,
            marking_import=self.marking_import,
        )

    def test_returns_chart_data_successfully(self):
        self.create_marking(1, time(8, 5))
        self.create_marking(1, time(8, 45))
        self.create_marking(2, time(8, 15))
        self.create_marking(2, time(8, 55))

        response = self.client.get(f'/api/chart-data?date={self.date}')
        self.assertEqual(response.status_code, HTTPStatus.OK)

        data = response.json()
        self.assertIn('employee_interval_count', data)

        interval = data['employee_interval_count']
        self.assertIsInstance(interval, dict)
        self.assertIn('08:00', interval)
        self.assertIn('08:10', interval)
        self.assertIn('08:50', interval)

    def test_invalid_date_returns_bad_request(self):
        response = self.client.get('/api/chart-data?date=07-01-2024')
        self.assertEqual(response.status_code, HTTPStatus.BAD_REQUEST)

        payload = response.json()
        self.assertIn('error', payload)
        self.assertEqual(payload['error'], 'Invalid date format')

    def test_no_markings_returns_empty_interval_presence(self):
        response = self.client.get(f'/api/chart-data?date={self.date}')
        self.assertEqual(response.status_code, HTTPStatus.OK)

        interval_data = response.json()['employee_interval_count']
        for value in interval_data.values():
            self.assertEqual(value, 0)

    def test_single_employee_multiple_entries(self):
        self.create_marking(1, time(9, 3))
        self.create_marking(1, time(9, 45))

        response = self.client.get(f'/api/chart-data?date={self.date}')
        interval = response.json()['employee_interval_count']

        for key in interval:
            if '09:00' <= key < '09:40':
                self.assertGreaterEqual(interval[key], 1)
            elif '09:40' <= key < '10:00':
                self.assertEqual(interval[key], 0)

    def test_multiple_employees_in_and_out(self):
        self.create_marking(1, time(10, 5))
        self.create_marking(2, time(10, 7))
        self.create_marking(1, time(10, 35))
        self.create_marking(2, time(10, 55))

        response = self.client.get(f'/api/chart-data?date={self.date}')
        data = response.json()['employee_interval_count']

        self.assertGreaterEqual(data['10:10'], 2)
        self.assertEqual(data['10:40'], 1)
        self.assertEqual(data['11:00'], 0)
