from django import forms
from django.contrib import admin
from django.contrib.auth.models import Group
from django.core.exceptions import ValidationError

from django.db import transaction

from apps.employees.models import Organization, PrefectureEmployee, RatingsUser, \
    RegionEmployee
from apps.employees.tasks import generate_token_and_send_email


class EmployeeForm(forms.ModelForm):
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

    def clean_email(self):
        email = self.cleaned_data['email']
        if not self.instance.id:
            if RatingsUser.objects.filter(email=email).exists():
                raise ValidationError('Пользователь с таким email уже существует')
        else:
            if RatingsUser.objects.exclude(id=self.instance.user.id).filter(email=email).exists():
                raise ValidationError('Пользователь с таким email уже существует')
        return email

    @transaction.atomic
    def save(self, commit=True):
        email = self.cleaned_data.get('email')
        is_active = self.cleaned_data.get('is_active')
        # If PrefectureEmployee exists
        if self.instance.id:
            changed = False
            if self.instance.user.email != email:
                self.instance.user.email = email
                changed = True
                self.instance.user.set_unusable_password()
                subject = 'Подтверждение данных на сайте prefecture-ratings.ru'
                body = ('Для вашего аккаунта был изменен адрес электронной почты.'
                        '\n\nЧтобы его подтвердить, перейдите по ссылке - {base_url}/password_set/{url_token} и установите новый пароль.'
                        '\n\nСсылка действительна в течении 24 часов.')
                generate_token_and_send_email(email, subject, body)
            if self.instance.user.is_active != is_active:
                self.instance.user.is_active = is_active
                changed = True
            if changed:
                self.instance.user.save()
        # If creating new PrefectureEmployee
        else:
            self.instance.user = RatingsUser.objects.create_user(email)
            subject = 'Регистрация на сайте prefecture-ratings.ru'
            body = ('Для вас был создан аккаунт на сайте prefecture-ratings.ru.'
                    '\n\nЧтобы подтвердить свой email и установить пароль, перейдите по ссылке - {base_url}/password_set/{url_token}.'
                    '\n\nСсылка действительна в течении 24 часов.')
            generate_token_and_send_email(email, subject, body)
        return super(EmployeeForm, self).save(commit=commit)


class PrefectureEmployeeForm(EmployeeForm):

    def clean_organization(self):
        organization = self.cleaned_data['organization']
        if not organization.district:
            raise ValidationError(
                'У сотрудника префектуры в качестве организации можно '
                'указать только префектуру.'
            )
        return organization

    class Meta:
        model = PrefectureEmployee
        fields = ('email', 'last_name', 'first_name', 'patronymic',
                  'organization', 'can_approve_rating',)


class RegionEmployeeForm(EmployeeForm):
    def clean_organization(self):
        organization = self.cleaned_data['organization']
        if not organization.region:
            raise ValidationError(
                'У сотрудника района в качестве организации можно '
                'указать только районную организацию.'
            )
        return organization

    class Meta:
        model = RegionEmployee
        fields = ('email', 'last_name', 'first_name', 'patronymic',
                  'organization', )


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


class RegionEmployeeAdmin(admin.ModelAdmin):
    form = RegionEmployeeForm


admin.site.unregister(Group)
admin.site.register(PrefectureEmployee, PrefectureEmployeeAdmin)
admin.site.register(RegionEmployee, RegionEmployeeAdmin)
admin.site.register(Organization, OrganizationAdmin)
