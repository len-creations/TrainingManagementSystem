from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from .models import Profile
 

# @receiver(post_save, sender=User)
# def update_profile_email(sender, instance, created, **kwargs):
#     if created:
#         Profile.objects.get_or_create(user=instance, email=instance.email)
#     else:
#         profile = Profile.objects.get(user=instance)
#         profile.email = instance.email  # Update profile's email to match user's email
#         profile.save()
User = get_user_model()
@receiver(post_save, sender=User)
def update_profile_email(sender, instance, created, **kwargs):
    if created:
        Profile.objects.get_or_create(user=instance, defaults={'email': instance.email})
    else:
        Profile.objects.filter(user=instance).update(email=instance.email)