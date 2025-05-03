# financefusion/reports/views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from expenses.models import Expense
from expenses.serializers import ExpenseSerializer
import pandas as pd
from io import BytesIO
import pdfkit  # Requires wkhtmltopdf installed on your system
import json
import logging

# Set up logging
logger = logging.getLogger(__name__)

class FinancialReportView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        logger.info("FinancialReportView accessed")
        logger.info(f"Query params: {request.query_params}")
        
        # Extract query parameters
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        categories = request.query_params.get('categories')
        payment_methods = request.query_params.get('payment_methods')

        # Handle categories and payment_methods safely
        try:
            if categories:
                # If categories is a string, try to parse it
                if isinstance(categories, str):
                    # Remove URL encoding artifacts and parse
                    if categories.startswith('[') and categories.endswith(']'):
                        try:
                            categories = json.loads(categories)
                        except json.JSONDecodeError:
                            # If JSON parsing fails, treat it as a comma-separated string
                            categories = categories.strip('[]').replace('"', '').split(',')
                            categories = [cat.strip() for cat in categories if cat.strip()]
                    else:
                        categories = [categories]
                # Ensure categories is a list
                if not isinstance(categories, list):
                    return Response({"error": "Categories must be a list"}, status=status.HTTP_400_BAD_REQUEST)
            else:
                categories = None

            if payment_methods:
                if isinstance(payment_methods, str):
                    if payment_methods.startswith('[') and payment_methods.endswith(']'):
                        try:
                            payment_methods = json.loads(payment_methods)
                        except json.JSONDecodeError:
                            payment_methods = payment_methods.strip('[]').replace('"', '').split(',')
                            payment_methods = [pm.strip() for pm in payment_methods if pm.strip()]
                    else:
                        payment_methods = [payment_methods]
                if not isinstance(payment_methods, list):
                    return Response({"error": "Payment methods must be a list"}, status=status.HTTP_400_BAD_REQUEST)
            else:
                payment_methods = None
        except Exception as e:
            logger.error(f"Error processing filters: {str(e)}")
            return Response({"error": f"Error processing filters: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)

        # Validate date range
        if not start_date or not end_date:
            return Response({"error": "Start date and end date are required"}, status=status.HTTP_400_BAD_REQUEST)

        # Fetch expenses
        expenses = Expense.objects.filter(
            user=request.user,
            date__range=[start_date, end_date]
        )
        if categories:
            expenses = expenses.filter(category__in=categories)
        if payment_methods:
            expenses = expenses.filter(payment_method__in=payment_methods)

        serializer = ExpenseSerializer(expenses, many=True)
        expense_data = serializer.data

        # Prepare expense breakdown
        expense_breakdown = []
        for exp in expense_data:
            expense_breakdown.append({
                'category': exp['category'],
                'category_display': exp['category_display'],
                'payment_method': exp['payment_method'],
                'payment_method_display': exp['payment_method_display'],
                'total': float(exp['amount'])
            })

        total_expenses = sum(float(exp['amount']) for exp in expense_data)
        financial_health = {'total_expenses': total_expenses}

        # Comparative analysis
        previous_expenses = Expense.objects.filter(
            user=request.user,
            date__lt=start_date
        )
        previous_total = sum(float(exp['amount']) for exp in ExpenseSerializer(previous_expenses, many=True).data)

        comparative_analysis = {
            'current_period': {'expenses': total_expenses, 'income': 0},
            'previous_period': {'expenses': previous_total, 'income': 0}
        }

        return Response({
            'expense_breakdown': expense_breakdown,
            'financial_health': financial_health,
            'comparative_analysis': comparative_analysis
        }, status=status.HTTP_200_OK)

class FinancialReportDownloadView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        logger.info("FinancialReportDownloadView accessed")
        logger.info(f"Query params: {request.query_params}")
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        total_income = float(request.query_params.get('total_income', 0))
        categories = request.query_params.get('categories')
        payment_methods = request.query_params.get('payment_methods')
        format_type = request.query_params.get('format')

        # Handle categories and payment_methods safely
        try:
            if categories:
                if isinstance(categories, str):
                    if categories.startswith('[') and categories.endswith(']'):
                        try:
                            categories = json.loads(categories)
                        except json.JSONDecodeError:
                            categories = categories.strip('[]').replace('"', '').split(',')
                            categories = [cat.strip() for cat in categories if cat.strip()]
                    else:
                        categories = [categories]
                if not isinstance(categories, list):
                    return Response({"error": "Categories must be a list"}, status=status.HTTP_400_BAD_REQUEST)
            else:
                categories = None

            if payment_methods:
                if isinstance(payment_methods, str):
                    if payment_methods.startswith('[') and payment_methods.endswith(']'):
                        try:
                            payment_methods = json.loads(payment_methods)
                        except json.JSONDecodeError:
                            payment_methods = payment_methods.strip('[]').replace('"', '').split(',')
                            payment_methods = [pm.strip() for pm in payment_methods if pm.strip()]
                    else:
                        payment_methods = [payment_methods]
                if not isinstance(payment_methods, list):
                    return Response({"error": "Payment methods must be a list"}, status=status.HTTP_400_BAD_REQUEST)
            else:
                payment_methods = None
        except Exception as e:
            logger.error(f"Error processing filters: {str(e)}")
            return Response({"error": f"Error processing filters: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)

        # Validate date range
        if not start_date or not end_date:
            return Response({"error": "Start date and end date are required"}, status=status.HTTP_400_BAD_REQUEST)

        # Fetch expenses
        expenses = Expense.objects.filter(
            user=request.user,
            date__range=[start_date, end_date]
        )
        if categories:
            expenses = expenses.filter(category__in=categories)
        if payment_methods:
            expenses = expenses.filter(payment_method__in=payment_methods)

        serializer = ExpenseSerializer(expenses, many=True)
        expense_data = serializer.data

        # Prepare data for download
        df = pd.DataFrame(expense_data)
        if df.empty:
            df = pd.DataFrame(columns=['id', 'amount', 'category', 'payment_method', 'date'])

        total_expenses = sum(float(exp['amount']) for exp in expense_data)
        net_cash_flow = total_income - total_expenses

        if format_type == 'csv':
            csv_buffer = BytesIO()
            df.to_csv(csv_buffer, index=False)
            csv_buffer.seek(0)
            return Response(
                csv_buffer.getvalue(),
                headers={
                    'Content-Disposition': f'attachment; filename=financial_report_{start_date}_to_{end_date}.csv',
                    'Content-Type': 'text/csv'
                },
                status=status.HTTP_200_OK
            )

        elif format_type == 'pdf':
            # Simple HTML template for PDF
            html_content = f"""
            <html>
            <body>
                <h1>Financial Report: {start_date} to {end_date}</h1>
                <h2>Summary</h2>
                <p>Total Income: ₹{total_income:.2f}</p>
                <p>Total Expenses: ₹{total_expenses:.2f}</p>
                <p>Net Cash Flow: ₹{net_cash_flow:.2f}</p>
                <h2>Expense Breakdown</h2>
                {df.to_html(index=False)}
            </body>
            </html>
            """
            pdf_buffer = BytesIO()
            pdfkit.from_string(html_content, pdf_buffer)
            pdf_buffer.seek(0)
            return Response(
                pdf_buffer.getvalue(),
                headers={
                    'Content-Disposition': f'attachment; filename=financial_report_{start_date}_to_{end_date}.pdf',
                    'Content-Type': 'application/pdf'
                },
                status=status.HTTP_200_OK
            )

        return Response({"error": "Invalid format specified"}, status=status.HTTP_400_BAD_REQUEST)