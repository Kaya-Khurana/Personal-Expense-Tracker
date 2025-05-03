from celery import shared_task
from django.core.mail import send_mail
from django.contrib.auth.models import User

@shared_task
def send_budget_reminders():
    users = User.objects.all()
    for user in users:
        send_mail(
            "Weekly Budget Reminder",
            "Reminder: Stick to your budget for better financial management!",
            "kayakhurana2106@gmail.com",
            [user.email],
        )
