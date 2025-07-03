from datetime import date, time

from django.test import TestCase

from pharmacy.core.models import Marking, MarkingImport


class MarkingImportModelTest(TestCase):
    def test_create_marking_import(self):
        mi = MarkingImport.objects.create(filename='import_001.csv', markings_count=10)

        self.assertIsInstance(mi.id, int)
        self.assertEqual(mi.filename, 'import_001.csv')
        self.assertEqual(mi.markings_count, 10)
        self.assertIsNotNone(mi.uploaded_at)
        self.assertIsInstance(mi.to_dict(), dict)
        self.assertIn('filename', mi.to_dict())

    def test_to_dict_method(self):
        mi = MarkingImport.objects.create(filename='import_002.csv', markings_count=5)
        payload = mi.to_dict()

        self.assertIn('id', payload)
        self.assertIn('filename', payload)
        self.assertIn('markings_count', payload)
        self.assertIn('uploaded_at', payload)
        self.assertEqual(payload['filename'], mi.filename)
        self.assertEqual(payload['markings_count'], mi.markings_count)
        self.assertEqual(payload['uploaded_at'], mi.uploaded_at)


class MarkingModelTest(TestCase):
    def setUp(self):
        self.marking_import = MarkingImport.objects.create(filename='import_002.csv', markings_count=5)

    def test_create_marking(self):
        marking = Marking.objects.create(
            employee_id=1001,
            date=date(2025, 7, 2),
            hour=time(8, 0),
            marking_import=self.marking_import,
        )

        self.assertEqual(marking.employee_id, 1001)
        self.assertEqual(marking.date, date(2025, 7, 2))
        self.assertEqual(marking.hour, time(8, 0))
        self.assertEqual(marking.marking_import, self.marking_import)
        self.assertIsInstance(marking.to_dict(), dict)

    def test_to_dict_method(self):
        marking = Marking.objects.create(
            employee_id=1001,
            date=date(2025, 7, 2),
            hour=time(8, 0),
            marking_import=self.marking_import,
        )
        payload = marking.to_dict()

        self.assertIn('id', payload)
        self.assertIn('employee_id', payload)
        self.assertIn('date', payload)
        self.assertIn('hour', payload)
        self.assertIn('marking_import', payload)
        self.assertEqual(payload['employee_id'], marking.employee_id)
        self.assertEqual(payload['date'], marking.date)
        self.assertEqual(payload['hour'], marking.hour)
