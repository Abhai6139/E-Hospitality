# newapp/forms.py
from django import forms
from .models import *

class DoctorProfileForm(forms.ModelForm):
    class Meta:
        model = Doctor
        fields = ['registration_number', 'qualification', 'specialization']
        widgets = {
            'registration_number': forms.TextInput(attrs={'class': 'form-control'}),
            'qualification': forms.TextInput(attrs={'class': 'form-control'}),
            'specialization': forms.TextInput(attrs={'class': 'form-control'}),
        }

class PatientProfileForm(forms.ModelForm):
    class Meta:
        model=Patient
        fields=['Age', 'Gender', 'Address']
        widgets= {
            'Age':forms.TextInput(attrs={'class':'form-control'}),
            'Gender':forms.TextInput(attrs={'class':'form-control'}),
            'Address':forms.TextInput(attrs={'class':'form-control'})
        }

# newapp/forms.py
from django import forms
from .models import User

class UserRegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    confirm_password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ['username', 'password', 'confirm_password', 'role']
        widgets = {
            'role': forms.Select(attrs={'class': 'form-control'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password != confirm_password:
            self.add_error('confirm_password', "Passwords do not match.")

class TimeslotForm(forms.ModelForm):
    class Meta:
        model = Timeslot
        fields = ['date', 'start_time', 'end_time']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'start_time': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'end_time': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
        }

from django.core.exceptions import ValidationError

class AppointmentForm(forms.ModelForm):
    doctor = forms.ModelChoiceField(
        queryset=User.objects.filter(role='doctor'),
        widget=forms.Select(attrs={'class': 'form-control'}),
        label="Doctor"
    )

    class Meta:
        model = Appointment
        fields = ['doctor', 'timeslot']

    def __init__(self, *args, **kwargs):
        super(AppointmentForm, self).__init__(*args, **kwargs)
        self.fields['doctor'].queryset = User.objects.filter(role='doctor')
        # Customizing the label to show specialization along with the username
        self.fields['doctor'].label_from_instance = lambda obj: f"Dr. {obj.username} - {obj.doctor.specialization}"

    def clean_timeslot(self):
        timeslot = self.cleaned_data['timeslot']
        
        # Check if the selected timeslot already has 2 appointments
        existing_appointments = Appointment.objects.filter(timeslot=timeslot, status='scheduled').count()
        
        if existing_appointments >= 2:
            raise ValidationError("This timeslot is fully booked. Please select another timeslot.")
        
        return timeslot

class MedicalHistoryForm(forms.ModelForm):
    class Meta:
        model = MedicalHistory
        fields = ['date', 'description', 'diagnosis', 'treatment']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control'}),
            'diagnosis': forms.TextInput(attrs={'class': 'form-control'}),
            'treatment': forms.Textarea(attrs={'class': 'form-control'}),
        }


class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'role', 'is_active']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            
            'role': forms.Select(attrs={'class': 'form-control'}),
            'is_active': forms.CheckboxInput (attrs={'class': 'form-check-input'}),
        }

class InsuranceForm(forms.ModelForm):
    class Meta:
        model = Insurance
        fields = ['policy_number', 'provider_name', 'coverage_details']
        widgets = {
            'policy_number': forms.TextInput(attrs={'class': 'form-control'}),
            'provider_name': forms.TextInput(attrs={'class': 'form-control'}),
            'coverage_details': forms.Textarea(attrs={'class': 'form-control'}),
        }

class Appointment1Form(forms.ModelForm):
    doctor = forms.ModelChoiceField(queryset=User.objects.filter(role='doctor'), required=True)
    patient = forms.ModelChoiceField(queryset=User.objects.filter(role='patient'), required=True)
    timeslot = forms.ModelChoiceField(queryset=Timeslot.objects.filter(is_available=True), required=True)

    class Meta:
        model = Appointment
        fields = ['doctor', 'patient', 'timeslot', 'status']
        widgets = {
            'status': forms.Select(attrs={'class': 'form-control'}),
        }

class PrescriptionForm(forms.ModelForm):
    class Meta:
        model = Prescription
        fields = ['patient']  # You may add other fields if necessary

class MedicationForm(forms.ModelForm):
    class Meta:
        model = Medication
        fields = ['medication_name', 'dosage', 'frequency', 'instructions']