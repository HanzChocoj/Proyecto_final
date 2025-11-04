from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required
def home(request):
    """Página principal después del login."""
    return render(request, "home.html")
