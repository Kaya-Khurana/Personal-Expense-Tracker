import streamlit as st
import requests
import pandas as pd
from datetime import datetime
import plotly.express as px
from expenses.models import Expense
# API Endpoints
REGISTER_URL = "http://127.0.0.1:8000/api/users/register/"
LOGIN_URL = "http://127.0.0.1:8000/api/users/login/"
API_BASE_URL = "http://127.0.0.1:8000/api/expenses/"
TOKEN = "f7d51549a85eb0af0d2fca304043e6e1b72c66e9"

headers = {"Authorization": f"Token {TOKEN}", "Content-Type": "application/json"}

# Session State Initialization
if "page" not in st.session_state:
    st.session_state.page = "login"
if "user" not in st.session_state:
    st.session_state.user = None

def fetch_expenses():
    response = requests.get(API_BASE_URL, headers=headers)
    if response.status_code == 200:
        return response.json()
    st.error("Failed to fetch expenses.")
    return []


def add_expense(amount, category, payment_method):
    data = {"amount": amount, "category": category.lower(), "payment_method": payment_method.lower()}
    response = requests.post(API_BASE_URL, json=data, headers=headers)
    return response.status_code == 201

def update_expense(expense_id, amount, category, payment_method):
    url = f"http://127.0.0.1:8000/api/expenses/expenses/update/{expense_id}/"  # Correct URL
    data = {"amount": amount, "category": category, "payment_method": payment_method}
    response = requests.put(url, json=data, headers=headers)

def delete_expense(expense_id):
    url = f"http://127.0.0.1:8000/api/expenses/expenses/delete/{expense_id}/"  # Fixed URL path
    response = requests.delete(url, headers=headers)  # Changed PUT to DELETE
    return response.status_code == 204

def home_page():
    st.title("🏠 Home - FinanceFusion")
    if st.session_state.user:
        st.subheader(f"Welcome, {st.session_state.user['username']}! 👋")
        menu = ["Expense Tracker", "Budget Management", "Milestones", "Reports"]
        choice = st.selectbox("📌 Quick Access", menu)
        if choice=="Expense Tracker":
            expense_dashboard()
        if st.button("🚪 Logout"):
            st.session_state.user = None
            st.session_state.page = "login"
    else:
        st.warning("You are not logged in. Redirecting to login page...")
        st.session_state.page = "login"

def login_page():
    st.title("🔐 User Login")
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        response = requests.post(LOGIN_URL, json={"email": email, "password": password})
        if response.status_code == 200:
            st.session_state.user = response.json()["user"]
            st.success("Login successful! Redirecting...")
            st.session_state.page = "home"
        else:
            st.error("Invalid credentials")
    if st.button("New User? Register Here!"):
        st.session_state.page = "register"

def register_page():
    st.title("📝 User Registration")
    username = st.text_input("Full Name")
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")
    confirm_password = st.text_input("Confirm Password", type="password")
    phone = st.text_input("Phone Number")
    dob = st.date_input("Date of Birth")

    if st.button("New Existing User? Login Here!"):
           st.session_state.page = "login"    

    if st.button("Register"):
        payload = {
            "username": username,
            "email": email,
            "password": password,
            "confirm_password": confirm_password,
            "phone": phone,
            "dob": str(dob),
        }
        
        response = requests.post(REGISTER_URL, json=payload)
        
        # Debugging response
        #st.write("Response Status Code:", response.status_code)
        #st.write("Response JSON:", response.json())

        if response.status_code == 201:
            st.success("Registered successfully! Please log in.")
            st.session_state.page = "login"
        else:
            st.error(f"Registration failed: {response.json()}")  # Show exact error

       

def expense_dashboard():
    st.title("💰 Expense Tracker & AI Insights")
    menu = ["Add Expense", "Update Expense", "Delete Expense", "View Expenses", "AI Insights"]
    choice = st.sidebar.selectbox("Select Action", menu)

    # 📌 Add Expense
    if choice == "Add Expense":
        st.subheader("Add a New Expense")
        amount = st.number_input("Expense Amount", min_value=0.01, step=0.01)
        category = st.selectbox("Category", ["Food", "Entertainment", "Transport", "Bills", "Shopping", "Other"])
        payment_method = st.selectbox("Payment Method", ["Cash", "Card", "UPI", "Other"])
        #description = st.text_area("Description")
        date = st.date_input("Expense Date", datetime.today())

        if st.button("Add Expense"):
            try:
                Expense.objects.create(
                    amount=amount, category=category, payment_method=payment_method, date=date
                )
                st.success("Expense Added Successfully!")
                #st.experimental_rerun()
            except Exception as e:
                st.error(f"Error: {e}")

    # 📌 View Expenses
    elif choice == "View Expenses":
        st.subheader("View All Expenses")
        start_date = st.date_input("Start Date", datetime.today())
        end_date = st.date_input("End Date", datetime.today())
        selected_category = st.selectbox("Filter by Category", ["All", "Food", "Entertainment", "Transport", "Bills", "Shopping", "Other"])

        try:
            expenses = Expense.objects.filter(date__range=[start_date, end_date])
            if selected_category != "All":
                expenses = expenses.filter(category=selected_category)

            expenses = list(expenses.values())

            if expenses:
                df = pd.DataFrame(expenses)
                df["date"] = pd.to_datetime(df["date"]).dt.strftime("%Y-%m-%d")
                st.dataframe(df)

                st.subheader("Expense Summary")
                summary = df.groupby("category")["amount"].sum().reset_index()
                st.bar_chart(summary.set_index("category"))
            else:
                st.warning("No expenses found.")
        except Exception as e:
            st.error(f"Error: {e}")

    # 📌 Update Expense
    elif choice == "Update Expense":
        st.subheader("Update an Expense")
        expense_ids = list(Expense.objects.values_list("id", flat=True))

        if expense_ids:
            expense_id = st.selectbox("Select Expense ID", expense_ids)
            expense = Expense.objects.get(id=expense_id)

            new_amount = st.number_input("New Amount", min_value=0.01, step=0.01, value=expense.amount)
            new_category = st.selectbox("New Category", ["Food", "Entertainment", "Transport", "Bills", "Shopping", "Other"], index=["Food", "Entertainment", "Transport", "Bills", "Shopping", "Other"].index(expense.category))
            new_payment_method = st.selectbox("New Payment Method", ["Cash", "Card", "UPI", "Other"], index=["Cash", "Card", "UPI", "Other"].index(expense.payment_method))
            new_description = st.text_area("New Description", value=expense.description)
            new_date = st.date_input("New Date", expense.date)

            if st.button("Update Expense"):
                try:
                    Expense.objects.filter(id=expense_id).update(
                        amount=new_amount, category=new_category, payment_method=new_payment_method, description=new_description, date=new_date
                    )
                    st.success("Expense Updated Successfully!")
                    st.experimental_rerun()
                except Exception as e:
                    st.error(f"Error: {e}")
        else:
            st.warning("No expenses available to update.")

    # 📌 Delete Expense
    elif choice == "Delete Expense":
        st.subheader("Delete an Expense")
        expense_ids = list(Expense.objects.values_list("id", flat=True))

        if expense_ids:
            expense_id = st.selectbox("Select Expense ID to Delete", expense_ids)
            if st.button("Delete Expense"):
                try:
                    Expense.objects.filter(id=expense_id).delete()
                    st.warning("Expense Deleted Successfully!")
                    st.experimental_rerun()
                except Exception as e:
                    st.error(f"Error: {e}")
        else:
            st.warning("No expenses available to delete.")

    # 📌 AI Insights
    elif choice == "AI Insights":
        st.subheader("📈 AI-Based Insights")
        expenses = fetch_expenses()
        if expenses:
            df = pd.DataFrame(expenses)
            if "amount" in df.columns and "category" in df.columns:
                fig = px.pie(df, names="category", values="amount", title="Spending Breakdown")
                st.plotly_chart(fig)
            else:
                st.error("⚠️ Required fields are missing in API response.")
        else:
            st.warning("⚠️ No expenses to show insights.")

    elif choice == "View Expenses":
        expenses = fetch_expenses()
        if expenses:
            df = pd.DataFrame(expenses)
            st.dataframe(df)
    
    elif choice == "AI Insights":
        expenses = fetch_expenses()
        if expenses:
            df = pd.DataFrame(expenses)
            if "amount" in df.columns and "category" in df.columns:
                fig = px.pie(df, names="category", values="amount", title="Spending Breakdown")
                st.plotly_chart(fig)

if st.session_state.page == "home":
    home_page()
elif st.session_state.page == "register":
    register_page()
elif st.session_state.page == "expense_tracker":
    expense_dashboard()
elif st.session_state.page == "login":
    login_page()
