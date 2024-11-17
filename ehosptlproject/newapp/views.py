from django.shortcuts import render

# Create your views here.
from django.shortcuts import render

from . models import *


from django.shortcuts import render

def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()
            messages.success(request, "Registration successful.")
            return redirect('login')
    else:
        form = UserRegistrationForm()
    
    return render(request, 'register.html', {'form': form})


def book_apointment(request):
    return render(request, 'appointment.html')


# newapp/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from. forms import *

def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        
        # Authenticate the user
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)  # Log in the user

            if user.role == 'doctor':
                Doctor.objects.get_or_create(user=user)
            if user.role == 'patient':
                Patient.objects.get_or_create(user=user)
            # Redirect based on user role
            if user.role == 'patient':
                return redirect('patient_dashboard')
            elif user.role == 'doctor':
                return redirect('doctor_dashboard')
            elif user.role == 'admin':
                return redirect('admin_dashboard')
            else:
                messages.error(request, "Invalid role assigned.")
                return redirect('login')
        else:
            messages.error(request, "Invalid username or password.")
    
    return render(request, 'login.html')  # Render the login page

def logout_view(request):
    logout(request)  # Log out the user
    return redirect('login')  # Redirect to login page after logout

# newapp/views.py
from django.contrib.auth.decorators import login_required
from django.shortcuts import render




@login_required
def patient_dashboard(request):
    if request.user.role != 'patient':
        return redirect('login')  # Redirect if not a patient
    
    patient = get_object_or_404(Patient, user=request.user)
    
    if request.method == 'POST':
        form = PatientProfileForm(request.POST, instance=patient)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated successfully.")
            return redirect('patient_dashboard')
    else:
        form = PatientProfileForm(instance=patient)
    
    context = {
        'patient': patient,
        'form': form,
    }
    return render(request, 'patient_dashboard.html', context)

@login_required
def admin_dashboard(request):
    if request.user.role != 'admin':
        return redirect('login')  # Redirect if not an admin
    return render(request, 'admin_dashboard.html')





@login_required
def book_appointment(request):
    if request.user.role != 'patient':
        return redirect('login')

    if request.method == 'POST':
        form = AppointmentForm(request.POST)
        if form.is_valid():
            appointment = form.save(commit=False)
            appointment.patient = request.user
            appointment.status = 'scheduled'
            form.cleaned_data['timeslot'].is_available = False  # Mark timeslot as booked if needed
            form.cleaned_data['timeslot'].save()
            appointment.save()
            messages.success(request, "Appointment booked successfully.")
            return redirect('appointments')
        else:
            messages.error(request, "Error: " + str(form.errors['timeslot'][0]))
    else:
        form = AppointmentForm()

    return render(request, 'book_appointment.html', {'form': form})




@login_required
def reschedule_appointment(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id, patient=request.user)

    if request.method == 'POST':
        form = AppointmentForm(request.POST, instance=appointment)
        if form.is_valid():
            appointment.status = 'rescheduled'
            form.save()
            messages.success(request, "Appointment rescheduled successfully.")
            return redirect('appointments')
    else:
        form = AppointmentForm(instance=appointment)
    
    return render(request, 'reschedule_appointment.html', {'form': form})

@login_required
def cancel_appointment(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id, patient=request.user)
    appointment.status = 'canceled'
    appointment.save()
    messages.success(request, "Appointment canceled successfully.")
    return redirect('appointments')


@login_required
def doctor_dashboard(request):
    if request.user.role != 'doctor':
         return redirect('login')

     # Retrieve the doctor’s profile (created in login_view if not existing)
    doctor = get_object_or_404(Doctor, user=request.user)
    
    if request.method == 'POST':
         form = DoctorProfileForm(request.POST, instance=doctor)
         if form.is_valid():
             form.save()
             messages.success(request, "Profile updated successfully.")
             return redirect('doctor_dashboard')
    else:
         form = DoctorProfileForm(instance=doctor)

    context = {
         'doctor': doctor,
         'form': form,
     }
    # Get all scheduled appointments for this doctor
    
    return render(request, 'doctor_dashboard.html', context)


def Scheduledappointmentview(request):
    appointments = Appointment.objects.filter(doctor=request.user, status='scheduled').select_related('patient', 'timeslot')
    
    context = {
        'appointments': appointments,
    }
    return render(request, 'schedule.html', context)


@login_required
def manage_timeslots(request):
    if request.user.role != 'doctor':
        return redirect('login')

    if request.method == 'POST':
        form = TimeslotForm(request.POST)
        if form.is_valid():
            timeslot = form.save(commit=False)
            timeslot.doctor = request.user
            timeslot.save()
            messages.success(request, "Timeslot added successfully.")
            return redirect('manage_timeslots')
    else:
        form = TimeslotForm()

    # Show all timeslots for this doctor
    timeslots = Timeslot.objects.filter(doctor=request.user)

    return render(request, 'manage_timeslots.html', {'form': form, 'timeslots': timeslots})

@login_required
def view_patient_profile(request, appointment_id):
    # Ensure only doctors can access this view
    if request.user.role != 'doctor':
        return redirect('login')
    
    # Get the appointment and verify that the logged-in doctor is the one associated with it
    appointment = get_object_or_404(Appointment, id=appointment_id, doctor=request.user)
    patient = appointment.patient  # The patient associated with the appointment

    # Retrieve all medical history records for this patient
    medical_history = MedicalHistory.objects.filter(patient=patient).order_by('-date')

    # Handle the form submission to add a new medical history record
    if request.method == 'POST':
        form = MedicalHistoryForm(request.POST)
        if form.is_valid():
            new_record = form.save(commit=False)
            new_record.patient = patient
            new_record.doctor = request.user  # Associate the record with the logged-in doctor
            new_record.save()
            messages.success(request, "Medical history record added successfully.")
            return redirect('view_patient_profile', appointment_id=appointment.id)
    else:
        form = MedicalHistoryForm()

    context = {
        'patient': patient,
        'medical_history': medical_history,
        'form': form,
    }
    return render(request, 'view_patient_profile.html', context)

@login_required
def cancel_appointment_by_doctor(request, appointment_id):
    # Ensure the logged-in user is a doctor
    if request.user.role != 'doctor':
        return redirect('login')
    
    # Get the appointment and verify the doctor is the one associated with the appointment
    appointment = get_object_or_404(Appointment, id=appointment_id, doctor=request.user)
    appointment.status = 'canceled'  # Update the status to canceled
    appointment.save()
    messages.success(request, "Appointment canceled successfully.")
    return redirect('schedule')

@login_required
def view_medical_history(request):
    # Ensure only patients can access this view
    if request.user.role != 'patient':
        return redirect('login')

    # Retrieve all medical history records for the logged-in patient
    medical_history = MedicalHistory.objects.filter(patient=request.user).order_by('-date')

    context = {
        'medical_history': medical_history,
    }
    return render(request, 'view_medical_history.html', context)

@login_required
def view_billing_statements(request):
    # Ensure only patients can access this view
    if request.user.role != 'patient':
        return redirect('login')

    # Retrieve all billing statements for the logged-in patient
    billing_statements = BillingStatement.objects.filter(patient=request.user).order_by('amount')

    context = {
        'billing_statements': billing_statements,
    }
    return render(request, 'view_billing_statements.html', context)


@login_required
def mark_as_viewed(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id)
    if request.user != appointment.doctor:
        messages.error(request, "You are not authorized to update this appointment.")
        return redirect('doctor_schedule')

    # Update appointment status
    appointment.status = 'viewed'
    appointment.save()

    # Add a billing statement for the patient
    BillingStatement.objects.create(
        patient=appointment.patient,
        description="Consultation Fee",
        amount=300
    )

    messages.success(request, f"Appointment marked as viewed, and bill added for {appointment.patient.username}.")
    return redirect('schedule')



@login_required
def view_insurance_info(request):
    # Ensure only patients can access this view
    if request.user.role != 'patient':
        return redirect('login')

    patient = getattr(request.user, 'patient', None)
    if not patient:
        return redirect('no_patient')  # Redirect if no patient record is found

    # Try to get the insurance details for the patient
    insurance = Insurance.objects.filter(patient=patient).first()

    context = {
        'insurance': insurance,
    }
    return render(request, 'view_insurance_info.html', context)


@login_required
def UsersListview(request):
    if request.user.role != 'admin':
        return redirect('login')

    # Separate users based on their roles
    patients = User.objects.filter(role='patient')
    doctors = User.objects.filter(role='doctor')
    admins = User.objects.filter(role='admin')

    context = {
        'patients': patients,
        'doctors': doctors,
        'admins': admins,
    }
    return render(request, 'userslist.html', context)

@login_required
def update_user(request, user_id):
    # Ensure only admins can access this view
    if request.user.role != 'admin':
        return redirect('login')

    user = get_object_or_404(User, id=user_id)

    if request.method == 'POST':
        form = UserUpdateForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, f"User {user.username} updated successfully.")
            return redirect('userlist')
        else:
            messages.error(request, f"User {user.username} already exists.")
    else:
        form = UserUpdateForm(instance=user)

    context = {
        'form': form,
        'user': user,
    }
    return render(request, 'update_user.html', context)

@login_required
def delete_user(request, user_id):
    # Ensure only admins can access this view
    if request.user.role != 'admin':
        return redirect('login')

    user = get_object_or_404(User, id=user_id)

    # Delete the user
    if request.method == 'POST':
        user.delete()
        messages.success(request, f"User {user.username} deleted successfully.")
        return redirect('userlist')

    context = {
        'user': user,
    }
    return render(request, 'delete_user.html', context)

@login_required
def add_insurance_info(request):
    # Ensure only patients can access this view
    if request.user.role != 'patient':
        return redirect('login')

    patient = getattr(request.user, 'patient', None)
    if not patient:
        return redirect('no_patient')  # Redirect if no patient record is found

    if request.method == 'POST':
        form = InsuranceForm(request.POST)
        if form.is_valid():
            insurance = form.save(commit=False)
            insurance.patient = patient
            insurance.save()
            return redirect('view_insurance_info')  # Redirect to view the newly added insurance details
    else:
        form = InsuranceForm()

    context = {'form': form}
    return render(request, 'add_insurance_info.html', context)

@login_required
def health_education_resources(request):
    # Define educational content as examples
    resources = [
        {
            "title": "Healthy Eating Tips",
            "content": "Learn about balanced diets, nutritious foods, and more to improve your daily diet."
        },
        {
            "title": "Exercise and Fitness",
            "content": "Discover exercises and fitness routines to keep your body strong and healthy."
        },
        {
            "title": "Mental Wellness",
            "content": "Resources on managing stress, improving mental health, and practicing mindfulness."
        },
    ]

    context = {
        'resources': resources,
    }
    return render(request, 'health_education_resources.html', context)

@login_required
def manage_appointments(request):
    # Ensure only admins can access this view
    if request.user.role != 'admin':
        return redirect('login')

    appointments = Appointment.objects.all().order_by('timeslot__date', 'timeslot__start_time')
    context = {
        'appointments': appointments,
    }
    return render(request, 'manage_appointments.html', context)

@login_required
def add_appointment(request):
    if request.user.role != 'admin':
        return redirect('login')

    if request.method == 'POST':
        form = Appointment1Form(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Appointment created successfully.")
            return redirect('manage_appointments')
    else:
        form = Appointment1Form()

    return render(request, 'add_appointment.html', {'form': form})

@login_required
def update_appointment(request, appointment_id):
    if request.user.role != 'admin':
        return redirect('login')

    appointment = get_object_or_404(Appointment, id=appointment_id)
    if request.method == 'POST':
        form = Appointment1Form(request.POST, instance=appointment)
        if form.is_valid():
            form.save()
            messages.success(request, "Appointment updated successfully.")
            return redirect('manage_appointments')
    else:
        form = Appointment1Form(instance=appointment)

    return render(request, 'update_appointment.html', {'form': form, 'appointment': appointment})

@login_required
def delete_appointment(request, appointment_id):
    if request.user.role != 'admin':
        return redirect('login')

    appointment = get_object_or_404(Appointment, id=appointment_id)
    if request.method == 'POST':
        appointment.delete()
        messages.success(request, "Appointment deleted successfully.")
        return redirect('manage_appointments')

    return render(request, 'delete_appointment.html', {'appointment': appointment})

@login_required
def add_medication(request, patient_id):
    if request.method == "POST":
        # Retrieve the latest prescription for this patient
        try:
            prescription = Prescription.objects.filter(patient_id=patient_id).latest('date_prescribed')
        except Prescription.DoesNotExist:
            # Handle case if no prescription exists for this patient
            return redirect('view_prescriptions', patient_id=patient_id)
        
        # Get form data
        medication_name = request.POST.get("medication_name")
        dosage = request.POST.get("dosage")
        frequency = request.POST.get("frequency")
        instructions = request.POST.get("instructions")

        # Create a new Medication object
        Medication.objects.create(
            prescription=prescription,
            name=medication_name,
            dosage=dosage,
            frequency=frequency,
            instructions=instructions,
        )

        # Redirect back to the prescription view page
        return redirect('view_prescriptions', patient_id=patient_id)
from datetime import date
    
@login_required
def view_prescriptions(request, patient_id):
    patient = Patient.objects.get(id=patient_id)  # Get the patient's details
    prescription = Prescription.objects.filter(patient_id=patient_id)
    prescriptions_with_medications = [
        {
            'prescription': prescription,
            'medications': prescription.medications.all()
        }
        for prescription in prescription
    ]
    
    # Initialize the medication form
    form = MedicationForm()

    if request.method == 'POST':
        form = MedicationForm(request.POST)
        if form.is_valid():
            medication = form.save(commit=False)
            # Set the prescription here (you may pass this prescription ID with the POST request)
            prescription_id = request.POST.get('prescription_id')
            medication.prescription = Prescription.objects.get(id=prescription_id)
            medication.save()
            return redirect('view_prescriptions', patient_id=patient_id)

    context = {
        'prescriptions_with_medications': prescriptions_with_medications,
        'form': form,
        'patient_id': patient_id,
        'patient_name': patient.user.username,  # Use username as the patient's name
        'prescription_date': date.today()
    }
    return render(request, 'view_prescriptions.html', context)






@login_required
def delete_medication(request, patient_id, medication_id):
    medication = get_object_or_404(Medication, id=medication_id)
    medication.delete()
    messages.success(request, "Medication deleted successfully.")
    return redirect('view_prescriptions', patient_id=patient_id)

@login_required
def send_to_pharmacy(request, patient_id):
    # Get all prescriptions for the patient
    prescriptions = Prescription.objects.filter(patient_id=patient_id)
    
    if not prescriptions.exists():
        # Handle case when no prescription is found
        return render(request, 'error.html', {'message': 'No prescriptions found for this patient.'})
    
    # Assuming you want to send the latest prescription, use the most recent one
    prescription = prescriptions.latest('date_prescribed')  # or any other field to sort by

    # Logic to send the prescription to the pharmacy
    # For example:
    # pharmacy_service.send_prescription(prescription)
    
    # Clear the prescription details or redirect after sending
    prescriptions.delete()  # Optional: delete all prescriptions for the patient
    
    return redirect('view_prescriptions', patient_id=patient_id)


import stripe
from django.conf import settings
stripe.api_key = settings.STRIPE_SECRET_KEY

from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
import stripe
from django.conf import settings

@login_required
def make_payment(request, billing_id):
    # Retrieve the billing statement for the logged-in user
    billing_statement = get_object_or_404(BillingStatement, id=billing_id, patient=request.user)

    # Check if the bill is already paid
    if billing_statement.is_paid:
        messages.info(request, "This bill is already paid.")
        return redirect('view_billing_statements')

    # Set up Stripe API key
    stripe.api_key = settings.STRIPE_SECRET_KEY

    # Create a Stripe Checkout Session
    session = stripe.checkout.Session.create(
        payment_method_types=['card'],
        line_items=[{
            'price_data': {
                'currency': 'inr',
                'product_data': {
                    'name': billing_statement.description,
                },
                'unit_amount': int(billing_statement.amount * 100),  # Convert to cents
            },
            'quantity': 1,
        }],
        mode='payment',
        success_url=request.build_absolute_uri('/payment/success/') + '?session_id={CHECKOUT_SESSION_ID}',
        cancel_url=request.build_absolute_uri('/payment/cancel/'),
    )

    # Redirect to the Stripe payment page
    return redirect(session.url)


@login_required
def payment_success(request):
    session_id = request.GET.get('session_id')
    stripe.api_key = settings.STRIPE_SECRET_KEY

    # Retrieve the Stripe session
    session = stripe.checkout.Session.retrieve(session_id)

    # Retrieve the list of line items from the session
    line_items = stripe.checkout.Session.list_line_items(session_id)

    # Extract the description and amount from the first line item
    description = line_items['data'][0]['description']
    amount = line_items['data'][0]['amount_total'] / 100  # Convert cents to dollars

    # Retrieve all matching billing statements and mark them as paid
    billing_statements = BillingStatement.objects.filter(description=description, patient=request.user, amount=amount)

    if billing_statements.exists():
        for statement in billing_statements:
            statement.is_paid = True
            statement.save()
        messages.success(request, "Payment was successful!")
    else:
        messages.error(request, "No matching billing statement found.")

    return redirect('view_billing_statements')




@login_required
def payment_cancel(request):
    messages.warning(request, "Payment was canceled.")
    return redirect('view_billing_statements')
