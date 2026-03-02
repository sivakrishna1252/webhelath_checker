from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.core.mail import send_mail
from django.conf import settings
from .models import Website

@receiver(post_save, sender=Website)
def website_added_alert(sender, instance, created, **kwargs):
    if created:
        subject = f"🆕 Website Added to Monitoring: {instance.name}"
        message = f"""
Dear Administrator,

A new website has been successfully added to the Web Health Checker monitoring system.

Website Details:
- Name: {instance.name}
- URL: {instance.url}
- Alert Email: {instance.alert_email}
- Check Interval: Every {instance.check_interval} seconds

The system will now begin monitoring this website and will notify you if any issues are detected.

Best regards,
Web Health Checker System
        """
        try:
            send_mail(
                subject.strip(),
                message.strip(),
                settings.DEFAULT_FROM_EMAIL,
                [instance.alert_email],
                fail_silently=True
            )
        except Exception:
            pass

@receiver(post_delete, sender=Website)
def website_deleted_alert(sender, instance, **kwargs):
    subject = f"🗑️ Website Removed from Monitoring: {instance.name}"
    message = f"""
Dear Administrator,

The website '{instance.name}' has been permanently removed from the Web Health Checker monitoring system.

Deleted Website Details:
- Name: {instance.name}
- URL: {instance.url}

All background monitoring checks and alerts for this website have been discontinued.

Best regards,
Web Health Checker System
    """
    try:
        send_mail(
            subject.strip(),
            message.strip(),
            settings.DEFAULT_FROM_EMAIL,
            [instance.alert_email],
            fail_silently=True
        )
    except Exception:
        pass
