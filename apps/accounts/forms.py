"""Authentication and profile forms (FR-01..FR-05)."""

from __future__ import annotations

from django import forms
from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.password_validation import validate_password

User = get_user_model()


class RegisterForm(forms.Form):
    """Customer self-registration form (FR-01)."""

    first_name = forms.CharField(label="Ism", max_length=150)
    last_name = forms.CharField(label="Familiya", max_length=150, required=False)
    email = forms.EmailField(label="Email")
    phone = forms.CharField(label="Telefon", max_length=32, required=False)
    password = forms.CharField(label="Parol", widget=forms.PasswordInput)
    password_confirm = forms.CharField(
        label="Parolni tasdiqlang", widget=forms.PasswordInput
    )

    def clean_email(self) -> str:
        email = self.cleaned_data["email"].strip().lower()
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("Bunday email allaqachon ro'yxatdan o'tgan.")
        return email

    def clean(self) -> dict:
        cleaned = super().clean()
        password = cleaned.get("password")
        confirm = cleaned.get("password_confirm")
        if password and confirm and password != confirm:
            self.add_error("password_confirm", "Parollar mos kelmadi.")
        if password:
            validate_password(password)
        return cleaned


class LoginForm(forms.Form):
    """Email/password login form (FR-02)."""

    email = forms.EmailField(label="Email")
    password = forms.CharField(label="Parol", widget=forms.PasswordInput)

    def __init__(self, *args: object, **kwargs: object) -> None:
        self.request = kwargs.pop("request", None)
        self.user = None
        super().__init__(*args, **kwargs)  # type: ignore[arg-type]

    def clean(self) -> dict:
        cleaned = super().clean()
        email = cleaned.get("email")
        password = cleaned.get("password")
        if email and password:
            user = authenticate(
                self.request, username=email.strip().lower(), password=password
            )
            if user is None:
                raise forms.ValidationError("Email yoki parol noto'g'ri.")
            self.user = user
        return cleaned


class ChangePasswordForm(forms.Form):
    """Change password while authenticated (FR-04)."""

    old_password = forms.CharField(label="Joriy parol", widget=forms.PasswordInput)
    new_password = forms.CharField(label="Yangi parol", widget=forms.PasswordInput)
    new_password_confirm = forms.CharField(
        label="Yangi parolni tasdiqlang", widget=forms.PasswordInput
    )

    def clean(self) -> dict:
        cleaned = super().clean()
        new = cleaned.get("new_password")
        confirm = cleaned.get("new_password_confirm")
        if new and confirm and new != confirm:
            self.add_error("new_password_confirm", "Parollar mos kelmadi.")
        if new:
            validate_password(new)
        return cleaned


class PasswordResetRequestForm(forms.Form):
    """Request a password reset email (FR-05)."""

    email = forms.EmailField(label="Email")


class SetNewPasswordForm(forms.Form):
    """Set a new password via a reset link (FR-05)."""

    new_password = forms.CharField(label="Yangi parol", widget=forms.PasswordInput)
    new_password_confirm = forms.CharField(
        label="Yangi parolni tasdiqlang", widget=forms.PasswordInput
    )

    def clean(self) -> dict:
        cleaned = super().clean()
        new = cleaned.get("new_password")
        confirm = cleaned.get("new_password_confirm")
        if new and confirm and new != confirm:
            self.add_error("new_password_confirm", "Parollar mos kelmadi.")
        if new:
            validate_password(new)
        return cleaned


class ProfileForm(forms.ModelForm):
    """Edit the authenticated user's profile (FR-04)."""

    class Meta:
        model = User
        fields = ["first_name", "last_name", "phone"]
        labels = {
            "first_name": "Ism",
            "last_name": "Familiya",
            "phone": "Telefon",
        }
