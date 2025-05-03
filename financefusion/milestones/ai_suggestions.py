from expenses.models import Expense
from django.db.models import Sum
from datetime import datetime, timedelta
import decimal
from django.contrib.auth import get_user_model  # Add this import

User = get_user_model()

def get_milestone_suggestions(user_id, milestone):
    suggestions = []
    # Fetch the User object using the user_id
    user = User.objects.get(id=user_id)
    remaining_amount = milestone.target_amount - milestone.current_amount
    days_left = milestone.days_until_deadline()

    if days_left <= 0:
        suggestions.append("Your milestone is overdue! Consider extending the deadline or increasing your savings rate.")
        return suggestions

    # Calculate required monthly savings
    days_per_month = decimal.Decimal(str(days_left)) / decimal.Decimal('30')
    monthly_savings_needed = remaining_amount / days_per_month

    # Analyze recent expenses (last 30 days)
    one_month_ago = datetime.now().date() - timedelta(days=30)
    recent_expenses = Expense.objects.filter(user=user, date__gte=one_month_ago)
    category_spending = recent_expenses.values('category').annotate(total=Sum('amount')).order_by('-total')

    # Suggestion 1: Highlight high-spending categories
    if category_spending:
        top_category = category_spending[0]
        suggestions.append(
            f"You spent {top_category['total']} on {top_category['category']} in the last 30 days. "
            f"Reducing spending in this category could help you save more for your milestone."
        )

    # Suggestion 2: Recommend monthly savings
    suggestions.append(
        f"To reach your milestone, you need to save {monthly_savings_needed:.2f} per month. "
        f"Try setting aside this amount from your budget."
    )

    # Suggestion 3: Adjust deadline if savings rate is too high
    if monthly_savings_needed > 1000:  # Arbitrary threshold, adjust as needed
        suggested_months = remaining_amount / decimal.Decimal('1000')
        suggested_days = suggested_months * decimal.Decimal('30')
        new_deadline = datetime.now().date() + timedelta(days=int(suggested_days))
        suggestions.append(
            f"Saving {monthly_savings_needed:.2f}/month might be challenging. "
            f"Consider extending your deadline to {new_deadline.strftime('%Y-%m-%d')}."
        )

    return suggestions