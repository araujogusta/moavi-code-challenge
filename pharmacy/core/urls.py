from django.urls import path

from pharmacy.core import views

urlpatterns = [
    path("", views.root, name="root"),
    path("markings", views.markings, name="markings"),
    path("api/markings-imports", views.get_markings_import, name="get_markings_import"),
    path("api/markings", views.get_markings, name="get_markings"),
    path("api/upload", views.upload_csv_file, name="upload_csv_files"),
]
