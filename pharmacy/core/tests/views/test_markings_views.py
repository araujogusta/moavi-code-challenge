from datetime import timedelta
from http import HTTPStatus

from django.test import Client, TestCase
from django.utils import timezone

from pharmacy.core.models import Marking, MarkingImport


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
