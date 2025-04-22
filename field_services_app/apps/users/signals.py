"""
Signal handlers for the users app.
"""

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from django.conf import settings
import os

User = get_user_model()


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """
    Signal handler to create related user profiles when a user is created.
    This can be extended to create different profile types based on the user's role.
    """
    if created:
        # Create technician profile if user is a technician
        if instance.role == 'technician':
            from apps.technicians.models import Technician
            Technician.objects.create(user=instance)
        
        # Other role-specific profile creation can be added here
        # e.g., Customer profile, Supplier profile, etc.


@receiver(post_save, sender=User)
def clean_profile_pictures(sender, instance, **kwargs):
    """
    Signal handler to clean up old profile pictures when a user updates their profile picture.
    """
    if instance.profile_picture and hasattr(instance, '_prior_profile_picture'):
        prior_path = instance._prior_profile_picture
        if prior_path and prior_path != instance.profile_picture.path:
            # Delete the old profile picture if it exists and is different
            if os.path.isfile(prior_path):
                os.remove(prior_path)
