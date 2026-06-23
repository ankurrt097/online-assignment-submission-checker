from django.urls import path
from . import views

urlpatterns = [
    # Home / Auth
    path('', views.admin_login, name='home'),
    path('admin-login/', views.admin_login, name='admin_login'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),

    # Admin
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('create-teacher/', views.create_teacher, name='create_teacher'),
    path('teachers/', views.teacher_list, name='teacher_list'),
    path('admin-create-course/', views.create_course, name='create_course'),
    path('admin-courses/', views.admin_course_list, name='admin_course_list'),
    path('admin-create-subject/', views.create_subject, name='create_subject'),
    path('admin-subjects/', views.admin_subjects, name='admin_subjects'),
    path('admin-edit-subject/<int:subject_id>/', views.edit_subject, name='edit_subject'),
    path('admin-delete-subject/<int:subject_id>/', views.delete_subject, name='delete_subject'),


    # Teacher
    path('teacher/dashboard/', views.teacher_dashboard, name='teacher_dashboard'),
    path('teacher/profile/', views.teacher_profile, name='teacher_profile'),
    path('teacher/profile/edit/', views.edit_teacher_profile, name='edit_teacher_profile'),

    path('teacher/my-semesters/', views.teacher_dashboard, name='teacher_semesters'), # Changed from class_list which I might have missed refactoring
    path('teacher/semester/<int:semester_id>/', views.semester_detail, name='semester_detail'),
    path('teacher/semester/<int:semester_id>/add-student/', views.add_student_to_semester, name='add_student'),
    path('create-assignment/', views.create_assignment, name='create_assignment'),
    path('teacher-assignments/', views.teacher_assignments, name='teacher_assignments'),
    path('teacher/assignment/<int:id>/', views.assignment_detail, name='assignment_detail'),
    path('teacher/assignment/<int:id>/edit/', views.edit_assignment, name='edit_assignment'),
    path('teacher/assignment/<int:id>/delete/', views.delete_assignment, name='delete_assignment'),
    path('teacher/submissions/<int:assignment_id>/', views.submissions, name='submissions'),
    path('teacher/all-submissions/', views.all_submissions, name='all_submissions'),
    path("teacher/submission/<int:submission_id>/check/",views.check_submission,name="check_submission"),

    # Student
    path('student/dashboard/', views.student_dashboard, name='student_dashboard'),
    path('student/assignments/', views.student_assignments, name='student_assignments'),
    path('student/submit/<int:assignment_id>/', views.submit_assignment, name='submit_assignment'),
    path('student/profile/', views.student_profile, name='student_profile'),
    path('student/profile/edit/', views.edit_student_profile, name='edit_student_profile'),

    path("create-student/", views.create_student, name="create_student"),
    path("view-classes/", views.view_classes, name="view_classes"),


    path("forgot-password/",views.forgot_password,name="forgot_password"),
    path("verify-otp/",views.verify_otp,name="verify_otp"),
    path("reset-password/",views.reset_password,name="reset_password"),
]



