from django.contrib.auth.decorators import login_required, permission_required
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib import messages
from .forms import UserCreateForm, UserEditForm
from .models import User

# --- Listado de usuarios ---
@login_required
def users_list(request):
    users = User.objects.all().order_by("username")
    return render(request, "accounts/user_list.html", {"users": users})

# --- Crear usuario ---
@login_required
@permission_required("auth.add_user", raise_exception=True)
def users_create(request):
    if request.method == "POST":
        form = UserCreateForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Usuario creado correctamente.")
            return redirect(reverse("accounts:users_list"))
    else:
        form = UserCreateForm()
    return render(request, "accounts/user_form.html", {"form": form, "accion": "Crear"})

# --- Editar usuario ---
@login_required
@permission_required("auth.change_user", raise_exception=True)
def users_edit(request, pk):
    user = get_object_or_404(User, pk=pk)
    if request.method == "POST":
        form = UserEditForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, "Usuario actualizado correctamente.")
            return redirect(reverse("accounts:users_list"))
    else:
        form = UserEditForm(instance=user)
    return render(request, "accounts/user_form.html", {"form": form, "accion": "Editar", "usuario": user})

# --- Eliminar usuario ---
@login_required
@permission_required("auth.delete_user", raise_exception=True)
def users_delete(request, pk):
    user = get_object_or_404(User, pk=pk)
    if request.method == "POST":
        user.delete()
        messages.success(request, "Usuario eliminado correctamente.")
        return redirect("accounts:users_list")
    return render(request, "accounts/user_confirm_delete.html", {"usuario": user})
