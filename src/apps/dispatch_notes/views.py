# src/apps/dispatch_notes/views.py

from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.http import JsonResponse, HttpResponse
from django.db import transaction
from django.template.loader import render_to_string
from weasyprint import HTML
from .models import DispatchNote, DispatchItem
from .forms import DispatchNoteForm, DispatchItemFormSet
from apps.inventory.models import Product, Client, Supplier
from django.db.models import F
from django.contrib import messages
from django.db.models import Q
from django.utils import timezone
from django.db import models  # Para usar models.Sum en las estadísticas

# Vistas de la interfaz de usuario
class DispatchNoteListView(LoginRequiredMixin, ListView):
    model = DispatchNote
    template_name = 'dispatch_notes/dispatch_list.html'
    context_object_name = 'dispatches'
    paginate_by = 15
    
    def get_queryset(self):
        queryset = super().get_queryset().prefetch_related('items').order_by('-dispatch_date')
        
        # Filtros
        search_query = self.request.GET.get('q')
        status_filter = self.request.GET.get('status')
        date_filter = self.request.GET.get('date')
        
        if search_query:
            queryset = queryset.filter(
                Q(dispatch_number__icontains=search_query) |
                Q(client__name__icontains=search_query) |
                Q(beneficiary__icontains=search_query) |
                Q(driver_name__icontains=search_query)
            )
        
        if status_filter:
            queryset = queryset.filter(status=status_filter)
            
        if date_filter:
            queryset = queryset.filter(dispatch_date__date=date_filter)
            
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Estadísticas para las tarjetas
        total_dispatches = DispatchNote.objects.count()
        pending_count = DispatchNote.objects.filter(status='PENDING').count()
        completed_count = DispatchNote.objects.filter(status='DISPATCHED').count()
        total_value = DispatchNote.objects.aggregate(total=models.Sum('total'))['total'] or 0
        
        context.update({
            'total_dispatches': total_dispatches,
            'pending_count': pending_count,
            'completed_count': completed_count,
            'total_value': total_value,
        })
        
        return context

class DispatchNoteCreateView(LoginRequiredMixin, CreateView):
    model = DispatchNote
    form_class = DispatchNoteForm
    template_name = 'dispatch_notes/dispatch_form.html'
    success_url = reverse_lazy('dispatch_notes:list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['formset'] = DispatchItemFormSet(self.request.POST)
        else:
            context['formset'] = DispatchItemFormSet()
        
        # Agregar clientes y proveedores para el template
        context['clients'] = Client.objects.filter(is_active=True)
        context['suppliers'] = Supplier.objects.filter(is_active=True)
        
        return context

    def post(self, request, *args, **kwargs):
        self.object = None
        form = self.get_form()
        formset = DispatchItemFormSet(self.request.POST)
        
        if form.is_valid() and formset.is_valid():
            return self.form_valid(form, formset)
        else:
            return self.form_invalid(form, formset)

    def form_valid(self, form, formset):
        print("=== DEBUG FORM VALIDATION CREATE ===")
        print(f"Form is valid: {form.is_valid()}")
        print(f"Formset is valid: {formset.is_valid()}")
        
        if not formset.is_valid():
            print("Formset errors:", formset.errors)
            print("Formset non-form errors:", formset.non_form_errors())
            
            # DEBUG DETALLADO DE CADA FORMULARIO
            for i, item_form in enumerate(formset):
                print(f"\n--- Form {i} ---")
                print(f"Is valid: {item_form.is_valid()}")
                if not item_form.is_valid():
                    print(f"Errors: {item_form.errors}")
                    print(f"Non field errors: {item_form.non_field_errors()}")
                    if hasattr(item_form, 'cleaned_data'):
                        print(f"Cleaned data: {item_form.cleaned_data}")
                    else:
                        print("Cleaned data: Not available")
        
        # Si el formset no es válido, retornar error
        if not formset.is_valid():
            messages.error(self.request, "Error en los productos. Por favor revisa los datos.")
            return self.form_invalid(form, formset)
        
        try:
            with transaction.atomic():
                self.object = form.save(commit=False)
                self.object.created_by = self.request.user
                self.object.dispatch_date = timezone.now()  # Establecer fecha actual
                
                # El número se generará automáticamente en el save() del modelo
                self.object.save()

                # DEBUG: Mostrar lo que se va a guardar
                print("=== GUARDANDO ITEMS ===")
                items_to_save = formset.save(commit=False)
                print(f"Items to save: {len(items_to_save)}")
                
                for i, item in enumerate(items_to_save):
                    print(f"\n--- Guardando item {i} ---")
                    print(f"Product: {item.product}")
                    print(f"Quantity: {item.quantity}")
                    print(f"Unit price: {item.unit_price}")
                    
                    # Asegurarse de que el producto esté establecido
                    if not item.product:
                        print(f"⚠️  Skipping item without product: {item}")
                        continue
                        
                    item.dispatch_note = self.object
                    
                    # Si no hay precio unitario, usar el del producto
                    if not item.unit_price and hasattr(item.product, 'unit_price'):
                        item.unit_price = item.product.unit_price
                    
                    item.subtotal = item.quantity * (item.unit_price if item.unit_price else 0)
                    print(f"Subtotal: {item.subtotal}")
                    item.save()
                    print(f"✅ Item guardado con ID: {item.id}")
                
                # Guardar los elementos eliminados
                for obj in formset.deleted_objects:
                    print(f"🗑️  Eliminando objeto: {obj}")
                    obj.delete()
                
                # Recalcular total
                total = sum(item.subtotal for item in self.object.items.all())
                self.object.total = total
                self.object.save()
                print(f"💰 Total guardado: {self.object.total}")
                print(f"🔢 Número de despacho generado: {self.object.dispatch_number}")
                
        except Exception as e:
            print(f"❌ Error durante el guardado: {str(e)}")
            import traceback
            traceback.print_exc()
            messages.error(self.request, f"Error al guardar: {str(e)}")
            return self.form_invalid(form, formset)
        
        messages.success(self.request, f"Nota de Despacho N°{self.object.dispatch_number} creada exitosamente.")
        return redirect(self.get_success_url())
    
    def form_invalid(self, form, formset):
        print("=== FORM INVALID ===")
        print(f"Form errors: {form.errors}")
        print(f"Formset errors: {formset.errors}")
        
        # Agregar clientes y proveedores al contexto incluso en caso de error
        context = self.get_context_data(form=form, formset=formset)
        context['clients'] = Client.objects.filter(is_active=True)
        context['suppliers'] = Supplier.objects.filter(is_active=True)
        
        return self.render_to_response(context)

class DispatchNoteUpdateView(LoginRequiredMixin, UpdateView):
    model = DispatchNote
    form_class = DispatchNoteForm
    template_name = 'dispatch_notes/dispatch_form.html'
    success_url = reverse_lazy('dispatch_notes:list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['formset'] = DispatchItemFormSet(self.request.POST, instance=self.object)
        else:
            context['formset'] = DispatchItemFormSet(instance=self.object)
        
        # Agregar clientes y proveedores para el template
        context['clients'] = Client.objects.filter(is_active=True)
        context['suppliers'] = Supplier.objects.filter(is_active=True)
        
        return context

    def post(self, request, *args, **kwargs):
        print("=== DEBUG UPDATE POST ===")
        print("POST data keys:", list(request.POST.keys()))
        
        self.object = self.get_object()
        
        # No permitir edición si ya está despachado
        if self.object.status == 'DISPATCHED':
            messages.error(request, "No se puede editar una nota de despacho ya despachada.")
            return redirect('dispatch_notes:detail', pk=self.object.pk)
        
        form = self.get_form()
        formset = DispatchItemFormSet(self.request.POST, instance=self.object)

        if form.is_valid() and formset.is_valid():
            return self.form_valid(form, formset)
        else:
            return self.form_invalid(form, formset)

    def form_valid(self, form, formset):
        print("=== DEBUG FORM VALIDATION UPDATE ===")
        print(f"Form is valid: {form.is_valid()}")
        print(f"Formset is valid: {formset.is_valid()}")
        
        if not form.is_valid():
            print("Form errors:", form.errors)
            
        if not formset.is_valid():
            print("Formset errors:", formset.errors)
            print("Formset non-form errors:", formset.non_form_errors())
            for i, item_form in enumerate(formset):
                if not item_form.is_valid():
                    print(f"Form {i} errors:", item_form.errors)
        
        # Si el formset no es válido, retornar error
        if not formset.is_valid():
            messages.error(self.request, "Error en los productos. Por favor revisa los datos.")
            return self.form_invalid(form, formset)
        
        with transaction.atomic():
            self.object = form.save()
            items_to_save = formset.save(commit=False)
            
            for item in items_to_save:
                item.dispatch_note = self.object
                
                # Si no hay precio unitario, usar el del producto
                if not item.unit_price and hasattr(item.product, 'unit_price'):
                    item.unit_price = item.product.unit_price
                
                item.subtotal = item.quantity * (item.unit_price if item.unit_price else 0)
                item.save()
            
            # Manejar items eliminados
            for item in formset.deleted_objects:
                item.delete()
            
            # Recalcular total
            self.object.total = sum(item.subtotal for item in self.object.items.all())
            self.object.save()
        
        messages.success(self.request, f"Nota de Despacho N°{self.object.dispatch_number} actualizada exitosamente.")
        return redirect(self.get_success_url())

    def form_invalid(self, form, formset):
        print("=== FORM INVALID ===")
        print(f"Form errors: {form.errors}")
        print(f"Formset errors: {formset.errors}")
        
        # Agregar clientes y proveedores al contexto incluso en caso de error
        context = self.get_context_data(form=form, formset=formset)
        context['clients'] = Client.objects.filter(is_active=True)
        context['suppliers'] = Supplier.objects.filter(is_active=True)
        
        return self.render_to_response(context)
    
class DispatchNoteDetailView(LoginRequiredMixin, DetailView):
    model = DispatchNote
    template_name = 'dispatch_notes/dispatch_detail.html'
    context_object_name = 'dispatch_note'
    
    def get_queryset(self):
        return super().get_queryset().select_related('client', 'created_by', 'supplier').prefetch_related('items__product')


class DispatchNotePrintView(LoginRequiredMixin, DetailView):
    model = DispatchNote
    template_name = 'dispatch_notes/dispatch_print.html'
    context_object_name = 'dispatch'
    
    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        context = self.get_context_data(object=self.object)
        
        html_string = render_to_string(self.template_name, context)
        html = HTML(string=html_string, base_url=request.build_absolute_uri())
        pdf = html.write_pdf()
        
        response = HttpResponse(pdf, content_type='application/pdf')
        response['Content-Disposition'] = f'inline; filename="nota_despacho_{self.object.dispatch_number}.pdf"'
        
        return response
    
# Vista para confirmar despacho
def dispatch_note_confirm(request, pk):
    dispatch_note = get_object_or_404(DispatchNote, pk=pk)
    
    if request.method == 'POST':
        if dispatch_note.status == 'PENDING':
            try:
                with transaction.atomic():
                    # 1. Actualizar el estado de la nota de despacho a 'DESPACHADO'
                    dispatch_note.status = 'DISPATCHED'
                    dispatch_note.save()
                    
                    # 2. Descontar el stock de cada producto
                    for item in dispatch_note.items.all():
                        product = item.product
                        # Verificar stock suficiente
                        if product.current_stock < item.quantity:
                            messages.warning(
                                request, 
                                f"Stock insuficiente para {product.description}. Stock actual: {product.current_stock}, solicitado: {item.quantity}"
                            )
                            continue
                            
                        # Utilizamos F() para evitar condiciones de carrera
                        Product.objects.filter(pk=product.pk).update(
                            current_stock=F('current_stock') - item.quantity
                        )
                        
                    messages.success(request, f"La Nota de Despacho #{dispatch_note.dispatch_number} ha sido confirmada como 'Despachada'.")
            except Exception as e:
                messages.error(request, f"Ocurrió un error al despachar la nota: {e}")
                
        else:
            messages.warning(request, "Esta nota de despacho ya ha sido despachada o cancelada.")
    
    return redirect('dispatch_notes:detail', pk=pk)

# Vista para cancelar despacho
def dispatch_note_cancel(request, pk):
    dispatch_note = get_object_or_404(DispatchNote, pk=pk)
    
    if request.method == 'POST':
        if dispatch_note.status == 'PENDING':
            dispatch_note.status = 'CANCELLED'
            dispatch_note.save()
            messages.success(request, f"Nota de Despacho #{dispatch_note.dispatch_number} cancelada exitosamente.")
        else:
            messages.warning(request, "Solo se pueden cancelar notas de despacho pendientes.")
    
    return redirect('dispatch_notes:detail', pk=pk)
    
# API para búsqueda de productos
def product_search_api(request):
    try:
        product_id = request.GET.get('id')
        query = request.GET.get('q', '')
        all_products = request.GET.get('all')
        
        print(f"DEBUG API: id={product_id}, q={query}, all={all_products}")
        
        if all_products:
            # Devolver todos los productos activos
            products = Product.objects.filter(is_active=True)[:50]  # Limitar a 50
            products_data = []
            for product in products:
                product_data = {
                    'id': product.id,
                    'product_code': getattr(product, 'product_code', ''),
                    'description': getattr(product, 'description', ''),
                    'unit_price': float(product.unit_price) if hasattr(product, 'unit_price') and product.unit_price else 0.0,
                    'current_stock': getattr(product, 'current_stock', 0)
                }
                
                # Campos opcionales
                if hasattr(product, 'brand'):
                    product_data['brand'] = product.brand
                if hasattr(product, 'model'):
                    product_data['model'] = product.model
                if hasattr(product, 'category'):
                    product_data['category'] = str(product.category) if product.category else ''
                
                products_data.append(product_data)
                
            print(f"DEBUG API: Returning {len(products_data)} products for all=true")
            return JsonResponse(products_data, safe=False)
        
        elif product_id:
            try:
                product_id_int = int(product_id)
                product = Product.objects.filter(pk=product_id_int, is_active=True).first()
                products_data = []
                
                if product:
                    product_data = {
                        'id': product.id,
                        'product_code': getattr(product, 'product_code', ''),
                        'description': getattr(product, 'description', ''),
                        'unit_price': float(product.unit_price) if hasattr(product, 'unit_price') and product.unit_price else 0.0,
                        'current_stock': getattr(product, 'current_stock', 0)
                    }
                    
                    # Campos opcionales
                    if hasattr(product, 'brand'):
                        product_data['brand'] = product.brand
                    if hasattr(product, 'model'):
                        product_data['model'] = product.model
                    if hasattr(product, 'category'):
                        product_data['category'] = str(product.category) if product.category else ''
                    
                    products_data.append(product_data)
                    
                print(f"Search by ID {product_id_int}: Found {len(products_data)} products")
                return JsonResponse(products_data, safe=False)
            except (ValueError, TypeError):
                # Buscar por código o descripción
                products = Product.objects.filter(
                    Q(product_code__iexact=product_id) | Q(description__icontains=product_id),
                    is_active=True
                )[:1]
                products_data = []
                for product in products:
                    product_data = {
                        'id': product.id,
                        'product_code': getattr(product, 'product_code', ''),
                        'description': getattr(product, 'description', ''),
                        'unit_price': float(product.unit_price) if hasattr(product, 'unit_price') and product.unit_price else 0.0,
                        'current_stock': getattr(product, 'current_stock', 0)
                    }
                    
                    products_data.append(product_data)
                    
                return JsonResponse(products_data, safe=False)
        
        elif query:
            # Búsqueda por texto
            products = Product.objects.filter(
                Q(product_code__icontains=query) | Q(description__icontains=query),
                is_active=True
            )[:10]
            products_data = []
            for product in products:
                product_data = {
                    'id': product.id,
                    'product_code': getattr(product, 'product_code', ''),
                    'description': getattr(product, 'description', ''),
                    'unit_price': float(product.unit_price) if hasattr(product, 'unit_price') and product.unit_price else 0.0,
                    'current_stock': getattr(product, 'current_stock', 0)
                }
                
                # Campos opcionales
                if hasattr(product, 'brand'):
                    product_data['brand'] = product.brand
                if hasattr(product, 'model'):
                    product_data['model'] = product.model
                if hasattr(product, 'category'):
                    product_data['category'] = str(product.category) if product.category else ''
                
                products_data.append(product_data)
                
            print(f"Found {len(products_data)} products for query: {query}")
            return JsonResponse(products_data, safe=False)
        
        else:
            products_data = []
            print("No search criteria provided")
            return JsonResponse(products_data, safe=False)
            
    except Exception as e:
        print(f"ERROR in product_search_api: {str(e)}")
        import traceback
        traceback.print_exc()
        return JsonResponse({'error': str(e)}, status=500)

# API para obtener datos de cliente
def client_data_api(request, client_id):
    try:
        client = get_object_or_404(Client, pk=client_id)
        data = {
            'id': client.id,
            'name': client.name,
            'phone': client.phone,
            'email': client.email,
            'address': client.address,
        }
        return JsonResponse(data)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=404)