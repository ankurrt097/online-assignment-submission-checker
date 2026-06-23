# Create your models here.
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings
from django.utils import timezone
import uuid


class CustomUser(AbstractUser):
    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('teacher', 'Teacher'),
        ('student', 'Student'),
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
  

    def __str__(self):
        return self.username

class Course(models.Model):
    name = models.CharField(max_length=100)
    total_semesters = models.IntegerField(default=1)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)
        if is_new:
            for i in range(1, self.total_semesters + 1):
                Semester.objects.get_or_create(course=self, semester_number=i)

class Semester(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='semesters')
    semester_number = models.IntegerField()
    students = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name='enrolled_semesters',
        limit_choices_to={'role': 'student'},
        blank=True
    )

    def __str__(self):
        return f"{self.course.name} - Sem {self.semester_number}"

class TeacherProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    qualification = models.CharField(max_length=200, blank=True)
    experience = models.IntegerField(null=True, blank=True)
    phone = models.CharField(max_length=15, blank=True)
    profile_pic = models.ImageField(upload_to='profile_pics/', blank=True, null=True)

    def __str__(self):
        return self.user.username

class StudentProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    phone = models.CharField(max_length=15, blank=True)
    bio = models.TextField(blank=True)
    enrollment_id = models.CharField(max_length=50, unique=True, blank=True, null=True)
    course = models.ForeignKey(Course, on_delete=models.SET_NULL, null=True, blank=True)
    semester = models.ForeignKey(Semester, on_delete=models.SET_NULL, null=True, blank=True)
    section = models.CharField(max_length=10, blank=True, null=True)
    profile_pic = models.ImageField(upload_to='profile_pics/', blank=True, null=True)

    def __str__(self):
        return self.user.username


class Subject(models.Model):
    name = models.CharField(max_length=100)
    semester = models.ForeignKey(Semester, on_delete=models.CASCADE, related_name='subjects', null=True, blank=True)
    teacher = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        limit_choices_to={'role': 'teacher'},
        related_name='subjects'
    )

    def __str__(self):
        if self.semester and self.semester.course:
            return f"{self.name} ({self.semester.course.name} - Sem {self.semester.semester_number})"
        return self.name

class Assignment(models.Model):
    teacher = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )
    title = models.CharField(max_length=200)
    description = models.TextField()
    file = models.FileField(upload_to='assignments/')
    semester = models.ForeignKey(Semester, on_delete=models.CASCADE, related_name='assignments', null=True, blank=True)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    deadline = models.DateField()

    @property
    def is_overdue(self):
        return timezone.now().date() > self.deadline

    def __str__(self):
        return self.title

# class Submission(models.Model):
#     assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE)
#     student = models.ForeignKey(
#         settings.AUTH_USER_MODEL,
#         on_delete=models.CASCADE,
#         limit_choices_to={'role': 'student'}
#     )
#     file = models.FileField(upload_to='submissions/')
#     submitted_at = models.DateTimeField(auto_now_add=True)

#     class Meta:
#         unique_together = ('assignment', 'student')

#     def __str__(self):
#         return f"{self.student.username} - {self.assignment.title}"

class Submission(models.Model):
    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE)

    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        limit_choices_to={'role': 'student'}
    )

    file = models.FileField(upload_to='submissions/')
    submitted_at = models.DateTimeField(auto_now_add=True)

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('correct', 'Correct'),
        ('incorrect', 'Incorrect')
    ]

    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='pending'
    )

    class Meta:
        unique_together = ('assignment', 'student')

    def __str__(self):
        return f"{self.student.username} - {self.assignment.title}"






class PasswordResetOTP(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    otp = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user} - {self.otp}"
