from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.urls import reverse
from .forms import AdminLoginForm, EditStudentForm, FeesForm, EditFeeForm, ClassForm, EditClassForm, EditTeacherForm, EditSubjectForm, SubjectForm
from students_app.models import * # Student, Attendance, Subject, Fee, SchoolClass
from teachers_app.models import Teacher,  Result
from django.db.models import Count, Sum, FloatField 
from django.core.mail import send_mail
from django.conf import settings
from django.contrib import messages
from django.db.models.functions import ExtractMonth
import json
from django.core.serializers.json import DjangoJSONEncoder
from students_app .forms import AdmissionForm
from django.core.paginator import Paginator
from django.db.models import Q



@login_required
def admin_dashboard(request):
    enrollment_data = Student.objects.extra({'month': "EXTRACT(MONTH FROM created)"}).values('month').annotate(count=Count('id')).order_by('month')

    financial_data = (
    Student.objects.annotate(month=ExtractMonth('created'))
    .values('month')
    .annotate(total=Sum('amount_paid', output_field=FloatField()))
    .order_by('month')
)

    enrollment_chart = {
        'labels': [f'Month {data["month"]}' for data in enrollment_data],
        'values': [data['count'] for data in enrollment_data],
    }

    financial_chart = {
        'labels': [f'Month {data["month"]}' for data in financial_data],
        'values': [float(data['total']) for data in financial_data],
    }

    context = {
        'total_students': Student.objects.count(),
        'total_teachers': Teacher.objects.count(),
        'total_courses': Subject.objects.count(),
        'pending_students': Student.objects.filter(is_admitted=False).count(),
        'pending_teachers': Teacher.objects.filter(is_approved=False).count(),
        'pending_results' : Result.objects.filter(is_approved=False).count(),
        'enrollment_chart': enrollment_chart,
        'financial_chart': financial_chart,
        'financial_chart_json': json.dumps(financial_chart, cls=DjangoJSONEncoder),
    }

    return render(request, 'admin_app/admin_dashboard.html', context)





def admin_login(request):
    if request.user.is_authenticated:
        return redirect('principal:admin_dashboard') 
    form = AdminLoginForm(data=request.POST or None) 
    if request.method == 'POST':
        if form.is_valid():  
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('principal:admin_dashboard') if user.is_superuser else redirect('dashboard')
            else:
                form.add_error(None, "Invalid username or password.")
    return render(request, 'admin_app/login_admin.html', {'form': form})



def student_list(request):
    students = Student.objects.all()
    context = {'students' : students }
    return render(request, 'admin_app/student_list.html', context)



def edit_student(request, student_id):
    student = get_object_or_404(Student, id=student_id) 
    if request.method == "POST":
        form = EditStudentForm(request.POST, instance=student)
        if form.is_valid():
            form.save()
            return redirect('principal:students_list')
    else:
        form = EditStudentForm(instance=student)

    return render(request, 'admin_app/edit_student.html', {'form': form})


def delete_student(request, pk):
    student = get_object_or_404(Student, pk=pk)

    if request.method == "POST":
        user = student.user
        user.delete() 
        student.delete()  

        return redirect('principal:students_list')
    return render(request, 'admin_app/delete_student.html', {'student': student})


def approve_student(request, student_id):
    student = get_object_or_404(Student, id=student_id)
    user = student.user

    if request.method == 'POST':
        student.is_admitted = True
        student.generate_registration_number()  
        user.is_active = True
        user.save() 
        send_registration_email(student)
        student.save()
        messages.success(request, f"Student {student.user.username} has been approved and given a registration number.")
        return redirect('principal:not_approved_student_list')  
    return render(request, 'admin_app/approve_student.html', {'student': student, 'user': user})



def send_registration_email(student):
    subject = f"Welcome to {settings.SITE_NAME} - Your Registration"
    message = f"Dear {student.user.username},\n\n" \
              f"Congratulations! You have been approved for admission to {settings.SITE_NAME}.\n" \
              f"Your registration number is: {student.registration_number}\n\n" \
              f"Please log in to your account to complete the registration process.\n\n" \
              f"Best regards,\nThe {settings.SITE_NAME} Team"
    
    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,  
        [student.user.email],
        fail_silently=False,
    )





def not_approved_student_list(request):
    not_admitted_students = Student.objects.filter(is_admitted=False)
    context = {'not_admitted_students' : not_admitted_students }
    return render(request, 'admin_app/not_approved_student_list.html', context)


def logoutUser(request):
    logout(request)
    messages.success(request, "Logout successful!")
    return redirect('student:home')


def create_fee(request):
    if request.method == "POST":
        form = FeesForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('principal:fees_list') 
    else:
        form = FeesForm()

    return render(request, 'admin_app/create_fees.html', {'form': form})


def fees_list(request):
    fees = Fee.objects.all()
    context = {'fees' : fees }
    return render(request, 'admin_app/fees_list.html', context)



def delete_fees(request, fees_id):
    fees = get_object_or_404(Fee, id=fees_id)

    if request.method == "POST":
        fees.delete()  
        return redirect('principal:fees_list')
    return render(request, 'admin_app/delete_fees.html', {'fees': fees})


def edit_fees(request, fees_id):
    fees = get_object_or_404(Fee, id=fees_id)
    if request.method == "POST":
        form = EditFeeForm(request.POST, instance=fees)
        if form.is_valid():
            form.save()
            return redirect('principal:fees_list')
    else:
        form = EditFeeForm(instance=fees)

    return render(request, 'admin_app/edit_fees.html', {'form': form, 'fees' : fees})


def class_list(request):
    classes = SchoolClass.objects.all()
    context = {'classes' : classes }
    return render(request, 'admin_app/class_list.html', context)


def create_class(request):
    if request.method == "POST":
        form = ClassForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('principal:class_list') 
    else:
        form = ClassForm()

    return render(request, 'admin_app/create_class.html', {'form': form})


def delete_class(request, class_id):
    classes = get_object_or_404(SchoolClass, id=class_id)

    if request.method == "POST":
        classes.delete()  
        return redirect('principal:fees_list')
    return render(request, 'admin_app/delete_class.html', {'classes': classes})



def edit_class(request, class_id):
    classes = get_object_or_404(SchoolClass, id=class_id)
    if request.method == "POST":
        form = EditClassForm(request.POST, instance=classes)
        if form.is_valid():
            form.save()
            return redirect('principal:class_list')
    else:
        form = EditClassForm(instance=classes)

    return render(request, 'admin_app/edit_class.html', {'form': form, 'classes' : classes})



def teachers_list(request):
    teachers_with_classes = []
    teachers = Teacher.objects.all()
    
    for teacher in teachers:
        try:
            assigned_class = SchoolClass.objects.filter(class_teacher=teacher).first()
            
            teachers_with_classes.append({
                'teacher': teacher,
                'assigned_class': assigned_class
            })
        except SchoolClass.DoesNotExist:
            teachers_with_classes.append({
                'teacher': teacher,
                'assigned_class': None
            })
    context = {
        'teachers_with_classes': teachers_with_classes
    }
    
    return render(request, 'admin_app/teachers_list.html', context)


def edit_teacher(request, teacher_id):
    teacher = get_object_or_404(Teacher, id=teacher_id)
    if request.method == "POST":
        form = EditTeacherForm(request.POST, instance=teacher)
        if form.is_valid():
            form.save()
            return redirect('principal:teachers_list')
    else:
        form = EditTeacherForm(instance=teacher)

    return render(request, 'admin_app/edit_teacher.html', {'form': form, 'teacher' : teacher})



def delete_teacher(request, teacher_id):
    teacher = get_object_or_404(Teacher, id=teacher_id)
    if request.method == 'POST':
        teacher.delete()
        return redirect('principal:teachers_list')
    return render(request, 'admin_app/delete_teacher.html', {'teacher' : teacher})



def subjects_list(request):
    subjects = Subject.objects.prefetch_related('teachers_list').all()
    
    context = {'subjects' : subjects }
    return render(request, 'admin_app/subjects_list.html', context)



def edit_subject(request, subject_id):
    subjects = get_object_or_404(Subject, id=subject_id) 
    if request.method == "POST":
        form = EditSubjectForm(request.POST, instance=subjects)
        if form.is_valid():
            form.save()
            return redirect('principal:subjects_list')
    else:
        form = EditSubjectForm(instance=subjects)

    return render(request, 'admin_app/edit_subject.html', {'form': form})


def delete_subject(request, subject_id):
    subjects = get_object_or_404(Subject, id=subject_id) 
    if request.method == 'POST':
        subjects.delete()
        return redirect('principal:subjects_list')
    return render(request, 'admin_app/delete_subject.html', {'subjects' : subjects})



def create_subject(request):
    if request.method == "POST":
        form = SubjectForm(request.POST)
        if form.is_valid():
            subject = form.save(commit=False)
            subject.save()
            form.save_m2m()
            return redirect('principal:subjects_list') 
    else:
        form = SubjectForm()

    return render(request, 'admin_app/create_subjects.html', {'form': form})



def not_approved_teacher_list(request):
    not_admitted_teachers = Teacher.objects.filter(is_approved=False)
    context = {'not_admitted_teachers' : not_admitted_teachers }
    return render(request, 'admin_app/not_approved_teachers_list.html', context)


def approve_teacher(request, teacher_id):
    teacher = get_object_or_404(Teacher, id=teacher_id)
    user = teacher.user

    if request.method == 'POST':
        teacher.is_approved = True
        
        user.is_active = True
        user.save() 
        send_approval_email(teacher)
        teacher.save()
        messages.success(request, f"Teacher {teacher.user.username} has been approved.")
        return redirect('principal:not_approved_teachers_list')  
    return render(request, 'admin_app/approve_teacher.html', {'teacher': teacher, 'user': user})



def send_approval_email(teacher):
    subject = f"Welcome to {settings.SITE_NAME} - Your Registration"
    message = f"Dear {teacher.user.username},\n\n" \
              f"Congratulations! You have been approved to {settings.SITE_NAME}.\n" \
              f"Please log in to your account to complete the registration process.\n\n" \
              f"Best regards,\nThe {settings.SITE_NAME} Team"
    
    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,  
        [teacher.user.email],
        fail_silently=False,
    )




def approve_results(request):
    # Base queryset
    results = Result.objects.filter(is_approved=False)
    
    # Filtering
    student_query = request.GET.get('student', '')
    subject_query = request.GET.get('subject', '')
    teacher_query = request.GET.get('teacher', '')
    
    # Apply filters
    if student_query:
        results = results.filter(student__user__username__icontains=student_query)
    
    if subject_query:
        results = results.filter(subject__name__icontains=subject_query)
    
    if teacher_query:
        results = results.filter(uploaded_by__id=teacher_query)
    
    # Pagination
    paginator = Paginator(results, 10)  # 10 results per page
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    
    # Get all teachers for the dropdown
    teachers = Teacher.objects.all()
    
    context = {
        'pending_results': page_obj,
        'teachers': teachers,
        'is_paginated': page_obj.has_other_pages(),
        'page_obj': page_obj,
    }
    
    # Handle bulk actions
    if request.method == 'POST':
        action = request.POST.get('action')
        result_ids = request.POST.getlist('result_ids')
        
        if action == 'bulk_approve':
            Result.objects.filter(id__in=result_ids).update(is_approved=True)
        elif action == 'bulk_reject':
            Result.objects.filter(id__in=result_ids).update(is_approved=False)
        else:
            if action == 'approve':
                Result.objects.filter(id__in=result_ids).update(is_approved=True)
            elif action == 'reject':
                Result.objects.filter(id__in=result_ids).update(is_approved=False)
        
        return redirect('principal:approve_results')
    
    return render(request, 'admin_app/approve_results.html', context)

