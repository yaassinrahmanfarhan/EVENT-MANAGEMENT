from django.db.models.signals import post_save, m2m_changed
from django.dispatch import receiver
from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.urls import reverse
from django.conf import settings

from .models import Event


# Signal: Send activation email when user is created (and inactive)
@receiver(post_save, sender=User)
def send_activation_email(sender, instance, created, **kwargs):
    if created and not instance.is_active:
        token = default_token_generator.make_token(instance)
        activation_link = settings.SITE_URL + reverse('activate_account', kwargs={
            'uid': instance.pk,
            'token': token,
        })

        subject = 'Activate Your Account'
        message = f'Hi {instance.username},\n\nPlease activate your account by clicking the link below:\n{activation_link}'
        from_email = settings.DEFAULT_FROM_EMAIL
        recipient_list = [instance.email]

        send_mail(subject, message, from_email, recipient_list)


# Signal: Send confirmation email when user RSVPs to an event
@receiver(m2m_changed, sender=Event.participant.through)
def send_rsvp_confirmation_email(sender, instance, action, pk_set, **kwargs):
    if action == "post_add":
        users = User.objects.filter(pk__in=pk_set)
        for user in users:
            subject = f'RSVP Confirmation for {instance.name}'
            message = f'Hi {user.username},\n\nYou have successfully RSVP’d to the event: {instance.name}.\nDate: {instance.date}\nLocation: {instance.location}\n\nThank you!'
            from_email = settings.DEFAULT_FROM_EMAIL
            recipient_list = [user.email]

            send_mail(subject, message, from_email, recipient_list)
