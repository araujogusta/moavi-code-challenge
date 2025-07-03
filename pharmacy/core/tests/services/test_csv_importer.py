from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase

from pharmacy.core.models import Marking, MarkingImport
from pharmacy.core.services.csv_importer import import_markings_from_csv


class ImportMarkingsFromCSVTest(TestCase):
    def setUp(self):
        self.csv_content = 'employee_id;date;hour\n1;2025-07-01;08:00:00\n2;2025-07-01;08:05:00\n'
        self.uploaded_file = SimpleUploadedFile(
            'test_markings.csv', self.csv_content.encode('utf-8'), content_type='text/csv'
        )

    def test_import_creates_markings_and_import_record(self):
        markings_import = import_markings_from_csv(self.uploaded_file)

        self.assertIsInstance(markings_import, MarkingImport)
        self.assertEqual(markings_import.filename, 'test_markings.csv')
        self.assertEqual(markings_import.markings_count, 2)

        markings = Marking.objects.filter(marking_import=markings_import)
        self.assertEqual(markings.count(), 2)

        marking_1 = markings.get(employee_id='1')
        self.assertEqual(str(marking_1.date), '2025-07-01')
        self.assertEqual(str(marking_1.hour), '08:00:00')

        marking_2 = markings.get(employee_id='2')
        self.assertEqual(str(marking_2.date), '2025-07-01')
        self.assertEqual(str(marking_2.hour), '08:05:00')

    def test_import_empty_file_does_not_create_anything(self):
        empty_csv = SimpleUploadedFile('empty.csv', b'employee_id;date;hour\n')
        result = import_markings_from_csv(empty_csv)

        self.assertEqual(result.markings_count, 0)
        self.assertEqual(Marking.objects.count(), 0)

    def test_import_invalid_format_raises_error(self):
        bad_csv = SimpleUploadedFile('bad.csv', b'employee_id;date;hour\n1;2025-07-01\n', content_type='text/csv')

        with self.assertRaises(ValueError):
            import_markings_from_csv(bad_csv)
