"""Vistas protegidas de administración de usuarios."""

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db.models import Q
from django.db.models.deletion import ProtectedError
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, ListView, UpdateView

from .forms import UserCreateForm, UserUpdateForm
from .models import User, UserRole


class AdminRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    raise_exception = True

    def test_func(self):
        return self.request.user.is_admin


class UserListView(AdminRequiredMixin, ListView):
    model = User
    template_name = "users/administration.html"
    context_object_name = "users"
    ordering = ("username",)


class UserCreateView(AdminRequiredMixin, CreateView):
    form_class = UserCreateForm
    template_name = "users/user_form.html"
    success_url = reverse_lazy("dashboard:administration")

    def form_valid(self, form):
        messages.success(self.request, "El usuario se creó correctamente.")
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["page_title"] = "Crear usuario"
        return context


class UserUpdateView(AdminRequiredMixin, UpdateView):
    model = User
    form_class = UserUpdateForm
    template_name = "users/user_form.html"
    success_url = reverse_lazy("dashboard:administration")

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["actor"] = self.request.user
        return kwargs

    def form_valid(self, form):
        messages.success(self.request, "Los datos del usuario se actualizaron correctamente.")
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["page_title"] = "Editar usuario"
        return context


class UserDeleteView(AdminRequiredMixin, DeleteView):
    model = User
    template_name = "users/user_confirm_delete.html"
    success_url = reverse_lazy("dashboard:administration")

    def form_valid(self, form):
        user = self.object
        if user.pk == self.request.user.pk:
            messages.error(self.request, "No puedes eliminar tu propia cuenta.")
            return redirect(self.success_url)

        if user.is_active and user.is_admin:
            active_admins = User.objects.filter(is_active=True).filter(
                Q(role=UserRole.ADMIN) | Q(is_superuser=True)
            )
            if not active_admins.exclude(pk=user.pk).exists():
                messages.error(self.request, "No se puede eliminar al último administrador activo.")
                return redirect(self.success_url)

        try:
            response = super().form_valid(form)
        except ProtectedError:
            messages.error(
                self.request,
                "No se puede eliminar esta cuenta porque tiene acciones vinculadas al historial. "
                "Puedes desactivarla desde su edición.",
            )
            return redirect(self.success_url)

        messages.success(self.request, "El usuario se eliminó correctamente.")
        return response
