
from celery import shared_task
from .services import MonitoringService
import logging

logger = logging.getLogger(__name__)


@shared_task
def run_monitoring_checks():
    """Celery task to run monitoring checks."""
    try:
        logger.info("Starting monitoring checks task")
        monitoring_service = MonitoringService()
        monitoring_service.run_monitoring_cycle()
        logger.info("Monitoring checks task completed successfully")
        return "Monitoring checks completed successfully"
    except Exception as e:
        logger.error(f"Error in monitoring checks task: {str(e)}")
        raise


@shared_task
def check_single_website(website_id):
    """Check a single website."""
    try:
        from .models import Website
        website = Website.objects.get(id=website_id)
        monitoring_service = MonitoringService()
        monitoring_service.run_monitoring_cycle()
        return f"Check completed for website: {website.name}"
    except Website.DoesNotExist:
        logger.error(f"Website with id {website_id} not found")
        return f"Website with id {website_id} not found"
    except Exception as e:
        logger.error(f"Error checking website {website_id}: {str(e)}")
        raise


@shared_task
def check_single_internal_app(internal_app_id):
    """Check a single internal app."""
    try:
        from .models import InternalApp
        internal_app = InternalApp.objects.get(id=internal_app_id)
        monitoring_service = MonitoringService()
        monitoring_service.run_monitoring_cycle()
        return f"Check completed for internal app: {internal_app.name}"
    except InternalApp.DoesNotExist:
        logger.error(f"Internal app with id {internal_app_id} not found")
        return f"Internal app with id {internal_app_id} not found"
    except Exception as e:
        logger.error(f"Error checking internal app {internal_app_id}: {str(e)}")
        raise






#celery -A server_checker worker -l info clery check command 
#celery -A server_checker beat -l info clery beat command