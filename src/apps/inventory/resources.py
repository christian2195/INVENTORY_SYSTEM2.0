# apps/inventory/resources.py
from import_export import resources, fields
from import_export.widgets import DecimalWidget, IntegerWidget
from .models import Product

class ProductResource(resources.ModelResource):
    # Campos personalizados con widgets y valores por defecto
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
    
    def before_import_row(self, row, **kwargs):
        """Limpia los datos antes de importar - ESTA ES LA SOLUCIÓN PRINCIPAL"""
        # Convertir unit_price nulo/vacío a 0.00
        unit_price = row.get('unit_price', '')
        if unit_price in ['', 'null', 'NULL', 'None', None, 'NaN']:
            row['unit_price'] = '0.00'
        elif unit_price is None:
            row['unit_price'] = '0.00'
        
        # Convertir current_stock nulo/vacío a 0
        current_stock = row.get('current_stock', '')
        if current_stock in ['', 'null', 'NULL', 'None', None, 'NaN']:
            row['current_stock'] = '0'
        
        # Valores por defecto para otros campos numéricos
        min_stock = row.get('min_stock', '')
        if min_stock in ['', 'null', 'NULL', 'None', None, 'NaN']:
            row['min_stock'] = '0'
            
        max_stock = row.get('max_stock', '') 
        if max_stock in ['', 'null', 'NULL', 'None', None, 'NaN']:
            row['max_stock'] = '0'
            
        # Asegurar que is_active tenga valor por defecto
        if not row.get('is_active'):
            row['is_active'] = 'True'
    
    # REMOVER el método import_field sobreescrito - NO ES NECESARIO
    # El before_import_row es suficiente para manejar los valores nulos