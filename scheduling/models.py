from django.conf import settings
from django.db import models

from patients.models import Patient


class Appointment(models.Model):
    class Status(models.TextChoices):
        PENDING = "PENDING", "Pending"
        COMPLETED = "COMPLETED", "Completed"
        CANCELLED = "CANCELLED", "Cancelled"

    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name="appointments")
    doctor = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="appointments"
    )
    date = models.DateField()
    # Stored as "HH:MM" to match the frontend's plain-string time formatting.
    time = models.CharField(max_length=5)
    reason = models.CharField(max_length=200, blank=True, null=True)
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.PENDING)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-date", "time"]

    def __str__(self):
        return f"{self.patient} with {self.doctor} on {self.date}"
