from django.contrib.auth.models import AbstractUser
from django.db import models


class Role(models.TextChoices):
    ADMIN = "ADMIN", "Administrator"
    DOCTOR = "DOCTOR", "Doctor"
    NURSE = "NURSE", "Nurse"
    RECORDS_OFFICER = "RECORDS_OFFICER", "Records Officer"
    PHARMACIST = "PHARMACIST", "Pharmacist"


class User(AbstractUser):
    """
    Staff account. `username`/`password`/`is_active` come from AbstractUser;
    `is_active` doubles as the ACTIVE/INACTIVE status the frontend expects.
    """

    name = models.CharField(max_length=150)
    role = models.CharField(max_length=20, choices=Role.choices)
    specialisation = models.CharField(max_length=100, blank=True, null=True)

    REQUIRED_FIELDS = ["name", "role"]

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return f"{self.name} ({self.role})"

    @property
    def status(self):
        return "ACTIVE" if self.is_active else "INACTIVE"
