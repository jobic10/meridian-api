from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView

from core.permissions import IsSchedulingRole

from .models import Appointment
from .serializers import AppointmentCreateSerializer, AppointmentSerializer


class AppointmentListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsSchedulingRole]

    def get_serializer_class(self):
        return AppointmentCreateSerializer if self.request.method == "POST" else AppointmentSerializer

    def get_queryset(self):
        qs = Appointment.objects.select_related("patient", "doctor")
        user = self.request.user
        if user.role == "DOCTOR":
            qs = qs.filter(doctor=user)
        patient_id = self.request.query_params.get("patient")
        if patient_id:
            qs = qs.filter(patient_id=patient_id)
        return qs[:150]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        appointment = serializer.save()
        return Response(AppointmentSerializer(appointment).data, status=status.HTTP_201_CREATED)


class AppointmentStatusUpdateView(APIView):
    permission_classes = [IsSchedulingRole]

    def patch(self, request, pk):
        try:
            appointment = Appointment.objects.get(pk=pk)
        except Appointment.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        new_status = request.data.get("status")
        if new_status not in Appointment.Status.values:
            return Response({"detail": "Invalid status."}, status=status.HTTP_400_BAD_REQUEST)

        appointment.status = new_status
        appointment.save(update_fields=["status"])
        return Response(AppointmentSerializer(appointment).data)
