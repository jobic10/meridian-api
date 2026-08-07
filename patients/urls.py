from django.urls import path

from .views import (
    DashboardSummaryView,
    PatientDetailView,
    PatientListCreateView,
    ReportsSummaryView,
)

urlpatterns = [
    path("patients/", PatientListCreateView.as_view(), name="patient-list-create"),
    path("patients/<int:pk>/", PatientDetailView.as_view(), name="patient-detail"),
    path("dashboard/summary/", DashboardSummaryView.as_view(), name="dashboard-summary"),
    path("reports/summary/", ReportsSummaryView.as_view(), name="reports-summary"),
]
