from .models import Doctor, HealthReports
import django_filters


class DoctorFilters(django_filters.FilterSet):
    doctor_name = django_filters.CharFilter(lookup_expr='icontains')

    class Meta:
        model = Doctor
        fields = ['doctor_name', 'gender', 'city_of_practice', ]
