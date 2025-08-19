from django.db import models
from django.contrib.auth.models import User
from students_app.models import Subject
from .utils import convert_to_grade
from django.utils.timezone import now

class Teacher(models.Model):
    class GenderChoices(models.TextChoices):
        MALE = 'M', 'Male'
        FEMALE = 'F', 'Female'
        OTHER = 'O', 'Other'
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    is_approved = models.BooleanField(default=False)
    salary = models.DecimalField(max_digits=10, decimal_places=2)
    created = models.DateTimeField(auto_now=True)
    contact = models.CharField(blank=True, null=True, max_length=15)
    subjects = models.ManyToManyField(Subject, related_name='teachers_list', blank=True)
    profile_picture = models.ImageField(upload_to='profile_picture/', blank=True, null=True)
    gender = models.CharField(
        max_length=1,
        choices=GenderChoices.choices,
        default=GenderChoices.MALE
    )
   


    def __str__(self):
        return self.user.username



class Result(models.Model):
    student = models.ForeignKey('students_app.Student', on_delete=models.CASCADE)
    subject = models.ForeignKey('students_app.Subject', on_delete=models.CASCADE)
    score = models.IntegerField()  # Numeric score (0–100)
    grade = models.CharField(max_length=2, editable=False)  # Alphabetic grade
    uploaded_by = models.ForeignKey('teachers_app.Teacher', on_delete=models.CASCADE)
    created_at = models.DateTimeField(default=now)
    is_approved = models.BooleanField(default=False)
    def save(self, *args, **kwargs):
        self.grade = convert_to_grade(self.score)  # Automatically set the grade
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.student.user.username} - {self.subject.name} - {self.grade}"




