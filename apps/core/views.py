from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.core.paginator import Paginator
from django.db.models import OuterRef, Subquery
from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect, render
from django.views.generic import ListView, View
from django.views.generic.edit import CreateView, DeleteView, UpdateView
from django.http import JsonResponse
from django.urls import reverse_lazy
from django.http import JsonResponse, HttpResponseRedirect
from django.contrib.auth import get_user_model
from django.db.models import Q
from apps.core.models import AcademicSession, AcademicTerm
from apps.exam.models import Exam

from .models import StudentClass, Subject, User
User = get_user_model()  # ✅ Get the correct User model


from apps.core.forms import (
    AcademicSessionForm,
    AcademicTermForm,
    StaffCreateForm,
    StaffUpdateForm,
    StudentClassForm,
    SubjectForm,
    UserCreateForm,
    UserUpdateForm,
)



class OnlyAdminMixin(LoginRequiredMixin, UserPassesTestMixin):
    """Helper mixin to restrict view access to admin only"""

    def test_func(self):
        return self.request.user.is_superuser


class StaffAndAdminMixin(LoginRequiredMixin, UserPassesTestMixin):
    """Helper mixin to restrict view access to admin and staff only"""

    def test_func(self):
        return self.request.user.is_staff


class DashboardView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        user = self.request.user
        query = Exam.objects.select_related(
            "class_group", "session", "term", "subject", "author"
        )
        if user.is_superuser:
            return self.admin_page(query)
        elif user.is_staff:
            return self.staff_page(query)
        return self.student_page(query)

    def admin_page(self, query):
        paginator = Paginator(query, 20)
        page_number = self.request.GET.get("page")
        page_obj = paginator.get_page(page_number)
        context = {"exams": page_obj}
        return render(self.request, "admin.html", context)

    def staff_page(self, query):
        paginator = Paginator(query.filter(author=self.request.user), 20)
        page_number = self.request.GET.get("page")
        page_obj = paginator.get_page(page_number)
        context = {"exams": page_obj}
        return render(self.request, "admin.html", context)

    def student_page(self, query):
        exams = query.filter(
            class_group=self.request.user.student_class, published=True
        )
        context = {"exams": exams}
        return render(self.request, "dashboard.html", context)





class StudentListView(ListView):
    model = User
    template_name = "core/student_list.html"
    context_object_name = "students"
    paginate_by = 20  # Show 20 students per page

    def get_queryset(self):
        query = self.request.GET.get("q")
        students = User.objects.filter(is_staff=False).order_by("username")  # Order by username
        if query:
            students = (
                students.filter(username__icontains=query) |
                students.filter(first_name__icontains=query) |
                students.filter(last_name__icontains=query)
            ).order_by("username")  # Maintain order after filtering
        return students




class StudentCreateView(OnlyAdminMixin, CreateView):
    model = User
    form_class = UserCreateForm
    template_name = "modal_create.html"
    success_url = "/"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Add new student"
        return context

    def form_valid(self, form):
        super().form_valid(form)
        return HttpResponse(status=204)




class StudentUpdateView(OnlyAdminMixin, SuccessMessageMixin, UpdateView):
    model = User
    form_class = UserUpdateForm
    template_name = "modal_create.html"
    success_message = "User successfully updated."

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Update student"
        return context

    def form_valid(self, form):
        """Handle successful form submission with JSON response"""
        self.object = form.save()
        return JsonResponse({"success": True, "message": self.success_message}, status=200)

    def form_invalid(self, form):
        """Return errors as JSON response"""
        errors = {
            field: [{"message": error} for error in error_list]
            for field, error_list in form.errors.items()
        }
        return JsonResponse({"success": False, "errors": errors}, status=400)



class UserDeleteView(OnlyAdminMixin, DeleteView):
    model = User
    template_name = "delete.html"
    success_url = reverse_lazy("student_list")

    def form_valid(self, form):
        self.object.delete()
        #if self.request.META.get("HTTP_X_REQUESTED_WITH") == "XMLHttpRequest":
            #return JsonResponse({"message": "Student deleted successfully."})
        return HttpResponseRedirect(self.success_url)  # Redirect for normal requests








class StaffListView(OnlyAdminMixin, ListView):
    template_name = "core/staff_list.html"
    context_object_name = "object_list"
    paginate_by = 10  # ✅ Enable pagination

    def get_queryset(self):
        query = self.request.GET.get("q")
        staff_queryset = User.objects.filter(is_staff=True)  # ✅ Uses custom user model

        if query:
            staff_queryset = staff_queryset.filter(
                Q(first_name__icontains=query) | 
                Q(last_name__icontains=query) | 
                Q(username__icontains=query)
            )

        return staff_queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # ✅ Ensure pagination exists before trying to use `start_index`
        if "page_obj" in context and context["page_obj"]:
            context["start_index"] = context["page_obj"].start_index()
        else:
            context["start_index"] = 0  # Default to 0 if pagination is disabled

        return context



class StaffCreateView(OnlyAdminMixin, CreateView):
    model = User
    form_class = StaffCreateForm
    template_name = "modal_create.html"
    success_url = "/"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Add new staff"
        return context

    def form_valid(self, form):
        self.object = form.save()
        return JsonResponse({"success": True}, status=200)

    def form_invalid(self, form):
        errors = {}
        for field, error_list in form.errors.items():
            errors[field] = error_list[0]
        return JsonResponse({
            "success": False, 
            "errors": errors
        }, status=400)



class StaffUpdateView(OnlyAdminMixin, SuccessMessageMixin, UpdateView):
    model = User
    form_class = StaffUpdateForm
    template_name = "modal_create.html"
    success_url = reverse_lazy("staff_list")  # Replace "staff_list" with your actual URL name
    success_message = "User successfully updated."

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Update staff"
        return context

    def form_valid(self, form):
        self.object = form.save()
        return JsonResponse({
            "success": True, 
            "message": self.success_message,
            "redirect_url": str(self.success_url)  # Pass success URL to frontend
        }, status=200)

    def form_invalid(self, form):
        errors = {
            field: [{"message": error} for error in error_list]
            for field, error_list in form.errors.items()
        }
        return JsonResponse({
            "success": False, 
            "errors": errors
        }, status=400)



class TermSessionView(OnlyAdminMixin, View):
    template_name = "core/term_session_list.html"

    def get(self, request):
        context = {
            "terms": AcademicTerm.objects.all(),
            "sessions": AcademicSession.objects.all(),
            "subjects": Subject.objects.all(),
            "classes": StudentClass.objects.all(),
        }
        return render(request, self.template_name, context)


class AcademicTermCreateView(OnlyAdminMixin, CreateView):
    model = AcademicTerm
    form_class = AcademicTermForm
    template_name = "modal_create.html"
    success_url = "/"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Add new Term"
        return context

    def form_valid(self, form):
        super().form_valid(form)
        return HttpResponse(status=204)


class TermUpdateView(OnlyAdminMixin, SuccessMessageMixin, UpdateView):
    model = AcademicTerm
    form_class = AcademicTermForm
    template_name = "modal_create.html"
    success_message = "Term successfully updated."

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Update Term"
        return context

    def form_valid(self, form):
        form.save()
        return HttpResponse(status=204)


class AcademicTermDeleteView(LoginRequiredMixin, SuccessMessageMixin, DeleteView):
    model = AcademicTerm
    template_name = "modal_delete.html"
    success_url = "/"
    success_message = "AcademicTerm successfully deleted."

    def form_valid(self, form):
        super().form_valid(form)
        return HttpResponse(status=204)


class AcademicSessionCreateView(OnlyAdminMixin, CreateView):
    model = AcademicSession
    form_class = AcademicSessionForm
    template_name = "modal_create.html"
    success_url = "/"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Add new session"
        return context

    def form_valid(self, form):
        super().form_valid(form)
        return HttpResponse(status=204)


class AcademicSessionDeleteView(LoginRequiredMixin, SuccessMessageMixin, DeleteView):
    model = AcademicSession
    template_name = "modal_delete.html"
    success_url = "/"
    success_message = "AcademicSession successfully deleted."

    def form_valid(self, form):
        super().form_valid(form)
        return HttpResponse(status=204)


class SessionUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = AcademicSession
    form_class = AcademicSessionForm
    template_name = "modal_create.html"
    success_message = "Session successfully updated."

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Update Session"
        return context

    def form_valid(self, form):
        form.save()
        return HttpResponse(status=204)


class SubjectCreateView(OnlyAdminMixin, CreateView):
    model = Subject
    form_class = SubjectForm
    template_name = "modal_create.html"
    success_url = "/"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Add new subject"
        return context

    def form_valid(self, form):
        super().form_valid(form)
        return HttpResponse(status=204)


class SubjectDeleteView(LoginRequiredMixin, SuccessMessageMixin, DeleteView):
    model = Subject
    template_name = "modal_delete.html"
    success_url = "/"
    success_message = "Subject successfully deleted."

    def form_valid(self, form):
        super().form_valid(form)
        return HttpResponse(status=204)


class SubjectUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = Subject
    form_class = SubjectForm
    template_name = "modal_create.html"
    success_message = "Subject successfully updated."

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Update subject"
        return context

    def form_valid(self, form):
        form.save()
        return HttpResponse(status=204)


class ClassCreateView(OnlyAdminMixin, CreateView):
    model = StudentClass
    form_class = StudentClassForm
    template_name = "modal_create.html"
    success_url = "/"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Add new class"
        return context

    def form_valid(self, form):
        super().form_valid(form)
        return HttpResponse(status=204)


class ClassDeleteView(LoginRequiredMixin, SuccessMessageMixin, DeleteView):
    model = StudentClass
    template_name = "modal_delete.html"
    success_url = "/"
    success_message = "Class successfully deleted."

    def form_valid(self, form):
        super().form_valid(form)
        return HttpResponse(status=204)


class ClassUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = StudentClass
    form_class = StudentClassForm
    template_name = "modal_create.html"
    success_message = "Class successfully updated."

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Update class"
        return context

    def form_valid(self, form):
        form.save()
        return HttpResponse(status=204)

# ERRORS
def error_404(request, exception):
    return render(request, 'error/404.html', status=404)

def error_500(request):
    return render(request, 'error/500.html', status=500)

def error_503(request):
    return render(request, 'error/503.html', status=503)

def error_401(request, exception=None):
    return render(request, 'error/401.html', status=401)

def error_403(request, exception=None):
    return render(request, 'error/403.html', status=403)
