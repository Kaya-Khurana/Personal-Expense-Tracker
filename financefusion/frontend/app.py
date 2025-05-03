import streamlit as st
import requests

# Backend API Endpoints
REGISTER_URL = "http://127.0.0.1:8000/api/users/register/"
LOGIN_URL = "http://127.0.0.1:8000/api/users/login/"

# Session State to Manage Pages & User Data
if "page" not in st.session_state:
    st.session_state.page = "login"  # Default page is Login
if "user" not in st.session_state:
    st.session_state.user = None  # Store user info after login

# Function: Home Page
def home_page():
    st.title("🏠 Home - FinanceFusion")

    # Display User Info
    if st.session_state.user:
        user = st.session_state.user
        st.subheader(f"Welcome, {user['username']}! 👋")
        st.write(f"📧 Email: {user['email']}")
        st.write("---")

        # Quick Navigation
        st.subheader("📌 Quick Access")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("📊 Expense Tracker"):
                st.session_state.page = "expense_tracker"
        with col2:
            if st.button("💰 Budget Management"):
                st.session_state.page = "budget_management"

        col3, col4 = st.columns(2)
        with col3:
            if st.button("🎯 Milestones"):
                st.session_state.page = "milestone_tracker"
        with col4:
            if st.button("📜 Reports"):
                st.session_state.page = "reports"

        st.write("---")
        if st.button("🚪 Logout"):
            st.session_state.user = None
            st.session_state.page = "login"

    else:
        st.warning("You are not logged in. Redirecting to login page...")
        st.session_state.page = "login"

# Function: Login Page
def login_page():
    st.title("🔐 User Login")

    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        payload = {"email": email, "password": password}

        try:
            response = requests.post(LOGIN_URL, json=payload)
            if response.status_code == 200:
                data = response.json()
                st.session_state.user = data["user"]  # Store user details
                st.success("Login successful! Redirecting to Home Page...")
                st.session_state.page = "home"  # Redirect to Home
            else:
                st.error(f"Error: {response.json()['error']}")
        except requests.exceptions.RequestException as e:
            st.error(f"Request failed: {e}")

    st.write("---")
    if st.button("New User? Register Here!"):
        st.session_state.page = "register"

# Function: Registration Page
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
            st.error(f"Request failed: {e}")

    st.write("---")
    if st.button("Already have an account? Login here!"):
        st.session_state.page = "login"

# Show the Current Page
if st.session_state.page == "home":
    home_page()
elif st.session_state.page == "register":
    register_page()
else:
    login_page()
