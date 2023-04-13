from django.db.models.signals import post_save  # m2m_changed
from django.dispatch import receiver  # decorator for signals
from django.template.loader import render_to_string
from django.core.mail.message import EmailMultiAlternatives
from django.conf import settings
from datetime import datetime
from .models import Post

DEFAULT_FROM_EMAIL = settings.DEFAULT_FROM_EMAIL


@receiver(post_save, sender=Post)
def notify_about_new_post(sender, instance, created, **kwargs):
    if created:
        email_subject = f'Отклик "{instance.postText[:12]}..." was submitted at {instance.postDateTime.strftime("%b %d %Y %H:%M:%S")}'
        email_html_body = render_to_string(
            template_name='board/email/post_created.html',
            context={
                'post_name': instance.postText[:12],
                "post_create_date": instance.postDateTime.strftime("%b %d %Y %H:%M:%S"),
            }
        )
        msg = EmailMultiAlternatives(
            subject=email_subject,
            body='',
            from_email=DEFAULT_FROM_EMAIL,
            to=[instance.postToMessage.author.email, ]
        )
    else:
        email_subject = f'{instance.postText[:12]}... was approved at {datetime.now().strftime("%b %d %Y %H:%M:%S")}'
        email_html_body = render_to_string(
            template_name='board/email/post_approved.html',
            context={
                'post_name': instance.postText[:12],
                "post_approve_date": instance.postDateTime.strftime("%b %d %Y %H:%M:%S"),
            }
        )
        msg = EmailMultiAlternatives(
            subject=email_subject,
            body='',
            from_email=DEFAULT_FROM_EMAIL,
            to=[instance.postAuthor.email, ]
        )
    msg.attach_alternative(email_html_body, 'text/html')
    msg.send()