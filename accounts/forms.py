from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import User

class UserCreateForm(UserCreationForm):
    email = forms.EmailField(required=True, label="Correo electrónico")

    class Meta:
        model = User
        fields = ("username", "first_name", "last_name", "email", "role", "is_active")


class UserEditForm(UserChangeForm):
    password = None  # Ocultamos el campo de contraseña
    email = forms.EmailField(required=True, label="Correo electrónico")

    class Meta:
        model = User
        fields = ("username", "first_name", "last_name", "email", "role", "is_active")
