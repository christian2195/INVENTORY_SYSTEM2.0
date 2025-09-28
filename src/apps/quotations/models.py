# src/apps/quotations/models.py
from django.db import models, transaction  # ✅ AGREGAR transaction AQUÍ
from django.utils import timezone
from django.core.exceptions import ValidationError
from apps.inventory.models import Product, Client
from apps.dispatch_notes.models import DispatchNote

class Quotation(models.Model):
    STATUS_CHOICES = [
        ('DRAFT', 'Borrador'),
        ('SENT', 'Enviada'),
        ('APPROVED', 'Aprobada'),
        ('REJECTED', 'Rechazada'),
        ('CONVERTED', 'Convertida a Despacho'),
    ]
    
    quotation_number = models.CharField(max_length=50, unique=True)
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    date_created = models.DateTimeField(default=timezone.now)
    date_sent = models.DateTimeField(null=True, blank=True)
    date_approved = models.DateTimeField(null=True, blank=True)
    valid_until = models.DateField(null=True, blank=True)
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='DRAFT')
    notes = models.TextField(blank=True)
    dispatch_note = models.OneToOneField(
        DispatchNote, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='quotation'
    )
    created_by = models.ForeignKey('auth.User', on_delete=models.SET_NULL, null=True)

    class Meta:
        verbose_name = "Cotización"
        verbose_name_plural = "Cotizaciones"
        ordering = ['-date_created']

    def __str__(self):
        return f'Cotización N° {self.quotation_number}'

    def clean(self):
        if self.valid_until and self.valid_until < timezone.now().date():
            raise ValidationError('La fecha de validez no puede ser en el pasado.')

    def save(self, *args, **kwargs):
        if not self.quotation_number:
            self.quotation_number = self.generate_quotation_number()
        
        # Calcular total automáticamente - usar aggregate para mejor performance
        if self.pk:
            from django.db.models import Sum
            total_result = self.items.aggregate(total=Sum('subtotal'))
            self.total = total_result['total'] or 0
        
        super().save(*args, **kwargs)

    def generate_quotation_number(self):
        """Genera un número de cotización automático"""
        current_year = timezone.now().year
        last_quotation = Quotation.objects.filter(
            quotation_number__startswith=f'COT-{current_year}-'
        ).order_by('-quotation_number').first()
        
        if last_quotation:
            try:
                last_number = int(last_quotation.quotation_number.split('-')[-1])
                next_number = last_number + 1
            except (ValueError, IndexError):
                next_number = 1
        else:
            next_number = 1
        
        return f'COT-{current_year}-{next_number:04d}'

    def can_convert_to_dispatch(self):
        """Verifica si la cotización puede convertirse en despacho"""
        return self.status == 'APPROVED' and not self.dispatch_note

    def convert_to_dispatch_note(self, user):
        """Convierte la cotización en una nota de despacho"""
        if not self.can_convert_to_dispatch():
            return None
        
        from apps.dispatch_notes.models import DispatchNote, DispatchItem
        
        try:
            # ✅ CORREGIDO: Usar transaction.atomic() directamente
            with transaction.atomic():
                # DEBUG
                print("=== INICIANDO CONVERSIÓN ===")
                print(f"Cliente: {self.client}")
                print(f"Items: {self.items.count()}")
                
                # Crear la nota de despacho - el número se generará automáticamente
                dispatch_note = DispatchNote(
                    client=self.client,
                    dispatch_date=timezone.now(),
                    status='PENDING',
                    created_by=user,
                    notes=f'Generado desde cotización {self.quotation_number}'
                )
                dispatch_note.save()  # Esto generará el número automáticamente
                
                print(f"Despacho creado: {dispatch_note.dispatch_number}")
                
                # Crear los items del despacho
                items_created = 0
                for quotation_item in self.items.all():
                    DispatchItem.objects.create(
                        dispatch_note=dispatch_note,
                        product=quotation_item.product,
                        quantity=quotation_item.quantity,
                        unit_price=quotation_item.unit_price
                    )
                    items_created += 1
                
                print(f"Items creados: {items_created}")
                
                # Actualizar la cotización
                self.dispatch_note = dispatch_note
                self.status = 'CONVERTED'
                self.save()
                
                print("=== CONVERSIÓN EXITOSA ===")
                return dispatch_note
                
        except Exception as e:
            # Log del error para debug
            print(f"Error al convertir cotización a despacho: {str(e)}")
            import traceback
            traceback.print_exc()
            return None


class QuotationItem(models.Model):
    quotation = models.ForeignKey(Quotation, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, editable=False)

    class Meta:
        verbose_name = "Ítem de Cotización"
        verbose_name_plural = "Ítems de Cotización"

    def __str__(self):
        return f'{self.quantity} de {self.product.description} en {self.quotation.quotation_number}'

    def clean(self):
        """Validaciones adicionales"""
        if self.quantity <= 0:
            raise ValidationError({'quantity': 'La cantidad debe ser mayor a 0'})
        if self.unit_price < 0:
            raise ValidationError({'unit_price': 'El precio unitario no puede ser negativo'})

    def save(self, *args, **kwargs):
        # Calcular subtotal automáticamente
        self.subtotal = self.quantity * self.unit_price
        super().save(*args, **kwargs)
        
        # Actualizar el total de la cotización
        if self.quotation:
            self.quotation.save()