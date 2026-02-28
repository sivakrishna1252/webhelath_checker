from django.db import models
from django.contrib.auth.models import User
from django.core.validators import URLValidator
from django.core.mail import send_mail
from django.conf import settings
import requests
import time
from datetime import datetime, timedelta


class Website(models.Model):
    """Model to store website information and monitoring configuration."""
    
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('maintenance', 'Maintenance'),
    ]
    
    name = models.CharField(max_length=200, help_text="Display name for the website")
    url = models.URLField(validators=[URLValidator()], help_text="Full URL to monitor (e.g., https://example.com)")
    description = models.TextField(blank=True, help_text="Optional description of the website")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    check_interval = models.PositiveIntegerField(default=300, help_text="Check interval in seconds (default: 5 minutes)")
    timeout = models.PositiveIntegerField(default=30, help_text="Request timeout in seconds")
    expected_status_code = models.PositiveIntegerField(default=200, help_text="Expected HTTP status code")
    send_recovery_email = models.BooleanField(default=True, help_text="Send email when server recovers")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Email configuration for this website
    alert_email = models.EmailField(help_text="Email address to send alerts to")
    recovery_email = models.EmailField(blank=True, help_text="Email address for recovery notifications (if different from alert email)")
    
    class Meta:
        ordering = ['name']
    
    def __str__(self):
        return self.name
    
    @property
    def is_online(self):
        """Check if the website is currently online based on the very latest check."""
        latest_check = self.checks.first()
        return latest_check.is_online if latest_check else False
    
    @property
    def last_check_time(self):
        """Get the time of the last check."""
        latest_check = self.checks.first()
        return latest_check.check_time if latest_check else None
    
    @property
    def uptime_percentage(self):
        """Calculate uptime percentage for the last 20 checks (as configured)."""
        checks = self.checks.all()[:20]
        if not checks:
            return 0
        
        online_count = sum(1 for c in checks if c.is_online)
        total_count = len(checks)
        
        return round((online_count / total_count) * 100, 2)


class InternalApp(models.Model):
    """Model to store internal applications within a website."""
    
    APP_TYPE_CHOICES = [
        ('backend', 'Backend API'),
        ('landing', 'Landing Page'),
        ('admin', 'Admin Panel'),
        ('database', 'Database'),
        ('other', 'Other'),
    ]
    
    website = models.ForeignKey(Website, on_delete=models.CASCADE, related_name='internal_apps')
    name = models.CharField(max_length=200, help_text="Name of the internal app")
    app_type = models.CharField(max_length=20, choices=APP_TYPE_CHOICES, default='other')
    url = models.URLField(validators=[URLValidator()], help_text="Full URL to monitor")
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    expected_status_code = models.PositiveIntegerField(default=200)
    timeout = models.PositiveIntegerField(default=30)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['name']
        unique_together = ['website', 'name']
    
    def __str__(self):
        return f"{self.website.name} - {self.name}"
    
    @property
    def is_online(self):
        """Check if the internal app is currently online based on the very latest check."""
        latest_check = self.checks.first()
        return latest_check.is_online if latest_check else False


class MonitoringCheck(models.Model):
    """Model to store individual monitoring check results."""
    
    website = models.ForeignKey(Website, on_delete=models.CASCADE, related_name='checks', null=True, blank=True)
    internal_app = models.ForeignKey(InternalApp, on_delete=models.CASCADE, related_name='checks', null=True, blank=True)
    check_time = models.DateTimeField(auto_now_add=True)
    is_online = models.BooleanField(default=False)
    response_time = models.FloatField(null=True, blank=True, help_text="Response time in seconds")
    status_code = models.PositiveIntegerField(null=True, blank=True)
    error_message = models.TextField(blank=True)
    response_content = models.TextField(blank=True, help_text="First 1000 characters of response")
    
    class Meta:
        ordering = ['-check_time']
        indexes = [
            models.Index(fields=['website', 'check_time']),
            models.Index(fields=['internal_app', 'check_time']),
        ]

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        
        # Keep only the last 20 checks for this specific target
        if self.website and not self.internal_app:
            # Website checks
            old_checks = MonitoringCheck.objects.filter(
                website=self.website, 
                internal_app__isnull=True
            ).order_by('-check_time')[20:]
            if old_checks:
                old_ids = [c.id for c in old_checks]
                MonitoringCheck.objects.filter(id__in=old_ids).delete()
        elif self.internal_app:
            # Internal App checks
            old_checks = MonitoringCheck.objects.filter(
                internal_app=self.internal_app
            ).order_by('-check_time')[20:]
            if old_checks:
                old_ids = [c.id for c in old_checks]
                MonitoringCheck.objects.filter(id__in=old_ids).delete()
    
    def __str__(self):
        target = self.website or self.internal_app
        status = "Online" if self.is_online else "Offline"
        return f"{target} - {status} at {self.check_time}"
    
    @classmethod
    def perform_check(cls, target, url, expected_status=200, timeout=30):
        """Perform a monitoring check and return the result."""
        start_time = time.time()
        check = cls()
        
        if hasattr(target, 'website'):
            check.internal_app = target
            check.website = target.website
        else:
            check.website = target
        
        try:
            response = requests.get(url, timeout=timeout, allow_redirects=True)
            end_time = time.time()
            
            check.response_time = round(end_time - start_time, 3)
            check.status_code = response.status_code
            check.is_online = response.status_code == expected_status
            check.response_content = response.text[:1000]
            
            if not check.is_online:
                check.error_message = f"Expected status {expected_status}, got {response.status_code}"
            
        except requests.exceptions.Timeout:
            check.error_message = f"Request timed out after {timeout} seconds"
            check.is_online = False
        except requests.exceptions.ConnectionError:
            check.error_message = "Connection error - server may be down"
            check.is_online = False
        except requests.exceptions.RequestException as e:
            check.error_message = f"Request error: {str(e)}"
            check.is_online = False
        except Exception as e:
            check.error_message = f"Unexpected error: {str(e)}"
            check.is_online = False
        
        check.save()
        return check


class AlertLog(models.Model):
    """Model to track sent alerts and prevent spam."""
    
    ALERT_TYPES = [
        ('down', 'Server Down'),
        ('recovery', 'Server Recovery'),
        ('error', 'Error Alert'),
    ]
    
    website = models.ForeignKey(Website, on_delete=models.CASCADE, related_name='alerts')
    alert_type = models.CharField(max_length=20, choices=ALERT_TYPES)
    sent_at = models.DateTimeField(auto_now_add=True)
    email_sent_to = models.EmailField()
    subject = models.CharField(max_length=200)
    message = models.TextField()
    is_sent = models.BooleanField(default=True)
    is_cleared = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['-sent_at']
    
    def __str__(self):
        return f"{self.website.name} - {self.alert_type} at {self.sent_at}"
    
    @classmethod
    def should_send_alert(cls, website, alert_type):
        """Check if we should send an alert (prevent spam)."""
        from django.utils import timezone
        
        # Don't send duplicate alerts within 5 minutes
        recent_alert = cls.objects.filter(
            website=website,
            alert_type=alert_type,
            sent_at__gte=timezone.now() - timedelta(minutes=5)
        ).exists()
        
        return not recent_alert
    
    @classmethod
    def send_alert(cls, website, alert_type, subject, message, email_to=None):
        """Send an alert email and log it."""
        if not cls.should_send_alert(website, alert_type):
            return False
        
        email_to = email_to or website.alert_email
        
        try:
            send_mail(
                subject=subject,
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[email_to],
                fail_silently=False,
            )
            
            # Log the alert
            cls.objects.create(
                website=website,
                alert_type=alert_type,
                email_sent_to=email_to,
                subject=subject,
                message=message
            )
            return True
            
        except Exception as e:
            # Log failed alert
            cls.objects.create(
                website=website,
                alert_type=alert_type,
                email_sent_to=email_to,
                subject=subject,
                message=message,
                is_sent=False
            )
            return False


class MonitoringSettings(models.Model):
    """Global monitoring settings."""
    
    is_monitoring_active = models.BooleanField(default=True)
    global_check_interval = models.PositiveIntegerField(default=300, help_text="Global check interval in seconds")
    max_concurrent_checks = models.PositiveIntegerField(default=10, help_text="Maximum concurrent monitoring checks")
    alert_cooldown_minutes = models.PositiveIntegerField(default=5, help_text="Minutes to wait before sending duplicate alerts")
    
    class Meta:
        verbose_name = "Monitoring Settings"
        verbose_name_plural = "Monitoring Settings"
    
    def save(self, *args, **kwargs):
        # Ensure only one settings instance exists
        if not self.pk and MonitoringSettings.objects.exists():
            return
        super().save(*args, **kwargs)
    
    @classmethod
    def get_settings(cls):
        """Get the monitoring settings, creating if they don't exist."""
        settings, created = cls.objects.get_or_create(pk=1)
        return settings
