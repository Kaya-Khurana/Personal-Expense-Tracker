import streamlit as st
import requests
import pandas as pd
import plotly.express as px

API_BASE_URL = "http://127.0.0.1:8000/api/expenses/"
TOKEN = "f7d51549a85eb0af0d2fca304043e6e1b72c66e9"  # Replace with your actual token

headers = {
    "Authorization": f"Token {TOKEN}",
    "Content-Type": "application/json"
}

# 📌 Function to fetch expenses
def fetch_expenses():
    response = requests.get(API_BASE_URL, headers=headers)
    if response.status_code == 200:
        return response.json()
    st.error("Failed to fetch expenses.")
    return []

# 📌 Function to add a new expense
def add_expense(amount, category, payment_method):
    data = {"amount": amount, "category": category.lower(), "payment_method": payment_method.lower()}
    response = requests.post(API_BASE_URL, json=data, headers=headers)
    return response.status_code == 201

# 📌 Function to update an expense
def update_expense(expense_id, amount, category, payment_method):
    url = f"http://127.0.0.1:8000/api/expenses/expenses/update/{expense_id}/"  # Correct URL
    data = {"amount": amount, "category": category, "payment_method": payment_method}
    response = requests.put(url, json=data, headers=headers)

    # Debugging output
    #st.write("🔹 Update API Response:", response.status_code, response.text)  

    return response.status_code == 200  # Check if update was successful


# 📌 Function to delete an expense
def delete_expense(expense_id):
    url = f"http://127.0.0.1:8000/api/expenses/expenses/delete/{expense_id}/"  # Fixed URL path
    response = requests.delete(url, headers=headers)  # Changed PUT to DELETE
    return response.status_code == 204


# 🚀 Streamlit UI
def expense_dashboard():
    st.title("💰 Expense Tracker & AI Insights")
    menu = ["Add Expense", "Update Expense", "Delete Expense", "View Expenses", "AI Insights"]
    choice = st.sidebar.selectbox("Select Action", menu)

    # 📌 Add Expense
    if choice == "Add Expense":
        st.subheader("➕ Add Expense")
        amount = st.number_input("Amount", min_value=0.0, format="%.2f")
        category = st.selectbox("Category", ["Food", "Entertainment", "Transport", "Bills", "Shopping", "Other"])
        payment_method = st.selectbox("Payment Method", ["Cash", "Card", "UPI", "Other"])
        if st.button("Add Expense"):
            if add_expense(amount, category, payment_method):
                st.success("✅ Expense added successfully!")
                #st.experimental_rerun()
            else:
                st.error("❌ Failed to add expense.")

    # 📌 Update Expense
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

    # 📌 Delete Expense
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

    # 📌 View Expenses
    elif choice == "View Expenses":
        st.subheader("📊 Your Expenses")
        expenses = fetch_expenses()
        if expenses:
            df = pd.DataFrame(expenses)
            if "id" in df.columns:
                st.dataframe(df)
            else:
                st.error("⚠️ 'id' field is missing in API response.")
        else:
            st.warning("⚠️ No expenses found.")

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

# 🚀 Run the dashboard
if __name__ == "__main__":
    expense_dashboard()
