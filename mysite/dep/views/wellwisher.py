from django.views.generic import CreateView, UpdateView, ListView
from django.contrib.auth import login
from django.core.mail import send_mail
from mysite.settings import EMAIL_HOST_USER
from django.contrib import messages
from django.urls import reverse_lazy, reverse
from django.forms.formsets import formset_factory
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render, get_object_or_404
from itertools import chain
from ..models import ConnectionPatientWellWishers, WellWishers, User, RateDailyActivities, DailyActivity, Patient, \
    RelationTable, ImageUploadedByWellWisher, VideoUploadedByWellWishers
from ..forms import WellWisherSignUpForm, AddPatientForm, PatientAdded, RateDailyActivitiesForm, UploadVideoForm, \
    UploadImageForm
from ..decorators import wellwisher_required
from django.utils.decorators import method_decorator


class WellWisherSignUpView(CreateView):
    form_class = WellWisherSignUpForm
    template_name = 'registration/signup_form.html'

    def get_context_data(self, **kwargs):
        kwargs['user_type'] = 'wellwisher'
        return super().get_context_data(**kwargs)

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        return redirect('wellwisher:index')


@login_required
@wellwisher_required
def well_wisher_dasboard(request):
    wellwisher = WellWishers.objects.get(pk=request.user)
    query_result = ConnectionPatientWellWishers.objects.filter(well_wisher=wellwisher).order_by().values_list('patient').\
        distinct()
    patient_list = list()
    for i in query_result:
        temp = list()
        patient = Patient.objects.get(pk=i[0])
        temp.append(patient.p_name)
        count = ConnectionPatientWellWishers.objects.filter(well_wisher=wellwisher, patient=patient, relation_no__gt=0).count()
        if count == 0:
            temp.append(None)
        else:
            temp.append(count)
        query = ConnectionPatientWellWishers.objects.filter(well_wisher=wellwisher, patient=patient, relation_no__gt=0)
        relation_name = ''
        for j in query:
            relation_id = RelationTable.objects.get(pk=j.relation_no).relation_no
            if relation_id == 1:
                relation_name += 'Friend,'
            if relation_id == 2:
                relation_name += 'Relative,'
            if relation_id == 3:
                relation_name += 'Colleague,'
        relation_name = relation_name[0:len(relation_name)-1]
        temp.append(relation_name)
        temp.append(patient)
        patient_list.append(temp)

    return render(request, 'wellwisher/wellwisher_dashboard.html', {'patient_list': patient_list})


@login_required
@wellwisher_required
def add_patient(request):
    if request.method == 'POST':
        form = AddPatientForm(request.POST)
        if form.is_valid():
            patient = form.cleaned_data['patient']
            well_wisher = WellWishers.objects.get(pk=request.user)
            count = ConnectionPatientWellWishers.objects.filter(patient=patient, well_wisher=well_wisher).count()
            if count >= 1:
                return redirect('wellwisher:index')
            else:
                ConnectionPatientWellWishers.objects.create(well_wisher=well_wisher, patient=patient)
                return send_mail_to_patient(request, patient)
    else:
        form = AddPatientForm()
    return render(request, 'wellwisher/add_patient.html', {'form': form})


@login_required
@wellwisher_required
def send_mail_to_patient(request, patient):
    if request.method == 'POST':
        subject = 'FightDepression:You are added by wellwisher'
        wellwisher = User.objects.get(username=request.user)
        message = wellwisher.username+' has added you.You can add the relation with wellwisher from your dashboard..'
        recepient = User.objects.get(username=patient).email
        send_mail(subject, message, EMAIL_HOST_USER, [recepient], fail_silently=False)
        return redirect('wellwisher:index')


@login_required
@wellwisher_required
def remove_patient(request, patient):
    well_wisher = WellWishers.objects.get(pk=request.user)

    patient_name = request.GET.get('patient', '')
    temp = User.objects.get(username=patient_name).id
    temp1 = Patient.objects.get(user=temp)
    query_result = ConnectionPatientWellWishers.objects.get(well_wisher=well_wisher, patient=temp1).delete()
    subject = 'FightDepression:You are removed by wellwisher'

    wellwisher = User.objects.get(pk=well_wisher.pk)
    message = wellwisher.username + ' has removed you...'

    recepient = User.objects.get(username=patient_name).email
    send_mail(subject, message, EMAIL_HOST_USER, [recepient], fail_silently=False)
    return redirect('wellwisher:index')


@login_required
@wellwisher_required
def well_wisher_dashboard(request, pk):
    return render(request, 'wellwisher/wellwisher_access_dashboard.html', {'patient': pk})


@login_required
@wellwisher_required
def rate_daily_activity(request, patient):
    well_wisher = WellWishers.objects.get(pk=request.user)

    patient_name = request.GET.get('patient', '')
    temp = User.objects.get(username=patient_name).id
    temp1 = Patient.objects.get(user=temp)

    daily_activity_questions = DailyActivity.objects.all()

    query_result = ConnectionPatientWellWishers.objects.filter(well_wisher=well_wisher, patient=temp1).\
        exclude(relation_no=None)
    daily_activity_ques = []
    daily1_activity_ques = []
    daily2_activity_ques = []
    daily3_activity_ques = []

    relation_id_lst = []

    for entry in query_result:
        relation_id = RelationTable.objects.get(pk=entry.relation_no).relation_no
        patient_id = entry.patient
        relation_id_lst.append(relation_id)
        if relation_id == 1:
            daily1_activity_ques = daily_activity_questions[:12]
        if relation_id == 2:
            daily2_activity_ques = daily_activity_questions[12:24]
        if relation_id == 3:
            daily3_activity_ques = daily_activity_questions[24:]
        daily_activity_ques = list(chain(daily1_activity_ques, daily2_activity_ques, daily3_activity_ques))

    RatingFormset = formset_factory(RateDailyActivitiesForm, extra=len(daily_activity_ques))

    if request.method == 'POST':
        formset = RatingFormset(request.POST)
        if formset.is_valid():
            lst = []
            i = 0
            count = 0
            for form in formset:
                data = form.cleaned_data['Choices']
                lst.append(int(data))
                count += 1
                if count % 12 == 0:
                    total = sum(lst)
                    relation_id = RelationTable.objects.get(pk=relation_id_lst[i])
                    RateDailyActivities.objects.create(q1=lst[0], q2=lst[1], q3=lst[2], q4=lst[3], q5=lst[4],
                                                       q6=lst[5], q7=lst[6], q8=lst[7], q9=lst[8], q10=lst[9],
                                                       q11=lst[10], q12=lst[11], total=total,
                                                       p_user=patient_id, well_wisher=well_wisher, relation_no=relation_id)
                    lst = []
                    i += 1
            return redirect('wellwisher:index')
    else:
        formset = RatingFormset()
        ques_no = [item for item in range(1, len(daily_activity_ques)+1)]
    return render(request, 'wellwisher/daily_activity.html', {'data': zip(daily_activity_ques, formset, ques_no),
                                                              'formset': formset})


@login_required
@wellwisher_required
def upload_images(request, patient):
    well_wisher = WellWishers.objects.get(pk=request.user)

    patient_name = request.GET.get('patient', '')
    temp = User.objects.get(username=patient_name).id
    temp1 = Patient.objects.get(user=temp)

    query_result = ConnectionPatientWellWishers.objects.filter(well_wisher=well_wisher, patient=temp1)
    # print(query_result.well_wisher)
    for entry in query_result:
        patient_id = entry.patient
        break

    if "add_more" in request.POST:
        form = UploadImageForm(request.POST, request.FILES)
        if form.is_valid():
            description = form.cleaned_data['image_description']
            img = form.cleaned_data['image']
            ImageUploadedByWellWisher.objects.create(patient=patient_id, well_wisher=well_wisher,
                                                     image_description=description, image=img)
            form = UploadImageForm()
    elif "final_submit" in request.POST:
        form = UploadImageForm(request.POST, request.FILES)
        if form.is_valid():
            description = form.cleaned_data['image_description']
            img = form.cleaned_data['image']
            # patient_id = query_result.patient
            ImageUploadedByWellWisher.objects.create(patient=patient_id, well_wisher=well_wisher,
                                                     image_description=description, image=img)
            return redirect('wellwisher:index')
    else:
        form = UploadImageForm()
    return render(request, 'wellwisher/upload_images.html', {'form': form, 'patient': patient_name})


@login_required
@wellwisher_required
def upload_videos(request, patient):
    well_wisher = WellWishers.objects.get(pk=request.user)

    patient_name = request.GET.get('patient', '')
    temp = User.objects.get(username=patient_name).id
    temp1 = Patient.objects.get(user=temp)

    query_result = ConnectionPatientWellWishers.objects.filter(well_wisher=well_wisher, patient=temp1)
    for entry in query_result:
        patient_id = entry.patient

    if "add_more" in request.POST:
        form = UploadVideoForm(request.POST, request.FILES)
        if form.is_valid():
            description = form.cleaned_data['video_description']
            video = form.cleaned_data['video']
            VideoUploadedByWellWishers.objects.create(patient=patient_id, well_wisher=well_wisher,
                                                      video_description=description, video=video)
            form = UploadVideoForm()

    elif "final_submit" in request.POST:
        form = UploadVideoForm(request.POST, request.FILES)
        if form.is_valid():
            description = form.cleaned_data['video_description']
            video = form.cleaned_data['video']

            # patient_id = query_result.patient

            VideoUploadedByWellWishers.objects.create(patient=patient_id, well_wisher=well_wisher,
                                                      video_description=description, video=video)
            return redirect('wellwisher:index')

    else:
        form = UploadVideoForm()
    return render(request, 'wellwisher/upload_video.html', {'form': form})


@method_decorator([login_required, wellwisher_required], name='dispatch')
class ImagesListView(ListView):
    model = ImageUploadedByWellWisher
    template_name = 'wellwisher/list_images.html'
    context_object_name = 'image_list'

    def get_queryset(self, **kwargs):
        patient = self.request.GET.get('patient', '')
        temp = User.objects.get(username=patient).id
        temp1 = Patient.objects.get(user=temp)
        w_id = WellWishers.objects.get(pk=self.request.user)
        return ImageUploadedByWellWisher.objects.filter(well_wisher=w_id, patient=temp1).order_by('patient')

    def get_context_data(self, *, object_list=None, **kwargs):
        kwargs['patient'] = patient = self.request.GET.get('patient', '')
        return super().get_context_data(**kwargs)


@method_decorator([login_required, wellwisher_required], name='dispatch')
class VideoListView(ListView):
    model = VideoUploadedByWellWishers
    template_name = 'wellwisher/list_videos.html'
    context_object_name = 'videos_list'

    def get_queryset(self, **kwargs):
        patient = self.request.GET.get('patient', '')
        temp = User.objects.get(username=patient).id
        temp1 = Patient.objects.get(user=temp)
        w_id = WellWishers.objects.get(pk=self.request.user)
        return VideoUploadedByWellWishers.objects.filter(well_wisher=w_id, patient=temp1).order_by('patient')

    def get_context_data(self, *, object_list=None, **kwargs):
        kwargs['patient'] = patient = self.request.GET.get('patient', '')
        return super().get_context_data(**kwargs)


@login_required
@wellwisher_required
def remove_photo(request):
    patient = request.GET.get('patient', '')
    temp = User.objects.get(username=patient).id
    temp1 = Patient.objects.get(user=temp)

    well_wisher = WellWishers.objects.get(pk=request.user)
    image_name = request.GET.get('image_name', '')
    query_result = ImageUploadedByWellWisher.objects.get(pk=image_name).delete()
    return redirect('wellwisher:well_wisher_access', pk=patient)


@login_required
@wellwisher_required
def remove_video(request):
    patient = request.GET.get('patient', '')
    temp = User.objects.get(username=patient).id
    temp1 = Patient.objects.get(user=temp)

    well_wisher = WellWishers.objects.get(pk=request.user)
    video_name = request.GET.get('video_name', '')
    query_result = VideoUploadedByWellWishers.objects.get(pk=video_name).delete()
    return redirect('wellwisher:well_wisher_access',pk=patient )
