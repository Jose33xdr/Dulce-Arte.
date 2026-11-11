"""Formularios web para la administración de usuarios."""

from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.db.models import Q

from .models import User, UserRole


FIELD_CLASS = (
    "mt-1 block w-full rounded-xl border border-stone-300 bg-white px-3 py-2 "
    "text-sm text-stone-900 shadow-sm focus:border-[#773344] focus:outline-none "
    "focus:ring-2 focus:ring-[#773344]/20"
)


class UserCreateForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = (
            "username",
            "first_name",
            "last_name",
            "email",
            "role",
            "phone",
            "identification",
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        _style_fields(self)

    def save(self, commit=True):
        user = super().save(commit=False)
        user.is_staff = user.role == UserRole.ADMIN
        user.is_superuser = user.role == UserRole.ADMIN
        if commit:
            user.save()
            self.save_m2m()
        return user


class UserUpdateForm(forms.ModelForm):
    actor = None

    class Meta:
        model = User
        fields = (
            "username",
            "first_name",
            "last_name",
            "email",
            "role",
            "phone",
            "identification",
            "is_active",
        )
        labels = {"is_active": "Cuenta activa"}

    def __init__(self, *args, actor=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.actor = actor
        if actor and actor.pk == self.instance.pk:
            self.fields["role"].disabled = True
            self.fields["is_active"].disabled = True
        _style_fields(self)

    def clean(self):
        cleaned_data = super().clean()
        if not cleaned_data:
            return cleaned_data

        was_active_admin = self.instance.is_active and self.instance.is_admin
        will_be_active_admin = (
            cleaned_data.get("is_active", self.instance.is_active)
            and cleaned_data.get("role", self.instance.role) == UserRole.ADMIN
        )
        if was_active_admin and not will_be_active_admin:
            other_active_admins = User.objects.filter(is_active=True).filter(
                Q(role=UserRole.ADMIN) | Q(is_superuser=True)
            ).exclude(pk=self.instance.pk)
            if not other_active_admins.exists():
                message = "No se puede desactivar o quitar el rol del último administrador activo."
                self.add_error("role", message)
                self.add_error("is_active", message)
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.is_staff = user.role == UserRole.ADMIN
        user.is_superuser = user.role == UserRole.ADMIN
        if commit:
            user.save()
            self.save_m2m()
        return user


def _style_fields(form):
    for field in form.fields.values():
        field.widget.attrs["class"] = FIELD_CLASS
