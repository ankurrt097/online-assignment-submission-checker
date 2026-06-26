import email
from urllib import request
from urllib import request

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import ensure_csrf_cookie
from django.urls import reverse
from django.core.mail import send_mail
from django.db.models import Q
import random
import string
from django.contrib.auth.hashers import make_password
from django.contrib.auth import get_user_model
from dns import message
import traceback
from starlette.types import Send

from myproject import settings
from .models import PasswordResetOTP
from .models import CustomUser, TeacherProfile, StudentProfile, Course, Semester, Assignment, Submission, Subject
from django.utils import timezone
from datetime import timedelta
from django.shortcuts import redirect


def generate_password():
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for i in range(8))
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.views.decorators.csrf import ensure_csrf_cookie

from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.conf import settings
from django.core.mail import send_mail


@ensure_csrf_cookie
def admin_login(request):

    if request.method == "POST":

        username = request.POST.get("username")
        password = request.POST.get("password")

        print(username, password)

        user = authenticate(
            request,
            username=username,
            password=password
        )

        print("USER:", user)

        if user:

            print("ROLE:", user.role)

            login(request, user)

            return redirect("admin_dashboard")

        else:
            messages.error(request, "Invalid Username or Password")

    return render(request, "admin/admin_login.html")




@login_required
def admin_dashboard(request):
    # if request.user.role != 'admin':
    #     return redirect('admin_login')
        
    teachers_count = CustomUser.objects.filter(role='teacher').count()
    students_count = CustomUser.objects.filter(role='student').count()
    courses_count = Course.objects.count()
    subjects_count = Subject.objects.count()

    return render(request, "admin/dashboard.html", {
        'teachers_count': teachers_count,
        'students_count': students_count,
        'courses_count': courses_count,
        'subjects_count': subjects_count
    })




@login_required
def create_teacher(request):

    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")

        if CustomUser.objects.filter(username=username).exists():
            messages.error(request, "Username already exists!")
            return redirect("create_teacher")

        CustomUser.objects.create_user(
            username=username,
            email=email,
            password=password,
            role="teacher",
        )

        login_url = request.build_absolute_uri(reverse("login"))

        try:
            send_mail(
                subject="Your Teacher Account Created",
                message=f"""Hello {username},

Your teacher account has been created successfully.

Username: {username}
Password: {password}

Login here: {login_url}

Please change your password after login.

Regards,
Admin
""",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[email],
                fail_silently=False,
            )

            print("Email sent successfully")

        
        except Exception as e:
                print("EMAIL ERROR:", repr(e))
                traceback.print_exc()
            

        messages.success(request, "Teacher created successfully!")
        return redirect("admin_dashboard")

    return render(request, "admin/create_teacher.html")

@login_required
def teacher_list(request):
    # if request.user.role != 'admin':
    #     return redirect('admin_login')
    teachers = CustomUser.objects.filter(role='teacher')
    return render(request, "admin/teacher_list.html", {'teachers': teachers})



@login_required
def admin_course_list(request):
    # if request.user.role != 'admin':
    #     return redirect('login')

    courses = Course.objects.prefetch_related('semesters').all().order_by('name')
    return render(request, "admin/course_list.html", {"courses": courses})


@login_required
def create_course(request):
    # if request.user.role != 'admin':
    #     return redirect('admin_login')

    if request.method == "POST":
        name = request.POST.get("name")
        total_semesters = request.POST.get("total_semesters")
        
        if not name or not total_semesters:
            messages.error(request, "All fields are required")
            return redirect('create_course')
        
        Course.objects.create(name=name, total_semesters=int(total_semesters))
        messages.success(request, f"Course '{name}' and its semesters created successfully.")
        return redirect('admin_dashboard')

    return render(request, 'admin/create_course.html')

@login_required
def create_subject(request):
    # if request.user.role != 'admin':
    #     return redirect('admin_login')

    semesters = Semester.objects.select_related('course').all().order_by('course__name', 'semester_number')
    teachers = CustomUser.objects.filter(role='teacher')

    if request.method == "POST":
        name = request.POST.get("name")
        semester_id = request.POST.get("semester_id")
        teacher_id = request.POST.get("teacher_id")

        if not name or not semester_id or not teacher_id:
            messages.error(request, "All fields are required")
            return redirect('create_subject')

        semester = get_object_or_404(Semester, id=semester_id)
        teacher = get_object_or_404(CustomUser, id=teacher_id, role='teacher')

        Subject.objects.create(name=name, semester=semester, teacher=teacher)
        messages.success(request, f"Subject '{name}' created for {semester}")
        return redirect('admin_subjects')

    return render(request, 'admin/create_subject.html', {
        'semesters': semesters,
        'teachers': teachers
    })


@login_required
def edit_subject(request, subject_id):
    # if request.user.role != 'admin':
    #     return redirect('admin_login')
        
    subject = get_object_or_404(Subject, id=subject_id)
    semesters = Semester.objects.select_related('course').all()
    teachers = CustomUser.objects.filter(role='teacher')

    if request.method == "POST":
        name = request.POST.get("name")
        semester_id = request.POST.get("semester_id")
        teacher_id = request.POST.get("teacher_id")

        if not name or not semester_id or not teacher_id:
            messages.error(request, "All fields are required")
            return redirect('edit_subject', subject_id=subject.id)

        semester = get_object_or_404(Semester, id=semester_id)
        teacher = get_object_or_404(CustomUser, id=teacher_id, role='teacher')

        subject.name = name
        subject.semester = semester
        subject.teacher = teacher
        subject.save()
        
        messages.success(request, f"Subject '{name}' updated successfully!")
        return redirect('admin_subjects')

    return render(request, 'admin/edit_subject.html', {
        'subject': subject,
        'semesters': semesters,
        'teachers': teachers
    })


@login_required
def admin_subjects(request):
    # if request.user.role != 'admin':
    #     return redirect('admin_login')
    
    subjects = Subject.objects.select_related('semester__course', 'teacher').all().order_by('semester__course__name', 'name')
    return render(request, 'admin/subjects.html', {'subjects': subjects})


@login_required
def delete_subject(request, subject_id):
    # if request.user.role != 'admin':
    #     return redirect('admin_login')
    
    subject = get_object_or_404(Subject, id=subject_id)
    name = subject.name
    classroom_name = subject.classroom.name
    subject.delete()
    messages.success(request, f"Subject '{name}' deleted from {classroom_name}")
    return redirect('admin_subjects')

# ─── Auth Views ───────────────────────────────────────────────────────────────

@ensure_csrf_cookie
def user_login(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)
        if user:
            if user.role == 'admin':
                messages.error(request, "Admin cannot login here. Please use Admin Login page.")
                return redirect('admin_login')
            login(request, user)
            if user.role == 'teacher':
                return redirect('teacher_dashboard')
            elif user.role == 'student':
                return redirect('student_dashboard')
        else:
            messages.error(request, "Invalid Credentials")
    return render(request, "auth/login.html")


def user_logout(request):
    logout(request)
    return redirect('login')


@login_required
def student_dashboard(request):
    if request.user.role != 'student':
        return redirect('login')
    
    profile, created = StudentProfile.objects.get_or_create(user=request.user)
    
    # Get student's assignments based on their enrolled semesters
    semesters = request.user.enrolled_semesters.all()
    
    assignments = Assignment.objects.filter(
        semester__in=semesters
    ).select_related('subject', 'semester__course').order_by('-created_at')
    
    # Pre-calculate robust aliases
    for a in assignments:
        a.n = a.title
        a.s = a.subject.name if a.subject else "General"
        a.c = str(a.semester)
        a.d = a.deadline.strftime("%d %b %Y")
        a.o = a.is_overdue
    
    submissions = Submission.objects.filter(student=request.user)
    submission_dict = {s.assignment_id: s.status for s in submissions}
    submitted_ids = list(submission_dict.keys())
    
    for a in assignments:
        a.status = submission_dict.get(a.id)

    context = {
        'student_semesters': semesters,
        'assignments': assignments,
        'total_semesters': semesters.count(),
        'total_assignments': assignments.count(),
        'total_submissions': submissions.count(),
        'submitted_ids': submitted_ids,
        'profile': profile,
    }
    return render(request, "student/student_dashboard.html", context)


@login_required
def student_assignments(request):
    if request.user.role != 'student':
        return redirect('login')

    profile, created = StudentProfile.objects.get_or_create(user=request.user)
    semesters = request.user.enrolled_semesters.all()
    
    assignments = Assignment.objects.filter(
        semester__in=semesters
    ).select_related('subject', 'semester__course').order_by('-created_at')
    
    for a in assignments:
        a.n = a.title
        a.s = a.subject.name if a.subject else "General"
        a.c = str(a.semester)
        a.d = a.deadline.strftime("%d %b %Y")
        a.o = a.is_overdue
    
    submissions = Submission.objects.filter(student=request.user)
    submission_dict = {s.assignment_id: s.status for s in submissions}
    submitted_ids = list(submission_dict.keys())

    for a in assignments:
        a.status = submission_dict.get(a.id)

    return render(request, 'student/assignments.html', {
        'assignments': assignments,
        'submitted_ids': submitted_ids,
        'profile': profile,
    })


@login_required
def submit_assignment(request, assignment_id):
    if request.user.role != 'student':
        return redirect('login')

    assignment = get_object_or_404(Assignment, id=assignment_id)

    # Check if already submitted
    if Submission.objects.filter(assignment=assignment, student=request.user).exists():
        messages.error(request, "You have already submitted this assignment.")
        return redirect('student_dashboard')

    if request.method == "POST":
        file = request.FILES.get("file")
        if not file:
            messages.error(request, "Please select a file to submit.")
            return render(request, 'student/submit.html', {'assignment': assignment})

        Submission.objects.create(
            assignment=assignment,
            student=request.user,
            file=file
        )
        messages.success(request, "Assignment submitted successfully!")
        return redirect('student_dashboard')

    return render(request, 'student/submit.html', {'assignment': assignment})
@login_required
def student_profile(request):
    if request.user.role != 'student':
        return redirect('login')
    profile, created = StudentProfile.objects.get_or_create(user=request.user)
    return render(request, "student/profile.html", {'profile': profile})


@login_required
def edit_student_profile(request):
    # if request.user.role != 'student':
    #     return redirect('login')
    profile, created = StudentProfile.objects.get_or_create(user=request.user)
    if request.method == "POST":
        profile.phone = request.POST.get('phone')
        profile.bio = request.POST.get('bio')
        profile.enrollment_id = request.POST.get('enrollment_no') # Match template field name if it wasn't changed yet
        profile.semester = request.POST.get('semester', 1)
        if request.FILES.get("profile_pic"):
            profile.profile_pic = request.FILES.get("profile_pic")
        profile.save()
        messages.success(request, "Profile updated successfully!")
        return redirect('student_profile')
    return render(request, "student/edit_profile.html", {'profile': profile})



@login_required
def teacher_dashboard(request):
    # if request.user.role != 'teacher':
    #     return redirect('login')

    # Get semesters and subjects taught by the teacher
    subjects = Subject.objects.filter(teacher=request.user).select_related('semester__course')
    
    # Semesters where teacher teaches a subject
    semesters = Semester.objects.filter(
        subjects__teacher=request.user
    ).select_related('course').distinct()
    
    # Assignments created by teacher
    assignments = Assignment.objects.filter(teacher=request.user)
    
    # Submissions for teacher's assignments
    submissions_qs = Submission.objects.filter(assignment__subject__teacher=request.user)
    total_submissions = submissions_qs.count()
    
    # Accurate student count (students in any semester assigned to this teacher)
    total_students = CustomUser.objects.filter(role='student', enrolled_semesters__in=semesters).distinct().count()
    
    recent_submissions = submissions_qs.select_related('student', 'assignment').order_by('-submitted_at')[:5]

    for s in recent_submissions:
        student = s.student
        profile = getattr(student, 'studentprofile', None)
        s.n = student.username
        s.p = profile.profile_pic.url if profile and profile.profile_pic else None
        s.d = s.submitted_at.strftime("%d %b %Y")
        s.t = ""

    context = {
        'total_semesters': semesters.count(),
        'total_students': total_students,
        'total_subjects': subjects.count(),
        'total_assignments': assignments.count(),
        'total_submissions': total_submissions,
        'recent_submissions': recent_submissions,
    }
    return render(request, 'teacher/teacher_dashboard.html', context)


@login_required
def teacher_profile(request):
    # if request.user.role != 'teacher':
    #     return redirect('login')
    profile, _ = TeacherProfile.objects.get_or_create(user=request.user)
    return render(request, 'teacher/profile.html', {'profile': profile})


@login_required
def edit_teacher_profile(request):
    # if request.user.role != 'teacher':
    #     return redirect('login')

    profile, _ = TeacherProfile.objects.get_or_create(user=request.user)

    if request.method == "POST":
        profile.qualification = request.POST.get("qualification")
        profile.experience = request.POST.get("experience")
        profile.phone = request.POST.get("phone")
        if request.FILES.get("profile_pic"):
            profile.profile_pic = request.FILES.get("profile_pic")
        profile.save()
        messages.success(request, "Profile Updated Successfully")
        return redirect('teacher_profile')

    return render(request, 'teacher/edit_profile.html', {'profile': profile})




@login_required
def class_list(request):
    # if request.user.role != 'admin':
    #     return redirect('login')

    classes = ClassRoom.objects.all().order_by('semester', 'name')

    return render(request, "admin/class_list.html", {"classes": classes})


@login_required
def semester_detail(request, semester_id):
    # if request.user.role != 'teacher':
    #     return redirect('login')
        
    semester = get_object_or_404(
        Semester.objects.filter(subjects__teacher=request.user).distinct(),
        id=semester_id
    )
    subjects = Subject.objects.filter(semester=semester, teacher=request.user)
    students = semester.students.all()
    
    for student in students:
        profile = getattr(student, 'studentprofile', None)
        student.display_enrollment = profile.enrollment_id if profile else "N/A"
        student.display_email = student.email or "None"
        student.display_pic_url = profile.profile_pic.url if profile and profile.profile_pic else None
        student.n = student.username
        student.e = student.display_enrollment
        student.m = student.display_email
        student.p = student.display_pic_url

    return render(request, 'teacher/semester_detail.html', {
        'semester': semester,
        'subjects': subjects,
        'students': students
    })


@login_required
def add_student_to_semester(request, semester_id):
    semester = get_object_or_404(
        Semester.objects.filter(subjects__teacher=request.user).distinct(),
        id=semester_id
    )
    students = CustomUser.objects.filter(role='student')

    if request.method == "POST":
        student_id = request.POST.get("student_id")
        student = get_object_or_404(CustomUser, id=student_id, role='student')
        semester.students.add(student)
        
        # Also update profile
        profile, _ = StudentProfile.objects.get_or_create(user=student)
        profile.semester = semester
        profile.course = semester.course
        profile.save()
        
        messages.success(request, "Student Added Successfully")
        return redirect('semester_detail', semester_id=semester_id)

    return render(request, 'teacher/add_student.html', {
        'semester': semester,
        'students': students
    })


@login_required
def create_assignment(request):
    # if request.user.role != 'teacher':
    #     return redirect('login')
    
    subjects = Subject.objects.filter(teacher=request.user).select_related('semester__course')

    if request.method == "POST":
        title = request.POST.get("title")
        description = request.POST.get("description")
        subject_id = request.POST.get("subject_id")
        deadline = request.POST.get("deadline")
        file = request.FILES.get("file")

        if not title or not subject_id or not deadline or not file:
            messages.error(request, "All fields are required")
            return redirect('create_assignment')

        subject = get_object_or_404(Subject, id=subject_id, teacher=request.user)
        semester = subject.semester

        Assignment.objects.create(
            teacher=request.user,
            semester=semester,
            subject=subject,
            title=title,
            description=description,
            file=file,
            deadline=deadline
        )
        messages.success(request, f"Assignment created for {subject.name}")
        return redirect('teacher_assignments')

    return render(request, 'teacher/create_assignment.html', {'subjects': subjects})



@login_required
def teacher_assignments(request):
    # if request.user.role != 'teacher':
    #     return redirect('login')
    assignments = Assignment.objects.filter(subject__teacher=request.user).select_related('subject', 'semester__course').order_by('-created_at')
    
    for a in assignments:
        a.n = a.title
        a.s = a.subject.name if a.subject else "General"
        a.c = str(a.semester)
        a.d = a.deadline.strftime("%d %b %Y")
    
    return render(request, "teacher/assignments.html", {'assignments': assignments})


@login_required
def assignment_detail(request, id):
    assignment = get_object_or_404(Assignment, id=id, teacher=request.user)
    return render(request, "teacher/assignment_detail.html", {"assignment": assignment})


@login_required
def edit_assignment(request, id):
    # if request.user.role != 'teacher':
    #     return redirect('login')

    assignment = get_object_or_404(Assignment, id=id, teacher=request.user)
    subjects = Subject.objects.filter(teacher=request.user).select_related('semester__course')

    if request.method == "POST":
        title = request.POST.get("title")
        description = request.POST.get("description")
        deadline = request.POST.get("deadline")
        subject_id = request.POST.get("subject_id")

        if not title or not description or not deadline or not subject_id:
            messages.error(request, "All fields except file are required.")
            return render(request, 'teacher/edit_assignment.html', {
                'assignment': assignment,
                'subjects': subjects
            })

        try:
            subject = get_object_or_404(Subject, id=subject_id, teacher=request.user)
            assignment.title = title
            assignment.description = description
            assignment.deadline = deadline
            assignment.subject = subject
            assignment.semester = subject.semester
            
            if request.FILES.get("file"):
                assignment.file = request.FILES.get("file")
                
            assignment.save()
            messages.success(request, "Assignment updated successfully!")
            return redirect('teacher_assignments')
        except Exception as e:
            messages.error(request, f"Error updating assignment: {str(e)}")
            return render(request, 'teacher/edit_assignment.html', {
                'assignment': assignment,
                'subjects': subjects
            })

    for s in subjects:
        s.is_selected = (assignment.subject and s.id == assignment.subject.id)

    return render(request, 'teacher/edit_assignment.html', {
        'assignment': assignment,
        'subjects': subjects
    })


@login_required
def delete_assignment(request, id):
    

    assignment = get_object_or_404(Assignment, id=id, teacher=request.user)

    if request.method == "POST":
        assignment.delete()
        messages.success(request, "Assignment deleted successfully!")
        return redirect('teacher_assignments')

    return render(request, 'teacher/delete_assignment.html', {'assignment': assignment})


@login_required
def submissions(request, assignment_id):
    # if request.user.role != 'teacher':
    #     return redirect('login')

    assignment = get_object_or_404(
        Assignment, id=assignment_id, subject__teacher=request.user
    )
    subs = Submission.objects.filter(assignment=assignment)
    
    # Pre-calculate student attributes to avoid template tag splitting issues
    for s in subs:
        student = s.student
        profile = getattr(student, 'studentprofile', None)
        s.student_display_name = student.username
        s.student_enrollment = profile.enrollment_id if profile else "N/A"
        s.student_email = student.email or "None"
        s.student_pic_url = profile.profile_pic.url if profile and profile.profile_pic else None
        s.formatted_date = s.submitted_at.strftime("%d %b %Y")
        s.formatted_time = s.submitted_at.strftime("%I:%M %p")
        # Robust aliases for template stability
        s.n, s.e, s.m = s.student_display_name, s.student_enrollment, s.student_email
        s.p, s.d, s.t = s.student_pic_url, s.formatted_date, s.formatted_time

    context = {
        'assignment': assignment,
        'submissions': subs,
        'total_submissions': subs.count()
    }
    return render(request, 'teacher/submissions.html', context)

# All_submissions
@login_required
def all_submissions(request):
    # if request.user.role != 'teacher':
    #     return redirect('login')

    all_subs = Submission.objects.filter(
        assignment__subject__teacher=request.user
    ).order_by('-submitted_at')

    # Pre-calculate student attributes and robust aliases
    for s in all_subs:
        student = s.student
        profile = getattr(student, 'studentprofile', None)
        s.student_display_name = student.username
        s.student_enrollment = profile.enrollment_id if profile else "N/A"
        s.student_email = student.email or "None"
        s.student_pic_url = profile.profile_pic.url if profile and profile.profile_pic else None
        s.formatted_date = s.submitted_at.strftime("%d %b %Y")
        
        # Robust aliases
        s.n, s.e, s.m = s.student_display_name, s.student_enrollment, s.student_email
        s.p, s.d = s.student_pic_url, s.formatted_date
        s.sn = s.assignment.subject.name if s.assignment.subject else "General"

    context = {
        'submissions': all_subs,
        'total_submissions': all_subs.count()
    }
    return render(request, 'teacher/all_submissions.html', context)


# Create_students

@login_required
def create_student(request):
    # if request.user.role != 'admin':
    #     return redirect('admin_login')
    
    courses = Course.objects.all()
    semesters = Semester.objects.select_related('course').all().order_by('course__name', 'semester_number')
    
    if request.method == "POST":
        enrollment_id = request.POST.get("enrollment_id")
        name = request.POST.get("name")
        email = request.POST.get("email")
        section = request.POST.get("section")
        semester_id = request.POST.get("semester_id")

        if StudentProfile.objects.filter(enrollment_id=enrollment_id).exists() or CustomUser.objects.filter(username=enrollment_id).exists():
            messages.error(request, "Student with this Enrollment ID/Username already exists")
            return redirect("create_student")
        
        semester = get_object_or_404(Semester, id=semester_id)

        # Password is the same as enrollment_id (username) as requested
        user = CustomUser.objects.create_user(
            username=enrollment_id, email=email, first_name=name, role="student",
            password=enrollment_id
        )
        
        StudentProfile.objects.create(
            user=user, enrollment_id=enrollment_id, course=semester.course,
            semester=semester, section=section
        )

        semester.students.add(user)

        # Send login credentials via email
        if email:
            try:
                subject = 'Welcome to the College Portal - Your Login Credentials'
                message = f'Hello {name},\n\nYour student account has been created successfully.\n\nLogin Credentials:\nUsername: {enrollment_id}\nPassword: {enrollment_id}\n\nPlease login and change your password for security.\n\nBest regards,\nCollege Administration'
                send_mail(
                    subject,
                    message,
                    settings.DEFAULT_FROM_EMAIL,
                    [email],
                    fail_silently=False,
                        )
                email_status = "and credentials sent to email"
            except Exception as e:
                email_status = "but failed to send email"
                print(f"Email error: {e}")
        else:
            email_status = ""

        messages.success(request, f"Student created {email_status} and assigned to {semester}")
        return redirect("admin_dashboard")
        
    return render(request, "admin/create_student.html", {
        'courses': courses,
        'semesters': semesters
    })

#view classes
@login_required
def view_classes(request):
    # if request.user.role != 'admin':
    #     return redirect('admin_login')
    students = StudentProfile.objects.select_related('user', 'semester__course').order_by('semester__course__name', 'semester__semester_number', 'enrollment_id')
    semesters = {}
    for student in students:
        sem = str(student.semester)
        if sem not in semesters:
            semesters[sem] = []
        semesters[sem].append(student)
    context = {"semesters": semesters}
    return render(request, "admin/view_classes.html", context)



import random

def generate_otp():
    return str(random.randint(100000, 999999))


#forgot password
User = get_user_model()
def forgot_password(request):

    if request.method == "POST":
        email = request.POST.get("email")

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return render(request,"auth/forgot_password.html",{"error":"Email not found"})

        otp = generate_otp()

        PasswordResetOTP.objects.create(
            user=user,
            otp=otp
        )

        send_mail(
            "Password Reset OTP",
            f"Your OTP is {otp}",
            "noreply@gmail.com",
            [email],
            fail_silently=False
        )

        request.session["reset_user"] = user.id

        return redirect("verify_otp")

    return render(request, "auth/forgot_password.html")

#verify_otp


def verify_otp(request):

    user_id = request.session.get("reset_user")

    if not user_id:
        return redirect("login")

    if request.method == "POST":

        otp = request.POST.get("otp")

        record = PasswordResetOTP.objects.filter(
            user_id=user_id,
            otp=otp
        ).last()

        if record:

            expiry = record.created_at + timedelta(minutes=1)

            if timezone.now() > expiry:
                return render(request,"auth/verify_otp.html",{"error":"OTP Expired"})

            return redirect("reset_password")

        else:
            return render(request,"auth/verify_otp.html",{"error":"Invalid OTP"})
        

    return render(request, "auth/verify_otp.html")

#reset_password



def reset_password(request):

    user_id = request.session.get("reset_user")

    if request.method == "POST":

        password = request.POST.get("password")

        user = User.objects.get(id=user_id)
        user.password = make_password(password)
        user.save()

        return redirect("login")

    
    return render(request, "auth/reset_password.html")



@login_required
def check_submission(request, submission_id):

    submission = get_object_or_404(
        Submission,
        id=submission_id,
        assignment__subject__teacher=request.user
    )

    if request.method == "POST":
        status = request.POST.get("status")

        submission.status = status
        submission.save()

        messages.success(request, "Submission status updated")

        return redirect("submissions", assignment_id=submission.assignment.id)

    return render(request, "teacher/check_submission.html", {
        "submission": submission
    })

