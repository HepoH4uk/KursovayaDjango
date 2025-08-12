from django.core.mail import send_mail
from django.core.management.base import BaseCommand
from django.utils import timezone

from config import settings
from messaging.models import Mailing



class Command(BaseCommand):
    help = "Send scheduled messages"

    def handle(self, *args, **options):
        now = timezone.now()

        mailings = Mailing.objects.filter(
            start_time__lte=now, status=Mailing.CREATED, is_active=True
        ).exclude(end_time__lt=now)


        for mailing in mailings:
                mailing.status = Mailing.STARTED
                mailing.save()
                message = mailing.message
                clients = mailing.clients.all()

                for client in clients:
                    try:
                        send_mail(
                            subject=message.subject,
                            message=message.body,
                            from_email=settings.DEFAULT_FROM_EMAIL,
                            recipient_list=[client.email],
                        )

                    except Exception as e:
                        print(f"Ошибка при отправке клиенту {client.email}: {str(e)}")
                        continue

                mailing.status = "FINISHED"
                mailing.save()

