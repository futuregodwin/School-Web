from django.forms import ModelForm
from django import forms
from .models import Student
from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm





class AdmissionForm(forms.ModelForm):
    class  Meta:
       model = Student
       fields = '__all__'
       exclude = ['registration_number', 'user', 'is_admitted', 'fees']


class UserForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)  # Add password field

    class Meta:
        model = User
        fields = ['username', 'email']  