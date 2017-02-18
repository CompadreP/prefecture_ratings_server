from django import forms
from django.contrib import admin
from django.contrib.auth.models import Group
from django.core.exceptions import ValidationError
from django.core.mail import send_mail

from employees.models import Organization, PrefectureEmployee, RatingsUser


class PrefectureEmployeeForm(forms.ModelForm):
    email = forms.EmailField(required=True)
    is_active = forms.BooleanField(required=False,
                                   initial=True,
                                   label='Активный')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['organization'].label = self.fields['organization'].queryset.model._meta.verbose_name
        if 'instance' in kwargs and kwargs['instance']:
            instance = kwargs.get('instance')
            self.fields['email'].initial = instance.user.email
            self.fields['is_active'].initial = instance.user.is_active

    def save(self, commit=True):
        email = self.cleaned_data.get('email')
        is_active = self.cleaned_data.get('is_active')
        if self.instance.id:
            changed = False
            if self.instance.user.email != email:
                self.instance.user.email = email
                changed = True
            if self.instance.user.is_active != is_active:
                self.instance.user.is_active = is_active
                changed = True
            if changed:
                self.instance.user.save()
        else:
            self.instance.user = RatingsUser.objects.create_user(email)
            # TODO send email with hashed url for password setup
            send_mail(
                'Регистрация на сайте prefecture-ratings.ru',
                'Для вас был создан аккаунт на сайте prefecture-ratings.ru. '
                'Чтобы подтвердить свой email  и установить пароль, '
                'проследуйте по ссылке - https://',
                'info@prefecture-ratings.ru',
                [self.instance.user.email],
                fail_silently=False,
            )
        return super(PrefectureEmployeeForm, self).save(commit=commit)

    class Meta:
        model = PrefectureEmployee
        fields = ('email', 'first_name', 'last_name', 'patronymic',
                  'organization', 'can_approve_rating',)


correct_location_message = "У организации должен быть указан либо " \
                           "район, либо округ"


class OrganizationForm(forms.ModelForm):
    model = Organization

    def clean(self):
        super(OrganizationForm, self).clean()
        if (self.cleaned_data['district'] and self.cleaned_data['region']) \
                or (not self.cleaned_data['district']
                    and not self.cleaned_data['region']):
            raise ValidationError(correct_location_message)


class OrganizationAdmin(admin.ModelAdmin):
    form = OrganizationForm
    fieldsets = (
        (None, {'fields': ('name',)}),
        (None, {
            'fields': ('district', 'region'),
            'description': correct_location_message
        }),
    )


class PrefectureEmployeeAdmin(admin.ModelAdmin):
    form = PrefectureEmployeeForm


admin.site.unregister(Group)
admin.site.register(PrefectureEmployee, PrefectureEmployeeAdmin)
admin.site.register(Organization, OrganizationAdmin)
