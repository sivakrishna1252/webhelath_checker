
from django.core.management.base import BaseCommand
from monitoring.services import MonitoringService
from monitoring.models import MonitoringSettings
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Run monitoring checks for all active websites and internal apps'

    def add_arguments(self, parser):
        parser.add_argument(
            '--website-id',
            type=int,
            help='Check only a specific website by ID',
        )
        parser.add_argument(
            '--internal-app-id',
            type=int,
            help='Check only a specific internal app by ID',
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force run even if monitoring is disabled',
        )

    def handle(self, *args, **options):
        settings = MonitoringSettings.get_settings()
        
        if not settings.is_monitoring_active and not options['force']:
            self.stdout.write(
                self.style.WARNING('Monitoring is currently disabled. Use --force to run anyway.')
            )
            return

        monitoring_service = MonitoringService()
        
        if options['website_id']:
            from monitoring.models import Website
            try:
                website = Website.objects.get(id=options['website_id'])
                self.stdout.write(f'Checking website: {website.name}')
                monitoring_service.run_monitoring_cycle()
                self.stdout.write(
                    self.style.SUCCESS(f'Successfully checked website: {website.name}')
                )
            except Website.DoesNotExist:
                self.stdout.write(
                    self.style.ERROR(f'Website with ID {options["website_id"]} not found')
                )
        elif options['internal_app_id']:
            from monitoring.models import InternalApp
            try:
                internal_app = InternalApp.objects.get(id=options['internal_app_id'])
                self.stdout.write(f'Checking internal app: {internal_app.name}')
                monitoring_service.run_monitoring_cycle()
                self.stdout.write(
                    self.style.SUCCESS(f'Successfully checked internal app: {internal_app.name}')
                )
            except InternalApp.DoesNotExist:
                self.stdout.write(
                    self.style.ERROR(f'Internal app with ID {options["internal_app_id"]} not found')
                )
        else:
            self.stdout.write('Running monitoring checks for all active websites and internal apps...')
            monitoring_service.run_monitoring_cycle()
            self.stdout.write(
                self.style.SUCCESS('Monitoring checks completed successfully')
            )
