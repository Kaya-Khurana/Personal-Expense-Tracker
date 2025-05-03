from django.urls import path
from users.views import Register, login_user, Logout

urlpatterns = [
    path('register/', Register.as_view(), name='register'),
    path('login/', login_user, name='login'),
    path('login/', login_user, name='login'),
    path('logout/', Logout.as_view(), name='logout'),
]
