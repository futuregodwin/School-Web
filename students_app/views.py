from django.shortcuts import render, redirect
from django.contrib.auth.models import User, Group
from .models import SchoolClass, Subject, Student, Attendance, Fee
from .forms import AdmissionForm, UserForm
from django.contrib.auth import  authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.utils import timezone
from django.core.exceptions import ObjectDoesNotExist
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from django.http import HttpResponse
from django.contrib import messages
from django.conf import settings  
from teachers_app.models import Result
from decimal import Decimal
from django.db import IntegrityError



def is_student(user):
    return user.groups.filter(name='Student').exists()

def home(request):
    return render(request, 'students_app/home.html')


def apply_for_admission(request):
    if request.method == 'POST':
        user_form = UserForm(request.POST)
        admission_form = AdmissionForm(request.POST, request.FILES)
        class_id = request.POST.get('student_class')
        amount_paid = request.POST.get('amount_paid')

        try:
            student_class = SchoolClass.objects.get(id=class_id)
            fee = Fee.objects.get(class_fee=student_class)
            amount_due = fee.amount_due
            
            try:
                amount_paid = Decimal(amount_paid)
            except (ValueError, TypeError):
                messages.error(request, "Invalid amount paid.")
                return redirect('student:apply_for_admission')

            if amount_paid == amount_due:
                if user_form.is_valid() and admission_form.is_valid():
                    # Create user without logging in
                    user = user_form.save(commit=False)
                    user.set_password(user_form.cleaned_data['password'])
                    user.is_active = False  # Optional: make user inactive until approved
                    user.save()

                    student = admission_form.save(commit=False)
                    student.user = user
                    student.fees = fee
                    student.is_admitted = False  # Set to pending
                    student.save()
                    admission_form.save_m2m()

                    student_group, created = Group.objects.get_or_create(name='Student')
                    user.groups.add(student_group)

                    messages.success(request, "Application submitted successfully! Awaiting approval.")
                    return redirect('student:application_confirmation')  # Create this view/template
                else:
                    messages.error(request, "There was an error processing your form.")
            elif amount_paid > amount_due:
                messages.info(request, "You overpaid! Meet the Bursar with your receipt to claim the balance.")
            else:
                messages.error(request, "Incomplete payment!")
        except SchoolClass.DoesNotExist:
            messages.error(request, "Invalid class selected.")
        except Fee.DoesNotExist:
            messages.error(request, "No fee information found for the selected class.")
        # except IntegrityError:
        #      messages.error(request, "An error occurred while processing your data. Please try again.")

    # Initial forms
    user_form = UserForm()
    admission_form = AdmissionForm()

    context = {
        'user_form': user_form,
        'admission_form': admission_form,
    }
    return render(request, 'students_app/apply_for_admission.html', context)
  

@login_required(login_url='student_login')
@user_passes_test(is_student)
def students_dashboard(request):
    username = request.user.username
    contact = None
    fees = None
    try:
        student = Student.objects.get(user=request.user)
        contact = student.contact
        fees = student.fees.amount_due
        is_student = request.user.groups.filter(name="Student").exists()
        subjects = Subject.objects.filter()
    except Student.DoesNotExist:
       messages.error(request, "Student does not exist.")
    context = {'username': username, 'contact': contact, 'fees': fees, 'is_student': is_student, 'subjects': subjects}
    return render(request, 'students_app/students_dashboard.html', context)


def loginPage(request):
    page = 'student_login'

    if request.user.is_authenticated:
        return redirect('student:student_dashboard') 

    if request.method == 'POST':
        registration_number = request.POST.get('registration_number')
        password = request.POST.get('password')
        try:
            student = Student.objects.get(registration_number=registration_number).user.username

            try:
                    user = User.objects.get(username=student)
            except:
               
                messages.error(request, "User does not exist")
            
            user = authenticate(request, username=student, password=password)

            if user is not None:
                login(request, user)
                messages.success(request, "Login successful!")
                return redirect('student:student_dashboard')
            else:
                 messages.error(request, 'Reg. no OR password does not exist')
        except Student.DoesNotExist:
                 messages.error(request, "User does not exist")

    context = {'page':page}
    return render(request, 'students_app/loginPage.html', context)


def logoutUser(request):
    logout(request)
    messages.success(request, "Logout successful!")
    return redirect('student:home')



def student_attendance(request):
    try:
        student = Student.objects.get(user=request.user)
    except Student.DoesNotExist:
       messages.error(request, 'Student does not exit')
    attendance_records = Attendance.objects.filter(student=student).order_by('-date')
    total_days = attendance_records.count()
    days_present = attendance_records.filter(status='Present').count()
    days_absent = attendance_records.filter(status='Absent').count()

    context = {
        'attendance_records': attendance_records,
        'total_days': total_days,
        'days_present': days_present,
        'days_absent': days_absent,
    }
    return render(request, 'students_app/student_attendance.html', context)




def download_attendance_report(request):
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="attendance_report.pdf"'

    # Create a PDF canvas
    pdf_canvas = canvas.Canvas(response, pagesize=A4)
    width, height = A4

    # Draw header
    pdf_canvas.setFont("Helvetica-Bold", 16)
    pdf_canvas.drawString(100, height - 100, "Attendance Report")

    # Add attendance records
    y_position = height - 150
    pdf_canvas.setFont("Helvetica", 12)
    records = Attendance.objects.filter(student=request.user.student)

    if records.exists():
        pdf_canvas.drawString(100, y_position, f"Total Days: {records.count()}")
        y_position -= 20
        pdf_canvas.drawString(100, y_position, f"Days Present: {records.filter(status='Present').count()}")
        y_position -= 20
        pdf_canvas.drawString(100, y_position, f"Days Absent: {records.filter(status='Absent').count()}")
        y_position -= 40

        # Table Headers
        pdf_canvas.setFont("Helvetica-Bold", 12)
        pdf_canvas.drawString(100, y_position, "Date")
        pdf_canvas.drawString(250, y_position, "Status")
        y_position -= 20

        # Table Rows
        pdf_canvas.setFont("Helvetica", 10)
        for record in records:
            pdf_canvas.drawString(100, y_position, str(record.date))
            pdf_canvas.drawString(250, y_position, record.status)
            y_position -= 20
    else:
        pdf_canvas.drawString(100, y_position, "No attendance records found.")

    # Finish the PDF
    pdf_canvas.showPage()
    pdf_canvas.save()
    return response



def view_subjects(request):
    try:
        student = Student.objects.get(user=request.user)
        subjects = student.subjects.all()
        
    except Student.DoesNotExist:
        student = None
        subjects = []

    context = {
        'student': student,
        'subjects': subjects
    }

    return render(request, 'students_app/subject_view.html', context)





@login_required
def student_results(request):
    student = request.user.student  
    subjects = student.subjects.all()
    results = Result.objects.filter(student=student, is_approved=True)

    results_dict = {result.subject: result for result in results}
    display_results = []

    for subject in subjects:
        if subject in results_dict:
            display_results.append(results_dict[subject])
        else:
            display_results.append({'subject': subject, 'message': "Results not uploaded yet but will soon be."})

    return render(request, 'students_app/results.html', {'display_results': display_results})




def application_confirmation(request):
    return render(request, 'students_app/application_confirmation.html')