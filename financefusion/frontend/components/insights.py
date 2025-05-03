import requests
import streamlit as st
import plotly.express as px

API_URL = "http://127.0.0.1:8000/api/expenses/"

def fetch_expenses():
    response = requests.get(API_URL, headers={"Authorization": f"Bearer {st.session_state.token}"})
    if response.status_code == 200:
        return response.json()
    return []

def show_insights():
    st.subheader("📊 Spending Insights")
    expenses = fetch_expenses()

    if not expenses:
        st.write("No data available.")
        return

    df = px.DataFrame(expenses)

    # Pie Chart
    fig = px.pie(df, values='amount', names='category', title='Expense Breakdown')
    st.plotly_chart(fig)
