import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'financefusion.settings')
import django
django.setup()

from django.contrib.auth.models import User
import streamlit as st
from decimal import Decimal 
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import matplotlib.pyplot as plt
from django.http import HttpRequest
from budget_management.models import BudgetCategory  
from users.models import CustomUser
from expenses.models import Expense
from milestones.models import Milestone
from milestones.ai_suggestions import get_milestone_suggestions
from datetime import datetime, timedelta
import io
import json

# Backend API Endpoints
REGISTER_URL = "http://127.0.0.1:8000/api/users/register/"
LOGIN_URL = "http://127.0.0.1:8000/api/users/login/"
API_BASE_URL = "http://127.0.0.1:8000/api/expenses/"
MILESTONE_API_BASE_URL = "http://127.0.0.1:8000/api/milestones/"
REPORT_API_BASE_URL = "http://127.0.0.1:8000/api/reports/financial-report/"

# Initialize session state
if "page" not in st.session_state:
    st.session_state.page = "login"
if "user" not in st.session_state:
    st.session_state.user = None
if "token" not in st.session_state:
    st.session_state.token = None

# Expense Management Functions
def fetch_expenses():
    TOKEN = st.session_state.get("token")
    if not TOKEN:
        st.error("Authentication token missing. Please log in again.")
        st.session_state.page = "login"
        st.rerun()
        return []
    headers = {"Authorization": f"Token {TOKEN}", "Content-Type": "application/json"}
    try:
        response = requests.get(API_BASE_URL, headers=headers)
        if response.status_code == 200:
            expenses = response.json()
            #st.write("Fetch Expenses API Response:", expenses)  # Debug
            return expenses
        else:
            st.error(f"Failed to fetch expenses. Status: {response.status_code}, Error: {response.text}")
            return []
    except requests.exceptions.RequestException as e:
        st.error(f"Unable to connect to the server. Please ensure the backend server is running and try again.")
        return []

def add_expense(amount, category, payment_method):
    TOKEN = st.session_state.get("token")
    if not TOKEN:
        st.error("Authentication token missing. Please log in again.")
        st.session_state.page = "login"
        #st.rerun()
        return False
    headers = {"Authorization": f"Token {TOKEN}", "Content-Type": "application/json"}
    if not st.session_state.user:
        st.error("No user logged in. Please log in first.")
        return False
    user_id = st.session_state.user["id"]
    data = {
        "amount": amount,
        "category": category.lower(),
        "payment_method": payment_method.lower(),
        "user": user_id
    }
    try:
        response = requests.post(API_BASE_URL, json=data, headers=headers)
        if response.status_code == 201:
            return True
        else:
            st.error(f"Failed to add expense. Status: {response.status_code}, Error: {response.text}")
            return False
    except requests.exceptions.RequestException as e:
        st.error(f"Unable to connect to the server. Please ensure the backend server is running and try again.")
        return False

def update_expense(expense_id, amount, category, payment_method):
    TOKEN = st.session_state.get("token")
    if not TOKEN:
        st.error("Authentication token missing. Please log in again.")
        st.session_state.page = "login"
        #st.rerun()
        return False
    headers = {"Authorization": f"Token {TOKEN}", "Content-Type": "application/json"}
    url = f"{API_BASE_URL}expenses/update/{expense_id}/"
    data = {
        "amount": amount,
        "category": category.lower(),
        "payment_method": payment_method.lower(),
        "user": st.session_state.user["id"]
    }
    
    try:
        response = requests.put(url, json=data, headers=headers)
        if response.status_code == 200:
            return True
        else:
            st.error(f"Failed to update expense. Status: {response.status_code}, Error: {response.text}")
            return False
    except requests.exceptions.RequestException as e:
        st.error(f"Unable to connect to the server. Please ensure the backend server is running and try again.")
        return False

def delete_expense(expense_id):
    TOKEN = st.session_state.get("token")
    if not TOKEN:
        st.error("Authentication token missing. Please log in again.")
        st.session_state.page = "login"
        st.rerun()
        return False
    headers = {"Authorization": f"Token {TOKEN}", "Content-Type": "application/json"}
    url = f"{API_BASE_URL}expenses/delete/{expense_id}/"
    
    try:
        response = requests.delete(url, headers=headers)
        if response.status_code == 204:
            return True
        else:
            st.error(f"Failed to delete expense. Status: {response.status_code}, Error: {response.text}")
            return False
    except requests.exceptions.RequestException as e:
        st.error(f"Unable to connect to the server. Please ensure the backend server is running and try again.")
        return False

# Milestone Tracker Function
def milestone_tracker():
    st.title("🎯 Financial Milestone Tracker")
    if not st.session_state.user:
        st.error("🚫 No user logged in. Please log in first.")
        return

    user = st.session_state.user
    user_id = user['id']
    st.write(f"👋 Welcome, {user['username']}!")

    menu = ["Set Milestone", "Track Progress", "Adjust Milestone", "Delete Milestone", "Milestone History"]
    choice = st.sidebar.selectbox("Select Action", menu, key="milestone_action_select")

    TOKEN = st.session_state.get("token")
    if not TOKEN:
        st.error("Authentication token missing. Please log in again.")
        st.session_state.page = "login"
        st.rerun()
        return
    headers = {"Authorization": f"Token {TOKEN}", "Content-Type": "application/json"}

    def fetch_milestones():
        try:
            response = requests.get(MILESTONE_API_BASE_URL, headers=headers)
            if response.status_code == 200:
                return response.json()
            return []
        except requests.exceptions.RequestException as e:
            st.error(f"Unable to connect to the server. Please ensure the backend server is running and try again.")
            return []

    def delete_milestone(milestone_id):
        url = f"{MILESTONE_API_BASE_URL}delete/{milestone_id}/"
        
        try:
            response = requests.delete(url, headers=headers)
            if response.status_code == 204:
                return True
            else:
                st.error(f"Failed to delete milestone. Status: {response.status_code}, Error: {response.text}")
                return False
        except requests.exceptions.RequestException as e:
            st.error(f"Unable to connect to the server. Please ensure the backend server is running and try again.")
            return False

    if choice == "Set Milestone":
        st.subheader("➕ Set a New Financial Milestone")
        title = st.text_input("Milestone Title (e.g., Save for Vacation)")
        milestone_type = st.selectbox("Milestone Type", ["Savings", "Debt Reduction"], key="milestone_type_select")
        target_amount = st.number_input("Target Amount", min_value=0.0, step=100.0)
        deadline = st.date_input("Deadline")
        if st.button("Set Milestone"):
            if title and target_amount > 0 and deadline:
                data = {
                    "title": title,
                    "milestone_type": milestone_type.lower(),
                    "target_amount": target_amount,
                    "deadline": deadline.strftime('%Y-%m-%d'),
                }
                try:
                    response = requests.post(MILESTONE_API_BASE_URL, json=data, headers=headers)
                    if response.status_code == 201:
                        st.success("✅ Milestone set successfully!")
                        
                    else:
                        st.error(f"Failed to set milestone. Status: {response.status_code}, Error: {response.text}")
                except requests.exceptions.RequestException as e:
                    st.error(f"Unable to connect to the server. Please ensure the backend server is running and try again.")
            else:
                st.error("⚠️ Please fill in all fields with valid values.")

    elif choice == "Track Progress":
        st.subheader("📈 Track Milestone Progress")
        milestones = fetch_milestones()
        if milestones:
            df = pd.DataFrame(milestones)
            st.dataframe(df[['title', 'milestone_type', 'target_amount', 'current_amount', 'deadline', 'status', 'progress_percentage']])

            milestone_id = st.selectbox("Select Milestone to Update Progress", df["id"].tolist(), format_func=lambda x: df[df["id"] == x]["title"].values[0], key="milestone_progress_select")
            amount = st.number_input("Amount to Add to Progress", min_value=0.0, step=50.0, format="%.2f")
            if st.button("Update Progress"):
                if amount is not None and amount >= 0:
                    try:
                        response = requests.post(f"{MILESTONE_API_BASE_URL}progress/{milestone_id}/", json={"amount": float(amount)}, headers=headers)
                        if response.status_code == 200:
                            st.success("✅ Progress updated successfully!")
                            
                        else:
                            st.error(f"Failed to update progress. Status: {response.status_code}, Error: {response.text}")
                    except requests.exceptions.RequestException as e:
                        st.error(f"Unable to connect to the server. Please ensure the backend server is running and try again.")
                else:
                    st.error("⚠️ Please enter a valid positive amount.")

            st.subheader("📊 Progress Visualization")
            for milestone in milestones:
                progress = milestone['progress_percentage']
                fig = go.Figure(go.Indicator(
                    mode="gauge+number",
                    value=progress,
                    title={'text': milestone['title']},
                    gauge={'axis': {'range': [0, 100]}, 'bar': {'color': "green" if progress >= 50 else "red"}}
                ))
                st.plotly_chart(fig)

            

        else:
            st.warning("⚠️ No milestones found. Set a milestone above!")

    elif choice == "Adjust Milestone":
        st.subheader("✏️ Adjust Milestone")
        milestones = fetch_milestones()
        if milestones:
            df = pd.DataFrame(milestones)
            with st.form(key="adjust_milestone_form"):
                milestone_id = st.selectbox("Select Milestone to Adjust", df["id"].tolist(), format_func=lambda x: df[df["id"] == x]["title"].values[0], key="milestone_adjust_select")
                selected_milestone = df[df["id"] == milestone_id].iloc[0]
                new_target_amount = st.number_input("New Target Amount", min_value=0.0, value=float(selected_milestone["target_amount"]), step=100.0)
                new_deadline = st.date_input("New Deadline", value=datetime.strptime(selected_milestone["deadline"], '%Y-%m-%d'))
                submit_button = st.form_submit_button("Update Milestone")
                if submit_button:
                    data = {
                        "title": selected_milestone["title"],
                        "target_amount": new_target_amount,
                        "deadline": new_deadline.strftime('%Y-%m-%d'),
                    }
                    try:
                        response = requests.put(f"{MILESTONE_API_BASE_URL}update/{milestone_id}/", json=data, headers=headers)
                        if response.status_code == 200:
                            st.success("✅ Milestone updated successfully!")
                            #st.rerun()
                        else:
                            st.error(f"Failed to update milestone. Status: {response.status_code}, Error: {response.text}")
                    except requests.exceptions.RequestException as e:
                        st.error(f"Unable to connect to the server. Please ensure the backend server is running and try again.")
        else:
            st.warning("⚠️ No milestones available to adjust. Create a new milestone to get started!")
            if st.button("Go to Set Milestone"):
                st.session_state['milestone_action_select'] = "Set Milestone"
                st.rerun()

    elif choice == "Delete Milestone":
        st.subheader("🗑 Delete Milestone")
        milestones = fetch_milestones()
        if milestones:
            df = pd.DataFrame(milestones)
            st.dataframe(df[['id', 'title', 'milestone_type', 'target_amount', 'current_amount', 'deadline', 'status']])
            milestone_id = st.selectbox(
                "Select Milestone to Delete",
                df["id"].tolist(),
                format_func=lambda x: f"{df[df['id'] == x]['title'].values[0]} - {df[df['id'] == x]['target_amount'].values[0]} (Due: {df[df['id'] == x]['deadline'].values[0]})",
                key="delete_milestone_id"
            )
            if st.button("Delete Milestone"):
                success = delete_milestone(milestone_id)
                if success:
                    st.success("✅ Milestone deleted successfully!")
                    #st.rerun()
                else:
                    st.error("❌ Failed to delete milestone.")
        else:
            st.warning("⚠️ No milestones available to delete. Please set a milestone first.")

    elif choice == "Milestone History":
        st.subheader("📜 Milestone History")
        milestones = fetch_milestones()
        if milestones:
            df = pd.DataFrame(milestones)
            history = df[df["status"].isin(["completed", "failed"])]
            if not history.empty:
                st.dataframe(history[['title', 'milestone_type', 'target_amount', 'current_amount', 'deadline', 'status']])
            else:
                st.info("ℹ️ No completed or failed milestones yet.")
        else:
            st.warning("⚠️ No milestones found.")

def report_generator():
    st.title("📊 Custom Financial Report Generator")
    if not st.session_state.user:
        st.error("🚫 No user logged in. Please log in first.")
        return

    user = st.session_state.user
    st.write(f"👋 Welcome, {user['username']}!")

    TOKEN = st.session_state.get("token")
    if not TOKEN:
        st.error("🚫 Authentication token missing. Please log in again.")
        st.session_state.page = "login"
        st.rerun()
        return
    headers = {"Authorization": f"Token {TOKEN}", "Content-Type": "application/json"}

    @st.cache_data
    def fetch_categories_and_filters():
        try:
            response = requests.get(REPORT_API_BASE_URL, headers=headers)
            if response.status_code == 200:
                data = response.json()
                expenses = data.get("expenses", [])
                expense_categories = ['groceries', 'entertainment', 'utilities', 'transport', 'food', 'shopping', 'bills', 'other']
                payment_methods = ['cash', 'card', 'upi']
                expense_category_display = {
                    'groceries': 'Groceries',
                    'entertainment': 'Entertainment',
                    'utilities': 'Utilities',
                    'transport': 'Transport',
                    'food': 'Food',
                    'shopping': 'Shopping',
                    'bills': 'Bills',
                    'other': 'Other'
                }
                payment_method_display = {
                    'cash': 'Cash',
                    'card': 'Card',
                    'upi': 'UPI'
                }
                expense_category_display.update({exp["category"]: exp["category_display"] for exp in expenses})
                payment_method_display.update({exp["payment_method"]: exp["payment_method_display"] for exp in expenses})
                return (
                    expense_categories,
                    payment_methods,
                    expense_category_display,
                    payment_method_display
                )
            else:
                #st.error(f"Failed to fetch categories. Status: {response.status_code}, Error: {response.text}")
                expense_categories = ['groceries', 'entertainment', 'utilities', 'transport', 'food', 'shopping', 'bills', 'other']
                payment_methods = ['cash', 'card', 'upi']
                expense_category_display = {
                    'groceries': 'Groceries',
                    'entertainment': 'Entertainment',
                    'utilities': 'Utilities',
                    'transport': 'Transport',
                    'food': 'Food',
                    'shopping': 'Shopping',
                    'bills': 'Bills',
                    'other': 'Other'
                }
                payment_method_display = {
                    'cash': 'Cash',
                    'card': 'Card',
                    'upi': 'UPI'
                }
                return (
                    expense_categories,
                    payment_methods,
                    expense_category_display,
                    payment_method_display
                )
        except requests.exceptions.RequestException as e:
            st.error(f"Unable to connect to the server to fetch categories. Please ensure the backend server is running and try again.")
            expense_categories = ['groceries', 'entertainment', 'utilities', 'transport', 'food', 'shopping', 'bills', 'other']
            payment_methods = ['cash', 'card', 'upi']
            expense_category_display = {
                'groceries': 'Groceries',
                'entertainment': 'Entertainment',
                'utilities': 'Utilities',
                'transport': 'Transport',
                'food': 'Food',
                'shopping': 'Shopping',
                'bills': 'Bills',
                'other': 'Other'
            }
            payment_method_display = {
                'cash': 'Cash',
                'card': 'Card',
                'upi': 'UPI'
            }
            return (
                expense_categories,
                payment_methods,
                expense_category_display,
                payment_method_display
            )

    (
        expense_categories,
        payment_methods,
        expense_category_display,
        payment_method_display
    ) = fetch_categories_and_filters()

    st.subheader("Generate a Custom Financial Report")
    with st.form(key="report_form"):
        st.write("Select Date Range")
        date_range_option = st.selectbox("Date Range", ["Custom", "Last 7 Days", "Last 30 Days", "Last Year"])
        if date_range_option == "Custom":
            start_date = st.date_input("Start Date", value=datetime.now().date() - timedelta(days=30))
            end_date = st.date_input("End Date", value=datetime.now().date())
        elif date_range_option == "Last 7 Days":
            end_date = datetime.now().date()
            start_date = end_date - timedelta(days=7)
        elif date_range_option == "Last 30 Days":
            end_date = datetime.now().date()
            start_date = end_date - timedelta(days=30)
        else:
            end_date = datetime.now().date()
            start_date = end_date - timedelta(days=365)

        st.write("Enter Your Income")
        user_income = st.number_input(
            f"Total Income for {start_date} to {end_date} (₹)",
            min_value=0.0,
            value=0.0,
            step=100.0,
            format="%.2f"
        )

        st.write("Apply Filters")
        selected_expense_categories = st.multiselect(
            "Expense Categories",
            options=expense_categories,
            format_func=lambda x: expense_category_display.get(x, x)
        )
        selected_payment_methods = st.multiselect(
            "Payment Methods",
            options=payment_methods,
            format_func=lambda x: payment_method_display.get(x, x)
        )

        submit_button = st.form_submit_button("Generate Report")

    if submit_button:
        params = {
            "start_date": start_date.strftime('%Y-%m-%d'),
            "end_date": end_date.strftime('%Y-%m-%d'),
            "total_income": user_income,
        }
        if selected_expense_categories:
            params["categories"] = json.dumps(selected_expense_categories)
        if selected_payment_methods:
            params["payment_methods"] = json.dumps(selected_payment_methods)

        

        with st.spinner("Generating report..."):
            try:
                response = requests.get(REPORT_API_BASE_URL, headers=headers, params=params)
                
                if response.status_code == 200:
                    report_data = response.json()
                else:
                    st.error(f"Failed to fetch report data. Status: {response.status_code}, Error: {response.text}")
                    return
            except requests.exceptions.RequestException as e:
                st.error(f"Unable to connect to the server. Please ensure the backend server is running on http://127.0.0.1:8000 and try again.")
                return
            except ValueError as e:
                st.error(f"Failed to parse response as JSON: {e}")
                return

        st.subheader(f"Financial Report: {start_date} to {end_date}")

        st.write("### Expense Breakdown")
        expense_breakdown = pd.DataFrame(report_data["expense_breakdown"])
        if not expense_breakdown.empty:
            expense_breakdown_display = expense_breakdown.copy()
            expense_breakdown_display['category'] = expense_breakdown_display['category_display']
            expense_breakdown_display['payment_method'] = expense_breakdown_display['payment_method_display']
            st.dataframe(expense_breakdown_display[['category', 'payment_method', 'total']])
            fig_expense = px.pie(
                expense_breakdown,
                names='category_display',
                values='total',
                title="Expense Breakdown by Category"
            )
            st.plotly_chart(fig_expense)
            fig_payment = px.bar(
                expense_breakdown,
                x='total',
                y='payment_method_display',
                color='category_display',
                title="Expenses by Payment Method"
            )
            st.plotly_chart(fig_payment)
        else:
            st.write("No expenses found for the selected criteria.")

        st.write("### Financial Health Insights")
        financial_health = report_data["financial_health"]
        financial_health['total_income'] = user_income
        financial_health['net_cash_flow'] = financial_health['total_income'] - financial_health['total_expenses']
        financial_health['savings_rate'] = (financial_health['net_cash_flow'] / financial_health['total_income'] * 100) if financial_health['total_income'] > 0 else 0

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Income", f"₹{financial_health['total_income']:.2f}")
        with col2:
            st.metric("Total Expenses", f"₹{financial_health['total_expenses']:.2f}")
        with col3:
            st.metric("Net Cash Flow", f"₹{financial_health['net_cash_flow']:.2f}")
        st.write(f"**Savings Rate:** {financial_health['savings_rate']:.2f}%")

        st.write("### Comparative Analysis")
        comparative = report_data["comparative_analysis"]
        comparative["current_period"]["income"] = user_income
        comparison_df = pd.DataFrame({
            "Period": ["Current", "Previous"],
            "Income": [comparative["current_period"]["income"], comparative["previous_period"]["income"]],
            "Expenses": [comparative["current_period"]["expenses"], comparative["previous_period"]["expenses"]],
        })
        st.dataframe(comparison_df)
        fig_comparison = go.Figure()
        fig_comparison.add_trace(go.Bar(x=comparison_df["Income"], y=comparison_df["Period"], name="Income", orientation='h'))
        fig_comparison.add_trace(go.Bar(x=comparison_df["Expenses"], y=comparison_df["Period"], name="Expenses", orientation='h'))
        fig_comparison.update_layout(title="Income vs. Expenses: Current vs. Previous Period", barmode='group')
        st.plotly_chart(fig_comparison)

# Home Page Function
def home_page():
    st.title("🏠 Home - FinanceFusion")
    if st.session_state.user:
        user = st.session_state.user
        st.subheader(f"Welcome, {user['username']}! 👋")
        st.write(f"📧 Email: {user['email']}")
        st.sidebar.title("🔹 Navigation")
        menu = ["Expense Register", "Budget Management", "Milestone Tracker", "Reports", "Logout"]
        choice = st.sidebar.radio("Go to", menu)
        if choice == "Expense Register":
            expense_dashboard()
        elif choice == "Budget Management":
            budget_mng()
        elif choice == "Milestone Tracker":
            milestone_tracker()
        elif choice == "Reports":
            report_generator()
        elif choice == "Logout":
            st.session_state.user = None
            st.session_state.token = None
            st.session_state.page = "login"
            st.rerun()
    else:
        st.warning("You are not logged in. Redirecting to login page...")
        st.session_state.page = "login"
        st.rerun()

# Login and Registration Functions
def login_page():
    st.title("🔐 User Login")
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        response = requests.post(LOGIN_URL, json={"email": email, "password": password})
        if response.status_code == 200:
            data = response.json()
            st.session_state.user = data["user"]
            st.session_state.token = data["token"]
            st.success("Login successful! Redirecting to Home Page...")
            st.session_state.page = "home"
            st.rerun()
        else:
            st.error(f"Error: {response.json().get('error', 'Login failed')}")
            st.write(f"Status Code: {response.status_code}, Response: {response.text}")
    if st.button("New User? Register Here!"):
        st.session_state.page = "register"
        st.rerun()

def register_page():
    st.title("📝 User Registration")
    username = st.text_input("Full Name")
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")
    confirm_password = st.text_input("Confirm Password", type="password")
    phone = st.text_input("Phone Number")
    dob = st.date_input("Date of Birth")
    if st.button("Register"):
        payload = {
            "username": username,
            "email": email,
            "password": password,
            "confirm_password": confirm_password,
            "phone": phone,
            "dob": str(dob)
        }
        try:
            response = requests.post(REGISTER_URL, json=payload)
            if response.status_code == 201:
                st.success("User registered successfully! Please log in.")
                st.session_state.page = "login"
            else:
                st.error(f"Error: {response.json()}")
        except requests.exceptions.RequestException as e:
            st.error(f"Unable to connect to the server. Please ensure the backend server is running and try again.")
    st.write("---")
    if st.button("Already have an account? Login here!"):
        st.session_state.page = "login"

# Budget Management Function
def budget_mng():
    st.title("📊 Budget Management Dashboard")
    if st.session_state.user:
        user = st.session_state.user
        st.write(f"👋 Welcome, {user['username']}!")
    else:
        st.error("🚫 No user logged in. Please log in first.")
        return  
    st.subheader("➕ Add Budget Category")
    category_name = st.text_input("Category Name")
    budget_limit = st.number_input("Budget Limit", min_value=0.0, step=100.0)
    budget_type = st.selectbox("Budget Type", ["Monthly", "Yearly"], key="budget_type_select") 
    if st.button("Add Budget"):
        if category_name and budget_limit:
            BudgetCategory.objects.create(
                name=category_name,
                limit=budget_limit,
                spent=0,  
                budget_type=budget_type.lower(),
                user_id=user['id']
            )
            st.success(f"✅ Budget '{category_name}' ({budget_type}) added successfully!")
            st.rerun()
        else:
            st.error("⚠️ Please provide a valid category name and budget limit.")
    budget_data = BudgetCategory.objects.filter(user=user['id'])
    if not budget_data.exists():
        st.warning("⚠️ No budget data found. Add a category above!")
        return  
    df = pd.DataFrame(
        [(b.id, b.name, b.limit, b.spent, b.remaining_budget(), b.budget_type) for b in budget_data],
        columns=["ID", "Category", "Limit", "Spent", "Remaining", "Type"]
    )
    st.subheader("📄 Budget Overview")
    st.dataframe(df.drop(columns=["ID"]))
    st.subheader("📝 Update Budget")
    update_id = st.selectbox("Select a Budget Category", df["ID"], format_func=lambda x: df[df["ID"] == x]["Category"].values[0], key="update_budget_select")
    new_limit = st.number_input("New Budget Limit", min_value=0.0, step=100.0)
    if st.button("Update Budget"):
        budget_item = BudgetCategory.objects.get(id=update_id)
        budget_item.limit = new_limit
        budget_item.save()
        st.success(f"✅ Updated budget for '{budget_item.name}' to {new_limit}!")
        st.rerun()
    st.subheader("💸 Add Spent Money")
    spend_id = st.selectbox("Select a Budget Category to Spend", df["ID"], format_func=lambda x: df[df["ID"] == x]["Category"].values[0], key="spend_budget_select")
    spend_amount = st.number_input("Amount Spent", min_value=0.0, step=50.0)
    if st.button("Log Spending"):
        budget_item = BudgetCategory.objects.get(id=spend_id)
        if spend_amount <= budget_item.remaining_budget():
            budget_item.spent += Decimal(str(spend_amount))
            budget_item.save()
            st.success(f"✅ Spent {spend_amount} on '{budget_item.name}'. Remaining budget: {budget_item.remaining_budget()}!")
            st.rerun()
        else:
            st.error("⚠️ Spending exceeds the remaining budget!")
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.bar(df["Category"], df["Spent"], label="Spent", color="red")
    ax.bar(df["Category"], df["Remaining"], bottom=df["Spent"], label="Remaining", color="green")
    ax.set_ylabel("Amount")
    ax.set_title("Budget Breakdown")
    ax.legend()
    plt.xticks(rotation=45)
    plt.tight_layout()
    st.pyplot(fig)

# Expense Dashboard Function
def expense_dashboard():
    st.title("💰 Expense Register & AI Insights")
    menu = ["Add Expense", "Update Expense", "Delete Expense", "View Expenses", "AI Insights"]
    choice = st.sidebar.selectbox("Select Action", menu, key="expense_action_select")

    if choice == "Add Expense":
        st.subheader("➕ Add Expense")
        amount = st.number_input("Amount", min_value=0.0, format="%.2f")
        category = st.selectbox("Category", ["groceries", "entertainment", "utilities", "transport", "food", "shopping", "bills", "other"], key="add_expense_category")
        payment_method = st.selectbox("Payment Method", ["cash", "card", "upi"], key="add_expense_payment")
        if st.button("Add Expense"):
            success = add_expense(amount, category, payment_method)
            if success:
                st.success("✅ Expense added successfully!")
                

    elif choice == "Update Expense":
        st.subheader("✏️ Update Expense")
        expenses = fetch_expenses()
        if expenses:
            df = pd.DataFrame(expenses)
            if "id" in df.columns:
                st.dataframe(df[['id', 'amount', 'category', 'payment_method', 'date']])
                expense_id = st.selectbox(
                    "Select Expense to Update",
                    df["id"].tolist(),
                    format_func=lambda x: f"{df[df['id'] == x]['category'].values[0]} - {df[df['id'] == x]['amount'].values[0]} on {df[df['id'] == x]['date'].values[0]}",
                    key="update_expense_id"
                )
                selected_expense = df[df["id"] == expense_id].iloc[0]
                new_amount = st.number_input("New Amount", min_value=0.0, value=float(selected_expense["amount"]), format="%.2f")
                category_options = ["groceries", "entertainment", "utilities", "transport", "food", "shopping", "bills", "other"]
                category_index = category_options.index(selected_expense["category"].lower()) if selected_expense["category"].lower() in category_options else 0
                new_category = st.selectbox("New Category", category_options, index=category_index, key="update_expense_category")
                payment_options = ["cash", "card", "upi"]
                payment_index = payment_options.index(selected_expense["payment_method"].lower()) if selected_expense["payment_method"].lower() in payment_options else 0
                new_payment_method = st.selectbox("New Payment Method", payment_options, index=payment_index, key="update_expense_payment")
                if st.button("Update Expense"):
                    success = update_expense(expense_id, new_amount, new_category, new_payment_method)
                    if success:
                        st.success("✅ Expense updated successfully!")
                        
                    else:
                        st.error("❌ Failed to update expense.")
            else:
                st.error("⚠️ 'id' field is missing in API response.")
        else:
            st.warning("⚠️ No expenses available to update. Please add an expense first.")

    elif choice == "Delete Expense":
        st.subheader("🗑 Delete Expense")
        expenses = fetch_expenses()
        if expenses:
            df = pd.DataFrame(expenses)
            if "id" in df.columns:
                st.dataframe(df[['id', 'amount', 'category', "payment_method", 'date']])
                expense_id = st.selectbox(
                    "Select Expense to Delete",
                    df["id"].tolist(),
                    format_func=lambda x: f"{df[df['id'] == x]['category'].values[0]} - {df[df['id'] == x]['amount'].values[0]} on {df[df['id'] == x]['date'].values[0]}",
                    key="delete_expense_id"
                )
                if st.button("Delete Expense"):
                    success = delete_expense(expense_id)
                    if success:
                        st.success("✅ Expense deleted successfully!")
                        #st.rerun()
                    else:
                        st.error("❌ Failed to delete expense.")
            else:
                st.error("⚠️ 'id' field is missing in API response.")
        else:
            st.warning("⚠️ No expenses available to delete. Please add an expense first.")

    elif choice == "View Expenses":
        st.subheader("📋 View Expenses")
        expenses = fetch_expenses()
        if expenses:
            df = pd.DataFrame(expenses)
            st.dataframe(df[['id', 'amount', 'category', 'payment_method', 'date']])
        else:
            st.warning("⚠️ No expenses available to view. Please add an expense first.")

    elif choice == "AI Insights":
        st.subheader("💡 AI Insights")
        expenses = fetch_expenses()
        if expenses and "amount" in expenses[0] and "category" in expenses[0]:
            df = pd.DataFrame(expenses)
            fig = px.pie(df, names="category", values="amount", title="Spending Breakdown")
            st.plotly_chart(fig)
        else:
            st.warning("⚠️ No valid expense data for insights. Please add an expense first.")

# Main App Logic
if st.session_state.page == "home":
    home_page()
elif st.session_state.page == "register":
    register_page()
else:
    login_page()