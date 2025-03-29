from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.forms.widgets import CheckboxInput, Textarea, PasswordInput

from .models import AcademicSession, AcademicTerm, StudentClass, Subject, User


class ResponsiveForm(forms.Form):
    """Apply Bootstrap styling to form fields dynamically."""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            if isinstance(field.widget, CheckboxInput):
                field.widget.attrs["class"] = "form-check-input"
            elif isinstance(field.widget, Textarea):
                field.widget.attrs["class"] = "form-control mysummernote"
            else:
                field.widget.attrs["class"] = "form-control"


# 🟢 User Creation Form
class UserCreateForm(UserCreationForm, ResponsiveForm):
    class Meta:
        model = User
        fields = [
            "username",
            "first_name",
            "last_name",
            "gender",
            "student_class",
            "password1",
            "password2",
            "profile_picture",
        ]

    def clean_password2(self):
        """Validate that passwords match and meet security requirements."""
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")

        if password1 and password2:
            if password1 != password2:
                raise forms.ValidationError("🚨 Passwords do not match! Please enter the same password.")
            if len(password1) < 8:
                raise forms.ValidationError("⚠️ Password must be at least 8 characters long.")
            if password1.isdigit():
                raise forms.ValidationError("❌ Password should not be entirely numeric.")

        return password2


# 🟢 User Update Form
class UserUpdateForm(forms.ModelForm, ResponsiveForm):
    password = forms.CharField(
        required=False,
        widget=PasswordInput(attrs={"class": "form-control"}),
        help_text="Leave blank if you do not want to change the password.",
    )

    class Meta:
        model = User
        fields = [
            "username",
            "first_name",
            "last_name",
            "gender",
            "student_class",
            "profile_picture",
            "password",
        ]

    def save(self, commit=True):
        """Update user details and change password if a new one is provided."""
        instance = super().save(commit=False)
        password = self.cleaned_data.get("password")

        if password:  # Only update password if a new one is provided
            if len(password) < 8:
                raise forms.ValidationError("❌ Password must be at least 8 characters long.")
            instance.set_password(password)

        if commit:
            instance.save()
        return instance


# 🟢 Staff Creation Form
class StaffCreateForm(UserCreationForm, ResponsiveForm):
    class Meta:
        model = User
        fields = [
            "username",
            "first_name",
            "last_name",
            "gender",
            "password1",
            "password2",
        ]

    def save(self, commit=True):
        """Create a staff member with staff permissions."""
        instance = super().save(commit=False)
        instance.is_staff = True
        instance.save()
        return instance


# 🟢 Staff Update Form
class StaffUpdateForm(forms.ModelForm, ResponsiveForm):
    password = forms.CharField(
        required=False,
        widget=PasswordInput(attrs={"class": "form-control"}),
        help_text="Leave blank if you do not want to change the password.",
    )

    class Meta:
        model = User
        fields = [
            "username",
            "first_name",
            "last_name",
            "gender",
            "password",
        ]

    def save(self, commit=True):
        """Update staff details and change password if a new one is provided."""
        instance = super().save(commit=False)
        password = self.cleaned_data.get("password")

        if password:
            if len(password) < 8:
                raise forms.ValidationError("❌ Password must be at least 8 characters long.")
            instance.set_password(password)

        if commit:
            instance.save()
        return instance


# 🟢 Academic Session Form
class AcademicSessionForm(forms.ModelForm, ResponsiveForm):
    class Meta:
        model = AcademicSession
        exclude = ()


# 🟢 Academic Term Form
class AcademicTermForm(forms.ModelForm, ResponsiveForm):
    class Meta:
        model = AcademicTerm
        exclude = ()


# 🟢 Subject Form
class SubjectForm(forms.ModelForm, ResponsiveForm):
    class Meta:
        model = Subject
        exclude = ()


# 🟢 Student Class Form
class StudentClassForm(forms.ModelForm, ResponsiveForm):
    class Meta:
        model = StudentClass
        exclude = ()


# 🟢 Subject Update Form
class SubjectUpdateForm(forms.ModelForm, ResponsiveForm):
    class Meta:
        model = Subject
        exclude = ()
