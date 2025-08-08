# tasks/signals.py
from django.db.models.signals import post_save, m2m_changed
from django.dispatch import receiver
from django.contrib.auth.models import User, Group
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.urls import reverse
from django.conf import settings
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes


from .models import Event

# Send activation email when user is created and inactive
@receiver(post_save, sender=User)
def send_activation_email(sender, instance, created, **kwargs):
    # Only send if created and not active (so we can create admin active users manually)
    if created and not instance.is_active:
        token = default_token_generator.make_token(instance)
        uid = urlsafe_base64_encode(force_bytes(instance.pk))
        activation_link = settings.SITE_URL + reverse('activate_account', kwargs={'uidb64': uid, 'token': token})
        subject = 'Activate Your Account'
        message = f'Hi {instance.username},\n\nPlease activate your account by clicking the link below:\n{activation_link}\n\nIf you did not register, ignore this email.'
        from_email = settings.DEFAULT_FROM_EMAIL
        recipient_list = [instance.email] if instance.email else []
        if recipient_list:
            send_mail(subject, message, from_email, recipient_list)

# Send confirmation email when user RSVPs (m2m on Event.participant)
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
                    f'Date: {instance.date}\nLocation: {instance.location}\n\nThanks!'
                )
                send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [user.email])
