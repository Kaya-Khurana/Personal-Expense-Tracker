import pandas as pd
import numpy as np
from .models import Expense

def analyze_spending(user):
    """
    Analyze user’s spending history and provide AI-based saving suggestions.
    """
    expenses = Expense.objects.filter(user=user).values("amount", "category", "date")

    if not expenses:
        return {"message": "No spending data available to analyze."}

    df = pd.DataFrame(expenses)
    df["date"] = pd.to_datetime(df["date"])

    # Calculate total spending per category
    category_totals = df.groupby("category")["amount"].sum().to_dict()

    # Identify top spending category
    top_category = max(category_totals, key=category_totals.get)

    # AI Suggestions based on spending patterns
    suggestions = {
        "food": "Try meal prepping at home to reduce dining-out expenses.",
        "entertainment": "Consider free entertainment options like parks or local community events.",
        "transport": "Use public transportation or carpooling to save money.",
        "utilities": "Switch to energy-efficient appliances to lower bills.",
        "other": "Review discretionary spending to identify unnecessary costs."
    }

    return {
        "top_spending_category": top_category,
        "total_spent": category_totals[top_category],
        "suggestion": suggestions.get(top_category, "Consider tracking your discretionary spending.")
    }
