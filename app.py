import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Function to calculate trap count ETL
def calculate_trap_count_etl(df, pest_etl=None, damage_etl=None):
    trap_etl_values = []

    # Based on pest per leaf ETL
    if pest_etl is not None and "No_of_pests" in df.columns:
        pest_df = df[df["No_of_pests"] >= pest_etl]
        if not pest_df.empty:
            trap_etl_values.append(pest_df["Trap_counts"].iloc[0])

    # Based on % leaf damage ETL
    if damage_etl is not None and "Percent_damage" in df.columns:
        damage_df = df[df["Percent_damage"] >= damage_etl]
        if not damage_df.empty:
            trap_etl_values.append(damage_df["Trap_counts"].iloc[0])

    # Return minimum trap count ETL if both available
    if trap_etl_values:
        return min(trap_etl_values)
    else:
        return None


# ---------------- Streamlit UI ----------------
st.title("Trap Count ETL Calculator")

# Upload CSV
uploaded_file = st.file_uploader("Upload CSV File", type=["csv"])

# ETL inputs
pest_etl = st.number_input("Enter Pest Count per Leaf ETL (optional)", min_value=0.0, step=0.1, value=None, format="%.2f")
damage_etl = st.number_input("Enter % Leaf Damage ETL (optional)", min_value=0.0, step=0.1, value=None, format="%.2f")

# Submit button
if st.button("Submit"):
    if uploaded_file is not None:
        # Load data
        df = pd.read_csv(uploaded_file)

        # Ensure correct column names
        required_cols = ["No_of_pests", "Trap_counts", "Percent_damage"]
        if not all(col in df.columns for col in required_cols):
            st.error(f"CSV must contain columns: {required_cols}")
        else:
            # Calculate ETL
            trap_etl = calculate_trap_count_etl(df, 
                                                pest_etl if pest_etl > 0 else None, 
                                                damage_etl if damage_etl > 0 else None)

            if trap_etl is not None:
                st.metric("Trap Count ETL", f"{trap_etl:.2f}")
            else:
                st.warning("Could not determine Trap Count ETL with given inputs.")

            # -------- Graphs --------
            fig, ax = plt.subplots(1, 2, figsize=(12, 5))

            # Scatter plot: Pest count vs Trap count
            ax[0].scatter(df["Trap_counts"], df["No_of_pests"], c="blue", label="Pests/Leaf")
            if pest_etl and trap_etl:
                ax[0].axhline(pest_etl, color="red", linestyle="--", label="Pest ETL")
                ax[0].axvline(trap_etl, color="green", linestyle="--", label="Trap ETL")
            ax[0].set_xlabel("Trap Counts")
            ax[0].set_ylabel("Pests per Leaf")
            ax[0].legend()
            ax[0].set_title("Pests vs Trap Counts")

            # Scatter plot: % Leaf Damage vs Trap count
            ax[1].scatter(df["Trap_counts"], df["Percent_damage"], c="orange", label="% Leaf Damage")
            if damage_etl and trap_etl:
                ax[1].axhline(damage_etl, color="red", linestyle="--", label="Damage ETL")
                ax[1].axvline(trap_etl, color="green", linestyle="--", label="Trap ETL")
            ax[1].set_xlabel("Trap Counts")
            ax[1].set_ylabel("% Leaf Damage")
            ax[1].legend()
            ax[1].set_title("Leaf Damage vs Trap Counts")

            st.pyplot(fig)
    else:
        st.error("Please upload a CSV file.")
