from django.db import models
from django.conf import settings
from users.models import CustomUser 

class BudgetCategory(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True,blank=True)
    name = models.CharField(max_length=255)
    limit = models.DecimalField(max_digits=10, decimal_places=2)
    spent = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    budget_type = models.CharField(
        max_length=10,
        choices=[("monthly", "Monthly"), ("yearly", "Yearly")],
        default="monthly",
    )

    def remaining_budget(self):
        return self.limit - self.spent

    def percentage_spent(self):
        return (self.spent / self.limit) * 100 if self.limit else 0

    def __str__(self):
        return self.name
