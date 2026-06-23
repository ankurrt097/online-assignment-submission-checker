from django.contrib import admin
from .models import CustomUser, TeacherProfile, StudentProfile, Course, Semester, Subject, Assignment, Submission

admin.site.register(CustomUser)
admin.site.register(TeacherProfile)
admin.site.register(StudentProfile)
admin.site.register(Course)
admin.site.register(Semester)
admin.site.register(Subject)
admin.site.register(Assignment)
admin.site.register(Submission)
