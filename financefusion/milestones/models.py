from django.db import models
from django.conf import settings
from django.utils import timezone

class Milestone(models.Model):
    TYPE_CHOICES = [
        ('savings', 'Savings'),
        ('debt_reduction', 'Debt Reduction'),
    ]

    STATUS_CHOICES = [
        ('ongoing', 'Ongoing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    milestone_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='savings')
    target_amount = models.DecimalField(max_digits=10, decimal_places=2)
    current_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    deadline = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='ongoing')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} - {self.title} ({self.milestone_type})"

    def progress_percentage(self):
        if self.target_amount > 0:
            return (self.current_amount / self.target_amount) * 100
        return 0

    def days_until_deadline(self):
        return (self.deadline - timezone.now().date()).days

    def is_overdue(self):
        return self.days_until_deadline() < 0 and self.status == 'ongoing'