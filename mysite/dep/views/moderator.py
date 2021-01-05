from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required
from ..decorators import moderator_required
from django.views.generic import ListView
from django.forms.formsets import formset_factory
from django.utils.decorators import method_decorator
from django.core.mail import send_mail
from mysite.settings import EMAIL_HOST_USER
from ..models import Doctor, Moderator, User
from ..forms import CheckDoctorForm


@login_required
@moderator_required
def index(request):
    return render(request, 'moderator/moderator_dashboard.html')


@method_decorator([login_required, moderator_required()], name='dispatch')
class PendingDoctorsListView(ListView):
    model = Doctor
    template_name = 'moderator/list_pending_doctor.html'
    context_object_name = 'pending_doctor_list'

    def get_queryset(self, **kwargs):
        return Doctor.objects.filter(is_doctor=False)


@login_required
@moderator_required
def check_doctors(request, doctor):
    doctor = request.GET.get('doctor', '')
    CheckDoctorFormSet = formset_factory(CheckDoctorForm, extra=17)
    doc = User.objects.get(username=doctor).pk
    query = Doctor.objects.get(user=doc)

    if request.method == 'POST':
        formset = CheckDoctorFormSet(request.POST)
        if formset.is_valid():
            values = ['Gender', 'Contact Number', 'Degree', 'Location Of Clinic', 'City Of Practice',
                      'Locality Of Practice', 'Registration Number', 'Registration Council', 'College Name',
                      'Year Of Completion', 'Registration Year', 'Choices Of Establishment', 'Identity Proof',
                      'Establishment Proof', 'Medical Registration Proof', 'Year of Experience', 'Establishment Name']
            count = 0
            msg = ''
            for form in formset:
                print(form.cleaned_data['choices'])
                if form.cleaned_data['choices'] == 'reject':
                    msg = msg + ',' + values[count]
                count += 1
            if len(msg) == 0:
                Doctor.objects.filter(user=doc).update(is_doctor=True)
                return redirect('moderator:index')
            else:
                return send_mail_to_doctor(request, doc, msg)
    else:
        formset = CheckDoctorFormSet()
        # print(formset)
    return render(request, 'moderator/check_doctor.html', {'doctor': query, 'formset': formset})


@login_required
@moderator_required
def send_mail_to_doctor(request, doc, msg):
    if request.method == 'POST':
        recipient = User.objects.get(pk=doc).email
        name = Doctor.objects.get(user=doc).doctor_name
        subject = 'FightDepression:Incorrect details'
        message = 'Dr. '+name+' Your entered details of'+msg+' is/are incorrect'
        send_mail(subject, message, EMAIL_HOST_USER, [recipient], fail_silently=False)
        return redirect('moderator:index')
