from http import HTTPStatus

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase


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
