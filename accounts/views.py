from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth import views as auth_views
from django.shortcuts import render, redirect
from django.urls import reverse
from .forms import UserCreateForm
from .models import User

@login_required
def users_list(request):
    users = User.objects.all().order_by("username")
    return render(request, "accounts/user_list.html", {"users": users})

@login_required
@permission_required("auth.add_user", raise_exception=True)
def users_create(request):
    if request.method == "POST":
        form = UserCreateForm(request.POST)
        if form.is_valid():
            user = form.save()
            return redirect(reverse("accounts:users_list"))
    else:
        form = UserCreateForm()
    return render(request, "accounts/user_form.html", {"form": form})
