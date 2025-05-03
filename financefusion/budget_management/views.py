from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import BudgetCategory
from django.core.mail import send_mail
from django.conf import settings
from decimal import Decimal 

@login_required
def budget_dashboard(request):
    categories = BudgetCategory.objects.filter(user=request.user)
    return render(request, 'budget_management/dashboard.html', {'categories': categories})


@login_required
def create_budget(request):
    if request.method == "POST":
        name = request.POST['name']
        limit = request.POST['limit']

        BudgetCategory.objects.create(user=request.user, name=name, limit=limit)
        messages.success(request, "Budget category added successfully!")
        return redirect('budget_dashboard')

    return render(request, 'budget_management/create_budget.html')

@login_required
def update_spending(request, category_id):
    category = BudgetCategory.objects.get(id=category_id, user=request.user)
    
    if request.method == "POST":
        amount = Decimal(request.POST['amount'])
        category.spent += amount
        category.save()

        # Trigger alert if necessary
        if category.spent >= category.limit * Decimal('0.9'):  # 90% spent
            send_budget_alert(request.user.email, category.name, category.spent, category.limit)

        messages.success(request, f"Spending updated for {category.name}.")
        return redirect('budget_dashboard')

    return render(request, 'budget_management/update_spending.html', {'category': category})

def send_budget_alert(email, category_name, spent, limit):
    subject = f"Budget Alert: {category_name}"
    message = f"Warning! You've spent {spent}/{limit} in {category_name}. Consider adjusting your budget."
    send_mail(subject, message, settings.EMAIL_HOST_USER, [email])
