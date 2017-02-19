from django import forms
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError

from employees.common import decrypt_token
from employees.models import RatingsUser


class PasswordSetForm(forms.Form):
    password = forms.CharField(required=True, label='Пароль')
    password_repeat = forms.CharField(required=True, label='Пароль еще раз')

    def clean(self):
        if self.cleaned_data['password'] != self.cleaned_data['password_repeat']:
            raise ValidationError("Введенные пароли не совпадают!")
        validate_password(self.cleaned_data['password'])
        return self.cleaned_data

    def set_user_password(self, token):
        email, _ = decrypt_token(token)
        user = RatingsUser.objects.get(email=email)
        user.set_password(self.cleaned_data['password'])
        user.save()
