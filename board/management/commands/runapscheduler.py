import logging
from django.conf import settings
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
from django.core.management.base import BaseCommand
from django_apscheduler.jobstores import DjangoJobStore
from django_apscheduler.models import DjangoJobExecution
from django.template.loader import render_to_string
from django.core.mail.message import EmailMultiAlternatives
from datetime import datetime, timedelta
from news.models import Message


DEFAULT_FROM_EMAIL = settings.DEFAULT_FROM_EMAIL
logger = logging.getLogger(__name__)


def my_job():
    #time_now = datetime.today()
    time_now = datetime.now().date()
    time_week_before = time_now + timedelta(days=-7)
    messages_in_week = Message.objects.filter(messageDateTime__date__gte=time_week_before)
    usrs_mails = []
    for usr in User.objects.all():
        usrs_mails.append(usr.email)
    mail_weekly_html = render_to_string(
        template_name='board/email/mail_weekly.html',
        context={"messages_in_week": messages_in_week,}
        )
    msg = EmailMultiAlternatives(
        subject='New publications by last 7 days',
        body='',
        from_email=DEFAULT_FROM_EMAIL,
        to=usrs_mails
    )
    msg.attach_alternative( mail_weekly_html, 'text/html')
    msg.send()


# функция которая будет удалять неактуальные задачи
def delete_old_job_executions(max_age=604_800):
    """This job deletes all apscheduler job executions older than `max_age` from the database."""
    DjangoJobExecution.objects.delete_old_job_executions(max_age)


class Command(BaseCommand):
    help = "Runs apscheduler."

    def handle(self, *args, **options):
        scheduler = BlockingScheduler(timezone=settings.TIME_ZONE)
        scheduler.add_jobstore(DjangoJobStore(), "default")


        scheduler.add_job(
            my_job,
            trigger=CronTrigger( day_of_week="mon", hour="00", minute="00"),  #second="*/10"),
            id="my_job",  # уникальный айди
            max_instances=1,
            replace_existing=True,
        )
        logger.info("Added job 'my_job'.")

        scheduler.add_job(
            delete_old_job_executions,
            trigger=CronTrigger(day_of_week="mon", hour="00", minute="00"),
            # Каждую неделю будут удаляться старые задачи, которые либо не удалось выполнить, либо уже выполнять не надо.
            id="delete_old_job_executions",
            max_instances=1,
            replace_existing=True,
        )
        logger.info(
            "Added weekly job: 'delete_old_job_executions'."
        )

        try:
            logger.info("Starting scheduler...")
            scheduler.start()
        except KeyboardInterrupt:
            logger.info("Stopping scheduler...")
            scheduler.shutdown()
            logger.info("Scheduler shut down successfully!")
