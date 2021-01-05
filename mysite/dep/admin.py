from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import UserChangeForm
from .models import Phq9Questions, Phq9Answer, State, City, RegistrationCouncil, CollegeName, \
    RegistrationYear, Location, FromTimings, ToTimings, Weekdays, RelationTable, DailyActivity, Moderator, User

admin.site.register(Phq9Questions)
admin.site.register(Phq9Answer)
admin.site.register(RelationTable)
admin.site.register(DailyActivity)
admin.site.register(City)
admin.site.register(State)
admin.site.register(RegistrationCouncil)
admin.site.register(CollegeName)
admin.site.register(RegistrationYear)
admin.site.register(Location)
admin.site.register(FromTimings)
admin.site.register(ToTimings)
admin.site.register(Weekdays)


class ModeratorAdmin(admin.StackedInline):
    model = Moderator
    can_delete = False
    verbose_name_plural = 'Moderator'
    fk_name = 'user'


class MyUserChangeForm(UserChangeForm):
    class Meta(UserChangeForm.Meta):
        model = User


class MyUserAdmin(UserAdmin):
    form = MyUserChangeForm
    inlines = (ModeratorAdmin,)
    fieldsets = UserAdmin.fieldsets + (
        (None, {'fields': ('is_moderator',)}),
    )

    def get_inline_instances(self, request, obj=None):
        if not obj:
            return list()
        return super(MyUserAdmin, self).get_inline_instances(request, obj)


admin.site.register(User, MyUserAdmin)
