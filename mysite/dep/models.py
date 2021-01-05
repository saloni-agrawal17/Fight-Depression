from django.db import models
from django.contrib.auth.models import AbstractUser
from django.urls import reverse
from django.core.validators import FileExtensionValidator
from phonenumber_field.modelfields import PhoneNumberField


class User(AbstractUser):
    is_patient = models.BooleanField(default=False)
    is_doctor = models.BooleanField(default=False)
    is_wellwisher = models.BooleanField(default=False)
    is_receptionist = models.BooleanField(default=False)
    is_moderator = models.BooleanField(default=False)


class Moderator(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    name = models.CharField(max_length=200)
    choices = (
        ('male', "Male"),
        ('female', "Female"),
        ('other', "Other")
    )
    gender = models.CharField(max_length=8, choices=choices)
    #contact_number = PhoneField()


class State(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name


class City(models.Model):
    state = models.ForeignKey(State, on_delete=models.CASCADE)
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name


class Location(models.Model):
    city = models.ForeignKey(City, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Weekdays(models.Model):
    days = models.CharField(max_length=10)
    session_id = models.IntegerField()

    def __str__(self):
        return self.days


class FromTimings(models.Model):
    from_timings = models.CharField(max_length=10)

    def __str__(self):
        return self.from_timings


class ToTimings(models.Model):
    to_timings = models.CharField(max_length=10)

    def __str__(self):
        return self.to_timings


class RegistrationCouncil(models.Model):
    council_name = models.CharField(max_length=200)

    def __str__(self):
        return self.council_name


class RegistrationYear(models.Model):
    year = models.CharField(max_length=10)

    def __str__(self):
        return self.year


class CollegeName(models.Model):
    college_name = models.CharField(max_length=200)

    def __str__(self):
        return self.college_name


class Doctor(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    doctor_name = models.CharField(max_length=200)
    choices = (
        ('male', "Male"),
        ('female', "Female"),
        ('other', "Other")
    )
    gender = models.CharField(max_length=8, choices=choices)
    registration_number = models.CharField(max_length=10, null=True)
    registration_council = models.ForeignKey(RegistrationCouncil, on_delete=models.SET_NULL, null=True)
    college_name = models.ForeignKey(CollegeName, on_delete=models.SET_NULL, null=True)
    registration_year = models.ForeignKey(RegistrationYear, on_delete=models.SET_NULL, null=True,
                                          related_name='registration_year')
    year_of_completion = models.ForeignKey(RegistrationYear, on_delete=models.SET_NULL, null=True,
                                           related_name='years_of_completion')
    years_of_experience = models.IntegerField(null=True)
    choices_of_establishment = (
        ('owns establishment', "I own establishment"),
        ('visit establishment', "I visit establishment")
    )
    establishment_choice = models.CharField(max_length=25, choices=choices_of_establishment,
                                            default='owns establishment')
    identity_proof = models.ImageField(upload_to='images/')
    medical_registration_proof = models.ImageField(upload_to='images/')
    establishment_proof = models.ImageField(upload_to='images/')
    photo_proof = models.ImageField(upload_to='images/', null=True)
    establishment_name = models.CharField(max_length=100)
    city_of_practice = models.ForeignKey(City, on_delete=models.SET_NULL, null=True, related_name='city_of_practice')
    location = models.ForeignKey(Location, on_delete=models.SET_NULL, null=True)
    is_doctor = models.BooleanField(default=False)
    fees_for_clinic_patient = models.IntegerField(null=True)
    fees_for_telemedicine_patient = models.IntegerField(null=True)
    degree = models.CharField(max_length=50, default=None, null=True)
    location_of_clinic = models.CharField(max_length=100, default=None, null=True)
    contact_number = PhoneNumberField(default=None, null=True)
    choices = (
        ('yes', 'Yes'),
        ('no', 'No')
    )
    telemedicine_facility = models.CharField(max_length=10, default='yes', choices=choices, null=True)
    reports_needed_for_telemedicine = models.CharField(max_length=500, null=True)

    def __str__(self):
        return self.user.username

    def get_absolute_url(self):
        return reverse('patient:doctor_information', args=[str(self.user.id)])

    def get_absolute_url_for_telemedicine(self):
        return reverse('patient:doctor_telemedicine_information', args=[str(self.user.id)])


class DoctorEstablishmentTimings(models.Model):
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE)
    session_id = models.IntegerField()
    monday = models.CharField(max_length=20)
    tuesday = models.CharField(max_length=20)
    wednesday = models.CharField(max_length=20)
    thursday = models.CharField(max_length=20)
    friday = models.CharField(max_length=20)
    saturday = models.CharField(max_length=20)
    sunday = models.CharField(max_length=20)


class Receptionist(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    user_email = models.EmailField(max_length=254)


class ConnectionDoctorReceptionist(models.Model):
    receptionist = models.ForeignKey(Receptionist, on_delete=models.CASCADE)
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, null=True)
    is_accept = models.BooleanField(default=False)

    def __str__(self):
        return self.receptionist.user.username

    def get_absolute_url(self):
        return reverse('receptionist:doctor_access', args=[str(self.doctor)])


class Patient(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    p_emailid = models.EmailField(max_length=254)
    p_name = models.CharField(max_length=200)
    #p_contact = models.IntegerField('Contact No',validators=[MinLengthValidator(10)])
    choices = (
        ('male', "Male"),
        ('female', "Female"),
        ('other', "Other")
    )
    p_sex = models.CharField(max_length=8, choices=choices)
    state = models.ForeignKey(State, on_delete=models.SET_NULL, null=True)
    city = models.ForeignKey(City, on_delete=models.SET_NULL, null=True)
    p_occupation = models.CharField(max_length=100)
    date_of_birth = models.DateField(null=True)
    contact_number = PhoneNumberField(default=None, null=True)

    def __str__(self):
        return self.user.username


class Phq9Questions(models.Model):
    q_id = models.IntegerField(primary_key=True)
    question_name = models.CharField(max_length=200)

    def __str__(self):
        return self.question_name


class Phq9Answer(models.Model):
    answer_id = models.IntegerField(primary_key=True)
    que = models.ForeignKey('Phq9Questions', on_delete=models.SET_NULL, null=True)
    choices = (
        ('Not at all', "Not at all"),
        ('Several days', "Several days"),
        ('More than half days', "More than half days"),
        ('Nearly every days', "Nearly every days")
    )
    phq9_option = models.CharField(max_length=30, choices=choices)
    score = models.IntegerField()


class Phq9Score(models.Model):
    p_userid = models.ForeignKey('Patient', on_delete=models.SET_NULL,null=True)
    q1 = models.IntegerField()
    q2 = models.IntegerField()
    q3 = models.IntegerField()
    q4 = models.IntegerField()
    q5 = models.IntegerField()
    q6 = models.IntegerField()
    q7 = models.IntegerField()
    q8 = models.IntegerField()
    q9 = models.IntegerField()
    q10 = models.IntegerField()
    date = models.DateField()
    total = models.IntegerField()


class DoctorSessionTime(models.Model):
    doctor = models.ForeignKey(Doctor, on_delete=models.SET_NULL, null=True)
    session_1_from = models.TimeField(null=True, blank=True)
    session_1_to = models.TimeField(null=True, blank=True)
    session_2_from = models.TimeField(null=True, blank=True)
    session_2_to = models.TimeField(null=True, blank=True)
    date_of_appointment = models.DateField()


class AppointmentDoctorPatient(models.Model):
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, null=True)
    slot_time = models.TimeField(null=True)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, null=True)
    date_of_appointment = models.DateField()
    is_accept = models.BooleanField(default=False)
    is_reject = models.BooleanField(default=False)

    def __str__(self):
        return str(self.slot_time)


class DoctorSessionTimeOfTeleMedicine(models.Model):
    doctor = models.ForeignKey(Doctor, on_delete=models.SET_NULL, null=True)
    session_1_from = models.TimeField(null=True, blank=True)
    session_1_to = models.TimeField(null=True, blank=True)
    session_2_from = models.TimeField(null=True, blank=True)
    session_2_to = models.TimeField(null=True, blank=True)
    date_of_appointment = models.DateField()


class AppointmentDoctorPatientOfTeleMedicine(models.Model):
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, null=True)
    slot_time = models.TimeField(null=True)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, null=True)
    date_of_appointment = models.DateField()
    is_accept = models.BooleanField(default=False)

    def __str__(self):
        return str(self.slot_time)


class RelationTable(models.Model):
    relation_no = models.IntegerField(primary_key=True)
    relation_name = models.CharField(max_length=100)

    def __int__(self):
        return self.relation_no


class WellWishers(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    user_email = models.EmailField(max_length=254)

    def __str__(self):
        return self.user.username


class ConnectionPatientWellWishers(models.Model):
    well_wisher = models.ForeignKey(WellWishers, on_delete=models.CASCADE)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, null=True)
    relation_no = models.ForeignKey(RelationTable, on_delete=models.CASCADE, null=True)

    class Meta:
        ordering = ['patient']

    def __str__(self):
        return self.well_wisher.user.username

    def get_absolute_url(self):
        return reverse('wellwisher:well_wisher_access', args=[str(self.patient)])


class DailyActivity(models.Model):
    q_id = models.IntegerField(primary_key=True)
    question_name = models.CharField(max_length=200)

    def __str__(self):
        return self.question_name


class RateDailyActivities(models.Model):
    p_user = models.ForeignKey(Patient, on_delete=models.CASCADE)
    well_wisher = models.ForeignKey(WellWishers, on_delete=models.CASCADE)
    q1 = models.IntegerField()
    q2 = models.IntegerField()
    q3 = models.IntegerField()
    q4 = models.IntegerField()
    q5 = models.IntegerField()
    q6 = models.IntegerField()
    q7 = models.IntegerField()
    q8 = models.IntegerField()
    q9 = models.IntegerField()
    q10 = models.IntegerField()
    q11 = models.IntegerField()
    q12 = models.IntegerField()
    date = models.DateField(auto_now_add=True)
    total = models.IntegerField()
    relation_no = models.ForeignKey(RelationTable, on_delete=models.SET_NULL, null=True)


class ImageUploadedByWellWisher(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    well_wisher = models.ForeignKey(WellWishers, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
    image_description = models.CharField(max_length=500)
    image = models.ImageField(upload_to='images/')


class VideoUploadedByWellWishers(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    well_wisher = models.ForeignKey(WellWishers, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
    video_description = models.CharField(max_length=500)
    video = models.FileField(upload_to='videos/', validators=[FileExtensionValidator(
        allowed_extensions=['mp4', 'ogg', 'wmv', 'flv', 'mkv'])])


class HealthReports(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
    name_of_report = models.CharField(max_length=100)
    image = models.ImageField(upload_to='images/')


class PatientTreatmentAndMedicineInfo(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    doctor = models.ForeignKey(Doctor, on_delete=models.SET_NULL, null=True)
    medicine_name = models.CharField(max_length=500)
    name_of_treatment = models.CharField(max_length=500)
    timestamp = models.DateField(auto_now_add=True, null=True)

