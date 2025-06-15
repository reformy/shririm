from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.db.models.signals import post_save
from django.dispatch import receiver
import pytz

class Device(models.Model):
    """
    Represents a gym device
    """
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='device_images/', blank=True, null=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class Plan(models.Model):
    """
    Represents a workout plan - an ordered list of devices with settings
    """
    name = models.CharField(max_length=100)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class PlanDevice(models.Model):
    """
    Represents a device in a plan with its settings
    """
    plan = models.ForeignKey(Plan, on_delete=models.CASCADE, related_name='plan_devices')
    device = models.ForeignKey(Device, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    order = models.PositiveIntegerField()
    chair_position = models.CharField(max_length=50, blank=True)
    weight = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    sets = models.PositiveIntegerField(default=3)
    moves_per_set = models.PositiveIntegerField(default=12)
    
    class Meta:
        ordering = ['order']
        # Ensure unique names within a plan
        unique_together = [['plan', 'name']]

    def __str__(self):
        display_name = self.name if self.name else self.device.name
        return f"{display_name} in {self.plan.name}"
        
    def save(self, *args, **kwargs):
        # If no name is provided, use the device name and ensure uniqueness
        if not self.name and self.device:
            self.name = self._get_unique_name()
        super().save(*args, **kwargs)
        
    def _get_unique_name(self):
        """Generate a unique name based on the device name"""
        base_name = self.device.name
        name = base_name
        suffix = 1
        
        # Check if the name already exists in this plan
        while PlanDevice.objects.filter(plan=self.plan, name=name).exists():
            # If this is an update of an existing object and the name matches itself, it's OK
            if self.pk and PlanDevice.objects.get(plan=self.plan, name=name).pk == self.pk:
                break
            # Otherwise, append a number and try again
            name = f"{base_name} #{suffix}"
            suffix += 1
            
        return name

class Session(models.Model):
    """
    Represents a workout session
    """
    STATUS_CHOICES = (
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    )
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    plan = models.ForeignKey(Plan, on_delete=models.CASCADE)
    start_time = models.DateTimeField(default=timezone.now)
    end_time = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='in_progress')
    
    def __str__(self):
        return f"Session {self.id} - {self.plan.name}"
    
    def close_session(self):
        """Close session and delete device sessions that were not performed"""
        self.end_time = timezone.now()
        self.status = 'completed'
        # Delete all device sessions that weren't performed
        self.device_sessions.filter(performed=False).delete()
        self.save()
        
    @property
    def completed_count(self):
        """Get the number of completed device sessions"""
        return self.device_sessions.filter(performed=True).count()
        
    @property
    def total_count(self):
        """Get the total number of device sessions"""
        return self.device_sessions.count()
        
    @property
    def completion_percentage(self):
        """Get the percentage of completed device sessions"""
        total = self.total_count
        if total == 0:
            return 0
        return int((self.completed_count / total) * 100)

class DeviceSession(models.Model):
    """
    Represents a device used in a particular session
    """
    session = models.ForeignKey(Session, on_delete=models.CASCADE, related_name='device_sessions')
    device = models.ForeignKey(Device, on_delete=models.CASCADE)
    plan_device = models.ForeignKey(PlanDevice, on_delete=models.CASCADE, null=True)
    name = models.CharField(max_length=100)  # Custom name from the plan device
    chair_position = models.CharField(max_length=50, blank=True)
    weight = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    sets = models.PositiveIntegerField(default=3)
    moves_per_set = models.PositiveIntegerField(default=12)
    order = models.PositiveIntegerField()
    performed = models.BooleanField(default=False)
    notes = models.TextField(blank=True)
    
    class Meta:
        ordering = ['order']

    def __str__(self):
        display_name = self.name if self.name else self.device.name
        return f"{display_name} in Session {self.session.id}"
    
    @classmethod
    def create_from_plan_device(cls, session, plan_device):
        """Create a device session from a plan device, copying settings from previous session if exists"""
        # Try to find the latest session for this plan device NAME by the same user
        previous_session = DeviceSession.objects.filter(
            name=plan_device.name,  # Match by plan device name instead of device
            session__user=session.user,
            performed=True
        ).order_by('-session__start_time').first()
        
        if previous_session:
            # Copy settings from previous session
            return cls.objects.create(
                session=session,
                device=plan_device.device,
                plan_device=plan_device,
                name=plan_device.name,  # Use the plan device name
                chair_position=previous_session.chair_position,
                weight=previous_session.weight,
                sets=previous_session.sets,
                moves_per_set=previous_session.moves_per_set,
                order=plan_device.order,
            )
        else:
            # Use default settings from the plan
            return cls.objects.create(
                session=session,
                device=plan_device.device,
                plan_device=plan_device,
                name=plan_device.name,  # Use the plan device name
                chair_position=plan_device.chair_position,
                weight=plan_device.weight,
                sets=plan_device.sets,
                moves_per_set=plan_device.moves_per_set,
                order=plan_device.order,
            )


class UserProfile(models.Model):
    """
    Extension of the User model with additional profile information
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    bio = models.TextField(blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    weight = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    height = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    goal = models.CharField(max_length=200, blank=True)
    timezone = models.CharField(max_length=50, default='UTC', choices=[(tz, tz) for tz in pytz.common_timezones])
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user.username}'s profile"
        
    def save(self, *args, **kwargs):
        # If timezone is not set, try to guess it
        if not self.timezone or self.timezone == 'UTC':
            try:
                # Try to get the timezone from the user's IP or other means
                # For simplicity, we'll use America/New_York as a default for now
                # In a real app, you'd use a geolocation service based on the user's IP
                self.timezone = 'America/New_York'
            except:
                # If we can't guess, fall back to UTC
                self.timezone = 'UTC'
        super().save(*args, **kwargs)

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """Create a user profile when a new user is created"""
    if created:
        UserProfile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """Save the user profile when the user is saved"""
    instance.profile.save()