import random
from django.db import models
from django.contrib.auth.models import User

class SchoolClass(models.Model):
    name = models.CharField(max_length=100)
    level = models.IntegerField()  # Example: JSS1, JSS2, etc.
    class_teacher = models.ForeignKey('teachers_app.Teacher', on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.name} - {self.level}"


class Subject(models.Model):
    name = models.CharField(max_length=100)
    teachers = models.ManyToManyField('teachers_app.Teacher', related_name='subjects_list')

    def __str__(self):
        return self.name

class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    registration_number = models.CharField(max_length=8, unique=True, blank=True)
    is_admitted = models.BooleanField(default=False)
    student_class = models.ForeignKey(SchoolClass, on_delete=models.SET_NULL, null=True, related_name='students')
    payment_status = models.BooleanField(default=False)
    payment_proof = models.ImageField(upload_to='payment_proofs/', blank=True, null=True)
    subjects = models.ManyToManyField(Subject, related_name='students', blank=True)
    created = models.DateTimeField(auto_now=True)
    contact = models.CharField(blank=True, null=True, max_length=15)
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2)
    fees = models.ForeignKey('Fee', related_name='school_fees', on_delete=models.CASCADE)
    first_name = models.CharField(blank=True, null=True, max_length=100)
    last_name = models.CharField(blank=True, null=True, max_length=100)


    def __str__(self):
        return f'{self.user.username} - {self.registration_number}'
    


    def generate_registration_number(self):
        while True:
            number = str(random.randint(10000000, 99999999))
            if not Student.objects.filter(registration_number=number).exists():
                return number

    def __str__(self):
        return self.user.username


    def save(self, *args, **kwargs):
            if self.is_admitted and not self.registration_number:
                self.registration_number = self.generate_registration_number()
            super(Student, self).save(*args, **kwargs)



class Attendance(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    date = models.DateField()
    status = models.CharField(max_length=10, choices=[('Present', 'Present'), ('Absent', 'Absent')])

    class Meta:
        unique_together = ('student', 'date')  


class Fee(models.Model):
    class_fee = models.ForeignKey(SchoolClass, on_delete=models.CASCADE)
    amount_due = models.DecimalField(max_digits=10, decimal_places=2)