from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from gym.models import UserProfile


class Command(BaseCommand):
    help = 'Creates UserProfile objects for users who do not have one'

    def handle(self, *args, **options):
        users_without_profile = 0
        
        for user in User.objects.all():
            try:
                # Check if the user has a profile
                user.profile
                self.stdout.write(f"User {user.username} already has a profile")
            except UserProfile.DoesNotExist:
                # Create a profile for the user
                UserProfile.objects.create(user=user)
                users_without_profile += 1
                self.stdout.write(self.style.SUCCESS(f"Created profile for user: {user.username}"))
        
        if users_without_profile == 0:
            self.stdout.write(self.style.SUCCESS("All users have profiles!"))
        else:
            self.stdout.write(self.style.SUCCESS(f"Created {users_without_profile} profiles for users without profiles"))