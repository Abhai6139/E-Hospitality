from django.db import models

# Create your models here.
from django.db import models
from django.contrib.auth.models import AbstractUser
# Create your models here.


class User(AbstractUser):
    ROLE_CHOICES=(
        ('admin', 'Admin'),
        ('doctor', 'Doctor'),
        ('patient', 'Patient')
        )
    role=models.CharField(max_length=250, choices=ROLE_CHOICES)

    groups = models.ManyToManyField(
        'auth.Group',
        related_name='custom_user_set',  # Change this to avoid conflict
        blank=True,
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='custom_user_permissions_set',  # Change this to avoid conflict
        blank=True,
    )


class Doctor(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    registration_number = models.CharField(max_length=20, blank=True)
    qualification = models.CharField(max_length=100, blank=True)
    specialization = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return self.user.username

class Patient(models.Model):
    user=models.OneToOneField(User, on_delete=models.CASCADE)
    Medical_history=models.TextField(blank=True)
    Age=models.CharField(max_length=50, blank=True)
    Gender=models.CharField(max_length=100, blank=True)
    Address=models.TextField(blank=True)


from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Timeslot(models.Model):
    doctor = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'role': 'doctor'})
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    is_available = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.doctor.username}: {self.date} from {self.start_time} to {self.end_time}"

class Appointment(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('viewed', 'Viewed'),
        ('completed', 'Completed')
    )

    patient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='patient_appointments', limit_choices_to={'role': 'patient'})
    doctor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='doctor_appointments', limit_choices_to={'role': 'doctor'})
    timeslot = models.ForeignKey(Timeslot, on_delete=models.SET_NULL, null=True, blank=True)
    status = models.CharField(max_length=100, choices=STATUS_CHOICES, default='pending')

    def __str__(self):
        return f"Appointment with Dr. {self.doctor.username} on {self.timeslot.date} at {self.timeslot.start_time}"

User = get_user_model()

class MedicalHistory(models.Model):
    patient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='medical_histories', limit_choices_to={'role': 'patient'})
    date = models.DateField()
    description = models.TextField()
    diagnosis = models.CharField(max_length=255)
    treatment = models.TextField()
    doctor = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, limit_choices_to={'role': 'doctor'})

    def __str__(self):
        return f"Medical History for {self.patient.username} on {self.date}"
    

# newapp/models.py
from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()

class Insurance(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    provider_name = models.CharField(max_length=100)
    policy_number = models.CharField(max_length=150)
    coverage_details = models.TextField()

    def __str__(self):
        return f"{self.patient.username} - {self.provider_name}"

class BillingStatement(models.Model):
    patient = models.ForeignKey(User, on_delete=models.CASCADE)
    description = models.CharField(max_length=255)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    is_paid = models.BooleanField(default=False)
    stripe_session_id = models.CharField(max_length=255, blank=True, null=True, unique=True)


    def __str__(self):
        return f"Bill for {self.patient.username} - {self.description}"

class Payment(models.Model):
    billing_statement = models.ForeignKey(BillingStatement, on_delete=models.CASCADE)
    payment_date = models.DateField(default=timezone.now)
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=50)
    transaction_id = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return f"Payment of ${self.amount_paid} on {self.payment_date} for {self.billing_statement.patient.username}"

from django.db import models

class Prescription(models.Model):
    doctor = models.ForeignKey(User, related_name="prescribed_doctor", on_delete=models.CASCADE)
    patient = models.ForeignKey(User, related_name="prescribed_patient", on_delete=models.CASCADE)
    medication_name = models.CharField(max_length=150)
    dosage = models.CharField(max_length=50)
    frequency = models.CharField(max_length=50)
    instructions = models.CharField(max_length=250, blank=True)
    date_prescribed = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.medication_name} for {self.patient.username}"
User = get_user_model()

class Medication(models.Model):
    prescription = models.ForeignKey(Prescription, related_name="medications", on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    description = models.TextField()
    side_effects = models.TextField(blank=True)
    medication_name = models.CharField(max_length=150)
    dosage = models.CharField(max_length=50)
    frequency = models.CharField(max_length=50)
    instructions = models.CharField(max_length=250, blank=True)

    def __str__(self):
        return self.name

# models.py
