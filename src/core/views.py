# src/core/views.py
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required

def home_redirect(request):
    """Redirige a login si no está autenticado, o al dashboard si está autenticado"""
    if request.user.is_authenticated:
        return redirect('inventory:inventory_dashboard')
    else:
        return redirect('login')

def page_not_found(request, exception):
    return render(request, '404.html', status=404)

def server_error(request):
    return render(request, '500.html', status=500)