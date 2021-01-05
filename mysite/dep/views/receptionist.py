from django.views.generic import CreateView, UpdateView, ListView
from django.contrib.auth import login
from django.core.mail import send_mail
from mysite.settings import EMAIL_HOST_USER
from datetime import datetime, timedelta, time
from django.urls import reverse_lazy, reverse
from django.forms.formsets import formset_factory
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.shortcuts import redirect, render, get_object_or_404
from ..models import Receptionist, ConnectionDoctorReceptionist, User, DoctorSessionTime, Doctor, AppointmentDoctorPatient, \
    Patient, DoctorSessionTimeOfTeleMedicine, AppointmentDoctorPatientOfTeleMedicine
from ..forms import ReceptionistSignUpForm, AddDoctorForm, DoctorAddSessionForm, DoctorChangeSessionForm
from ..decorators import receptionist_required


class ReceptionistSignUpView(CreateView):
    form_class = ReceptionistSignUpForm
    template_name = 'registration/signup_form.html'

    def get_context_data(self, **kwargs):
        kwargs['user_type'] = 'receptionist'
        return super().get_context_data(**kwargs)

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        return redirect('receptionist:index')


@method_decorator([login_required, receptionist_required], name='dispatch')
class ReceptionistDashboardView(ListView):
    model = ConnectionDoctorReceptionist
    template_name = 'receptionist/receptionist_dashboard.html'
    context_object_name = 'doctor_list'

    def get_queryset(self):
        r_id = Receptionist.objects.get(pk=self.request.user)
        return ConnectionDoctorReceptionist.objects.filter(receptionist=r_id)


@login_required
@receptionist_required
def add_doctor(request):
    if request.method == 'POST':
        form = AddDoctorForm(request.POST)
        if form.is_valid():
            doctor = form.cleaned_data['doctor']
            receptionist = Receptionist.objects.get(pk=request.user)
            count = ConnectionDoctorReceptionist.objects.filter(doctor=doctor, receptionist=receptionist).count()
            if count >= 1:
                return redirect('receptionist:index')
            else:
                ConnectionDoctorReceptionist.objects.create(doctor=doctor, receptionist=receptionist)
                return send_mail_to_doctor(request, doctor)
    else:
        form = AddDoctorForm()
    return render(request, 'receptionist/add_doctor.html', {'form': form})


@login_required
@receptionist_required
def send_mail_to_doctor(request, doctor):
    if request.method == 'POST':
        subject = 'FightDepression:You are added by receptionist'
        receptionist = User.objects.get(username=request.user)
        message = receptionist.username+' has added you.You can add the relation with receptionist from your ' \
                                        'dashboard..'
        recepient = User.objects.get(username=doctor).email
        send_mail(subject, message, EMAIL_HOST_USER, [recepient], fail_silently=False)
        return redirect('receptionist:index')


@login_required
@receptionist_required
def remove_doctor(request, doctor):
    receptionist = Receptionist.objects.get(pk=request.user)

    doctor_name = request.GET.get('doctor', '')
    temp = User.objects.get(username=doctor_name).id
    temp1 = Doctor.objects.get(user=temp)

    query_result = ConnectionDoctorReceptionist.objects.get(receptionist=receptionist, doctor=temp1).delete()
    return send_mail_to_doctor_when_removed(request, doctor_name)
'''
    try:
        query_result = AppointmentDoctorPatient.objects.filter(doctor=temp1).delete()
        query_result = DoctorSessionTime.objects.filter(doctor=temp1).delete()
    except AppointmentDoctorPatient.DoesNotExist:
        doctor = None
    return redirect('receptionist:index')
'''


@login_required
@receptionist_required
def send_mail_to_doctor_when_removed(request, doctor_name):
    subject = 'FightDepression:You are removed by receptionist'
    receptionist = User.objects.get(username=request.user)
    message = receptionist.username+' has removed you!'
    recepient = User.objects.get(username=doctor_name).email
    send_mail(subject, message, EMAIL_HOST_USER, [recepient], fail_silently=False)
    return redirect('receptionist:index')


@login_required
@receptionist_required
def receptionist_dashboard(request, pk):
    temp = User.objects.get(username=pk).id
    temp1 = Doctor.objects.get(user=temp)
    if temp1.telemedicine_facility == 'yes':
        telemedicine = 1
    else:
        telemedicine = None
    return render(request, 'receptionist/receptionist_access_dashboard.html', {'doctor': pk, 'telemedicine': telemedicine})


@login_required
@receptionist_required
def add_timings(request, doctor):
    doctor_name = request.GET.get('doctor', '')
    temp = User.objects.get(username=doctor_name).id
    temp1 = Doctor.objects.get(user=temp)

    count_of_days = DoctorSessionTime.objects.filter(doctor=temp1, date_of_appointment__gte=datetime.now().date()).\
        count()
    no_of_days_to_be_added = 7 - count_of_days

    add_timing_formset = formset_factory(DoctorAddSessionForm, extra=no_of_days_to_be_added)
    date_values = []
    date_value_in_format = []
    date_to_be_added = datetime.now()+timedelta(days=count_of_days)

    for i in range(no_of_days_to_be_added):
        ans = date_to_be_added.strftime("%d") + ' ' + date_to_be_added.strftime("%B") + '(' + \
            date_to_be_added.strftime("%A") + ')' + ' ' + date_to_be_added.strftime("%Y")
        date_value_in_format.append(date_to_be_added.date())
        date_values.append(ans)  # Yeh template side ke liye hai
        date_to_be_added += timedelta(days=1)

    if request.method == 'POST':
        formset = add_timing_formset(request.POST)
        if formset.is_valid():
            i = 0
            for form in formset:
                check_holiday = form.cleaned_data['holiday']
                enter_appointment_slots(request, temp1, form, date_value_in_format[i])

                if check_holiday == 'yes':
                    DoctorSessionTime.objects.create(doctor=temp1, session_1_from=None, session_1_to=None,
                                                     session_2_from=None, session_2_to=None,
                                                     date_of_appointment=date_value_in_format[i])

                else:
                    session_1_from = form.cleaned_data['session_1_from']
                    session_1_to = form.cleaned_data['session_1_to']
                    session_2_from = form.cleaned_data['session_2_from']
                    session_2_to = form.cleaned_data['session_2_to']
                    DoctorSessionTime.objects.create(doctor=temp1, session_1_from=session_1_from,
                                                     session_1_to=session_1_to, session_2_from=session_2_from,
                                                     session_2_to=session_2_to,
                                                     date_of_appointment=date_value_in_format[i])
                i += 1
            return redirect('receptionist:index')
    else:
        formset = add_timing_formset()
    return render(request, 'receptionist/add_sessions.html', {'data': zip(date_values, formset), 'formset': formset})


@login_required
@receptionist_required
def enter_appointment_slots(request, doctor, form, date):
    check_holiday = form.cleaned_data['holiday']
    if check_holiday == 'yes':
        AppointmentDoctorPatient.objects.create(doctor=doctor, date_of_appointment=date, slot_time=None)
    else:
        session_1_from = form.cleaned_data['session_1_from']
        session_1_to = form.cleaned_data['session_1_to']
        session_2_from = form.cleaned_data['session_2_from']
        session_2_to = form.cleaned_data['session_2_to']

        if session_1_from is None:
            AppointmentDoctorPatient.objects.create(doctor=doctor, date_of_appointment=date, slot_time=None)
        else:
            session_1_from_time = datetime.strptime(str(session_1_from), '%H:%M:%S')
            session_1_to_time = datetime.strptime(str(session_1_to), '%H:%M:%S')

            while session_1_from_time < session_1_to_time:
                AppointmentDoctorPatient.objects.create(doctor=doctor, date_of_appointment=date, slot_time=
                                                        session_1_from_time)
                session_1_from_time += timedelta(minutes=40)

        if session_2_from is None:
            AppointmentDoctorPatient.objects.create(doctor=doctor, date_of_appointment=date, slot_time=None)
        else:
            session_2_from_time = datetime.strptime(str(session_2_from), '%H:%M:%S')
            session_2_to_time = datetime.strptime(str(session_2_to), '%H:%M:%S')

            while session_2_from_time < session_2_to_time:
                AppointmentDoctorPatient.objects.create(doctor=doctor, date_of_appointment=date, slot_time=
                                                        session_2_from_time)
                session_2_from_time += timedelta(minutes=40)


@login_required
@receptionist_required
def change_timings(request, doctor):
    doctor_name = request.GET.get('doctor', '')
    temp = User.objects.get(username=doctor_name).id
    temp1 = Doctor.objects.get(user=temp)
    no_of_days_to_be_shown = DoctorSessionTime.objects.filter(doctor=temp1, date_of_appointment__gte=
                                                                            datetime.now().date()).count()

    add_timing_formset = formset_factory(DoctorChangeSessionForm, extra=no_of_days_to_be_shown)
    date_values = []
    date_value_in_format = []
    date_to_be_added = datetime.now() + timedelta(days=0)

    for i in range(no_of_days_to_be_shown):
        ans = date_to_be_added.strftime("%d") + ' ' + date_to_be_added.strftime("%B") + '(' + \
              date_to_be_added.strftime("%A") + ')' + ' ' + date_to_be_added.strftime("%Y")
        date_value_in_format.append(date_to_be_added.date())
        date_values.append(ans)  # Yeh template side ke liye hai
        date_to_be_added += timedelta(days=1)

    if request.method == 'POST':
        formset = add_timing_formset(request.POST)
        if formset.is_valid():
            i = 0
            for form in formset:
                check_change = form.cleaned_data['session_1_from']
                check_change = str(check_change)
                check_holiday = form.cleaned_data['holiday']
                print(date_value_in_format[i])
                if (check_change != 'None') or (check_holiday == 'yes'):
                    change_appointment_slots(request, temp1, form, date_value_in_format[i])
                    DoctorSessionTime.objects.filter(doctor=temp1, date_of_appointment=date_value_in_format[i]).delete()

                    if check_holiday == 'yes':
                        DoctorSessionTime.objects.create(doctor=temp1, session_1_from=None, session_1_to=None,
                                                         session_2_from=None, session_2_to=None,
                                                         date_of_appointment=date_value_in_format[i])

                    else:
                        session_1_from = form.cleaned_data['session_1_from']
                        session_1_to = form.cleaned_data['session_1_to']
                        session_2_from = form.cleaned_data['session_2_from']
                        session_2_to = form.cleaned_data['session_2_to']
                        DoctorSessionTime.objects.create(doctor=temp1, session_1_from=session_1_from,
                                                         session_1_to=session_1_to, session_2_from=session_2_from,
                                                         session_2_to=session_2_to,
                                                         date_of_appointment=date_value_in_format[i])
                i += 1
            return redirect('receptionist:index')
    else:
        formset = add_timing_formset()
    return render(request, 'receptionist/change_sessions.html', {'data': zip(date_values, formset), 'formset': formset})


@login_required
@receptionist_required
def change_appointment_slots(request, doctor, form, date):
    check_holiday = form.cleaned_data['holiday']
    AppointmentDoctorPatient.objects.filter(date_of_appointment=date, doctor=doctor).delete()
    if check_holiday == 'yes':
        AppointmentDoctorPatient.objects.create(doctor=doctor, date_of_appointment=date, slot_time=None)
    else:
        session_1_from = form.cleaned_data['session_1_from']
        session_1_to = form.cleaned_data['session_1_to']
        session_2_from = form.cleaned_data['session_2_from']
        session_2_to = form.cleaned_data['session_2_to']

        if session_1_from is None:
            AppointmentDoctorPatient.objects.create(doctor=doctor, date_of_appointment=date, slot_time=None)
        else:
            session_1_from_time = datetime.strptime(str(session_1_from), '%H:%M:%S')
            session_1_to_time = datetime.strptime(str(session_1_to), '%H:%M:%S')

            while session_1_from_time < session_1_to_time:
                AppointmentDoctorPatient.objects.create(doctor=doctor, date_of_appointment=date, slot_time=
                                                        session_1_from_time)
                session_1_from_time += timedelta(minutes=40)

        if session_2_from is None:
            AppointmentDoctorPatient.objects.create(doctor=doctor, date_of_appointment=date, slot_time=None)
        else:
            session_2_from_time = datetime.strptime(str(session_2_from), '%H:%M:%S')
            session_2_to_time = datetime.strptime(str(session_2_to), '%H:%M:%S')

            while session_2_from_time < session_2_to_time:
                AppointmentDoctorPatient.objects.create(doctor=doctor, date_of_appointment=date, slot_time=
                                                        session_2_from_time)
                session_2_from_time += timedelta(minutes=40)


@login_required
@receptionist_required
def add_timings_of_telemedicine(request, doctor):
    doctor_name = request.GET.get('doctor', '')
    temp = User.objects.get(username=doctor_name).id
    temp1 = Doctor.objects.get(user=temp)

    count_of_days = DoctorSessionTimeOfTeleMedicine.objects.filter(doctor=temp1, date_of_appointment__gte=datetime.now()
                                                                   .date()).count()
    no_of_days_to_be_added = 7 - count_of_days

    add_timing_formset = formset_factory(DoctorAddSessionForm, extra=no_of_days_to_be_added)
    date_values = []
    date_value_in_format = []
    date_to_be_added = datetime.now()+timedelta(days=count_of_days)

    for i in range(no_of_days_to_be_added):
        ans = date_to_be_added.strftime("%d") + ' ' + date_to_be_added.strftime("%B") + '(' + \
            date_to_be_added.strftime("%A") + ')' + ' ' + date_to_be_added.strftime("%Y")
        date_value_in_format.append(date_to_be_added.date())
        date_values.append(ans)  # Yeh template side ke liye hai
        date_to_be_added += timedelta(days=1)

    if request.method == 'POST':
        formset = add_timing_formset(request.POST)
        if formset.is_valid():
            i = 0
            for form in formset:
                check_holiday = form.cleaned_data['holiday']
                enter_appointment_slots_of_telemedicine(request, temp1, form, date_value_in_format[i])

                if check_holiday == 'yes':
                    DoctorSessionTimeOfTeleMedicine.objects.create(doctor=temp1, session_1_from=None, session_1_to=None,
                                                                   session_2_from=None, session_2_to=None,
                                                                   date_of_appointment=date_value_in_format[i])

                else:
                    session_1_from = form.cleaned_data['session_1_from']
                    session_1_to = form.cleaned_data['session_1_to']
                    session_2_from = form.cleaned_data['session_2_from']
                    session_2_to = form.cleaned_data['session_2_to']
                    DoctorSessionTimeOfTeleMedicine.objects.create(doctor=temp1, session_1_from=session_1_from,
                                                                   session_1_to=session_1_to, session_2_from=session_2_from,
                                                                   session_2_to=session_2_to,
                                                                   date_of_appointment=date_value_in_format[i])
                i += 1
            return redirect('receptionist:index')
    else:
        formset = add_timing_formset()
    return render(request, 'receptionist/add_sessions.html', {'data': zip(date_values, formset), 'formset': formset})


@login_required
@receptionist_required
def enter_appointment_slots_of_telemedicine(request, doctor, form, date):
    check_holiday = form.cleaned_data['holiday']
    if check_holiday == 'yes':
        AppointmentDoctorPatientOfTeleMedicine.objects.create(doctor=doctor, date_of_appointment=date, slot_time=None)
    else:
        session_1_from = form.cleaned_data['session_1_from']
        session_1_to = form.cleaned_data['session_1_to']
        session_2_from = form.cleaned_data['session_2_from']
        session_2_to = form.cleaned_data['session_2_to']

        if session_1_from is None:
            AppointmentDoctorPatientOfTeleMedicine.objects.create(doctor=doctor, date_of_appointment=date, slot_time=None)
        else:
            session_1_from_time = datetime.strptime(str(session_1_from), '%H:%M:%S')
            session_1_to_time = datetime.strptime(str(session_1_to), '%H:%M:%S')

            while session_1_from_time < session_1_to_time:
                AppointmentDoctorPatientOfTeleMedicine.objects.create(doctor=doctor, date_of_appointment=date, slot_time=
                                                                      session_1_from_time)
                session_1_from_time += timedelta(minutes=40)

        if session_2_from is None:
            AppointmentDoctorPatientOfTeleMedicine.objects.create(doctor=doctor, date_of_appointment=date, slot_time=None)
        else:
            session_2_from_time = datetime.strptime(str(session_2_from), '%H:%M:%S')
            session_2_to_time = datetime.strptime(str(session_2_to), '%H:%M:%S')

            while session_2_from_time < session_2_to_time:
                AppointmentDoctorPatientOfTeleMedicine.objects.create(doctor=doctor, date_of_appointment=date, slot_time=
                                                                      session_2_from_time)
                session_2_from_time += timedelta(minutes=40)


@login_required
@receptionist_required
def change_timings_of_telemedicine(request, doctor):
    doctor_name = request.GET.get('doctor', '')
    temp = User.objects.get(username=doctor_name).id
    temp1 = Doctor.objects.get(user=temp)
    no_of_days_to_be_shown = DoctorSessionTimeOfTeleMedicine.objects.filter(doctor=temp1, date_of_appointment__gte=
                                                                            datetime.now().date()).count()

    add_timing_formset = formset_factory(DoctorChangeSessionForm, extra=no_of_days_to_be_shown)
    date_values = []
    date_value_in_format = []
    date_to_be_added = datetime.now() + timedelta(days=0)

    for i in range(no_of_days_to_be_shown):
        ans = date_to_be_added.strftime("%d") + ' ' + date_to_be_added.strftime("%B") + '(' + \
              date_to_be_added.strftime("%A") + ')' + ' ' + date_to_be_added.strftime("%Y")
        date_value_in_format.append(date_to_be_added.date())
        date_values.append(ans)  # Yeh template side ke liye hai
        date_to_be_added += timedelta(days=1)

    if request.method == 'POST':
        formset = add_timing_formset(request.POST)
        if formset.is_valid():
            i = 0
            for form in formset:
                check_change = form.cleaned_data['session_1_from']
                check_change = str(check_change)
                check_holiday = form.cleaned_data['holiday']
                print(date_value_in_format[i])
                if (check_change != 'None') or (check_holiday == 'yes'):
                    change_appointment_slots_of_telemedicine(request, temp1, form, date_value_in_format[i])
                    DoctorSessionTimeOfTeleMedicine.objects.filter(doctor=temp1,
                                                                   date_of_appointment=date_value_in_format[i]).delete()

                    if check_holiday == 'yes':
                        DoctorSessionTimeOfTeleMedicine.objects.create(doctor=temp1, session_1_from=None,
                                                                       session_1_to=None, session_2_from=None,
                                                                       session_2_to=None, date_of_appointment=
                                                                       date_value_in_format[i])

                    else:
                        session_1_from = form.cleaned_data['session_1_from']
                        session_1_to = form.cleaned_data['session_1_to']
                        session_2_from = form.cleaned_data['session_2_from']
                        session_2_to = form.cleaned_data['session_2_to']
                        DoctorSessionTimeOfTeleMedicine.objects.create(doctor=temp1, session_1_from=session_1_from,
                                                                       session_1_to=session_1_to,
                                                                       session_2_from=session_2_from,session_2_to=
                                                                       session_2_to, date_of_appointment=
                                                                       date_value_in_format[i])
                i += 1
            return redirect('receptionist:index')
    else:
        formset = add_timing_formset()
    return render(request, 'receptionist/change_sessions.html', {'data': zip(date_values, formset), 'formset': formset})


@login_required
@receptionist_required
def change_appointment_slots_of_telemedicine(request, doctor, form, date):
    check_holiday = form.cleaned_data['holiday']
    AppointmentDoctorPatientOfTeleMedicine.objects.filter(doctor=doctor, date_of_appointment=date).delete()
    if check_holiday == 'yes':
        AppointmentDoctorPatientOfTeleMedicine.objects.create(doctor=doctor, date_of_appointment=date, slot_time=None)
    else:
        session_1_from = form.cleaned_data['session_1_from']
        session_1_to = form.cleaned_data['session_1_to']
        session_2_from = form.cleaned_data['session_2_from']
        session_2_to = form.cleaned_data['session_2_to']

        if session_1_from is None:
            AppointmentDoctorPatientOfTeleMedicine.objects.create(doctor=doctor, date_of_appointment=date, slot_time=None)
        else:
            session_1_from_time = datetime.strptime(str(session_1_from), '%H:%M:%S')
            session_1_to_time = datetime.strptime(str(session_1_to), '%H:%M:%S')

            while session_1_from_time < session_1_to_time:
                AppointmentDoctorPatientOfTeleMedicine.objects.create(doctor=doctor, date_of_appointment=date, slot_time=
                                                                      session_1_from_time)
                session_1_from_time += timedelta(minutes=40)

        if session_2_from is None:
            AppointmentDoctorPatientOfTeleMedicine.objects.create(doctor=doctor, date_of_appointment=date, slot_time=None)
        else:
            session_2_from_time = datetime.strptime(str(session_2_from), '%H:%M:%S')
            session_2_to_time = datetime.strptime(str(session_2_to), '%H:%M:%S')

            while session_2_from_time < session_2_to_time:
                AppointmentDoctorPatientOfTeleMedicine.objects.create(doctor=doctor, date_of_appointment=date, slot_time=
                                                                      session_2_from_time)
                session_2_from_time += timedelta(minutes=40)


@login_required
@receptionist_required
def patient_appointment_information(request):
    doctor_name = request.GET.get('doctor', '')
    temp = User.objects.get(username=doctor_name).id
    temp1 = Doctor.objects.get(user=temp)
    next = int(request.GET.get('next', ''))
    date_to_be_fetched = datetime.now()+timedelta(days=next)
    date_to_be_fetched = date_to_be_fetched.date()
    query = AppointmentDoctorPatient.objects.filter(doctor=temp1, date_of_appointment=date_to_be_fetched).\
        exclude(slot_time=None).order_by('slot_time')

    return render(request, 'receptionist/patient_appointment_information.html', {
        'doctor': temp1,
        'next': next+1,
        'appointment_info_list': query,
        'appointment_date': date_to_be_fetched
    })


@login_required
@receptionist_required
def approve_appointment(request):
    doctor = request.GET.get('doctor', '')
    patient_name = request.GET.get('patient', '')
    key = int(request.GET.get('pk', ''))

    AppointmentDoctorPatient.objects.filter(pk=key).update(is_accept=True)

    subject = 'FightDepression:Thanks for visiting us'
    message = 'Thanks for visiting us!!'
    recepient = User.objects.get(username=patient_name).email
    send_mail(subject, message, EMAIL_HOST_USER, [recepient], fail_silently=False)
    return redirect('receptionist:doctor_access', pk=doctor)


@login_required
@receptionist_required
def reject_appointment(request):
    doctor = request.GET.get('doctor', '')
    patient_name = request.GET.get('patient', '')
    key = int(request.GET.get('pk', ''))

    AppointmentDoctorPatient.objects.filter(pk=key).update(is_reject=True)

    subject = 'FightDepression:Cancelled Appointment'
    receptionist = User.objects.get(username=request.user)
    message = 'Since you have not visited clinic, Your appointment is cancelled.Go to your dashboard to take the ' \
              'appointment again'
    recepient = User.objects.get(username=patient_name).email
    send_mail(subject, message, EMAIL_HOST_USER, [recepient], fail_silently=False)
    return redirect('receptionist:doctor_access', pk=doctor)


@login_required
@receptionist_required
def patient_telemedicine_appointment_information(request):
    doctor_name = request.GET.get('doctor', '')
    temp = User.objects.get(username=doctor_name).id
    temp1 = Doctor.objects.get(user=temp)
    next = int(request.GET.get('next', ''))
    date_to_be_fetched = datetime.now() + timedelta(days=next)
    date_to_be_fetched = date_to_be_fetched.date()
    query = AppointmentDoctorPatientOfTeleMedicine.objects.filter(doctor=temp1, date_of_appointment=date_to_be_fetched).\
        exclude(slot_time=None).order_by('slot_time')

    return render(request, 'receptionist/patient_telemedicine_appointment_information.html', {
        'doctor': temp1,
        'next': next + 1,
        'appointment_info_list': query,
        'appointment_date': date_to_be_fetched
    })


@login_required
@receptionist_required
def approve_payment(request):
    doctor = request.GET.get('doctor', '')
    patient_name = request.GET.get('patient', '')
    key = int(request.GET.get('pk', ''))

    AppointmentDoctorPatientOfTeleMedicine.objects.filter(pk=key).update(is_accept=True)

    subject = 'FightDepression:Thanks for choosing us.'
    message = 'Thanks for visiting us!!'
    recepient = User.objects.get(username=patient_name).email
    send_mail(subject, message, EMAIL_HOST_USER, [recepient], fail_silently=False)
    return redirect('receptionist:doctor_access', pk=doctor)
