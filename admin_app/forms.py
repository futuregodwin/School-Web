from django import forms
from django.contrib.auth.forms import AuthenticationForm
from students_app .models import Student, Fee, SchoolClass, Subject
from teachers_app .models import Teacher

class AdminLoginForm(AuthenticationForm):
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control p-2 border border-gray-300 rounded-md w-full',
            'placeholder': 'Enter your username'
        }),
        label="Username"
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control p-2 border border-gray-300 rounded-md w-full',
            'placeholder': 'Enter your password'
        }),
        label="Password"
    )


class EditStudentForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = '__all__' 
        exclude = ['registration_number', 'user', 'fees'] 
        widgets = {
            'contact': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Contact'}),  
            
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.user: 
            self.fields['username'] = forms.CharField(
                initial=self.instance.user.username,  
                widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Username'})
            )


class FeesForm(forms.ModelForm):
    class Meta:
        model = Fee
        fields = ['class_fee', 'amount_due']
        widgets = {
            'class_fee': forms.Select(attrs={'class': 'w-full p-2 border rounded-lg'}),
            'amount_due': forms.NumberInput(attrs={'class': 'w-full p-2 border rounded-lg', 'placeholder': 'Enter amount'}),
        }


class EditFeeForm(forms.ModelForm):
    class Meta:
        model = Fee
        fields = ['class_fee', 'amount_due']
        widgets = {
            'class_fee': forms.Select(attrs={'class': 'w-full p-2 border rounded-lg'}),
            'amount_due': forms.NumberInput(attrs={'class': 'w-full p-2 border rounded-lg', 'placeholder': 'Enter amount'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance:  
            self.fields['class_fee'].widget.attrs.update({
                'readonly': True  
            })


class ClassForm(forms.ModelForm):
    class Meta:
        model = SchoolClass
        fields = ['name', 'level', 'class_teacher']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'w-full p-2 border rounded-lg', 'placeholder': 'Enter class name'}),
            'level': forms.NumberInput(attrs={'class': 'w-full p-2 border rounded-lg', 'placeholder': 'Enter level'}),
            'class_teacher': forms.Select(attrs={'class': 'w-full p-2 border rounded-lg'}),
        }


class EditClassForm(forms.ModelForm):
    class Meta:
        model = SchoolClass
        fields = ['name', 'level', 'class_teacher']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'w-full p-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-600',
                'placeholder': 'Class Name'
            }),
            'level': forms.NumberInput(attrs={
                'class': 'w-full p-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-600',
                'placeholder': 'Class Level'
            }),
            'class_teacher': forms.Select(attrs={
                'class': 'w-full p-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-600',
            })
        }


class EditTeacherForm(forms.ModelForm):
    class Meta:
        model = Teacher
        fields = '__all__' 
        exclude = ['user'] 
        widgets = {
            'contact': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Contact'}),  
            
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.user: 
            self.fields['username'] = forms.CharField(
                initial=self.instance.user.username,  
                widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Username'})
            )


class EditSubjectForm(forms.ModelForm):
    class Meta:
        model = Subject
        fields = ['name', 'teachers']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'w-full p-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-600',
                'placeholder': 'Subject Name'
            }),
            'teachers': forms.SelectMultiple(attrs={
                'class': 'w-full p-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-600',
            })
        }


class SubjectForm(forms.ModelForm):
    class Meta:
        model = Subject
        fields = ['name', 'teachers']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'w-full p-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-600',
                'placeholder': 'Subject Name'
            }),
            'teachers': forms.SelectMultiple(attrs={
                'class': 'w-full p-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-600',
            })
        }