# financefusion/milestones/urls.py
from django.urls import path
from .views import MilestoneListCreateView, MilestoneUpdateView, MilestoneDeleteView, update_milestone_progress

urlpatterns = [
    path('', MilestoneListCreateView.as_view(), name='milestone-list-create'),
    path('update/<int:pk>/', MilestoneUpdateView.as_view(), name='milestone-update'),
    path('delete/<int:pk>/', MilestoneDeleteView.as_view(), name='milestone-delete'),
    path('progress/<int:pk>/', update_milestone_progress, name='milestone-progress'),
]