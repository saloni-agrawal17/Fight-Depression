from django.contrib.auth import login
from django.shortcuts import get_object_or_404, redirect, render, HttpResponseRedirect
from django.views.generic import (CreateView, DeleteView, DetailView, ListView,
                                  UpdateView, FormView)
from django.urls import reverse_lazy, reverse
from django.utils.decorators import method_decorator
from django.forms.formsets import formset_factory
from datetime import datetime, date
from django.http import JsonResponse
from ..models import User, Doctor, City, Location, Weekdays, DoctorEstablishmentTimings, ConnectionDoctorReceptionist, \
    Receptionist, AppointmentDoctorPatient, Phq9Score, RateDailyActivities, PatientTreatmentAndMedicineInfo, Patient, \
    HealthReports, AppointmentDoctorPatientOfTeleMedicine
from ..forms import DoctorSignUpForm, MedicalRegistrationForm, EducationQualificationForm, EstablishmentChoiceForm, \
    EstablishmentDetailsForm, UploadIdentityProofForm, UploadMedicalRegistrationProof, UploadEstablishmentProof, \
    AddExtraInformationOfDoctorForm, AddReceptionistForm, PatientTreatmentAndMedicineInfoForm, \
    AddReportsForTeleMedicineForm, UploadPhotoProof
from django.contrib.auth.decorators import login_required
from ..decorators import doctor_required


class DoctorSignUpView(CreateView):
    model = User
    form_class = DoctorSignUpForm
    template_name = 'registration/signup_form.html'

    def get_context_data(self, **kwargs):
        kwargs['user_type'] = 'doctor'
        return super().get_context_data(**kwargs)

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        return redirect('doctor:index')


@login_required
@doctor_required
def load_location(request):
    city_id = request.GET.get('city')
    locations = Location.objects.filter(city_id=city_id).order_by('name')
    return render(request, 'load_city/city_dropdown_list_options.html', {'cities': locations})


@method_decorator([login_required, doctor_required], name='dispatch')
class DoctorProfileDetailsView(UpdateView):
    model = Doctor
    form_class = MedicalRegistrationForm
    template_name = 'doctor/medical_registration.html'

    def get_success_url(self, **kwargs):
        return reverse('doctor:education_qualification', kwargs={'pk': self.object.pk})


@method_decorator([login_required, doctor_required], name='dispatch')
class DoctorEducationQualificationView(UpdateView):
    model = Doctor
    form_class = EducationQualificationForm
    template_name = 'doctor/education_qualification.html'
    success_url = reverse_lazy('doctor:clinic_details')

    def get_success_url(self, **kwargs):
        return reverse('doctor:clinic_details', kwargs={'pk': self.object.pk})


'''@method_decorator([login_required, doctor_required], name='dispatch')
class DoctorEstablishmentChoiceView(UpdateView):
    model = Doctor
    form_class = EstablishmentChoiceForm
    template_name = 'doctor/practice_perform.html'
    success_url = reverse_lazy('doctor:clinic_details')

    def get_success_url(self, **kwargs):
        return reverse('doctor:clinic_details', kwargs={'pk': self.object.pk})
'''


@method_decorator([login_required, doctor_required], name='dispatch')
class DoctorEstablishmentDetailsView(UpdateView):
    model = Doctor
    form_class = EstablishmentDetailsForm
    template_name = 'doctor/clinic_details.html'

    def get_context_data(self, **kwargs):
        doc = Doctor.objects.get(pk=self.request.user)
        context = super(DoctorEstablishmentDetailsView, self).get_context_data(**kwargs)
        '''
        if doc.establishment_choice == 'owns establishment':
            context['progress'] = 100
        else:
            context['progress'] = 83
        '''
        context['progress'] = 100
        return context

    def get_success_url(self):
        doc = Doctor.objects.get(pk=self.request.user)
        if doc.establishment_choice == 'owns establishment':
            return reverse('doctor:index')
        else:
            return reverse('doctor:practice_suggestions')


@method_decorator([login_required, doctor_required], name='dispatch')
class DoctorPracticeSuggestionsView(ListView):
    model = Doctor
    template_name = 'doctor/practice_suggestion.html'
    context_object_name = 'clinic_suggestions'

    def get_queryset(self):
        doc = Doctor.objects.get(pk=self.request.user)
        doc_city = doc.city_of_practice
        filtered_query = Doctor.objects.filter(city_of_practice=doc_city)
        return filtered_query


@method_decorator([login_required, doctor_required], name='dispatch')
class DoctorIdentityProofView(UpdateView):
    model = Doctor
    form_class = UploadIdentityProofForm
    template_name = 'doctor/identity_proof.html'

    def get_success_url(self, **kwargs):
        return reverse('doctor:registration_proof', kwargs={'pk': self.object.pk})


@method_decorator([login_required, doctor_required], name='dispatch')
class DoctorMedicalRegistrationProofView(UpdateView):
    model = Doctor
    form_class = UploadMedicalRegistrationProof
    template_name = 'doctor/medical_registration_proof.html'

    def get_success_url(self, **kwargs):
        return reverse('doctor:establishment_proof', kwargs={'pk': self.object.pk})


@method_decorator([login_required, doctor_required], name='dispatch')
class DoctorEstablishmentProofView(UpdateView):
    model = Doctor
    form_class = UploadEstablishmentProof
    template_name = 'doctor/clinic_proof.html'
    success_url = reverse_lazy('doctor:photo_proof')

    def get_success_url(self, **kwargs):
        return reverse('doctor:photo_proof', kwargs={'pk': self.object.pk})


@method_decorator([login_required, doctor_required], name='dispatch')
class DoctorPhotoProofView(UpdateView):
    model = Doctor
    form_class = UploadPhotoProof
    template_name = 'doctor/photo_proof.html'
    success_url = reverse_lazy('doctor:index')


@method_decorator([login_required, doctor_required], name='dispatch')
class DoctorExtraInformationView(UpdateView):
    model = Doctor
    form_class = AddExtraInformationOfDoctorForm
    template_name = 'doctor/add_extra_info.html'
    success_url = reverse_lazy('doctor:index')


@login_required
@doctor_required
def index(request):
    doctor = request.user.doctor
    ans = Doctor.objects.get(user=doctor).is_doctor
    temp1 = Doctor.objects.get(user=doctor)
    if temp1.telemedicine_facility == 'yes':
        telemedicine = 1
    else:
        telemedicine = None
    return render(request, 'doctor/doctor_dashboard.html', {'doctor': doctor, 'check': ans, 'telemedicine': telemedicine})


@method_decorator([login_required, doctor_required], name='dispatch')
class AddReceptionistView(FormView):
    form_class = AddReceptionistForm
    template_name = 'doctor/add_receptionist.html'

    def get_success_url(self):
        choice = self.form.cleaned_data['receptionist']
        user = Doctor.objects.get(pk=self.request.user)
        ConnectionDoctorReceptionist.objects.filter(doctor=user, pk=choice).update(is_accept=True)
        return reverse('doctor:index')

    def form_valid(self, form):
        self.form = form
        return HttpResponseRedirect(self.get_success_url())

    def get_form_kwargs(self):
        kwargs = super(AddReceptionistView, self).get_form_kwargs()
        user = Doctor.objects.get(pk=self.request.user)
        kwargs.update({'user': user})
        return kwargs


@login_required
@doctor_required
def check_patient(request):
    doctor = Doctor.objects.get(user=request.user)
    query_result = AppointmentDoctorPatient.objects.filter(doctor=doctor, date_of_appointment=datetime.now().date()). \
        exclude(patient=None)
    patient_list = list()
    for i in query_result:
        temp = list()
        temp.append(i.patient.p_name)
        temp.append(i.patient.p_sex)
        temp.append(i.patient.p_occupation)
        birth_date = i.patient.date_of_birth
        days_in_year = 365.2425
        age = int((date.today() - birth_date).days / days_in_year)
        temp.append(age)
        temp.append(i.patient)
        patient_list.append(temp)
    return render(request, 'doctor/list_of_patient_dashboard.html', {'patient_list': patient_list})


@login_required
@doctor_required
def check_patient_of_telemedicine(request):
    doctor = Doctor.objects.get(user=request.user)
    query_result = \
        AppointmentDoctorPatientOfTeleMedicine.objects.filter(doctor=doctor, date_of_appointment=datetime.now().date()). \
        exclude(patient=None)
    patient_list = list()
    for i in query_result:
        temp = list()
        temp.append(i.patient.p_name)
        temp.append(i.patient.p_sex)
        temp.append(i.patient.p_occupation)
        birth_date = i.patient.date_of_birth
        days_in_year = 365.2425
        age = int((date.today() - birth_date).days / days_in_year)
        temp.append(age)
        temp.append(i.patient)
        temp.append(i.patient.user.username)
        patient_list.append(temp)
    return render(request, 'doctor/list_of_telemedicine_patient_dashboard.html', {'patient_list': patient_list})


@login_required
@doctor_required
def review_report(request, patient):
    patient = request.GET.get('patient', '')
    return render(request, 'doctor/review_patient_report.html', {'patient': patient})


@login_required
@doctor_required
def phq9_questions_report(request, patient):
    patient = request.GET.get('patient', '')
    return render(request, 'doctor/phq9_questions_report.html', {'patient': patient})


@login_required
@doctor_required
def chart_phq9_question(request):
    patient = request.GET.get('patient', '')
    patient = User.objects.get(username=patient).pk
    result = Phq9Score.objects.filter(p_userid=patient)

    dates = []
    score = []
    for entry in result:
        dates.append('%s' % entry.date)
        score.append(entry.total)

    chart = {
        'chart': {'type': 'column'},
        'title': {'text': ' Graphical representation of PHQ-9 Questions'},
        'xAxis': {'categories': dates},
        'series': [{
            'name': 'Scores of each date',
            'data': score
        }]
    }
    return JsonResponse(chart)


@login_required
@doctor_required
def daily_activity_report(request, patient):
    patient = request.GET.get('patient', '')
    return render(request, 'doctor/review_daily_activity_report.html', {'patient': patient})


@login_required
@doctor_required
def chart_daily_report(request):
    patient = request.GET.get('patient', '')
    patient = User.objects.get(username=patient).pk
    result1 = RateDailyActivities.objects.filter(p_user=patient, relation_no=1)
    result2 = RateDailyActivities.objects.filter(p_user=patient, relation_no=2)
    result3 = RateDailyActivities.objects.filter(p_user=patient, relation_no=3)

    dates = []
    score1 = []
    score2 = []
    score3 = []
    for entry in result1:
        dates.append('%s' % entry.date)
        score1.append(entry.total)

    for entry in result2:
        score2.append(entry.total)

    for entry in result3:
        score3.append(entry.total)

    chart = {
        'chart': {'type': 'column'},
        'title': {'text': ' Graphical representation of Daily-Activity Questions'},
        'xAxis': {'categories': dates},
        'series': [{
            'name': 'Friend',
            'data': score1
        }, {
            'name': 'Relative',
            'data': score2
        }, {
            'name': 'Colleague',
            'data': score3
        }
        ]
    }
    return JsonResponse(chart)


@login_required
@doctor_required
def give_prescriptions(request, patient):
    get_patient = request.GET.get('patient', '')
    patient_id = User.objects.get(username=get_patient).pk
    patient_id = Patient.objects.get(user=patient_id)
    doctor_id = Doctor.objects.get(user=request.user)
    if request.method == 'POST':
        form = PatientTreatmentAndMedicineInfoForm(request.POST)
        if form.is_valid():
            medicine_name = form.cleaned_data['medicine_name']
            name_of_treatment = form.cleaned_data['name_of_treatment']
            PatientTreatmentAndMedicineInfo.objects.create(doctor=doctor_id, patient=patient_id, medicine_name=
                                                           medicine_name, name_of_treatment=name_of_treatment)
            return redirect('doctor:check_patient')
    form = PatientTreatmentAndMedicineInfoForm()
    result = PatientTreatmentAndMedicineInfo.objects.filter(patient=patient_id)
    return render(request, 'doctor/check_prescriptions.html', {'form': form, 'result': result})


@login_required
@doctor_required
def review_uploaded_reports(request, patient):
    get_patient = request.GET.get('patient', '')
    patient_id = User.objects.get(username=get_patient).pk
    patient_id = Patient.objects.get(user=patient_id)
    result= HealthReports.objects.filter(patient=patient_id)
    return render(request, 'doctor/view_uploaded_report.html', {'report_list': result})


@method_decorator([login_required, doctor_required], name='dispatch')
class AddReportsForTelemedicine(UpdateView):
    model = Doctor
    form_class = AddReportsForTeleMedicineForm
    template_name = 'doctor/add_reports_for_telemedicine.html'
    success_url = reverse_lazy('doctor:index')