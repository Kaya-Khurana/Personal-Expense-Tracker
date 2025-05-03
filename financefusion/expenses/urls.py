from django.urls import path
from .views import ExpenseListCreateView, ExpenseUpdateView, ExpenseDeleteView
from .views import get_expense_choices


urlpatterns = [
    path('expenses/',ExpenseListCreateView.as_view(), name='expense-list-create'),
    path('', ExpenseListCreateView.as_view(), name='expense-list'),
    path('expenses/update/<int:pk>/', ExpenseUpdateView.as_view(), name='expense-update'),
    path('expenses/delete/<int:pk>/', ExpenseDeleteView.as_view(), name='expense-delete'),
    path('choices/', get_expense_choices, name='expense-choices'),
]
