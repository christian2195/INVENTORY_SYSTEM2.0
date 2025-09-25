# src/apps/dispatch_notes/admin.py
from django.contrib import admin
from django.utils.html import format_html
from .models import DispatchNote, DispatchItem

class DispatchItemInline(admin.TabularInline):
    model = DispatchItem
    extra = 1
    readonly_fields = ['subtotal']
    fields = ['product', 'quantity', 'unit_price', 'brand', 'model', 'subtotal']

@admin.register(DispatchNote)
class DispatchNoteAdmin(admin.ModelAdmin):
    list_display = (
        'dispatch_number',
        'client',
        'beneficiary',
        'dispatch_date',
        'status_badge',
        'driver_name',
        'license_plate',
        'total_display'
    )
    
    list_filter = ('dispatch_date', 'status', 'client', 'supplier')
    search_fields = ('dispatch_number', 'client__name', 'beneficiary', 'driver_name')
    readonly_fields = ('total', 'created_by', 'dispatch_number')
    inlines = [DispatchItemInline]
    
    fieldsets = (
        ('INFORMACIÓN PRINCIPAL', {
            'fields': (
                'dispatch_number',
                'dispatch_date',
                'status',
                'created_by',
                'total'
            )
        }),
        ('INFORMACIÓN DEL CLIENTE/PROVEEDOR', {
            'fields': (
                'client',
                'beneficiary',
                'supplier',
                'order_number'
            )
        }),
        ('INFORMACIÓN DEL TRANSPORTE', {
            'fields': (
                'driver_name',
                'driver_id',
                'vehicle_type',
                'vehicle_color',
                'license_plate'
            )
        }),
        ('OBSERVACIONES', {
            'fields': ('notes',)
        })
    )
    
    def status_badge(self, obj):
        colors = {
            'PENDING': 'warning',
            'DISPATCHED': 'success',
            'CANCELLED': 'danger'
        }
        return format_html(
            '<span class="badge bg-{}">{}</span>',
            colors.get(obj.status, 'secondary'),
            obj.get_status_display()
        )
    status_badge.short_description = 'Estado'
    
    def total_display(self, obj):
        return f"Bs. {obj.total:,.2f}"
    total_display.short_description = 'Total'
    
    def save_model(self, request, obj, form, change):
        if not obj.created_by:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)

@admin.register(DispatchItem)
class DispatchItemAdmin(admin.ModelAdmin):
    list_display = ('dispatch_note', 'product', 'quantity', 'unit_price', 'subtotal_display')
    list_filter = ('dispatch_note__dispatch_date',)
    search_fields = ('product__description', 'dispatch_note__dispatch_number')
    
    def subtotal_display(self, obj):
        return f"Bs. {obj.subtotal:,.2f}" if obj.subtotal else "-"
    subtotal_display.short_description = 'Subtotal'