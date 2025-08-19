from django.urls import path
from . import views

app_name = 'teacher'

urlpatterns = [
    path('sign_up/', views.teachers_sign_up, name="sign_up"),
    path('teachers_login/', views.teachers_loginPage, name="teachers_login"),
    path('teachers_dashboard/', views.teachers_dashboard, name="teachers_dashboard"),
    path('logout/', views.logoutUser, name="logout"),
    path('edit_subject/<int:teacher_id>/', views.assign_subjects, name="edit_subject"),
    path('class/<int:class_id>/take_attendance/', views.take_attendance, name='take_attendance'),
    path('upload_results/', views.upload_results_from_excel, name='upload_results'),
    path('confirmation_page/', views.confirmation_page, name='confirmation_page'),
]