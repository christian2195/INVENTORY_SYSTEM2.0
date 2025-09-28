# src/apps/inventory/resources.py (VERSIÓN FINAL)
from import_export import resources, fields
from import_export.widgets import DecimalWidget, IntegerWidget
from .models import Product, Supplier, Warehouse 
from django.db.models import ObjectDoesNotExist # Importar para manejo de excepciones

class ProductResource(resources.ModelResource):
    # Definición de campos con valores por defecto y widgets
    unit_price = fields.Field(
        column_name='unit_price',
        attribute='unit_price',
        widget=DecimalWidget(),
        default=0.00
    )
    current_stock = fields.Field(
        column_name='current_stock', 
        attribute='current_stock',
        widget=IntegerWidget(),
        default=0
    )
    min_stock = fields.Field(
        column_name='min_stock',
        attribute='min_stock', 
        widget=IntegerWidget(),
        default=0
    )
    max_stock = fields.Field(
        column_name='max_stock',
        attribute='max_stock',
        widget=IntegerWidget(), 
        default=0
    )
    
    # Manejo de Claves Foráneas (ForeignKey)
    supplier = fields.Field(
        column_name='supplier',
        attribute='supplier',
    )
    warehouse = fields.Field(
        column_name='warehouse',
        attribute='warehouse',
    )

    class Meta:
        model = Product
        import_id_fields = ['product_code']
        skip_unchanged = True
        report_skipped = True
        fields = (
            'product_code', 'description', 'unit_price', 'current_stock', 
            'unit', 'min_stock', 'max_stock', 'location', 'category', 
            'supplier', 'warehouse', 'is_active'
        )
        export_order = fields
        # Excluir campos que pueden ser problemáticos en la importación (como IDs)
        # exclude = ('id',) 
    
    # MÉTODOS PARA RESOLVER LAS CLAVES FORÁNEAS (Supplier y Warehouse)
    def import_field(self, field, data, row, **kwargs):
        # Este método sobrescribe cómo se importa cada campo individualmente
        if field.attribute == 'supplier':
            supplier_name = row.get('supplier')
            if supplier_name:
                try:
                    # Intenta encontrar el proveedor por nombre
                    row['supplier'] = Supplier.objects.get(name__iexact=supplier_name)
                except ObjectDoesNotExist:
                    # Si no existe, puedes registrar el error o asignar None (si el modelo lo permite)
                    # Dado que en su modelo Product, supplier es null=True, podemos dejarlo None
                    row['supplier'] = None
            else:
                row['supplier'] = None
            return 
        
        if field.attribute == 'warehouse':
            warehouse_name = row.get('warehouse')
            if warehouse_name:
                try:
                    # Intenta encontrar el almacén por nombre
                    row['warehouse'] = Warehouse.objects.get(name__iexact=warehouse_name)
                except ObjectDoesNotExist:
                    row['warehouse'] = None
            else:
                row['warehouse'] = None
            return

        super().import_field(field, data, row, **kwargs)


    def before_import_row(self, row, **kwargs):
        """Limpia los datos antes de importar para evitar errores NOT NULL"""
        
        # --- Limpieza de campos numéricos (Su lógica original, simplificada) ---
        
        # unit_price
        unit_price = row.get('unit_price')
        if not unit_price or unit_price in ['', 'null', 'NULL', 'None', 'NaN']:
            row['unit_price'] = '0.00'
            
        # stock, min_stock, max_stock
        for field_name in ['current_stock', 'min_stock', 'max_stock']:
            value = row.get(field_name)
            if not value or value in ['', 'null', 'NULL', 'None', 'NaN']:
                row[field_name] = '0'
        
        # --- Manejo de campos de texto con restricción NOT NULL ---
        
        # unit (Unidad)
        unit = row.get('unit')
        if not unit or unit in ['', 'null', 'NULL', 'None', 'NaN']:
            row['unit'] = 'Unidad' # Valor por defecto
            
        # description
        description = row.get('description')
        if not description or description in ['', 'null', 'NULL', 'None', 'NaN']:
            # La descripción NO debe ser nula. Usar el código si no hay descripción.
            row['description'] = row.get('product_code', 'Sin descripción')
            
        # is_active
        if not row.get('is_active'):
            row['is_active'] = 'True'