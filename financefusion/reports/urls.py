# financefusion/reports/urls.py
from django.urls import path
from .views import FinancialReportView, FinancialReportDownloadView

urlpatterns = [
    path('financial-report/', FinancialReportView.as_view(), name='financial-report'),
    path('download/', FinancialReportDownloadView.as_view(), name='financial-report-download'),  # Updated endpoint
]