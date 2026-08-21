
from django.contrib import admin
from .models import Complaint, Department


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ['name', 'email']
    search_fields = ['name']


@admin.register(Complaint)
class ComplaintAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'title', 'user', 'category', 'urgency_score',
        'sentiment', 'status', 'department', 'created_at'
    ]
    list_filter = ['category', 'status', 'sentiment', 'department']
    search_fields = ['title', 'description', 'location', 'user__username']
    readonly_fields = ['category', 'category_confidence', 'urgency_score', 'sentiment']
    list_per_page = 25
    ordering = ['-urgency_score', '-created_at']

    fieldsets = (
        ('Complaint Info', {
            'fields': ('user', 'title', 'description', 'location', 'image')
        }),
        ('AI Analysis (Auto-generated)', {
            'fields': ('category', 'category_confidence', 'urgency_score', 'sentiment'),
            'classes': ('collapse',),
        }),
        ('Admin Actions', {
            'fields': ('status', 'department', 'admin_remarks'),
        }),
    )