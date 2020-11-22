#-*- coding: utf-8 -*-
from django import forms
from django.core.validators import RegexValidator
from captcha.fields import ReCaptchaField
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from iidxrank import models
from iidxrank import iidx


"""
membership related
"""

alphanumeric = RegexValidator(r'^[0-9a-zA-Z_]*$', 'ID: Only alphanumeric characters are allowed. 영문/숫자,_만 입력 가능합니다.')

class LoginForm(forms.Form):
    id = forms.CharField(widget=forms.TextInput(), min_length=4)
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class':'form-control input-sm'}))

    def clean(self):
        cleaned_data = super(LoginForm, self).clean()
        if ('id' not in cleaned_data):
            return
        if ('password' not in cleaned_data):
            return
        _username = cleaned_data['id']
        _password = cleaned_data['password']
        user = authenticate(username=_username, password=_password)
        if (user==None):
            raise forms.ValidationError('ID or Password does not exists.')

class JoinForm(forms.Form):
    captcha = ReCaptchaField()
    id = forms.CharField(widget=forms.TextInput(), min_length=4, validators=[alphanumeric])
    email = forms.CharField(widget=forms.EmailInput())
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class':'form-control input-sm'}),
            min_length=4)
    password_again = forms.CharField(widget=forms.PasswordInput(attrs={'class':'form-control input-sm'}))

    def clean(self):
        cleaned_data = super(JoinForm, self).clean()
        username = self.data['id']
        user = User.objects.filter(username=username).first()
        if (user != None):
            raise forms.ValidationError('%s is already exists' % username)
        if (self.data['password'] != self.data['password_again']):
            raise forms.ValidationError('Password does not match!')

class AccountForm(forms.Form):
    first_name = forms.CharField(widget=forms.TextInput())
    iidxid = forms.CharField(widget=forms.TextInput())
    iidxnick = forms.CharField(widget=forms.TextInput())
    classes = iidx.classes
    spclass = forms.ChoiceField(choices=classes)
    dpclass = forms.ChoiceField(choices=classes)


class SetPasswordForm(forms.Form):
    new_password = forms.CharField(widget=forms.PasswordInput(attrs={'class':'form-control input-sm'}), min_length=4)
    new_password_again = forms.CharField(widget=forms.PasswordInput(attrs={'class':'form-control input-sm'}))

    def clean(self):
        if (self.data['new_password'] != self.data['new_password_again']):
            raise forms.ValidationError('Password does not match!')

class WithdrawForm(forms.Form):
    id = forms.CharField(widget=forms.TextInput(attrs={'readonly':'readonly'}), min_length=5)
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class':'form-control input-sm'}))
    password_again = forms.CharField(widget=forms.PasswordInput(attrs={'class':'form-control input-sm'}))

    def clean(self):
        cleaned_data = super(WithdrawForm, self).clean()
        if (self.data['password'] != self.data['password_again']):
            raise forms.ValidationError('Password does not match!')
        user = authenticate(username=self.data['id'], password=self.data['password'])
        if (user==None):
            raise forms.ValidationError('ID or Password does not exists.')
