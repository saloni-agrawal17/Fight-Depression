from django.contrib.auth import login
from django.shortcuts import redirect, render, get_object_or_404, HttpResponseRedirect
from django.views.generic import CreateView, UpdateView, ListView, FormView, DetailView
from django.urls import reverse_lazy, reverse
from django.core.mail import send_mail
from mysite.settings import EMAIL_HOST_USER
from django.contrib.auth.decorators import login_required
from ..decorators import patient_required
from ..forms import PatientSignUpForm, Phq9AnswerForm, AddCitiesStateForm, AddWellWishersForm, BookAppointmentForm,\
    UploadHealthReportsForm, BookTeleMedicineAppointmentForm
from ..models import City, Phq9Questions, Phq9Score, RelationTable, Patient, ConnectionPatientWellWishers, \
    ImageUploadedByWellWisher, VideoUploadedByWellWishers, Doctor, AppointmentDoctorPatient, User, HealthReports, \
    WellWishers, AppointmentDoctorPatientOfTeleMedicine
from django.forms.formsets import formset_factory
from datetime import datetime, timedelta
from django.db import transaction
from django.utils.decorators import method_decorator
from ..filters import DoctorFilters


class PatientSignUpView(CreateView):
    form_class = PatientSignUpForm
    template_name = 'registration/signup_form.html'

    def get_context_data(self, **kwargs):
        kwargs['user_type'] = 'patient'
        return super().get_context_data(**kwargs)

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        return redirect('patient:add_cities_state', pk=user.pk)


class PatientUpdateView(UpdateView):
    model = Patient
    form_class = AddCitiesStateForm
    success_url = reverse_lazy('patient:index')


def load_cities(request):
    state_id = request.GET.get('state')
    cities = City.objects.filter(state_id=state_id).order_by('name')
    print(cities)
    return render(request, 'load_city/city_dropdown_list_options.html', {'cities': cities})


@login_required
@patient_required
def index(request):
    res_count = AppointmentDoctorPatient.objects.filter(patient=request.user.patient, date_of_appointment__gt=
                                                        datetime.now().date()).count()
    res1_count = AppointmentDoctorPatient.objects.filter(patient=request.user.patient, date_of_appointment=
                                                         datetime.now().date(), slot_time__gte=datetime.now().time()).count()

    res_tele_count = AppointmentDoctorPatientOfTeleMedicine.objects.filter(patient=request.user.patient, date_of_appointment__gt=
                                                        datetime.now().date()).count()
    res1_tele_count = AppointmentDoctorPatientOfTeleMedicine.objects.filter(patient=request.user.patient, date_of_appointment=
                                                         datetime.now().date(), slot_time__gte=datetime.now().time()).count()

    relation_count = ConnectionPatientWellWishers.objects.filter(patient=request.user.patient, relation_no__gt=0).count()
    relation1 = RelationTable.objects.get(pk=1)
    relation2 = RelationTable.objects.get(pk=2)
    relation3 = RelationTable.objects.get(pk=3)

    friend = ConnectionPatientWellWishers.objects.filter(patient=request.user.patient, relation_no=relation1).count()
    relative = ConnectionPatientWellWishers.objects.filter(patient=request.user.patient, relation_no=relation2).count()
    colleague = ConnectionPatientWellWishers.objects.filter(patient=request.user.patient, relation_no=relation3).count()

    if res_count == 0 and res1_count == 0 and res_tele_count == 0 and res1_tele_count == 0:
        res_count = None
    else:
        res_count = 2
    if relation_count == 3:
        relation_count = None
    else:
        relation_count = 1
    return render(request, 'patient/patient_dashboard.html', {'res_count': res_count, 'relation_count': relation_count,
                                                              'friend': friend, 'relative': relative,
                                                              'colleague': colleague})


@login_required
@patient_required
def phq9_questions(request):
    patient = request.user.patient
    Phq9AnswerFormSet = formset_factory(Phq9AnswerForm, extra=10)
    if request.method == 'POST':
        formset = Phq9AnswerFormSet(request.POST)
        if formset.is_valid():
            lst = []
            for form in formset:
                data = form.cleaned_data['phq9_option']
                if data == 'Not at all':
                    lst.append(0)
                elif data == 'Several days':
                    lst.append(1)
                elif data == 'More than half days':
                    lst.append(2)
                else:
                    lst.append(3)
            total = sum(lst)
            Phq9Score.objects.create(q1=lst[0], q2=lst[1], q3=lst[2], q4=lst[3], q5=lst[4], q6=lst[5], q7=lst[6],
                                     q8=lst[7], q9=lst[8], q10=lst[9], date=datetime.today(), total=total,
                                     p_userid=patient)

        return render(request, 'patient/patient_dashboard.html')
    else:
        questions = Phq9Questions.objects.all()
        formset = Phq9AnswerFormSet()
    return render(request, 'patient/phq9_question.html', {'data': zip(questions, formset), 'formset': formset})


def send_mail_to_patient(wellwisher, user):
    recepient = User.objects.get(username=wellwisher).email
    subject = 'FightDepression:You are added by patient'
    message = user.p_name + ' has added you.You can add the relation with wellwisher from your dashboard..'
    send_mail(subject, message, EMAIL_HOST_USER, [recepient], fail_silently=False)


@method_decorator([login_required, patient_required], name='dispatch')
class AddWellWisher1View(FormView):
    form_class = AddWellWishersForm
    template_name = 'patient/add_well_wishers.html'

    def get_success_url(self):
        wellwisher = self.form.cleaned_data['well_wisher']
        well_wisher = User.objects.get(username=wellwisher).pk
        well_wisher = WellWishers.objects.get(pk=well_wisher)

        relation_name = RelationTable.objects.get(pk=1)
        user = Patient.objects.get(pk=self.request.user)
        count = ConnectionPatientWellWishers.objects.filter(patient=user, well_wisher=well_wisher).count()

        if count == 1:
            query = ConnectionPatientWellWishers.objects.get(patient=user, well_wisher=well_wisher).relation_no
            if query is None:
                ConnectionPatientWellWishers.objects.filter(patient=user, well_wisher=well_wisher).\
                    update(relation_no=relation_name)
            else:
                ConnectionPatientWellWishers.objects.create(patient=user, well_wisher=well_wisher,
                                                            relation_no=relation_name)
        elif count > 1:
            ConnectionPatientWellWishers.objects.create(patient=user, well_wisher=well_wisher, relation_no=relation_name)
        send_mail_to_patient(wellwisher, user)
        return reverse('patient:index')

    def form_valid(self, form):
        self.form = form
        return HttpResponseRedirect(self.get_success_url())

    def get_form_kwargs(self):
        kwargs = super(AddWellWisher1View, self).get_form_kwargs()
        user = Patient.objects.get(pk=self.request.user)
        kwargs.update({'user': user})
        return kwargs

    def get_context_data(self, **kwargs):
        context = super(AddWellWisher1View, self).get_context_data(**kwargs)
        context['friend'] = 'Friend'
        return context


@method_decorator([login_required, patient_required], name='dispatch')
class AddWellWisher2View(FormView):
    form_class = AddWellWishersForm
    template_name = 'patient/add_well_wishers.html'

    def get_success_url(self):
        wellwisher = self.form.cleaned_data['well_wisher']
        well_wisher = User.objects.get(username=wellwisher).pk
        well_wisher = WellWishers.objects.get(pk=well_wisher)

        relation_name = RelationTable.objects.get(pk=2)
        user = Patient.objects.get(pk=self.request.user)
        count = ConnectionPatientWellWishers.objects.filter(patient=user, well_wisher=well_wisher).count()

        if count == 1:
            query = ConnectionPatientWellWishers.objects.get(patient=user, well_wisher=well_wisher).relation_no
            if query is None:
                ConnectionPatientWellWishers.objects.filter(patient=user, well_wisher=well_wisher). \
                    update(relation_no=relation_name)
            else:
                ConnectionPatientWellWishers.objects.create(patient=user, well_wisher=well_wisher,
                                                            relation_no=relation_name)
        elif count > 1:
            ConnectionPatientWellWishers.objects.create(patient=user, well_wisher=well_wisher,
                                                        relation_no=relation_name)
        send_mail_to_patient(wellwisher, user)
        return reverse('patient:index')

    def form_valid(self, form):
        self.form = form
        return HttpResponseRedirect(self.get_success_url())

    def get_form_kwargs(self):
        kwargs = super(AddWellWisher2View, self).get_form_kwargs()
        user = Patient.objects.get(pk=self.request.user)
        kwargs.update({'user': user})
        return kwargs

    def get_context_data(self, **kwargs):
        context = super(AddWellWisher2View, self).get_context_data(**kwargs)
        context['friend'] = 'Relative'
        return context


@method_decorator([login_required, patient_required], name='dispatch')
class AddWellWisher3View(FormView):
    form_class = AddWellWishersForm
    template_name = 'patient/add_well_wishers.html'

    def get_success_url(self):
        wellwisher = self.form.cleaned_data['well_wisher']
        well_wisher = User.objects.get(username=wellwisher).pk
        well_wisher = WellWishers.objects.get(pk=well_wisher)

        relation_name = RelationTable.objects.get(pk=3)

        user = Patient.objects.get(pk=self.request.user)
        count = ConnectionPatientWellWishers.objects.filter(patient=user, well_wisher=well_wisher).count()

        if count == 1:
            query = ConnectionPatientWellWishers.objects.get(patient=user, well_wisher=well_wisher).relation_no
            if query is None:
                ConnectionPatientWellWishers.objects.filter(patient=user, well_wisher=well_wisher). \
                    update(relation_no=relation_name)
            else:
                ConnectionPatientWellWishers.objects.create(patient=user, well_wisher=well_wisher,
                                                            relation_no=relation_name)
        elif count > 1:
            ConnectionPatientWellWishers.objects.create(patient=user, well_wisher=well_wisher,
                                                        relation_no=relation_name)
        send_mail_to_patient(wellwisher, user)
        return reverse('patient:index')

    def form_valid(self, form):
        self.form = form
        return HttpResponseRedirect(self.get_success_url())

    def get_form_kwargs(self):
        kwargs = super(AddWellWisher3View, self).get_form_kwargs()
        user = Patient.objects.get(pk=self.request.user)
        kwargs.update({'user': user})
        return kwargs

    def get_context_data(self, **kwargs):
        context = super(AddWellWisher3View, self).get_context_data(**kwargs)
        context['friend'] = 'Colleague'
        return context


@method_decorator([login_required, patient_required], name='dispatch')
class ImagesListView(ListView):
    model = ImageUploadedByWellWisher
    template_name = 'patient/list_images.html'
    context_object_name = 'image_list'

    def get_queryset(self, **kwargs):
        p_id = Patient.objects.get(pk=self.request.user)
        return ImageUploadedByWellWisher.objects.filter(patient_id=p_id).order_by('well_wisher')


@login_required
@patient_required
def remove_photo(request):
    image_name = request.GET.get('image_name', '')
    query_result = ImageUploadedByWellWisher.objects.get(pk=image_name).delete()
    return redirect('patient:index')


@method_decorator([login_required, patient_required], name='dispatch')
class VideoListView(ListView):
    model = VideoUploadedByWellWishers
    template_name = 'patient/list_videos.html'
    context_object_name = 'videos_list'

    def get_queryset(self, **kwargs):
        p_id = Patient.objects.get(pk=self.request.user)
        return VideoUploadedByWellWishers.objects.filter(patient_id=p_id).order_by('well_wisher')


@login_required
@patient_required
def remove_video(request):
    video_name = request.GET.get('video_name', '')
    query_result = VideoUploadedByWellWishers.objects.get(pk=video_name).delete()
    return redirect('patient:index')


@login_required
@patient_required
def choose_doctor_from_dashboard(request):
    queryList = Doctor.objects.filter(is_doctor=True)
    user_filter = DoctorFilters(request.GET, queryset=queryList)

    if 'gender' in request.GET and request.GET['gender']:
        gender = request.GET['gender']
        queryList = queryList.filter(gender=gender)
        user_filter = DoctorFilters(request.GET, queryset=queryList)

    if 'city_of_practice' in request.GET and request.GET['city_of_practice']:
        city = request.GET['city_of_practice']
        queryList = queryList.filter(city_of_practice=city)
        user_filter = DoctorFilters(request.GET, queryset=queryList)

    return render(request, 'patient/choose_doctor_dashboard.html', {'filter': user_filter})


@login_required
@patient_required
def choose_doctors_for_telemedicine(request):
    queryList = Doctor.objects.filter(is_doctor=True, telemedicine_facility='yes')
    user_filter = DoctorFilters(request.GET, queryset=queryList)

    if 'gender' in request.GET and request.GET['gender']:
        gender = request.GET['gender']
        queryList = queryList.filter(gender=gender)
        user_filter = DoctorFilters(request.GET, queryset=queryList)

    if 'city' in request.GET and request.GET['city']:
        city = request.GET['city']
        queryList = queryList.filter(city=city)
        user_filter = DoctorFilters(request.GET, queryset=queryList)

    return render(request, 'patient/choose_doctor_for_telemedicine_dashboard.html', {'filter': user_filter})


@method_decorator([login_required, patient_required], name='dispatch')
class DoctorInformationView(DetailView):
    model = Doctor
    template_name = 'patient/doctor_information.html'
    context_object_name = 'doctor'


@method_decorator([login_required, patient_required], name='dispatch')
class DoctorTeleMedicineInformationView(DetailView):
    model = Doctor
    template_name = 'patient/doctor_telemedicine_information.html'
    context_object_name = 'doctor'


@login_required
@patient_required
def load_slot_timings(request):
    date_id = request.GET.get('date_id')
    date = datetime.now().date()+timedelta(days=int(date_id))
    doctor_name = request.GET.get('doctor')
    doctor = User.objects.get(username=doctor_name).pk
    slot_timings = AppointmentDoctorPatient.objects.filter(date_of_appointment=date, doctor=doctor).\
        exclude(patient__gt=0).exclude(slot_time=None)
    return render(request, 'patient/slot_dropdown_list_options.html', {'slots': slot_timings})


@login_required
@patient_required
def load_slot_timings_for_telemedicine(request):
    date_id = request.GET.get('date_id')
    date = datetime.now().date() + timedelta(days=int(date_id))
    doctor_name = request.GET.get('doctor')
    doctor = User.objects.get(username=doctor_name).pk
    slot_timings = AppointmentDoctorPatientOfTeleMedicine.objects.filter(date_of_appointment=date, doctor=doctor).\
        exclude(patient__gt=0).exclude(slot_time=None)
    return render(request, 'patient/slot_dropdown_list_options.html', {'slots': slot_timings})


@method_decorator([login_required, patient_required], name='dispatch')
class BookAppointmentView(FormView):
    form_class = BookAppointmentForm
    template_name = 'patient/book_appointment.html'

    def get_context_data(self, **kwargs):
        context = super(BookAppointmentView, self).get_context_data(**kwargs)
        doctor_name = self.request.GET.get('doctor', '')
        context['doctor'] = doctor_name
        return context

    def get_form_kwargs(self):
        kwargs = super(BookAppointmentView, self).get_form_kwargs()
        doctor_name = self.request.GET.get('doctor')
        doctor = User.objects.get(username=doctor_name).pk
        kwargs.update({'doctor': doctor})
        return kwargs

    def form_valid(self, form):
        self.form = form
        return HttpResponseRedirect(self.get_success_url())

    @transaction.atomic
    def get_success_url(self):
        choice = self.form.cleaned_data['slot_timings']
        patient = Patient.objects.get(pk=self.request.user)
        AppointmentDoctorPatient.objects.filter(pk=choice).update(patient=patient)
        return reverse('patient:index')


@method_decorator([login_required, patient_required], name='dispatch')
class BookAppointmentForTeleMedicineView(FormView):
    form_class = BookTeleMedicineAppointmentForm
    template_name = 'patient/book_appointment_for_telemedicine.html'

    def get_context_data(self, **kwargs):
        context = super(BookAppointmentForTeleMedicineView, self).get_context_data(**kwargs)
        doctor_name = self.request.GET.get('doctor', '')
        context['doctor'] = doctor_name
        return context

    def get_form_kwargs(self):
        kwargs = super(BookAppointmentForTeleMedicineView, self).get_form_kwargs()
        doctor_name = self.request.GET.get('doctor')
        doctor = User.objects.get(username=doctor_name).pk
        kwargs.update({'doctor': doctor})
        return kwargs

    def form_valid(self, form):
        self.form = form
        return HttpResponseRedirect(self.get_success_url())

    @transaction.atomic
    def get_success_url(self):
        choice = self.form.cleaned_data['slot_timings']
        patient = Patient.objects.get(pk=self.request.user)
        AppointmentDoctorPatientOfTeleMedicine.objects.filter(pk=choice).update(patient=patient)
        return reverse('patient:index')


@method_decorator([login_required, patient_required], name='dispatch')
class CheckAppointmentView(ListView):
    model = AppointmentDoctorPatient
    template_name = 'patient/check_appointments.html'
    context_object_name = 'appointment_info_list'

    def get_queryset(self):
        patient = Patient.objects.get(pk=self.request.user)
        filtered_query = AppointmentDoctorPatient.objects.filter(patient=patient, date_of_appointment__gte=
                                                                 datetime.now().date())
        return filtered_query


@login_required
@patient_required
def check_appointment_of_patient(request):
    patient = Patient.objects.get(pk=request.user)
    filtered_query = AppointmentDoctorPatient.objects.filter(patient=patient, date_of_appointment__gte=
                                                             datetime.now().date())
    return render(request, 'patient/check_appointments.html', {'appointment_info_list': filtered_query})


@login_required
@patient_required
def check_telemedicine_appointments_of_patient(request):
    patient = Patient.objects.get(pk=request.user)
    filtered_query_for_telemedicine = AppointmentDoctorPatientOfTeleMedicine.objects.filter\
        (patient=patient, date_of_appointment__gte=datetime.now().date())
    return render(request, 'patient/check_telemedicine_appointments.html', {'appointment_info_list_telemedicine':
                                                               filtered_query_for_telemedicine})


@login_required
@patient_required
def cancel_appointments(request, cancel):
    pk = request.GET.get('cancel', '')
    AppointmentDoctorPatient.objects.filter(pk=pk).update(patient=None)
    return render(request, 'patient/patient_dashboard.html')


@login_required
@patient_required
def cancel_tele_appointments(request, cancel):
    pk = request.GET.get('cancel', '')
    AppointmentDoctorPatientOfTeleMedicine.objects.filter(pk=pk).update(patient=None)
    return render(request, 'patient/patient_dashboard.html')


@login_required
@patient_required
def reschedule_appointments(request, reschedule):
    pk = request.GET.get('reschedule', '')
    AppointmentDoctorPatient.objects.filter(pk=pk).update(patient=None)
    doctor = AppointmentDoctorPatient.objects.get(pk=pk).doctor
    doc = Doctor.objects.get(pk=doctor).pk
    return redirect('patient:book_appointment', doctor=doc)


@login_required
@patient_required
def upload_report(request):
    patient = Patient.objects.get(pk=request.user)

    if "add_more" in request.POST:
        form = UploadHealthReportsForm(request.POST, request.FILES)
        if form.is_valid():
            description = form.cleaned_data['name_of_report']
            img = form.cleaned_data['image']
            HealthReports.objects.create(patient=patient, name_of_report=description, image=img)
            form = UploadHealthReportsForm()
    elif "final_submit" in request.POST:
        form = UploadHealthReportsForm(request.POST, request.FILES)
        if form.is_valid():
            description = form.cleaned_data['name_of_report']
            img = form.cleaned_data['image']
            HealthReports.objects.create(patient=patient, name_of_report=description, image=img)
            return redirect('patient:index')
    else:
        form = UploadHealthReportsForm()
    return render(request, 'patient/upload_report.html', {'form': form})


@method_decorator([login_required, patient_required], name='dispatch')
class HealthReportListView(ListView):
    model = HealthReports
    template_name = 'patient/list_health_reports.html'
    context_object_name = 'reports_list'

    def get_queryset(self, **kwargs):
        p_id = Patient.objects.get(pk=self.request.user)
        return HealthReports.objects.filter(patient_id=p_id)


@method_decorator([login_required, patient_required], name='dispatch')
class ChangeWellWisher1(FormView):
    form_class = AddWellWishersForm
    template_name = 'patient/change_well_wishers.html'

    def get_success_url(self):
        wellwisher = self.form.cleaned_data['well_wisher']
        well_wisher = User.objects.get(username=wellwisher).pk
        well_wisher = WellWishers.objects.get(pk=well_wisher)

        relation_name = RelationTable.objects.get(pk=1)
        user = Patient.objects.get(pk=self.request.user)
        ConnectionPatientWellWishers.objects.filter(patient=user, relation_no=relation_name).update(relation_no=None)
        ConnectionPatientWellWishers.objects.filter(patient=user, well_wisher=well_wisher).update(relation_no=relation_name)
        print('ABC')
        print(wellwisher)
        send_mail_to_patient(wellwisher, user)
        return reverse('patient:index')

    def form_valid(self, form):
        self.form = form
        return HttpResponseRedirect(self.get_success_url())

    def get_form_kwargs(self):
        kwargs = super(ChangeWellWisher1, self).get_form_kwargs()
        user = Patient.objects.get(pk=self.request.user)
        kwargs.update({'user': user})
        return kwargs

    def get_context_data(self, **kwargs):
        context = super(ChangeWellWisher1, self).get_context_data(**kwargs)
        relation_name = RelationTable.objects.get(pk=1)
        user = Patient.objects.get(pk=self.request.user)
        try:
            query = ConnectionPatientWellWishers.objects.get(patient=user, relation_no=relation_name).well_wisher
            context['friend'] = 'Your current Friend is '+str(query)
        except ConnectionPatientWellWishers.DoesNotExist:
            context['friend'] = None
        return context


@method_decorator([login_required, patient_required], name='dispatch')
class ChangeWellWisher2(FormView):
    form_class = AddWellWishersForm
    template_name = 'patient/change_well_wishers.html'

    def get_success_url(self):
        wellwisher = self.form.cleaned_data['well_wisher']
        well_wisher = User.objects.get(username=wellwisher).pk
        well_wisher = WellWishers.objects.get(pk=well_wisher)

        relation_name = RelationTable.objects.get(pk=2)
        user = Patient.objects.get(pk=self.request.user)
        ConnectionPatientWellWishers.objects.filter(patient=user, relation_no=relation_name).update(relation_no=None)
        ConnectionPatientWellWishers.objects.filter(patient=user, well_wisher=well_wisher).update(relation_no=relation_name)
        send_mail_to_patient(wellwisher, user)
        return reverse('patient:index')

    def form_valid(self, form):
        self.form = form
        return HttpResponseRedirect(self.get_success_url())

    def get_form_kwargs(self):
        kwargs = super(ChangeWellWisher2, self).get_form_kwargs()
        user = Patient.objects.get(pk=self.request.user)
        kwargs.update({'user': user})
        return kwargs

    def get_context_data(self, **kwargs):
        context = super(ChangeWellWisher2, self).get_context_data(**kwargs)
        relation_name = RelationTable.objects.get(pk=2)
        user = Patient.objects.get(pk=self.request.user)
        try:
            query = ConnectionPatientWellWishers.objects.get(patient=user, relation_no=relation_name).well_wisher
            context['friend'] = 'Your current Relative is '+str(query)
        except ConnectionPatientWellWishers.DoesNotExist:
            context['friend'] = None
        return context


@method_decorator([login_required, patient_required], name='dispatch')
class ChangeWellWisher3(FormView):
    form_class = AddWellWishersForm
    template_name = 'patient/change_well_wishers.html'

    def get_success_url(self):
        wellwisher = self.form.cleaned_data['well_wisher']
        well_wisher = User.objects.get(username=wellwisher).pk
        well_wisher = WellWishers.objects.get(pk=well_wisher)

        relation_name = RelationTable.objects.get(pk=3)
        user = Patient.objects.get(pk=self.request.user)
        ConnectionPatientWellWishers.objects.filter(patient=user, relation_no=relation_name).update(relation_no=None)
        ConnectionPatientWellWishers.objects.filter(patient=user, well_wisher=well_wisher).update(relation_no=relation_name)
        send_mail_to_patient(wellwisher, user)
        return reverse('patient:index')

    def form_valid(self, form):
        self.form = form
        return HttpResponseRedirect(self.get_success_url())

    def get_form_kwargs(self):
        kwargs = super(ChangeWellWisher3, self).get_form_kwargs()
        user = Patient.objects.get(pk=self.request.user)
        kwargs.update({'user': user})
        return kwargs

    def get_context_data(self, **kwargs):
        context = super(ChangeWellWisher3, self).get_context_data(**kwargs)
        relation_name = RelationTable.objects.get(pk=3)
        user = Patient.objects.get(pk=self.request.user)
        try:
            query = ConnectionPatientWellWishers.objects.get(patient=user, relation_no=relation_name).well_wisher
            context['friend'] = 'Your current Colleague is '+str(query)
        except ConnectionPatientWellWishers.DoesNotExist:
            context['friend'] = None
        return context


@login_required
@patient_required
def remove_report(request):
    report_name = request.GET.get('report_name', '')
    query_result = HealthReports.objects.get(pk=report_name).delete()
    return redirect('patient:index')