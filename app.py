import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

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
st.title("🌾 Trap Count ETL Calculator (Interactive Dashboard)")

# Upload CSV
uploaded_file = st.file_uploader("Upload CSV File", type=["csv"])

# ETL inputs
pest_etl = st.number_input("Enter Pest Count per Leaf ETL (optional)", min_value=0.0, step=0.1, value=0.0, format="%.2f")
damage_etl = st.number_input("Enter % Leaf Damage ETL (optional)", min_value=0.0, step=0.1, value=0.0, format="%.2f")

# Submit button
if st.button("Submit"):
    if uploaded_file is not None:
        # Load data
        df = pd.read_csv(uploaded_file)

        # Ensure required column
        if "Trap_counts" not in df.columns:
            st.error("CSV must contain column: 'Trap_counts'")
        else:
            # Convert 0 to None
            pest_val = pest_etl if pest_etl > 0 else None
            damage_val = damage_etl if damage_etl > 0 else None

            # Calculate ETL
            trap_etl = calculate_trap_count_etl(df, pest_val, damage_val)

            if trap_etl is not None:
                st.subheader("📌 Calculated ETL and Risk Levels")

                # -------- Thresholds BELOW ETL --------
                trap_values = df["Trap_counts"].dropna()

                below_etl_values = trap_values[trap_values < trap_etl] if trap_etl else trap_values

                if not below_etl_values.empty:
                    low_thr = np.percentile(below_etl_values, 33)
                    med_thr = np.percentile(below_etl_values, 66)
                    high_thr = trap_etl  # ETL is the upper cutoff

                    # ---- Display Metrics Row ----
                    col1, col2, col3, col4 = st.columns(4)
                    col1.metric("Trap Count ETL", f"{trap_etl:.2f}")
                    col2.metric("Low", f"🟢 {low_thr:.2f}")
                    col3.metric("Medium", f"🟡 {med_thr:.2f}")
                    col4.metric("High", f"🔴 {high_thr:.2f}")

                    # -------- Plotly Graphs --------
                    st.subheader("📊 Interactive Visualizations")

                    # Histogram of Trap Counts
                    hist_fig = px.histogram(df, x="Trap_counts", nbins=15, title="Trap Counts Distribution",
                                            opacity=0.7, marginal="box")
                    hist_fig.add_vline(x=low_thr, line_dash="dash", line_color="green", annotation_text="Low")
                    hist_fig.add_vline(x=med_thr, line_dash="dash", line_color="orange", annotation_text="Medium")
                    hist_fig.add_vline(x=trap_etl, line_dash="dash", line_color="red", annotation_text="ETL")
                    st.plotly_chart(hist_fig, use_container_width=True)

                    # Scatter: Pests vs Trap Counts
                    if "No_of_pests" in df.columns:
                        pest_fig = px.scatter(df, x="Trap_counts", y="No_of_pests", color="No_of_pests",
                                              title="Pests per Leaf vs Trap Counts",
                                              labels={"Trap_counts": "Trap Counts", "No_of_pests": "Pests/Leaf"})
                        if pest_val:
                            pest_fig.add_hline(y=pest_val, line_dash="dash", line_color="red", annotation_text="Pest ETL")
                        pest_fig.add_vline(x=trap_etl, line_dash="dash", line_color="green", annotation_text="Trap ETL")
                        st.plotly_chart(pest_fig, use_container_width=True)

                    # Scatter: % Leaf Damage vs Trap Counts
                    if "Percent_damage" in df.columns:
                        damage_fig = px.scatter(df, x="Trap_counts", y="Percent_damage", color="Percent_damage",
                                                title="Leaf Damage % vs Trap Counts",
                                                labels={"Trap_counts": "Trap Counts", "Percent_damage": "% Leaf Damage"})
                        if damage_val:
                            damage_fig.add_hline(y=damage_val, line_dash="dash", line_color="red", annotation_text="Damage ETL")
                        damage_fig.add_vline(x=trap_etl, line_dash="dash", line_color="green", annotation_text="Trap ETL")
                        st.plotly_chart(damage_fig, use_container_width=True)

                else:
                    st.warning("Not enough values below ETL to calculate thresholds.")

            else:
                st.warning("Could not determine Trap Count ETL with given inputs.")

    else:
        st.error("Please upload a CSV file.")
