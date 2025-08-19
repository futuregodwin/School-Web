from django.contrib import admin

from .models import Student, SchoolClass, Subject, Attendance

admin.site.register(Student)
admin.site.register(SchoolClass)
admin.site.register(Subject)
admin.site.register(Attendance)
