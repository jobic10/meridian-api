from django.urls import path

from .views import (
    LabResultCompleteView,
    LabResultCreateView,
    LabResultListView,
    MedicalRecordCreateView,
    PrescriptionDispenseView,
    PrescriptionListView,
)

urlpatterns = [
    path("medical-records/", MedicalRecordCreateView.as_view(), name="medical-record-create"),
    path("prescriptions/", PrescriptionListView.as_view(), name="prescription-list"),
    path(
        "prescriptions/<int:pk>/dispense/",
        PrescriptionDispenseView.as_view(),
        name="prescription-dispense",
    ),
    path("lab-results/", LabResultListView.as_view(), name="lab-result-list"),
    path("lab-results/create/", LabResultCreateView.as_view(), name="lab-result-create"),
    path(
        "lab-results/<int:pk>/complete/",
        LabResultCompleteView.as_view(),
        name="lab-result-complete",
    ),
]
