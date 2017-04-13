#-*- coding: utf-8 -*-
from django import forms
from captcha.fields import ReCaptchaField
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
import models


"""
membership related
"""
class LoginForm(forms.Form):
    id = forms.CharField(widget=forms.TextInput(), min_length=5)
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class':'form-control input-sm'}))

    def clean(self):
        cleaned_data = super(LoginForm, self).clean()
        _username = cleaned_data['id']
        _password = cleaned_data['password']
        user = authenticate(username=_username, password=_password)
        if (user==None):
            raise forms.ValidationError('ID or Password does not exists.')

class JoinForm(forms.Form):
    captcha = ReCaptchaField()
    id = forms.CharField(widget=forms.TextInput(), min_length=5)
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
