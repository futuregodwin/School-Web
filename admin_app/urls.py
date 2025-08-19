from django.urls import path
from . import views


app_name = 'principal'

urlpatterns = [
    path('login_admin/', views.admin_login, name="login_admin"),
    path('admin_logout/', views.logoutUser, name="admin_logout"),
    path('admin_dashboard/', views.admin_dashboard, name="admin_dashboard"),
    path('students_list/', views.student_list, name="students_list"),
    path('edit_student/<int:student_id>/', views.edit_student, name="edit_student"),
    path('delete_student/<int:pk>/', views.delete_student, name="delete_student"),
    path('not_approved_student_list/', views.not_approved_student_list, name='not_approved_student_list'),
    path('approve_student/<int:student_id>/', views.approve_student, name='approve_student'),
    path('create_fee/', views.create_fee, name='create_fee'),
    path('fees_list/', views.fees_list, name='fees_list'),
    path('class_list/', views.class_list, name='class_list'),
    path('delete_fees<int:fees_id>/', views.delete_fees, name='delete_fees'),
    path('edit_fees/<int:fees_id>/', views.edit_fees, name='edit_fees'),
    path('create_class/', views.create_class, name='create_class'),
    path('delete_class<int:class_id>/', views.delete_class, name='delete_class'),
    path('edit_class/<int:class_id>/', views.edit_class, name='edit_class'),
    path('teachers_list/', views.teachers_list, name='teachers_list'),
    path('teacher/edit_teacher/<int:teacher_id>/', views.edit_teacher, name='edit_teacher'),
    path('delete_teacher/<int:teacher_id>/', views.delete_teacher, name='delete_teacher'),
    path('subjects_list/', views.subjects_list, name='subjects_list'),
    path('edit_subject/<int:subject_id>/', views.edit_subject, name="edit_subject"),
    path('delete_subject/<int:subject_id>/', views.delete_subject, name='delete_subject'),
    path('create_subject/', views.create_subject, name='create_subject'),
    path('approve_teacher/<int:teacher_id>/', views.approve_teacher, name='approve_teacher'),
    path('not_approved_teachers_list/', views.not_approved_teacher_list, name='not_approved_teachers_list'),
    path('approve-results/', views.approve_results, name='approve_results'),
    
]



