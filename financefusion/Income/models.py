# incomes/models.py
from django.db import models
from django.conf import settings

class Income(models.Model):
    CATEGORY_CHOICES = [
        ('salary', 'Salary'),
        ('freelance', 'Freelance'),
        ('investment', 'Investment'),
        ('other', 'Other'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default='other')
    date = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.amount} ({self.category})"

    def save(self, *args, **kwargs):
        valid_categories = dict(self.CATEGORY_CHOICES)
        for key, value in valid_categories.items():
            if self.category.lower() == value.lower():
                self.category = key
                break
        super().save(*args, **kwargs)