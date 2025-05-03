from django.db import models
from django.conf import settings

class Expense(models.Model):
    CATEGORY_CHOICES = [
        ('groceries', 'Groceries'),
        ('entertainment', 'Entertainment'),
        ('utilities', 'Utilities'),
        ('transport', 'Transport'),
        ('food', 'Food'),
        ('shopping', 'Shopping'),
        ('bills', 'Bills'),
        ('other', 'Other'),
    ]

    PAYMENT_METHOD_CHOICES = [
        ('cash', 'Cash'),
        ('card', 'Card'),
        ('upi', 'UPI'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default='other')
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES, default='cash')
    date = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.amount} ({self.category})"

    def save(self, *args, **kwargs):
        # Convert category and payment method to correct format
        valid_categories = dict(self.CATEGORY_CHOICES)
        valid_payment_methods = dict(self.PAYMENT_METHOD_CHOICES)

        # Convert if needed
        for key, value in valid_categories.items():
            if self.category.lower() == value.lower():
                self.category = key
                break
        
        for key, value in valid_payment_methods.items():
            if self.payment_method.lower() == value.lower():
                self.payment_method = key
                break

        super().save(*args, **kwargs)
