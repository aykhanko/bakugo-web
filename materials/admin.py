from django.contrib import admin
from unfold.admin import ModelAdmin
from .models import ProjectMaterial


@admin.register(ProjectMaterial)
class ProjectMaterialAdmin(ModelAdmin):
    list_display = ('title', 'is_active', 'created_at')
    list_filter = ('is_active',)
    search_fields = ('title',)
    readonly_fields = ('created_at', 'updated_at')

    fieldsets = (
        ('General', {
            'fields': ('title', 'is_active'),
        }),
        ('Excel', {
            'fields': ('excel_file', 'excel_link'),
        }),
        ('GitHub', {
            'fields': ('github_link',),
        }),
        ('PowerPoint', {
            'fields': ('powerpoint_file', 'powerpoint_link'),
        }),
        ('PDF', {
            'fields': ('pdf_file', 'pdf_link'),
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
        }),
    )

