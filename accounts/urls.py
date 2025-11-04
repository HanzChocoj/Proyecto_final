from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = "accounts"

urlpatterns = [
    path("login/", auth_views.LoginView.as_view(template_name="accounts/login.html"), name="login"),

    path(
        "logout/",
        auth_views.LogoutView.as_view(next_page="/accounts/login/"),
        name="logout"
    ),


    # Reset de contraseña
    path("password-reset/", auth_views.PasswordResetView.as_view(), name="password_reset"),
    path("password-reset/done/", auth_views.PasswordResetDoneView.as_view(), name="password_reset_done"),
    path("reset/<uidb64>/<token>/", auth_views.PasswordResetConfirmView.as_view(), name="password_reset_confirm"),
    path("reset/done/", auth_views.PasswordResetCompleteView.as_view(), name="password_reset_complete"),

    # Usuarios
    path("users/", views.users_list, name="users_list"),
    path("users/new/", views.users_create, name="users_create"),
    path("users/<int:pk>/edit/", views.users_edit, name="users_edit"),
    path("users/<int:pk>/delete/", views.users_delete, name="users_delete"),
]
