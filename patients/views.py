from datetime import timedelta

from django.contrib.auth import get_user_model
from django.db.models import Count, Q
from django.utils import timezone
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from clinical.models import LabResult, MedicalRecord, Prescription
from core.permissions import IsAdmin, IsRecordsOrAdmin
from scheduling.models import Appointment
from scheduling.serializers import AppointmentSerializer

from .models import Patient
from .serializers import PatientCreateSerializer, PatientDetailSerializer, PatientListSerializer

User = get_user_model()


class PatientListCreateView(generics.ListCreateAPIView):
    def get_serializer_class(self):
        return PatientCreateSerializer if self.request.method == "POST" else PatientListSerializer

    def get_permissions(self):
        if self.request.method == "POST":
            return [IsRecordsOrAdmin()]
        return [IsAuthenticated()]

    def get_queryset(self):
        qs = Patient.objects.all()
        q = self.request.query_params.get("q")
        if q:
            qs = qs.filter(
                Q(first_name__icontains=q)
                | Q(last_name__icontains=q)
                | Q(patient_code__icontains=q)
                | Q(phone__icontains=q)
            )
        return qs[:100]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        year = timezone.now().year
        count = Patient.objects.filter(patient_code__startswith=f"PT-{year}-").count()
        patient = serializer.save(
            patient_code=f"PT-{year}-{count + 1:04d}",
            registered_by=request.user,
        )
        return Response(PatientListSerializer(patient).data, status=status.HTTP_201_CREATED)


class PatientDetailView(generics.RetrieveAPIView):
    queryset = Patient.objects.all()
    serializer_class = PatientDetailSerializer
    permission_classes = [IsAuthenticated]


class DashboardSummaryView(APIView):
    def get(self, request):
        user = request.user
        now = timezone.now()
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        today_end = today_start + timedelta(days=1)

        appointments_qs = Appointment.objects.select_related("patient", "doctor").filter(
            date__gte=today_start.date(), date__lt=today_end.date()
        )
        if user.role == "DOCTOR":
            appointments_qs = appointments_qs.filter(doctor=user)
        todays_appointments = AppointmentSerializer(
            appointments_qs.order_by("time")[:8], many=True
        ).data

        recent_patients = []
        if user.role in ("RECORDS_OFFICER", "ADMIN"):
            recent_patients = PatientListSerializer(
                Patient.objects.all()[:5], many=True
            ).data

        return Response(
            {
                "patientCount": Patient.objects.count(),
                "activeStaff": User.objects.filter(is_active=True).count()
                if user.role == "ADMIN"
                else None,
                "todaysAppointments": todays_appointments,
                "pendingPrescriptions": Prescription.objects.filter(dispensed=False).count(),
                "pendingLabs": LabResult.objects.filter(status="PENDING").count(),
                "recentPatients": recent_patients,
            }
        )


class ReportsSummaryView(APIView):
    permission_classes = [IsAdmin]

    def get(self, request):
        now = timezone.now()
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)

        patient_count = Patient.objects.count()
        appointment_count = Appointment.objects.count()
        active_staff = User.objects.filter(is_active=True).count()
        dispensed_count = Prescription.objects.filter(dispensed=True).count()

        # Weekly registrations, last 8 weeks (Monday-start buckets)
        week_start = today_start - timedelta(days=today_start.weekday())
        weeks = []
        for i in range(7, -1, -1):
            start = week_start - timedelta(weeks=i)
            end = start + timedelta(days=7)
            weeks.append(
                {
                    "label": start.strftime("%d %b"),
                    "value": Patient.objects.filter(
                        created_at__gte=start, created_at__lt=end
                    ).count(),
                }
            )

        status_counts = {
            row["status"]: row["count"]
            for row in Appointment.objects.values("status").annotate(count=Count("id"))
        }
        appointment_status = [
            {"label": "Pending", "value": status_counts.get("PENDING", 0), "tone": "warning"},
            {"label": "Completed", "value": status_counts.get("COMPLETED", 0), "tone": "success"},
            {"label": "Cancelled", "value": status_counts.get("CANCELLED", 0), "tone": "danger"},
        ]

        top_diagnoses = list(
            MedicalRecord.objects.values("diagnosis")
            .annotate(value=Count("id"))
            .order_by("-value")[:6]
        )
        top_diagnoses = [{"label": d["diagnosis"], "value": d["value"]} for d in top_diagnoses]

        return Response(
            {
                "patientCount": patient_count,
                "appointmentCount": appointment_count,
                "activeStaff": active_staff,
                "dispensedCount": dispensed_count,
                "weeklyRegistrations": weeks,
                "appointmentStatus": appointment_status,
                "topDiagnoses": top_diagnoses,
            }
        )
