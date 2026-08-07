from rest_framework import serializers

from accounts.serializers import UserSerializer

from .models import Appointment


class PatientCompactSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    firstName = serializers.CharField(source="first_name")
    lastName = serializers.CharField(source="last_name")
    patientCode = serializers.CharField(source="patient_code")


class AppointmentSerializer(serializers.ModelSerializer):
    doctor = UserSerializer(read_only=True)
    patient = PatientCompactSerializer(read_only=True)
    patientId = serializers.IntegerField(source="patient_id", read_only=True)
    createdAt = serializers.DateTimeField(source="created_at")

    class Meta:
        model = Appointment
        fields = [
            "id",
            "patient",
            "patientId",
            "doctor",
            "date",
            "time",
            "reason",
            "status",
            "createdAt",
        ]
        read_only_fields = ["status"]


class AppointmentCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Appointment
        fields = ["patient", "doctor", "date", "time", "reason"]

    def validate_doctor(self, value):
        if value.role != "DOCTOR" or not value.is_active:
            raise serializers.ValidationError("Select an active doctor.")
        return value
