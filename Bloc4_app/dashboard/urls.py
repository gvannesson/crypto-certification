from django.urls import path
from . import views

urlpatterns = [
    path("", views.dashboard_view, name="dashboard"),
    path("charts/", views.charts_view, name="charts"),
    path("monitoring/", views.monitoring_view, name="monitoring"),
    path("api/chart-data/", views.api_chart_data, name="api_chart_data"),
]
