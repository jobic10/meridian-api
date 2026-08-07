import datetime

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.utils import timezone

from clinical.models import LabResult, MedicalRecord, Prescription
from patients.models import Patient
from scheduling.models import Appointment

User = get_user_model()
DEMO_PASSWORD = "meridian123"


def days_from(base, offset, hour=9, minute=0):
    d = base + datetime.timedelta(days=offset)
    return d.replace(hour=hour, minute=minute, second=0, microsecond=0)


def years_ago(base, years, month, day):
    return datetime.date(base.year - years, month, day)


PATIENT_SEEDS = [
    dict(first_name="Chidinma", last_name="Okonkwo", gender="Female", years=34, month=3, day=12, blood_group="O+", allergies="Penicillin", phone="0803 214 7765"),
    dict(first_name="Emeka", last_name="Umeh", gender="Male", years=58, month=7, day=2, blood_group="A+", allergies=None, phone="0805 662 1190"),
    dict(first_name="Aisha", last_name="Mohammed", gender="Female", years=27, month=11, day=19, blood_group="B+", allergies=None, phone="0906 331 8842"),
    dict(first_name="Tobiloba", last_name="Ogunleye", gender="Male", years=6, month=1, day=30, blood_group="O-", allergies="Sulfa drugs", phone="0701 458 3320"),
    dict(first_name="Grace", last_name="Effiong", gender="Female", years=45, month=9, day=8, blood_group="AB+", allergies=None, phone="0813 902 4471"),
    dict(first_name="Ibrahim", last_name="Suleiman", gender="Male", years=62, month=4, day=22, blood_group="A-", allergies="Aspirin", phone="0902 117 6653"),
    dict(first_name="Blessing", last_name="Nwosu", gender="Female", years=19, month=6, day=4, blood_group="O+", allergies=None, phone="0810 774 2093"),
    dict(first_name="Segun", last_name="Ajayi", gender="Male", years=40, month=2, day=17, blood_group="B-", allergies=None, phone="0704 561 8827"),
    dict(first_name="Hadiza", last_name="Bello", gender="Female", years=3, month=5, day=25, blood_group="O+", allergies=None, phone="0816 330 9954"),
    dict(first_name="Chukwuemeka", last_name="Eze", gender="Male", years=71, month=10, day=11, blood_group="A+", allergies="Ibuprofen", phone="0803 665 2201"),
    dict(first_name="Folake", last_name="Adeoye", gender="Female", years=29, month=8, day=14, blood_group="AB-", allergies=None, phone="0909 224 6631"),
    dict(first_name="Yusuf", last_name="Abdullahi", gender="Male", years=52, month=12, day=3, blood_group="O+", allergies=None, phone="0705 883 1147"),
    dict(first_name="Ronke", last_name="Balogun", gender="Female", years=8, month=3, day=9, blood_group="B+", allergies="Penicillin", phone="0812 447 5560"),
    dict(first_name="Patrick", last_name="Osei", gender="Male", years=37, month=6, day=28, blood_group="A+", allergies=None, phone="0803 119 8834"),
]

VISIT_PLANS = [
    dict(symptoms="Persistent cough, mild fever for 4 days", diagnosis="Acute bronchitis", notes="Advised rest and fluids; review in a week if symptoms persist.", drugs=[("Amoxicillin", "500mg, 3x daily", "7 days")]),
    dict(symptoms="Headache and elevated blood pressure reading", diagnosis="Stage 1 hypertension", notes="Started on antihypertensives; recommended low-sodium diet.", drugs=[("Lisinopril", "10mg, once daily", "30 days")]),
    dict(symptoms="Abdominal pain and vomiting", diagnosis="Gastroenteritis", notes="Oral rehydration therapy commenced.", drugs=[("Oral Rehydration Salts", "1 sachet after each stool", "3 days"), ("Metronidazole", "400mg, 3x daily", "5 days")]),
    dict(symptoms="Joint pain and swelling in both knees", diagnosis="Osteoarthritis", notes="Referred for physiotherapy.", drugs=[("Diclofenac", "50mg, 2x daily", "10 days")]),
    dict(symptoms="Fever, chills and body aches", diagnosis="Malaria (P. falciparum)", notes="Confirmed via rapid diagnostic test.", drugs=[("Artemether/Lumefantrine", "4 tablets, 2x daily", "3 days")]),
    dict(symptoms="Routine antenatal review, no complaints", diagnosis="Normal antenatal visit — 28 weeks", notes="Foetal heart rate normal; next visit in 2 weeks.", drugs=[("Ferrous Sulphate", "200mg, once daily", "30 days")]),
    dict(symptoms="Sore throat and difficulty swallowing", diagnosis="Acute tonsillitis", notes="Advised warm saline gargles.", drugs=[("Amoxiclav", "625mg, 2x daily", "5 days")]),
    dict(symptoms="Skin rash with itching on both arms", diagnosis="Allergic dermatitis", notes="Suspected reaction to new detergent; avoid known irritant.", drugs=[("Cetirizine", "10mg, once daily", "7 days"), ("Hydrocortisone cream", "Apply thinly, 2x daily", "7 days")]),
]

REASONS = [
    "Follow-up consultation",
    "New complaint review",
    "Antenatal check-up",
    "Post-treatment review",
    "Routine check-up",
    "Vaccination",
]


class Command(BaseCommand):
    help = "Seed demo staff, patients, records and appointments."

    def handle(self, *args, **options):
        today = timezone.now()

        self.stdout.write("Clearing existing data...")
        LabResult.objects.all().delete()
        Prescription.objects.all().delete()
        MedicalRecord.objects.all().delete()
        Appointment.objects.all().delete()
        Patient.objects.all().delete()
        User.objects.all().delete()

        self.stdout.write("Seeding staff accounts...")
        admin = User.objects.create_user(
            username="admin", password=DEMO_PASSWORD, name="Adaeze Nwachukwu",
            email="adaeze.nwachukwu@ilera.example", role="ADMIN",
        )
        dr_adeyemi = User.objects.create_user(
            username="dr.adeyemi", password=DEMO_PASSWORD, name="Dr. Tunde Adeyemi",
            email="tunde.adeyemi@ilera.example", role="DOCTOR", specialisation="General Medicine",
        )
        dr_chukwu = User.objects.create_user(
            username="dr.chukwu", password=DEMO_PASSWORD, name="Dr. Ifeoma Chukwu",
            email="ifeoma.chukwu@ilera.example", role="DOCTOR", specialisation="Paediatrics",
        )
        nurse_okafor = User.objects.create_user(
            username="n.okafor", password=DEMO_PASSWORD, name="Ngozi Okafor",
            email="ngozi.okafor@ilera.example", role="NURSE",
        )
        records = User.objects.create_user(
            username="records", password=DEMO_PASSWORD, name="Bimpe Lawal",
            email="bimpe.lawal@ilera.example", role="RECORDS_OFFICER",
        )
        pharmacist = User.objects.create_user(
            username="pharm.bello", password=DEMO_PASSWORD, name="Musa Bello",
            email="musa.bello@ilera.example", role="PHARMACIST",
        )
        inactive_nurse = User.objects.create_user(
            username="k.fashola", password=DEMO_PASSWORD, name="Kunle Fashola",
            email="kunle.fashola@ilera.example", role="NURSE",
        )
        inactive_nurse.is_active = False
        inactive_nurse.save(update_fields=["is_active"])

        self.stdout.write("Seeding patients...")
        registrars = [records, admin]
        patients = []
        for i, p in enumerate(PATIENT_SEEDS, start=1):
            patient = Patient.objects.create(
                patient_code=f"PT-{today.year}-{i:04d}",
                first_name=p["first_name"],
                last_name=p["last_name"],
                gender=p["gender"],
                date_of_birth=years_ago(today.date(), p["years"], p["month"], p["day"]),
                address="Lagos, Nigeria",
                phone=p["phone"],
                next_of_kin=f"{p['last_name']} household",
                next_of_kin_phone=p["phone"],
                blood_group=p["blood_group"],
                allergies=p["allergies"],
                registered_by=registrars[i % len(registrars)],
            )
            Patient.objects.filter(pk=patient.pk).update(
                created_at=days_from(today, -(i * 6))
            )
            patients.append(patient)

        self.stdout.write("Seeding medical records, prescriptions and lab results...")
        doctors = [dr_adeyemi, dr_chukwu]
        record_index = 0
        for i, patient in enumerate(patients):
            visit_count = 2 if i % 3 == 0 else 1
            for _v in range(visit_count):
                plan = VISIT_PLANS[record_index % len(VISIT_PLANS)]
                doctor = doctors[record_index % len(doctors)]
                visit_date = days_from(today, -(record_index * 3 + 1))

                record = MedicalRecord.objects.create(
                    patient=patient,
                    doctor=doctor,
                    symptoms=plan["symptoms"],
                    diagnosis=plan["diagnosis"],
                    treatment_notes=plan["notes"],
                )
                MedicalRecord.objects.filter(pk=record.pk).update(
                    visit_date=visit_date, created_at=visit_date
                )

                for di, (drug, dosage, duration) in enumerate(plan["drugs"]):
                    is_dispensed = (record_index + di) % 3 != 0
                    Prescription.objects.create(
                        medical_record=record,
                        drug_name=drug,
                        dosage=dosage,
                        duration=duration,
                        dispensed=is_dispensed,
                        dispensed_by=pharmacist if is_dispensed else None,
                        dispensed_at=days_from(visit_date, 1) if is_dispensed else None,
                    )

                if record_index % 4 == 0:
                    has_result = record_index % 8 != 0
                    LabResult.objects.create(
                        patient=patient,
                        medical_record=record,
                        test_name="Full Blood Count",
                        result="WBC 7.2, Hb 13.1, Platelets 245" if has_result else None,
                        notes="Within normal range." if has_result else None,
                        status="COMPLETED" if has_result else "PENDING",
                        entered_by=nurse_okafor,
                        completed_at=days_from(visit_date, 1) if has_result else None,
                    )

                record_index += 1

        self.stdout.write("Seeding appointments...")
        appt_index = 0
        for i, patient in enumerate(patients):
            offsets = [-2, 3] if i % 2 == 0 else [5]
            for offset in offsets:
                doctor = doctors[appt_index % len(doctors)]
                hour = 9 + (appt_index % 6)
                Appointment.objects.create(
                    patient=patient,
                    doctor=doctor,
                    date=days_from(today, offset, hour).date(),
                    time=f"{hour:02d}:00",
                    reason=REASONS[appt_index % len(REASONS)],
                    status="COMPLETED" if offset < 0 else "PENDING",
                )
                appt_index += 1

        self.stdout.write(self.style.SUCCESS("\nDone. Seeded:"))
        self.stdout.write(f"  {len(patients)} patients")
        self.stdout.write(f"  {record_index} medical records")
        self.stdout.write(f"  {appt_index} appointments")
        self.stdout.write("\nDemo accounts (password: meridian123):")
        self.stdout.write("  admin        — Administrator")
        self.stdout.write("  dr.adeyemi   — Doctor (General Medicine)")
        self.stdout.write("  dr.chukwu    — Doctor (Paediatrics)")
        self.stdout.write("  n.okafor     — Nurse")
        self.stdout.write("  records      — Records Officer")
        self.stdout.write("  pharm.bello  — Pharmacist")
