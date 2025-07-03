from datetime import time, timedelta
from http import HTTPStatus

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase
from django.utils import timezone

from pharmacy.core.models import Marking, MarkingImport


class FileUploadTest(TestCase):
    def setUp(self):
        self.client = Client()

    def test_upload_view(self):
        file_data = b'matricula,data,hora\n1001;2025-07-02;08:00\n1002;2025-07-02;09:00'
        uploaded_file = SimpleUploadedFile('test_file.csv', file_data, content_type='text/csv')

        response = self.client.post('/api/upload', {'file': uploaded_file})

        self.assertEqual(response.status_code, HTTPStatus.CREATED)

        mi = response.json().get('markings_import', None)

        self.assertIsInstance(mi, dict)
        self.assertIn('filename', mi)
        self.assertEqual(mi['filename'], 'test_file.csv')
        self.assertEqual(mi['markings_count'], 2)
        self.assertIn('uploaded_at', mi)

    def test_upload_view_with_invalid_http_method(self):
        response = self.client.get('/api/upload')

        self.assertEqual(response.status_code, HTTPStatus.METHOD_NOT_ALLOWED)
        self.assertEqual(response.json(), {'error': 'Method now allowed'})

    def test_upload_view_without_file(self):
        response = self.client.post('/api/upload')

        self.assertEqual(response.status_code, HTTPStatus.BAD_REQUEST)
        self.assertEqual(response.json(), {'error': 'No files provided'})

    def test_upload_view_with_invalid_file_extension(self):
        file_data = b'matricula,data,hora\n1001;2025-07-02;08:00\n1002;2025-07-02;09:00'
        uploaded_file = SimpleUploadedFile('test_file.txt', file_data, content_type='text/plain')

        response = self.client.post('/api/upload', {'file': uploaded_file})

        self.assertEqual(response.status_code, HTTPStatus.BAD_REQUEST)
        self.assertEqual(response.json(), {'error': 'Only CSV files are allowed'})


class GetMarkingsImportTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.markings_import = MarkingImport.objects.create(filename='test_file.csv', markings_count=2)

    def test_get_markings_import(self):
        response = self.client.get('/api/markings-imports')
        self.assertEqual(response.status_code, HTTPStatus.OK)

        payload = response.json().get('markings_imports', None)

        self.assertIsInstance(payload, list)
        self.assertEqual(len(payload), 1)

    def test_multiple_markings_imports_are_ordered_by_id_desc(self):
        MarkingImport.objects.create(filename='file2.csv', markings_count=3)
        MarkingImport.objects.create(filename='file3.csv', markings_count=5)

        response = self.client.get('/api/markings-imports')
        self.assertEqual(response.status_code, HTTPStatus.OK)

        data = response.json().get('markings_imports', [])
        self.assertEqual(len(data), 3)
        ids = [entry['id'] for entry in data]
        self.assertEqual(ids, sorted(ids, reverse=True))

    def test_response_structure_of_each_marking_import(self):
        response = self.client.get('/api/markings-imports')
        self.assertEqual(response.status_code, HTTPStatus.OK)

        data = response.json()['markings_imports']
        for item in data:
            self.assertIn('id', item)
            self.assertIn('filename', item)
            self.assertIn('markings_count', item)
            self.assertIn('uploaded_at', item)

    def test_get_markings_import_with_no_data(self):
        MarkingImport.objects.all().delete()

        response = self.client.get('/api/markings-imports')
        self.assertEqual(response.status_code, HTTPStatus.OK)

        data = response.json().get('markings_imports', None)
        self.assertEqual(data, [])


class GetMarkingTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.marking_import = MarkingImport.objects.create(filename='test_file.csv', markings_count=1)

    def create_marking(self, **kwargs):
        defaults = {
            'date': timezone.now().date(),
            'hour': timezone.now().time(),
            'employee_id': 123,
            'marking_import': self.marking_import,
        }
        defaults.update(kwargs)
        return Marking.objects.create(**defaults)

    def test_returns_paginated_markings(self):
        for i in range(55):
            self.create_marking(employee_id=100 + i)

        response = self.client.get('/api/markings')
        self.assertEqual(response.status_code, HTTPStatus.OK)

        data = response.json()
        self.assertEqual(len(data['markings']), 50)
        self.assertTrue(data['has_next'])

    def test_returns_second_page(self):
        for i in range(60):
            self.create_marking(employee_id=200 + i)

        response = self.client.get('/api/markings?page=2')
        self.assertEqual(response.status_code, HTTPStatus.OK)

        data = response.json()
        self.assertEqual(len(data['markings']), 10)
        self.assertFalse(data['has_next'])

    def test_markings_ordered_by_date_and_hour(self):
        now = timezone.now()
        self.create_marking(date=now.date(), hour=now.time(), employee_id=1)
        self.create_marking(date=now.date(), hour=(now - timedelta(hours=1)).time(), employee_id=2)
        self.create_marking(date=now.date() - timedelta(days=1), hour=now.time(), employee_id=3)

        response = self.client.get('/api/markings')
        self.assertEqual(response.status_code, HTTPStatus.OK)

        employee_ids = [m['employee_id'] for m in response.json()['markings']]
        self.assertEqual(employee_ids, [1, 2, 3])

    def test_has_next_false_when_last_page(self):
        self.create_marking()

        response = self.client.get('/api/markings')
        self.assertEqual(response.status_code, HTTPStatus.OK)

        data = response.json()
        self.assertEqual(len(data['markings']), 1)
        self.assertFalse(data['has_next'])

    def test_invalid_page_returns_empty_list(self):
        response = self.client.get('/api/markings?page=999')
        self.assertEqual(response.status_code, HTTPStatus.OK)

        data = response.json()
        self.assertEqual(data['markings'], [])
        self.assertFalse(data['has_next'])

    def test_response_structure(self):
        self.create_marking()

        response = self.client.get('/api/markings')
        data = response.json()['markings'][0]

        self.assertIn('id', data)
        self.assertIn('date', data)
        self.assertIn('hour', data)
        self.assertIn('employee_id', data)
        self.assertIn('marking_import', data)
        self.assertIn('id', data['marking_import'])
        self.assertIn('filename', data['marking_import'])

    def test_no_page_param_defaults_to_first_page(self):
        for i in range(52):
            self.create_marking(employee_id=300 + i)

        response_with_param = self.client.get('/api/markings?page=1')
        response_without_param = self.client.get('/api/markings')

        self.assertEqual(response_with_param.json(), response_without_param.json())


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
