from django.contrib.auth.views import LogoutView
from django.urls import path

from . import views

urlpatterns = [
    # Dashboard
    path("", views.DashboardView.as_view(), name="dashboard"),
    
    # Student Management
    path("students/", views.StudentListView.as_view(), name="student_list"),
    path("students/create/", views.StudentCreateView.as_view(), name="student_create"),
    path("students/<int:pk>/update/", views.StudentUpdateView.as_view(), name="student-update"),
    path("students/<int:pk>/delete/", views.UserDeleteView.as_view(), name="student-delete"),  # Explicit student delete

    # Staff Management
    path("staff/", views.StaffListView.as_view(), name="staff_list"),
    path("staff/create/", views.StaffCreateView.as_view(), name="staff_create"),
    path("staff/<int:pk>/update/", views.StaffUpdateView.as_view(), name="staff-update"),
    path("staff/<int:pk>/delete/", views.UserDeleteView.as_view(), name="staff-delete"),  # Explicit staff delete

    # User Delete (generic, but students and staff have specific URLs now)
    path("user/<int:pk>/delete/", views.UserDeleteView.as_view(), name="user-delete"),

    # Academic Term and Session Management
    path("termsession/", views.TermSessionView.as_view(), name="term_session"),
    path("term/create/", views.AcademicTermCreateView.as_view(), name="term_create"),
    path("term/<int:pk>/update/", views.TermUpdateView.as_view(), name="term_update"),
    path("term/delete/<int:pk>/", views.AcademicTermDeleteView.as_view(), name="term_delete"),
    path("session/create/", views.AcademicSessionCreateView.as_view(), name="session_create"),
    path("session/<int:pk>/update/", views.SessionUpdateView.as_view(), name="session_update"),
    path("session/delete/<int:pk>/", views.AcademicSessionDeleteView.as_view(), name="session_delete"),

    # Subject Management
    path("subject/create/", views.SubjectCreateView.as_view(), name="subject_create"),
    path("subject/<int:pk>/update/", views.SubjectUpdateView.as_view(), name="subject_update"),
    path("subject/delete/<int:pk>/", views.SubjectDeleteView.as_view(), name="subject_delete"),

    # Class Management
    path("class/create/", views.ClassCreateView.as_view(), name="class_create"),
    path("class/<int:pk>/update/", views.ClassUpdateView.as_view(), name="class_update"),
    path("class/delete/<int:pk>/", views.ClassDeleteView.as_view(), name="class_delete"),

    # Authentication
    path("logout/", LogoutView.as_view(), name="logout"),  # Added logout URL
]

