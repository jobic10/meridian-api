from rest_framework import serializers

from clinical.serializers import LabResultSerializer, MedicalRecordSerializer
from scheduling.serializers import AppointmentSerializer

from .models import Patient


class PatientListSerializer(serializers.ModelSerializer):
    patientCode = serializers.CharField(source="patient_code")
    firstName = serializers.CharField(source="first_name")
    lastName = serializers.CharField(source="last_name")
    dateOfBirth = serializers.DateField(source="date_of_birth")
    bloodGroup = serializers.CharField(source="blood_group")
    createdAt = serializers.DateTimeField(source="created_at")

    class Meta:
        model = Patient
        fields = [
            "id",
            "patientCode",
            "firstName",
            "lastName",
            "gender",
            "dateOfBirth",
            "bloodGroup",
            "phone",
            "createdAt",
        ]


class PatientCreateSerializer(serializers.ModelSerializer):
    firstName = serializers.CharField(source="first_name")
    lastName = serializers.CharField(source="last_name")
    dateOfBirth = serializers.DateField(source="date_of_birth")
    nextOfKin = serializers.CharField(source="next_of_kin", required=False, allow_blank=True)
    nextOfKinPhone = serializers.CharField(
        source="next_of_kin_phone", required=False, allow_blank=True
    )
    bloodGroup = serializers.CharField(source="blood_group", required=False, allow_blank=True)

    class Meta:
        model = Patient
        fields = [
            "firstName",
            "lastName",
            "gender",
            "dateOfBirth",
            "address",
            "phone",
            "nextOfKin",
            "nextOfKinPhone",
            "bloodGroup",
            "allergies",
        ]

    def validate_dateOfBirth(self, value):
        from django.utils import timezone

        if value > timezone.now().date():
            raise serializers.ValidationError("Enter a valid date of birth.")
        return value


class PatientDetailSerializer(serializers.ModelSerializer):
    patientCode = serializers.CharField(source="patient_code")
    firstName = serializers.CharField(source="first_name")
    lastName = serializers.CharField(source="last_name")
    dateOfBirth = serializers.DateField(source="date_of_birth")
    nextOfKin = serializers.CharField(source="next_of_kin")
    nextOfKinPhone = serializers.CharField(source="next_of_kin_phone")
    bloodGroup = serializers.CharField(source="blood_group")
    createdAt = serializers.DateTimeField(source="created_at")
    registeredByName = serializers.SerializerMethodField()
    medicalRecords = MedicalRecordSerializer(source="medical_records", many=True, read_only=True)
    appointments = AppointmentSerializer(many=True, read_only=True)
    labResults = LabResultSerializer(source="lab_results", many=True, read_only=True)

    class Meta:
        model = Patient
        fields = [
            "id",
            "patientCode",
            "firstName",
            "lastName",
            "gender",
            "dateOfBirth",
            "address",
            "phone",
            "nextOfKin",
            "nextOfKinPhone",
            "bloodGroup",
            "allergies",
            "createdAt",
            "registeredByName",
            "medicalRecords",
            "appointments",
            "labResults",
        ]

    def get_registeredByName(self, obj):
        return obj.registered_by.name if obj.registered_by else None
