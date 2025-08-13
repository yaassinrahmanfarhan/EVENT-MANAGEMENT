from django.db.models.signals import post_save, m2m_changed
from django.dispatch import receiver
from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.urls import reverse
from django.conf import settings
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes

from .models import Event, UserProfile

# Activation email when user created (inactive)
@receiver(post_save, sender=User)
def send_activation_email(sender, instance, created, **kwargs):
    if created and not instance.is_active and instance.email:
        token = default_token_generator.make_token(instance)
        activation_link = settings.SITE_URL + reverse('activate_account', kwargs={'user_id': instance.id, 'token': token})
        subject = 'Activate Your Account'
        message = f'Hi {instance.username},\n\nPlease activate your account by clicking the link below:\n{activation_link}\n\nIf you did not register, please ignore this email.'
        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [instance.email])

# RSVP confirmation email when user added to event participants
@receiver(m2m_changed, sender=Event.participant.through)
def send_rsvp_confirmation_email(sender, instance, action, pk_set, **kwargs):
    if action == "post_add":
        users = User.objects.filter(pk__in=pk_set)
        for user in users:
            if user.email:
                subject = f'RSVP Confirmation for {instance.name}'
                message = (
                    f'Hi {user.get_full_name() or user.username},\n\n'
                    f'You have successfully RSVP’d to the event: {instance.name}.\n'
                    f'Date: {instance.date}\nLocation: {instance.location}\n\nThank you!'
                )
                send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [user.email])


@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)