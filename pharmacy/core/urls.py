from django.urls import path

from pharmacy.core.views import base_views, chart_views, markings_views, upload_views

urlpatterns = [
    path('', base_views.root, name='root'),
    path('markings', base_views.markings, name='markings'),
    path('chart', base_views.chart, name='chart'),
    path('api/markings-imports', markings_views.get_markings_import, name='get_markings_import'),
    path('api/markings', markings_views.get_markings, name='get_markings'),
    path('api/chart-data', chart_views.get_chart_data, name='get_chart_data'),
    path('api/upload', upload_views.upload_csv_file, name='upload_csv_files'),
]
