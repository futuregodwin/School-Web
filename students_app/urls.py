from django.urls import path
from . import views
 
app_name = "student"

urlpatterns = [
    path('', views.home, name="home"),
    path('admission_form/', views.apply_for_admission, name="admission_form"),
    path('student_dashboard/', views.students_dashboard, name="student_dashboard"),
    path('logout/', views.logoutUser, name="logout"),
    path('student_login/', views.loginPage, name="student_login"),
    path('Attendance/', views.student_attendance, name="Attendance"),
    path('attendance_report_download/', views.download_attendance_report, name="attendance_report_download"),
    path('view_subject/', views.view_subjects, name="view_subject"),
    path('view_results/', views.student_results, name="view_results"),
    path('application_confirmation/', views.application_confirmation, name="application_confirmation"),
]



