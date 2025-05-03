import streamlit as st
import requests
import pandas as pd
import plotly.express as px

# Backend API Endpoints
REGISTER_URL = "http://127.0.0.1:8000/api/users/register/"
LOGIN_URL = "http://127.0.0.1:8000/api/users/login/"
API_BASE_URL = "http://127.0.0.1:8000/api/expenses/"
TOKEN = "f7d51549a85eb0af0d2fca304043e6e1b72c66e9"  # Replace with your actual token

headers = {
    "Authorization": f"Token {TOKEN}",
    "Content-Type": "application/json"
}

# Session State to Manage Pages & User Data
if "page" not in st.session_state:
    st.session_state.page = "login"
if "user" not in st.session_state:
    st.session_state.user = None

def fetch_expenses():
    response = requests.get(API_BASE_URL, headers=headers)
    return response.json() if response.status_code == 200 else []

def add_expense(amount, category, payment_method):
    data = {"amount": amount, "category": category.lower(), "payment_method": payment_method.lower()}
    return requests.post(API_BASE_URL, json=data, headers=headers).status_code == 201

def update_expense(expense_id, amount, category, payment_method):
    url = f"{API_BASE_URL}expenses/update/{expense_id}/"
    data = {"amount": amount, "category": category, "payment_method": payment_method}
    return requests.put(url, json=data, headers=headers).status_code == 200

def delete_expense(expense_id):
    url = f"{API_BASE_URL}expenses/delete/{expense_id}/"
    return requests.delete(url, headers=headers).status_code == 204

def home_page():
    st.title("🏠 Home - FinanceFusion")
    if st.session_state.user:
        user = st.session_state.user
        st.subheader(f"Welcome, {user['username']}! 👋")
        st.write(f"📧 Email: {user['email']}")
        st.sidebar.title("🔹 Navigation")
        menu = ["Expense Tracker", "Budget Management", "Milestones", "Reports", "Logout"]
        choice = st.sidebar.radio("Go to", menu)
        if choice == "Expense Tracker":
            expense_dashboard()
        elif choice == "Logout":
            st.session_state.user = None
            st.session_state.page = "login"
            st.experimental_rerun()
    else:
        st.warning("You are not logged in. Redirecting to login page...")
        st.session_state.page = "login"
        st.experimental_rerun()

def login_page():
    st.title("🔐 User Login")
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        response = requests.post(LOGIN_URL, json={"email": email, "password": password})
        if response.status_code == 200:
            st.session_state.user = response.json()["user"]
            st.success("Login successful! Redirecting to Home Page...")
            st.session_state.page = "home"
            #st.experimental_rerun()
        else:
            st.error(f"Error: {response.json().get('error', 'Login failed')}")
    if st.button("New User? Register Here!"):
        st.session_state.page = "register"
        st.experimental_rerun()

def register_page():
    st.title("📝 User Registration")
    username = st.text_input("Full Name")
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")
    confirm_password = st.text_input("Confirm Password", type="password")
    phone = st.text_input("Phone Number")
    dob = st.date_input("Date of Birth")
    if st.button("Register"):
        response = requests.post(REGISTER_URL, json={
            "username": username,
            "email": email,
            "password": password,
            "confirm_password": confirm_password,
            "phone": phone,
            "dob": str(dob)
        })
        if response.status_code == 201:
            st.success("User registered successfully! Please log in.")
            st.session_state.page = "login"
            #st.experimental_rerun()
        else:
            st.error(f"Error: {response.json()}")
    if st.button("Already have an account? Login here!"):
        st.session_state.page = "login"
        st.experimental_rerun()

def expense_dashboard():
    st.title("💰 Expense Tracker & AI Insights")
    menu = ["Add Expense", "Update Expense", "Delete Expense", "View Expenses", "AI Insights"]
    choice = st.sidebar.selectbox("Select Action", menu)
    if choice == "Add Expense":
        amount = st.number_input("Amount", min_value=0.0, format="%.2f")
        category = st.selectbox("Category", ["Food", "Entertainment", "Transport", "Bills", "Shopping", "Other"])
        payment_method = st.selectbox("Payment Method", ["Cash", "Card", "UPI", "Other"])
        if st.button("Add Expense") and add_expense(amount, category, payment_method):
            st.success("✅ Expense added successfully!")
    elif choice == "Update Expense":
        st.subheader("✏️ Update Expense")
        expenses = fetch_expenses()
        if expenses:
            df = pd.DataFrame(expenses)
            if "id" in df.columns:
                st.dataframe(df)
                expense_id = st.selectbox("Select Expense ID", df["id"].tolist())
                new_amount = st.number_input("New Amount", min_value=0.0, format="%.2f")
                new_category = st.selectbox("New Category", ["food", "entertainment", "transport", "bills", "shopping", "other"])
                new_payment_method = st.selectbox("New Payment Method", ["cash", "uard", "UPI", "other"])
                if st.button("Update Expense"):
                    if update_expense(expense_id, new_amount, new_category, new_payment_method):
                        st.success("✅ Expense updated successfully!")
                        #st.experimental_rerun()
                    else:
                        st.error("❌ Failed to update expense.")
            else:
                st.error("⚠️ 'id' field is missing in API response.")
        else:
            st.warning("⚠️ No expenses available to update.")
    elif choice == "Delete Expense":
        st.subheader("🗑 Delete Expense")
        expenses = fetch_expenses()
        if expenses:
            df = pd.DataFrame(expenses)
            st.dataframe(df)
            if "id" in df.columns:
                expense_id = st.selectbox("Select Expense ID to Delete", df["id"].tolist())
                if st.button("Delete Expense"):
                    if delete_expense(expense_id):
                        st.success("✅ Expense deleted successfully!")
                        #st.experimental_rerun()
                    else:
                        st.error("❌ Failed to delete expense.")
            else:
                st.error("⚠️ 'id' field is missing in API response.")
        else:
            st.warning("⚠️ No expenses available to delete.")
    elif choice == "View Expenses":
        expenses = fetch_expenses()
        df = pd.DataFrame(expenses)
        if not df.empty:
            st.dataframe(df)
    elif choice == "AI Insights":
        expenses = fetch_expenses()
        df = pd.DataFrame(expenses)
        if "amount" in df and "category" in df:
            fig = px.pie(df, names="category", values="amount", title="Spending Breakdown")
            st.plotly_chart(fig)

if st.session_state.page == "home":
    home_page()
elif st.session_state.page == "register":
    register_page()
else:
    login_page()
