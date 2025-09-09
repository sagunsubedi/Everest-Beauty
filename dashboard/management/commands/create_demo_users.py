from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model


class Command(BaseCommand):
    help = "Create demo admin and user accounts for Everest Beauty"

    def handle(self, *args, **options):
        User = get_user_model()

        # Admin account
        admin_email = "admin@everestbeauty.com"
        admin_username = "admin"
        admin_password = "Admin@12345"

        admin_user, created_admin = User.objects.get_or_create(
            email=admin_email,
            defaults={
                "username": admin_username,
                "is_staff": True,
                "is_superuser": True,
                "first_name": "Everest",
                "last_name": "Admin",
            },
        )
        if created_admin:
            admin_user.set_password(admin_password)
            admin_user.save()
            self.stdout.write(self.style.SUCCESS(f"Created admin user: {admin_email} / {admin_password}"))
        else:
            self.stdout.write(self.style.WARNING(f"Admin user already exists: {admin_email}"))

        # Demo user account
        demo_email = "demo@everestbeauty.com"
        demo_username = "demo"
        demo_password = "Demo@12345"

        demo_user, created_demo = User.objects.get_or_create(
            email=demo_email,
            defaults={
                "username": demo_username,
                "is_staff": False,
                "is_superuser": False,
                "first_name": "Demo",
                "last_name": "User",
            },
        )
        if created_demo:
            demo_user.set_password(demo_password)
            demo_user.save()
            self.stdout.write(self.style.SUCCESS(f"Created demo user: {demo_email} / {demo_password}"))
        else:
            self.stdout.write(self.style.WARNING(f"Demo user already exists: {demo_email}"))

        self.stdout.write(self.style.MIGRATE_HEADING("If you need to reset passwords, run this command again after deleting the users or change them via admin."))



