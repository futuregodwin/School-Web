from django.forms import ModelForm
from django import forms
from .models import Teacher, Result
from students_app.models import Subject, Student
from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm
from datetime import date




class TeacherForm(forms.ModelForm):
    class  Meta:
       model = Teacher
       fields = '__all__'
       exclude = ['user']


class UserForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)  # Add password field

    class Meta:
        model = User
        fields = ['username', 'password', 'first_name', 'last_name', 'email'] 




class TeacherSubjectForm(forms.ModelForm):
    subjects = forms.ModelMultipleChoiceField(
        queryset=Subject.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False,
    )

    class Meta:
        model = Teacher
        fields = ['subjects']





class AttendanceForm(forms.Form):
    date = forms.DateField(widget=forms.DateInput(attrs={"type": "date"}))

    def __init__(self, *args, **kwargs):
        students = kwargs.pop("students", [])
        super().__init__(*args, **kwargs)

        for student in students:
            self.fields[f'present_{student.id}'] = forms.BooleanField(
                required=False,
                label=f"{student.user.username} ({student.registration_number})",
                initial=False
            )




class ResultUploadFileForm(forms.Form):
    excel_file = forms.FileField(label="Upload Excel File")
