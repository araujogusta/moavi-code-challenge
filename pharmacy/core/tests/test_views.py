from http import HTTPStatus

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase

from pharmacy.core.models import MarkingImport


class FileUploadTest(TestCase):
    def setUp(self):
        self.client = Client()

    def test_upload_view(self):
        file_data = b"matricula,data,hora\n1001;2025-07-02;08:00\n1002;2025-07-02;09:00"
        uploaded_file = SimpleUploadedFile(
            "test_file.csv", file_data, content_type="text/csv"
        )

        response = self.client.post("/api/upload", {"file": uploaded_file})

        self.assertEqual(response.status_code, HTTPStatus.CREATED)

        mi = response.json().get("markings_import", None)

        self.assertIsInstance(mi, dict)
        self.assertIn("filename", mi)
        self.assertEqual(mi["filename"], "test_file.csv")
        self.assertEqual(mi["markings_count"], 2)
        self.assertIn("uploaded_at", mi)

    def test_upload_view_with_invalid_http_method(self):
        response = self.client.get("/api/upload")

        self.assertEqual(response.status_code, HTTPStatus.METHOD_NOT_ALLOWED)
        self.assertEqual(response.json(), {"error": "Method now allowed"})

    def test_upload_view_without_file(self):
        response = self.client.post("/api/upload")

        self.assertEqual(response.status_code, HTTPStatus.BAD_REQUEST)
        self.assertEqual(response.json(), {"error": "No files provided"})

    def test_upload_view_with_invalid_file_extension(self):
        file_data = b"matricula,data,hora\n1001;2025-07-02;08:00\n1002;2025-07-02;09:00"
        uploaded_file = SimpleUploadedFile(
            "test_file.txt", file_data, content_type="text/plain"
        )

        response = self.client.post("/api/upload", {"file": uploaded_file})

        self.assertEqual(response.status_code, HTTPStatus.BAD_REQUEST)
        self.assertEqual(response.json(), {"error": "Only CSV files are allowed"})


class GetMarkingsImportTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.markings_import = MarkingImport.objects.create(
            filename="test_file.csv", markings_count=2
        )

    def test_get_markings_import(self):
        response = self.client.get("/api/markings-imports")
        self.assertEqual(response.status_code, HTTPStatus.OK)

        payload = response.json().get("markings_imports", None)

        self.assertIsInstance(payload, list)
        self.assertEqual(len(payload), 1)

    def test_multiple_markings_imports_are_ordered_by_id_desc(self):
        MarkingImport.objects.create(filename="file2.csv", markings_count=3)
        MarkingImport.objects.create(filename="file3.csv", markings_count=5)

        response = self.client.get("/api/markings-imports")
        self.assertEqual(response.status_code, HTTPStatus.OK)

        data = response.json().get("markings_imports", [])
        self.assertEqual(len(data), 3)
        ids = [entry["id"] for entry in data]
        self.assertEqual(ids, sorted(ids, reverse=True))

    def test_response_structure_of_each_marking_import(self):
        response = self.client.get("/api/markings-imports")
        self.assertEqual(response.status_code, HTTPStatus.OK)

        data = response.json()["markings_imports"]
        for item in data:
            self.assertIn("id", item)
            self.assertIn("filename", item)
            self.assertIn("markings_count", item)
            self.assertIn("uploaded_at", item)

    def test_get_markings_import_with_no_data(self):
        MarkingImport.objects.all().delete()

        response = self.client.get("/api/markings-imports")
        self.assertEqual(response.status_code, HTTPStatus.OK)

        data = response.json().get("markings_imports", None)
        self.assertEqual(data, [])
