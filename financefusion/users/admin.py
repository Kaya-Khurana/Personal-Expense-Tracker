from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth import get_user_model
from .models import CustomUser

admin.site.register(CustomUser)
User = get_user_model()

# Unregister default User model if it was already registered
try:
    admin.site.unregister(User)
except admin.sites.NotRegistered:
    pass

# Register custom User model
@admin.register(User)
class CustomUserAdmin(UserAdmin):
    pass
