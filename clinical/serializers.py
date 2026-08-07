from rest_framework import serializers

from accounts.serializers import UserSerializer

from .models import LabResult, MedicalRecord, Prescription


class PrescriptionSerializer(serializers.ModelSerializer):
    medicalRecordId = serializers.IntegerField(source="medical_record_id")
    drugName = serializers.CharField(source="drug_name")
    dispensedBy = UserSerializer(source="dispensed_by", read_only=True)
    dispensedAt = serializers.DateTimeField(source="dispensed_at")
    createdAt = serializers.DateTimeField(source="created_at")
    patientId = serializers.IntegerField(source="medical_record.patient_id", read_only=True)
    patientName = serializers.SerializerMethodField()
    doctorName = serializers.CharField(source="medical_record.doctor.name", read_only=True)
    diagnosis = serializers.CharField(source="medical_record.diagnosis", read_only=True)

    class Meta:
        model = Prescription
        fields = [
            "id",
            "medicalRecordId",
            "drugName",
            "dosage",
            "duration",
            "dispensed",
            "dispensedBy",
            "dispensedAt",
            "createdAt",
            "patientId",
            "patientName",
            "doctorName",
            "diagnosis",
        ]
        read_only_fields = ["dispensed", "dispensedBy", "dispensedAt"]

    def get_patientName(self, obj):
        p = obj.medical_record.patient
        return f"{p.first_name} {p.last_name}"


class PrescriptionInputSerializer(serializers.Serializer):
    """Used only for the nested `prescriptions: [...]` array on record creation."""

    drugName = serializers.CharField(max_length=100, source="drug_name")
    dosage = serializers.CharField(max_length=50)
    duration = serializers.CharField(max_length=50)


class LabResultSerializer(serializers.ModelSerializer):
    patientId = serializers.IntegerField(source="patient_id", read_only=True)
    patientName = serializers.SerializerMethodField()
    medicalRecordId = serializers.IntegerField(
        source="medical_record_id", read_only=True, allow_null=True
    )
    testName = serializers.CharField(source="test_name")
    enteredBy = UserSerializer(source="entered_by", read_only=True)
    createdAt = serializers.DateTimeField(source="created_at")
    completedAt = serializers.DateTimeField(source="completed_at")

    class Meta:
        model = LabResult
        fields = [
            "id",
            "patientId",
            "patientName",
            "medicalRecordId",
            "testName",
            "result",
            "notes",
            "status",
            "enteredBy",
            "createdAt",
            "completedAt",
        ]
        read_only_fields = ["status", "enteredBy", "completedAt"]

    def get_patientName(self, obj):
        return f"{obj.patient.first_name} {obj.patient.last_name}"


class MedicalRecordSerializer(serializers.ModelSerializer):
    doctor = UserSerializer(read_only=True)
    visitDate = serializers.DateTimeField(source="visit_date")
    treatmentNotes = serializers.CharField(source="treatment_notes")
    createdAt = serializers.DateTimeField(source="created_at")
    prescriptions = PrescriptionSerializer(many=True, read_only=True)
    labResults = LabResultSerializer(source="lab_results", many=True, read_only=True)

    class Meta:
        model = MedicalRecord
        fields = [
            "id",
            "patient",
            "doctor",
            "visitDate",
            "symptoms",
            "diagnosis",
            "treatmentNotes",
            "createdAt",
            "prescriptions",
            "labResults",
        ]
        read_only_fields = ["doctor", "visitDate"]


class MedicalRecordCreateSerializer(serializers.ModelSerializer):
    treatmentNotes = serializers.CharField(
        source="treatment_notes", required=False, allow_blank=True
    )
    prescriptions = PrescriptionInputSerializer(many=True, required=False, default=[])

    class Meta:
        model = MedicalRecord
        fields = ["patient", "symptoms", "diagnosis", "treatmentNotes", "prescriptions"]

    def create(self, validated_data):
        prescriptions = validated_data.pop("prescriptions", [])
        record = MedicalRecord.objects.create(
            doctor=self.context["request"].user, **validated_data
        )
        for p in prescriptions:
            Prescription.objects.create(medical_record=record, **p)
        return record
