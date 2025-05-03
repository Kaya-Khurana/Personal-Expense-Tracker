import requests
import streamlit as st
import pandas as pd
import plotly.express as px

# API Endpoint
API_URL = "http://127.0.0.1:8000/api/expenses/"
TOKEN = "YOUR_ACCESS_TOKEN"  # Replace this with a valid token

# Function to Fetch Expenses
def fetch_expenses():
    headers = {"Authorization": f"Bearer {TOKEN}"}
    try:
        response = requests.get(API_URL, headers=headers)
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Failed to fetch expenses. Error {response.status_code}")
            return []
    except Exception as e:
        st.error(f"API request failed: {str(e)}")
        return []

# Search & Display Expenses
def search_expenses():
    st.subheader("🔍 Search & View Expenses")

    # Fetch Expenses from API
    expenses = fetch_expenses()

    # Debugging: Show raw API data
    st.write("### API Response (Debugging)")
    st.json(expenses)  

    if not expenses:
        st.warning("No expenses found!")
        return

    # Search Box
    search_term = st.text_input("Search by category, payment method, or date")

    # Convert to Pandas DataFrame
    df = pd.DataFrame(expenses)

    # Apply Search Filter
    if search_term:
        df = df[df.apply(lambda row: search_term.lower() in str(row.values).lower(), axis=1)]

    # Show Filtered Data
    if df.empty:
        st.warning("No matching expenses found!")
    else:
        st.write("### 📋 Expense List")
        st.dataframe(df)

    # Expense Visualization (Bar Chart)
    st.write("### 📊 Spending Insights")
    if not df.empty:
        fig = px.bar(df, x="category", y="amount", title="Spending by Category", text="amount")
        st.plotly_chart(fig)

# Run Function
if __name__ == "__main__":
    search_expenses()
