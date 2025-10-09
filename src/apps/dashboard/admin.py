from django.contrib import admin
from .models import DashboardSetting

@admin.register(DashboardSetting)
class DashboardSettingAdmin(admin.ModelAdmin):
    list_display = ['name', 'value', 'description']
    list_editable = ['value']