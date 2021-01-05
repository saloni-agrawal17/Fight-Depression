from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.db import transaction
from datetime import datetime, timedelta
from django.forms.utils import ValidationError
from django.http import HttpResponse
from django.forms import ModelForm
from random import randint

from dep.models import (Patient, User, Doctor, Phq9Answer, City, WellWishers, ConnectionPatientWellWishers,
                        ImageUploadedByWellWisher, VideoUploadedByWellWishers, Receptionist, ConnectionDoctorReceptionist,
                        AppointmentDoctorPatient, HealthReports, PatientTreatmentAndMedicineInfo,
                        AppointmentDoctorPatientOfTeleMedicine)


class DoctorSignUpForm(UserCreationForm):
    name = forms.CharField(max_length=200)
    choices = (
        ('male', "Male"),
        ('female', "Female"),
        ('other', "Other")
    )
    gender = forms.ChoiceField(choices=choices)

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username', 'password1', 'password2', 'email')

    def __init__(self, *args, **kwargs):
        super(DoctorSignUpForm, self).__init__(*args, **kwargs)
        self.fields['username'].widget.attrs['placeholder'] = 'Write name containing of first name ' \
                                                              'along with last name and other characters'
        self.fields['name'].widget.attrs['placeholder'] = 'Write your full name'

    def clean(self):
        cleaned_data = super(DoctorSignUpForm, self).clean()
        username = cleaned_data.get('username')
        email = cleaned_data.get('email')
        find_index = email.find('@')
        value = randint(1, 100000)
        suggest_username = email[:find_index]+str(value)
        try:
            User._default_manager.get(username=username)
            raise forms.ValidationError('Try with different username like:'+suggest_username)
        except User.DoesNotExist:
            return cleaned_data

    @transaction.atomic
    def save(self):
        user = super().save(commit=False)
        user.is_doctor = True
        user.save()
        doctor = Doctor.objects.create(user=user, doctor_name=self.cleaned_data.get('name'),
                                       gender=self.cleaned_data.get('gender'))
        return user


class MedicalRegistrationForm(ModelForm):
    class Meta:
        model = Doctor
        fields = ('registration_number', 'registration_council', 'registration_year')


class EducationQualificationForm(ModelForm):
    class Meta:
        model = Doctor
        fields = ('college_name', 'year_of_completion', 'years_of_experience')


class EstablishmentChoiceForm(ModelForm):
    class Meta:
        model = Doctor
        fields = ('establishment_choice',)


class EstablishmentDetailsForm(ModelForm):
    class Meta:
        model = Doctor
        fields = ('establishment_name', 'city_of_practice', 'location')


class UploadIdentityProofForm(ModelForm):
    class Meta:
        model = Doctor
        fields = ['identity_proof', ]


class UploadMedicalRegistrationProof(ModelForm):
    class Meta:
        model = Doctor
        fields = ['medical_registration_proof', ]


class UploadEstablishmentProof(ModelForm):
    class Meta:
        model = Doctor
        fields = ['establishment_proof', ]


class UploadPhotoProof(ModelForm):
    class Meta:
        model = Doctor
        fields = ['photo_proof', ]


class AddExtraInformationOfDoctorForm(ModelForm):
    fees_for_telemedicine_patient = forms.IntegerField(required=False)

    class Meta:
        model = Doctor
        fields = ('degree', 'location_of_clinic', 'telemedicine_facility', 'contact_number', 'fees_for_clinic_patient',
                  'fees_for_telemedicine_patient')

    def __init__(self, *args, **kwargs):
        super(AddExtraInformationOfDoctorForm, self).__init__(*args, **kwargs)
        self.fields['degree'].widget.attrs['placeholder'] = 'Write your degree of psychiatrist(For e.g M.D or diploma ' \
                                                            'in Psychiatrist)'
        self.fields['location_of_clinic'].widget.attrs['placeholder'] = 'Write location of your clinic.'
        self.fields['contact_number'].widget.attrs['placeholder'] = 'Write your contact number starting with +91(For ' \
                                                                    'e.g +919874563210)'
        self.fields['fees_for_clinic_patient'].widget.attrs['placeholder'] = 'Enter fees for clinic patient'
        self.fields['fees_for_telemedicine_patient'].widget.attrs['placeholder'] = 'In case if you are not performing' \
                                                                                   'telemedicine keep this field blank'


class ReceptionistSignUpForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username', 'password1', 'password2', 'email',)

    def clean(self):
        cleaned_data = super(ReceptionistSignUpForm, self).clean()
        username = cleaned_data.get('username')
        email = cleaned_data.get('email')
        find_index = email.find('@')
        value = randint(1, 100000)
        suggest_username = email[:find_index] + str(value)
        try:
            User._default_manager.get(username=username)
            raise forms.ValidationError('Try with different username like:' + suggest_username)
        except User.DoesNotExist:
            return cleaned_data

    @transaction.atomic
    def save(self):
        user = super().save(commit=False)
        user.is_receptionist = True
        user.save()
        receptionist = Receptionist.objects.create(user=user, user_email=self.cleaned_data.get('email'))
        return user


class PatientSignUpForm(UserCreationForm):
    name = forms.CharField(max_length=200)
    choices = (
        ('male', "Male"),
        ('female', "Female"),
        ('other', "Other")
    )
    gender = forms.ChoiceField(choices=choices)
    occupation = forms.CharField(max_length=100)
    date_of_birth = forms.DateField()

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username', 'password1', 'password2', 'email',)

    def __init__(self, *args, **kwargs):
        super(PatientSignUpForm, self).__init__(*args, **kwargs)
        self.fields['username'].widget.attrs['placeholder'] = 'Write name containing of first name '\
                                                              'along with last name and other characters'
        self.fields['name'].widget.attrs['placeholder'] = 'Write your full name'
        self.fields['occupation'].widget.attrs['placeholder'] = 'Write your business occupations'

    def clean(self):
        cleaned_data = super(PatientSignUpForm, self).clean()
        username = cleaned_data.get('username')
        email = cleaned_data.get('email')
        find_index = email.find('@')
        value = randint(1, 100000)
        suggest_username = email[:find_index]+str(value)
        try:
            User._default_manager.get(username=username)
            raise forms.ValidationError('Username  already Exists.Try with different username like:'+suggest_username)
        except User.DoesNotExist:
            return cleaned_data

    @transaction.atomic
    def save(self):
        user = super().save(commit=False)
        user.is_patient = True
        user.save()
        patient = Patient.objects.create(user=user, p_emailid=self.cleaned_data.get('email'), p_name=self.cleaned_data.get('name'),
                                         p_sex=self.cleaned_data.get('gender'),
                                         p_occupation=self.cleaned_data.get('occupation'),
                                         date_of_birth=self.cleaned_data.get('date_of_birth'))
        return user


class AddCitiesStateForm(ModelForm):
    class Meta:
        model = Patient
        fields = ('state', 'city', 'contact_number', )

    def __init__(self, *args, **kwargs):
        super(AddCitiesStateForm, self).__init__(*args, **kwargs)
        self.fields['contact_number'].widget.attrs['placeholder'] = 'Write your contact number which is linked to your'\
                                                                    'paytm account and it should start with ' \
                                                                    '+91(For e.g +919874563210)'


class Phq9AnswerForm(forms.Form):
    choices = (
        ('Not at all', "Not at all"),
        ('Several days', "Several days"),
        ('More than half days', "More than half days"),
        ('Nearly every days', "Nearly every days")
    )
    phq9_option = forms.ChoiceField(choices=choices, initial=0, widget=forms.RadioSelect(
        attrs={
            'class': 'inline',
        }
    ))


class AddWellWishersForm(forms.Form):
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user")
        super(AddWellWishersForm, self).__init__(*args, **kwargs)
        self.fields['well_wisher'] = forms.ChoiceField(
            choices=[(o.well_wisher, str(o)) for o in ConnectionPatientWellWishers.objects.filter(patient=self.user)]
            )


class WellWisherSignUpForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username', 'password1', 'password2', 'email',)

    def clean(self):
        cleaned_data = super(WellWisherSignUpForm, self).clean()
        username = cleaned_data.get('username')
        email = cleaned_data.get('email')
        find_index = email.find('@')
        value = randint(1, 100000)
        suggest_username = email[:find_index]+str(value)
        try:
            User._default_manager.get(username=username)
            raise forms.ValidationError('Try with different username like:'+suggest_username)
        except User.DoesNotExist:
            return cleaned_data

    @transaction.atomic
    def save(self):
        user = super().save(commit=False)
        user.is_wellwisher = True
        user.save()
        wellwisher = WellWishers.objects.create(user=user, user_email=self.cleaned_data.get('email'))
        return user


class AddPatientForm(forms.ModelForm):
    class Meta:
        model = ConnectionPatientWellWishers
        fields = ('patient',)


class AddDoctorForm(forms.ModelForm):
    class Meta:
        model = ConnectionDoctorReceptionist
        fields = ('doctor',)


class AddReceptionistForm(forms.Form):
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user")
        super(AddReceptionistForm, self).__init__(*args, **kwargs)
        self.fields['receptionist'] = forms.ChoiceField(
            choices=[(o.id, str(o)) for o in ConnectionDoctorReceptionist.objects.filter(doctor=self.user)]
        )


class DoctorAddSessionForm(forms.Form):
    session_1_from = forms.TimeField(required=False)
    session_1_to = forms.TimeField(required=False)
    session_2_from = forms.TimeField(required=False)
    session_2_to = forms.TimeField(required=False)
    choices = (
        ('no', "No"),
        ('yes', "Yes")
    )
    holiday = forms.ChoiceField(choices=choices)

    def clean(self):
        cleaned_data = super(DoctorAddSessionForm, self).clean()
        session_1_from = cleaned_data.get('session_1_from')
        session_1_to = cleaned_data.get('session_1_to')
        session_2_from = cleaned_data.get('session_2_from')
        session_2_to = cleaned_data.get('session_2_to')

        session_1_from = str(session_1_from)
        if session_1_from == 'None':
            session_1_from = None

        session_1_to = str(session_1_to)
        if session_1_to == 'None':
            session_1_to = None

        session_2_from = str(session_2_from)
        if session_2_from == 'None':
            session_2_from = None

        session_2_to = str(session_2_to)
        if session_2_to == 'None':
            session_2_to = None

        if (session_1_from is None and session_1_to is not None) or \
                (session_1_from is not None and session_1_to is None) or (session_2_from is None and session_2_to is not None) \
                or (session_2_from is not None and session_2_to is None):
            raise forms.ValidationError('Both the from timings and to timings should be filled with valid values.')

        if session_1_from is not None and session_1_to is not None:
            if session_1_from >= session_1_to:
                raise forms.ValidationError('Value of from time should be less than to time')

        if session_2_from is not None and session_2_to is not None:
            if session_2_from >= session_2_to:
                raise forms.ValidationError('Value of from time should be less than to time')


class DoctorChangeSessionForm(forms.Form):
    session_1_from = forms.TimeField(required=False)
    session_1_to = forms.TimeField(required=False)
    session_2_from = forms.TimeField(required=False)
    session_2_to = forms.TimeField(required=False)
    choices = (
        ('no', "No"),
        ('yes', "Yes")
    )
    holiday = forms.ChoiceField(choices=choices)

    def clean(self):
        cleaned_data = super(DoctorChangeSessionForm, self).clean()
        session_1_from = cleaned_data.get('session_1_from')
        session_1_to = cleaned_data.get('session_1_to')
        session_2_from = cleaned_data.get('session_2_from')
        session_2_to = cleaned_data.get('session_2_to')

        session_1_from = str(session_1_from)
        if session_1_from == 'None':
            session_1_from = None

        session_1_to = str(session_1_to)
        if session_1_to == 'None':
            session_1_to = None

        session_2_from = str(session_2_from)
        if session_2_from == 'None':
            session_2_from = None

        session_2_to = str(session_2_to)
        if session_2_to == 'None':
            session_2_to = None

        if (session_1_from is None and session_1_to is None) and (session_2_from is not None and session_2_to is not None):
            raise forms.ValidationError('It is compulsory to enter this field irrespective of its timing is '
                                        'change or not')

        if (session_2_from is None and session_2_to is None) and (session_1_from is not None and session_1_to is not None):
            raise forms.ValidationError('It is compulsory to enter this field irrespective of its timing is '
                                        'change or not')

        if (session_1_from is None and session_1_to is not None) or \
                (session_1_from is not None and session_1_to is None) or (session_2_from is None and session_2_to is not None) \
                or (session_2_from is not None and session_2_to is None):
            raise forms.ValidationError('Both the from timings and to timings should be filled with valid values.')

        if session_1_from is not None and session_1_to is not None:
            if session_1_from >= session_1_to:
                raise forms.ValidationError('Value of from time should be less than to time')

        if session_2_from is not None and session_2_to is not None:
            if session_2_from >= session_2_to:
                raise forms.ValidationError('Value of from time should be less than to time')


def get_date_choices():
    choices = ()
    for i in range(7):
        date_to_be_added = datetime.now().date()+timedelta(days=i)
        choice = (i, date_to_be_added)
        choices = choices + (choice,)
    return choices


class BookAppointmentForm(forms.Form):
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("doctor")
        super(BookAppointmentForm, self).__init__(*args, **kwargs)
        self.fields['choose_timings'] = forms.ChoiceField(choices=get_date_choices())
        self.fields['slot_timings'] = forms.ChoiceField(
            choices=[(o.id, (str(o))) for o in AppointmentDoctorPatient.objects.filter(
                doctor=self.user, date_of_appointment__gte=datetime.now().date()).exclude(patient__gt=0)]
        )


class BookTeleMedicineAppointmentForm(forms.Form):
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("doctor")
        super(BookTeleMedicineAppointmentForm, self).__init__(*args, **kwargs)
        self.fields['choose_timings'] = forms.ChoiceField(choices=get_date_choices())
        self.fields['slot_timings'] = forms.ChoiceField(
            choices=[(o.id, (str(o))) for o in AppointmentDoctorPatientOfTeleMedicine.objects.filter(
                doctor=self.user, date_of_appointment__gte=datetime.now().date()).exclude(patient__gt=0)]
        )


class PatientAdded(forms.Form):
    email = forms.EmailField()

    def __str__(self):
        return self.email


class RateDailyActivitiesForm(forms.Form):
    choices = (
        (0, 0),
        (1, 1),
        (2, 2),
        (3, 3),
        (4, 4),
    )
    Choices = forms.ChoiceField(choices=choices, initial=0, widget=forms.RadioSelect(
        attrs={
            'class': 'inline',
        }
    ))


class UploadImageForm(ModelForm):
    class Meta:
        model = ImageUploadedByWellWisher
        fields = ('image', 'image_description')

    def __init__(self, *args, **kwargs):
        super(UploadImageForm, self).__init__(*args, **kwargs)
        self.fields['image_description'].widget.attrs['placeholder'] = 'Write something about the image that will '\
                                                                       'help them feel good and and help them ' \
                                                                       'cherish the present moments.'


class UploadVideoForm(ModelForm):
    class Meta:
        model = VideoUploadedByWellWishers
        fields = ('video', 'video_description',)

    def __init__(self, *args, **kwargs):
        super(UploadVideoForm, self).__init__(*args, **kwargs)
        self.fields['video_description'].widget.attrs['placeholder'] = 'Write something about the video that will '\
                                                                       'help them feel good and and help them ' \
                                                                       'cherish the present moments.'


class UploadHealthReportsForm(ModelForm):
    class Meta:
        model = HealthReports
        fields = ('image', 'name_of_report',)

    def __init__(self, *args, **kwargs):
        super(UploadHealthReportsForm, self).__init__(*args, **kwargs)
        self.fields['name_of_report'].widget.attrs['placeholder'] = 'Write name of the report which you are ' \
                                                                    'uploading'


class CheckDoctorForm(forms.Form):
    choices = (
        ('accept', 'Accept'),
        ('reject', 'Reject')
    )
    choices = forms.ChoiceField(choices=choices)


class PatientTreatmentAndMedicineInfoForm(forms.ModelForm):
    class Meta:
        model = PatientTreatmentAndMedicineInfo
        fields = ('medicine_name', 'name_of_treatment')

    def __init__(self, *args, **kwargs):
        super(PatientTreatmentAndMedicineInfoForm, self).__init__(*args, **kwargs)
        self.fields['medicine_name'].widget.attrs['placeholder'] = 'If more than one medicines are there use ' \
                                                                   'commas to separate them'


class AddReportsForTeleMedicineForm(ModelForm):
    class Meta:
        model = Doctor
        fields = ('reports_needed_for_telemedicine',)

    def __init__(self, *args, **kwargs):
        super(AddReportsForTeleMedicineForm, self).__init__(*args, **kwargs)
        self.fields['reports_needed_for_telemedicine'].widget.attrs['placeholder'] = 'If more than one reports are ' \
                                                                                     'there separate them with comma.'
