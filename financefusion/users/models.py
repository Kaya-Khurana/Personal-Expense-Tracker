from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=15, blank=True, null=True)
    dob = models.DateField(blank=True, null=True)
    USERNAME_FIELD = "email"  # Set email as the login field
    REQUIRED_FIELDS = ["username"]  
    

    def __str__(self):
        return self.email
