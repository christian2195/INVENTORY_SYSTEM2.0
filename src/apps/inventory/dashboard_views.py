from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from apps.reception_notes.models import ReceptionNote
from apps.dispatch_notes.models import DispatchNote
from apps.returns.models import ReturnNote
from apps.inventory.models import Product

@login_required
def custom_dashboard(request):
    pending_receptions = ReceptionNote.objects.filter(status='PENDING').count()
    pending_dispatches = DispatchNote.objects.filter(status='PENDING').count()
    pending_returns = ReturnNote.objects.filter(status='PENDING').count()
    total_products = Product.objects.count()

    context = {
        'pending_receptions': pending_receptions,
        'pending_dispatches': pending_dispatches,
        'pending_returns': pending_returns,
        'total_products': total_products,
    }
    return render(request, 'inventory/custom_dashboard.html', context)