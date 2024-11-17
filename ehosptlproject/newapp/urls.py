from django.urls import path, include

from .views import *
from . import views


# router = DefaultRouter()
# router.register(r'users', Userview)
# router.register(r'patients', Patientview)
# router.register(r'doctors', Doctorview)
# router.register(r'appointments', Appointmentview)

urlpatterns = [
    #path('router/', include(router.urls)),
    path('register/', views.register, name='register'),
    path('appointment/book/', views.book_apointment, name='appointments'),
    path('', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/doctor/', views.doctor_dashboard, name='doctor_dashboard'),
    path('dashboard/admin/', views.admin_dashboard, name='admin_dashboard'),
    path('dashboard/admin/user/', views.UsersListview, name='userlist'),
    path('dashboard/admin/user/<int:user_id>/update/', views.update_user, name='update_user'),
    path('dashboard/admin/user/<int:user_id>/delete/', views.delete_user, name='delete_user'),
    path('dashboard/admin/appointments/', views.manage_appointments, name='manage_appointments'),
    path('dashboard/admin/appointments/add/', views.add_appointment, name='add_appointment'),
    path('dashboard/admin/appointments/<int:appointment_id>/update/', views.update_appointment, name='update_appointment'),
    path('dashboard/admin/appointments/<int:appointment_id>/delete/', views.delete_appointment, name='delete_appointment'),
    path('dashboard/patient/', views.patient_dashboard, name='patient_dashboard'),
    path('dashboard/doctor/manage_timeslots/', views.manage_timeslots, name='manage_timeslots'),
    path('dashboard/doctor/schedule/', views.Scheduledappointmentview, name='schedule'),
    path('dashboard/doctor/appointment/<int:appointment_id>/view_patient/', views.view_patient_profile, name='view_patient_profile'),
    path('dashboard/doctor/appointment/<int:appointment_id>/cancel/', views.cancel_appointment_by_doctor, name='cancel_appointment_by_doctor'),
    path('dashboard/doctor/prescriptions/add/<int:patient_id>/', views.add_medication, name='add_medication'),
    path('dashboard/doctor/prescriptions/<int:patient_id>/', views.view_prescriptions, name='view_prescriptions'),
    path('dashboard/doctor/prescriptions/delete/<int:patient_id>/<int:medication_id>/', views.delete_medication, name='delete_medication'),
    path('dashboard/doctor/prescriptions/send/<int:patient_id>/', views.send_to_pharmacy, name='send_to_pharmacy'),
    path('dashboard/patient/appointment/book/', views.book_appointment, name='book_appointment'),
    path('dashboard/patient/appointment/<int:appointment_id>/reschedule/', views.reschedule_appointment, name='reschedule_appointment'),
    path('dashboard/patient/appointment/<int:appointment_id>/cancel/', views.cancel_appointment, name='cancel_appointment'),
    path('dashboard/patient/medical_history/', views.view_medical_history, name='medical_history'),
    path('dashboard/patient/billing/', views.view_billing_statements, name='view_billing_statements'),
    #path('dashboard/patient/billing/<int:billing_id>/payment/', views.make_payment, name='make_payment'),
    path('dashboard/patient/insurance/', views.view_insurance_info, name='view_insurance_info'),
    path('dashboard/patient/insurance/add/', views.add_insurance_info, name='add_insurance_info'),
    path('dashboard/patient/education/', views.health_education_resources, name='health_education_resources'),
    path('appointments/viewed/<int:appointment_id>/', views.mark_as_viewed, name='mark_as_viewed'),
    path('billing/payment/<int:billing_id>/', views.make_payment, name='make_payment'),
    path('payment/success/', views.payment_success, name='payment_success'),
    path('payment/cancel/', views.payment_cancel, name='payment_cancel'),
]


