from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils import timezone
from .models import Website, InternalApp, MonitoringCheck, AlertLog, MonitoringSettings


@admin.register(Website)
class WebsiteAdmin(admin.ModelAdmin):
    list_display = ['name', 'url', 'status', 'is_online_display', 'uptime_percentage', 'last_check_time', 'alert_email']
    list_filter = ['status', 'created_at', 'send_recovery_email']
    search_fields = ['name', 'url', 'description']
    readonly_fields = ['created_at', 'updated_at', 'is_online_display', 'uptime_percentage', 'last_check_time']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'url', 'description', 'status')
        }),
        ('Monitoring Configuration', {
            'fields': ('check_interval', 'timeout', 'expected_status_code', 'send_recovery_email')
        }),
        ('Email Configuration', {
            'fields': ('alert_email', 'recovery_email')
        }),
        ('Status Information', {
            'fields': ('is_online_display', 'uptime_percentage', 'last_check_time'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def is_online_display(self, obj):
        if obj.is_online:
            return format_html('<span style="color: green;">● Online</span>')
        else:
            return format_html('<span style="color: red;">● Offline</span>')
    is_online_display.short_description = 'Status'
    
    def uptime_percentage(self, obj):
        uptime = obj.uptime_percentage
        color = 'green' if uptime >= 99 else 'orange' if uptime >= 95 else 'red'
        return format_html('<span style="color: {};">{:.2f}%</span>', color, uptime)
    uptime_percentage.short_description = 'Uptime (24h)'


class InternalAppInline(admin.TabularInline):
    model = InternalApp
    extra = 0
    fields = ['name', 'app_type', 'url', 'is_active', 'expected_status_code', 'timeout']


@admin.register(InternalApp)
class InternalAppAdmin(admin.ModelAdmin):
    list_display = ['name', 'website', 'app_type', 'url', 'is_active', 'is_online_display']
    list_filter = ['app_type', 'is_active', 'website', 'created_at']
    search_fields = ['name', 'url', 'description', 'website__name']
    readonly_fields = ['created_at', 'updated_at', 'is_online_display']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('website', 'name', 'app_type', 'url', 'description', 'is_active')
        }),
        ('Monitoring Configuration', {
            'fields': ('expected_status_code', 'timeout')
        }),
        ('Status Information', {
            'fields': ('is_online_display',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def is_online_display(self, obj):
        if obj.is_online:
            return format_html('<span style="color: green;">● Online</span>')
        else:
            return format_html('<span style="color: red;">● Offline</span>')
    is_online_display.short_description = 'Status'


@admin.register(MonitoringCheck)
class MonitoringCheckAdmin(admin.ModelAdmin):
    list_display = ['check_time', 'website', 'internal_app', 'is_online_display', 'status_code', 'response_time']
    list_filter = ['is_online', 'check_time', 'website', 'internal_app']
    search_fields = ['website__name', 'internal_app__name', 'error_message']
    readonly_fields = ['check_time', 'is_online', 'response_time', 'status_code', 'error_message', 'response_content']
    date_hierarchy = 'check_time'
    
    fieldsets = (
        ('Check Information', {
            'fields': ('website', 'internal_app', 'check_time', 'is_online')
        }),
        ('Response Details', {
            'fields': ('status_code', 'response_time', 'error_message')
        }),
        ('Response Content', {
            'fields': ('response_content',),
            'classes': ('collapse',)
        })
    )
    
    def is_online_display(self, obj):
        if obj.is_online:
            return format_html('<span style="color: green;">● Online</span>')
        else:
            return format_html('<span style="color: red;">● Offline</span>')
    is_online_display.short_description = 'Status'
    
    def has_add_permission(self, request):
        return False  # Prevent manual creation of checks


@admin.register(AlertLog)
class AlertLogAdmin(admin.ModelAdmin):
    list_display = ['website', 'alert_type', 'sent_at', 'email_sent_to', 'is_sent_display']
    list_filter = ['alert_type', 'is_sent', 'sent_at', 'website']
    search_fields = ['website__name', 'email_sent_to', 'subject', 'message']
    readonly_fields = ['sent_at', 'is_sent', 'email_sent_to', 'subject', 'message']
    date_hierarchy = 'sent_at'
    
    fieldsets = (
        ('Alert Information', {
            'fields': ('website', 'alert_type', 'sent_at', 'is_sent')
        }),
        ('Email Details', {
            'fields': ('email_sent_to', 'subject', 'message')
        })
    )
    
    def is_sent_display(self, obj):
        if obj.is_sent:
            return format_html('<span style="color: green;">✓ Sent</span>')
        else:
            return format_html('<span style="color: red;">✗ Failed</span>')
    is_sent_display.short_description = 'Status'
    
    def has_add_permission(self, request):
        return False  # Prevent manual creation of alert logs


@admin.register(MonitoringSettings)
class MonitoringSettingsAdmin(admin.ModelAdmin):
    list_display = ['is_monitoring_active', 'global_check_interval', 'max_concurrent_checks', 'alert_cooldown_minutes']
    
    fieldsets = (
        ('Global Settings', {
            'fields': ('is_monitoring_active', 'global_check_interval', 'max_concurrent_checks', 'alert_cooldown_minutes')
        }),
    )
    
    def has_add_permission(self, request):
        return not MonitoringSettings.objects.exists()  # Only allow one settings instance


# Update Website admin to include inline
WebsiteAdmin.inlines = [InternalAppInline]
