import pandas as pd
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User, Group
from .utils import convert_to_grade
from django.contrib.auth import  authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.utils import timezone
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse
from django.contrib import messages
from .models import Teacher, Result
from .forms import TeacherSubjectForm, AttendanceForm, TeacherForm, UserForm, ResultUploadFileForm
from students_app.models import Subject, Student, SchoolClass, Attendance
from django.conf import settings
from datetime import date
from django.utils.timezone import now, timedelta



def is_teacher(user):
    return user.groups.filter(name='Teachers').exists()

def teachers_sign_up(request):
    if request.method == 'POST':
        user_form = UserForm(request.POST)
        teacher_form = TeacherForm(request.POST, request.FILES)
        
        if user_form.is_valid() and teacher_form.is_valid():
            user = user_form.save(commit=False)
            user.set_password(user_form.cleaned_data['password'])  
            user.is_active = False
            user.save()
            
            teacher = teacher_form.save(commit=False)
            teacher.user = user
            teacher.is_approved = False
            teacher.save()
            teacher_form.save_m2m()
            
            try:
                teacher_group, created = Group.objects.get_or_create(name='Teachers')
                user.groups.add(teacher_group)
            except Exception as e:
                messages.error(request, f"Error adding user to group: {e}")
            
            messages.success(request, "Application submitted successfully! Awaiting approval.")
            return redirect('teacher:confirmation_page')
        else:
            messages.error(request, "There was an error processing your form.")
    user_form = UserForm()
    teacher_form = TeacherForm()
    
    context = {
        'user_form': user_form,
        'teacher_form': teacher_form
    }
    return render(request, 'teachers_app/teachers_sign_up.html', context)


@login_required(login_url='teachers_login/')  
@user_passes_test(is_teacher)
def teachers_dashboard(request):
    first_name = request.user.first_name
    try:
        teacher = Teacher.objects.get(user=request.user)
    except Teacher.DoesNotExist:
        messages.error(request, "Teacher does not exist.")
    contact = teacher.contact
    salary = teacher.salary
    subjects =teacher.subjects.all()
    students = Student.objects.filter(subjects__in=teacher.subjects.all())
    is_teacher = request.user.groups.filter(name="Teachers").exists()
    context = {
        'username': first_name,
        'contact': contact,
        'salary': salary,
        'profile_picture': teacher.profile_picture.url if teacher.profile_picture else None,
        'subjects': subjects,
        'is_teacher': is_teacher,
        'students': students,
        'teacher':teacher,
        'classes': teacher.schoolclass_set.all()
    }
    return render(request, 'teachers_app/teachers_dashboard.html', context)


def teachers_loginPage(request):
    page = 'teachers_login'

    if request.user.is_authenticated:
        return redirect('teacher:teachers_dashboard') 

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        try:
            user = authenticate(request, username=username, password=password)

            if user is not None:
                login(request, user)
                messages.success(request, "Login successful!")
                return redirect('teacher:teachers_dashboard')
            else:
                 messages.error(request, 'Username OR password does not exist')
        except Teacher.DoesNotExist:
                 messages.error(request, "User does not exist")

    context = {'page':page}
    return render(request, 'teachers_app/teachers_loginPage.html', context)



def logoutUser(request):
    logout(request)
    messages.success(request, "Logout successful!")
    return redirect('student:home')





def assign_subjects(request, teacher_id):
    teacher = get_object_or_404(Teacher, id=teacher_id)

    if request.method == 'POST':
        form = TeacherSubjectForm(request.POST, instance=teacher)
        if form.is_valid():
            form.save()
            messages.success(request, "Subjects assigned successfully!")
            return redirect('teacher:teachers_dashboard')  
        else:
            messages.error(request, "Error assigning subjects.")
    else:
        form = TeacherSubjectForm(instance=teacher)

    return render(request, 'teachers_app/assign_subjects.html', {'form': form, 'teacher': teacher})



def take_attendance(request, class_id):
    teacher = request.user.teacher  
    selected_class = get_object_or_404(SchoolClass, id=class_id, class_teacher=teacher)
    students_in_class = selected_class.students.all()  

    if request.method == 'POST':
        form = AttendanceForm(request.POST, students=students_in_class)
        if form.is_valid():
            for student in students_in_class:
                status = form.cleaned_data.get(f'present_{student.id}')
                Attendance.objects.update_or_create(
                    student=student,
                    date=form.cleaned_data['date'],
                    defaults={'status': 'Present' if status else 'Absent'}
                )
            return redirect('teacher:teachers_dashboard')  
    else:
        form = AttendanceForm(students=students_in_class)

    present_fields = [
        field_name for field_name in form.fields if field_name.startswith("present_")
    ]

    return render(request, 'teachers_app/take_attendance.html', {
        'form': form,
        'selected_class': selected_class,
        'students_in_class': students_in_class,
        'present_fields': present_fields,
    })



def upload_results_from_excel(request):
    if request.method == 'POST':
        form = ResultUploadFileForm(request.POST, request.FILES)
        
        if form.is_valid():
            excel_file = request.FILES['excel_file']
            teacher = request.user.teacher  # Assuming teacher profile is linked to the logged-in user
            
            try:
                # Read the Excel file into a pandas DataFrame
                df = pd.read_excel(excel_file)
                
                # Process each row in the DataFrame and save to database
                for index, row in df.iterrows():
                    try:
                        # Get student and subject from the row
                        student = Student.objects.get(registration_number=row['student_reg'])
                        subject = Subject.objects.get(name=row['subject_name'], teachers=teacher)
                        score = row['score']
                        grade = convert_to_grade(score)

                        # Check if the student offers the subject
                        if not student.subjects.filter(id=subject.id).exists():
                            messages.error(
                                request, f"Student {student.user.username} does not offer {subject.name}."
                            )
                            continue

                        # Check if a result already exists within the timeframe
                        timeframe_start = now() - timedelta(days=30)
                        timeframe_end = now()
                        existing_result = Result.objects.filter(
                            student=student, 
                            subject=subject,
                            score = score,
                            grade = grade,
                            created_at__range=(timeframe_start, timeframe_end)
                        ).exists()
                        
                        if existing_result:
                            messages.error(
                                request, f"Result for {student.user.username} in {subject.name} has already been uploaded."
                            )
                            continue

                        # Create and save the result
                        Result.objects.create(
                            student=student,
                            subject=subject,
                            score=score,
                            grade=grade,
                            uploaded_by=teacher,
                            is_approved=False  # Unapproved by default
                        )
                    except Subject.DoesNotExist:
                        messages.error(
                            request, f"Subject '{row['subject_name']}' does not exist or is not assigned to you."
                        )
                    except Student.DoesNotExist:
                        messages.error(
                            request, f"Student with registration number '{row['student_reg']}' does not exist."
                        )
                
                messages.success(request, "Results uploaded successfully! Awaiting approval.")
                return redirect('teacher:teachers_dashboard')

            except Exception as e:
                messages.error(request, f"An error occurred: {e}")
        else:
            messages.error(request, "Invalid file uploaded. Please try again.")
    
    else:
        form = ResultUploadFileForm()

    return render(request, 'teachers_app/upload_results.html', {'form': form})


def confirmation_page(request):
    return render(request, 'teachers_app/confirmation_page.html')

