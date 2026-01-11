import asyncio
from django.core.management.base import BaseCommand
from scrobbling.scheduler import start_scrobbling


class Command(BaseCommand):
    help = "Run background scrobbling service"

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS("Starting scrobbling service...")
        )
        asyncio.run(start_scrobbling())
