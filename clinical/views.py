from django.utils import timezone
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView

from core.permissions import IsAdminOrDoctor, IsLabRole, IsPharmacyRole

from .models import LabResult, Prescription
from .serializers import (
    LabResultSerializer,
    MedicalRecordCreateSerializer,
    MedicalRecordSerializer,
    PrescriptionSerializer,
)


class MedicalRecordCreateView(generics.CreateAPIView):
    serializer_class = MedicalRecordCreateSerializer
    permission_classes = [IsAdminOrDoctor]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        record = serializer.save()
        return Response(MedicalRecordSerializer(record).data, status=status.HTTP_201_CREATED)


class PrescriptionListView(generics.ListAPIView):
    serializer_class = PrescriptionSerializer
    permission_classes = [IsPharmacyRole]

    def get_queryset(self):
        qs = Prescription.objects.select_related(
            "medical_record", "medical_record__patient", "medical_record__doctor", "dispensed_by"
        )
        dispensed = self.request.query_params.get("dispensed")
        if dispensed is not None:
            is_dispensed = dispensed == "true"
            qs = qs.filter(dispensed=is_dispensed)
            qs = qs.order_by("-dispensed_at") if is_dispensed else qs.order_by("created_at")
        return qs


class PrescriptionDispenseView(APIView):
    permission_classes = [IsPharmacyRole]

    def patch(self, request, pk):
        try:
            prescription = Prescription.objects.get(pk=pk)
        except Prescription.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        prescription.dispensed = True
        prescription.dispensed_by = request.user
        prescription.dispensed_at = timezone.now()
        prescription.save(update_fields=["dispensed", "dispensed_by", "dispensed_at"])
        return Response(PrescriptionSerializer(prescription).data)


class LabResultCreateView(generics.CreateAPIView):
    serializer_class = LabResultSerializer
    permission_classes = [IsLabRole]

    def create(self, request, *args, **kwargs):
        has_result = bool(str(request.data.get("result", "")).strip())
        lab = LabResult.objects.create(
            patient_id=request.data.get("patient"),
            medical_record_id=request.data.get("medical_record") or None,
            test_name=request.data.get("test_name"),
            result=request.data.get("result") or None,
            notes=request.data.get("notes") or None,
            status=LabResult.Status.COMPLETED if has_result else LabResult.Status.PENDING,
            entered_by=request.user,
            completed_at=timezone.now() if has_result else None,
        )
        return Response(LabResultSerializer(lab).data, status=status.HTTP_201_CREATED)


class LabResultListView(generics.ListAPIView):
    serializer_class = LabResultSerializer
    permission_classes = [IsLabRole]

    def get_queryset(self):
        qs = LabResult.objects.select_related("patient", "entered_by")
        status_param = self.request.query_params.get("status")
        if status_param:
            qs = qs.filter(status=status_param)
            qs = (
                qs.order_by("-completed_at")
                if status_param == "COMPLETED"
                else qs.order_by("created_at")
            )
        return qs


class LabResultCompleteView(APIView):
    permission_classes = [IsLabRole]

    def patch(self, request, pk):
        try:
            lab = LabResult.objects.get(pk=pk)
        except LabResult.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        result = request.data.get("result")
        if not result:
            return Response({"detail": "Enter the result."}, status=status.HTTP_400_BAD_REQUEST)

        lab.result = result
        lab.notes = request.data.get("notes") or lab.notes
        lab.status = LabResult.Status.COMPLETED
        lab.completed_at = timezone.now()
        lab.save(update_fields=["result", "notes", "status", "completed_at"])
        return Response(LabResultSerializer(lab).data)
