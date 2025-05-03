from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.budget_dashboard, name='budget_dashboard'),
    path('create/', views.create_budget, name='create_budget'),
    path('update/<int:category_id>/', views.update_spending, name='update_spending'),
]
