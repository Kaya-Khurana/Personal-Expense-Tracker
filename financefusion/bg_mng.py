import streamlit as st
import pandas as pd
import os
import django

# ✅ Set Django settings before any import
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'financefusion.settings')
django.setup()  # ✅ Initialize Django settings

from budget_management.models import BudgetCategory  # Now import models


st.title("Budget Management Dashboard")

# Fetch data
budget_data = BudgetCategory.objects.all()

# Convert to DataFrame
df = pd.DataFrame(
    [(b.name, b.limit, b.spent, b.remaining_budget()) for b in budget_data],
    columns=["Category", "Limit", "Spent", "Remaining"],
)

# Display Data
st.dataframe(df)

# Visualization
import matplotlib.pyplot as plt

fig, ax = plt.subplots()
ax.bar(df["Category"], df["Spent"], label="Spent")
ax.bar(df["Category"], df["Remaining"], bottom=df["Spent"], label="Remaining")
ax.legend()
st.pyplot(fig)
