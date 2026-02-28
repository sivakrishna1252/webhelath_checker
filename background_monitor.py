import os
import time
import django
from concurrent.futures import ThreadPoolExecutor

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'server_checker.settings')
django.setup()

from monitoring.models import Website, InternalApp, MonitoringSettings
from monitoring.services import MonitoringService

def check_target(target, is_website=True):
    """Worker function to check a single target in a thread."""
    service = MonitoringService()
    try:
        if is_website:
            service.check_website(target)
        else:
            service.check_internal_app(target)
    except Exception as e:
        print(f"Error checking {target.name}: {e}")

def run_professional_monitoring():
    print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Starting professional monitoring cycle...", flush=True)
    
    # Get active targets
    websites = list(Website.objects.filter(status='active'))
    internal_apps = list(InternalApp.objects.filter(is_active=True, website__status='active'))
    
    # Use ThreadPool to check everything in parallel
    # max_workers=10 ensures we don't overwhelm the local system or SQLite
    with ThreadPoolExecutor(max_workers=10) as executor:
        for site in websites:
            executor.submit(check_target, site, True)
        for app in internal_apps:
            executor.submit(check_target, app, False)

    print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Cycle completed.", flush=True)

if __name__ == "__main__":
    print("--- Professional Health Checker Started ---", flush=True)
    print("Checking 30+ sites in parallel every 60 seconds.", flush=True)
    
    while True:
        run_professional_monitoring()
        time.sleep(60)
