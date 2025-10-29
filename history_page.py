import streamlit as st
from backend.account_details import get_info, enter_height_weight_info
import pandas as pd
import plotly.express as px
import numpy as np
import plotly.graph_objects as go
import os

st.session_state.setdefault("switch", False)
st.session_state.setdefault("specific_time", None)
st.session_state.setdefault("specific_name", None)


cdc_info = """
**About the CDC(Center For Disease Control And Prevention) Growth Charts:**
The CDC provides growth charts to track child and teen growth compared to peers of the same age and gender.
These charts are based on U.S. population data from 2000. Recent studies show average weights and BMI have increased somewhat over the past 20+ years.
"""

adult_summary = """
**For Adults (20+ years):**
BMI(Body Mass Index) is used to assess health:
- BMI 18.5–24.9: Healthy
- BMI < 18.5: Underweight
- BMI 25–29.9: Overweight
- BMI ≥ 30: Obese
"""

with st.sidebar:
    st.page_link("Home.py", label="Home")
    st.page_link("pages/history_page.py", label="History")
    st.page_link("pages/checkup_page.py", label="Check Up")

user = st.session_state.get("user", None)
user_info = get_info(user)

@st.cache_data
def load_cdc_data():
    base_path = "data_analyze"
    weight_data = pd.read_excel(os.path.join(base_path, "wtage.xls"))
    height_data = pd.read_excel(os.path.join(base_path, "statage.xls"))
    bmi_data = pd.read_excel(os.path.join(base_path, "bmiagerev.xls"))
    return weight_data, height_data, bmi_data

weight_data, height_data, bmi_data = load_cdc_data()

def interpret_difference(diff, median):
    threshold = 0.1 * median
    if diff < -threshold:
        return "Below normal for age"
    elif diff > threshold:
        return "Above normal for age"
    else:
        return "Normal for age"

def cdc_summary(age, gender, height_cm, weight_kg):
    gender_code = 1 if gender == "male" else 2
    result = []

    wdata = weight_data[
        (weight_data["Sex"] == gender_code)
        & (np.isclose(weight_data["Agemos"], age * 12, atol=0.5))
    ]
    if not wdata.empty:
        median = wdata["P50"].iloc[0]
        diff = weight_kg - median
        status = interpret_difference(diff, median)
        result.append(f"**Weight:** {weight_kg:.1f} kgs")
        result.append(f"Median for age: {median:.1f} kgs")
        result.append(f"Difference from median: {diff:.1f} kgs")
        result.append(f"Status for weight: {status}\n")
    else:
        result.append("**Weight:** Data unavailable for that age range.")

    hdata = height_data[
        (height_data["Sex"] == gender_code)
        & (np.isclose(height_data["Agemos"], age * 12, atol=0.5))
    ]
    if not hdata.empty:
        median = hdata["P50"].iloc[0]
        diff = height_cm - median
        status = interpret_difference(diff, median)
        result.append("**HEIGHT**")
        result.append(f"**Height:** {height_cm:.1f} cm")
        result.append(f"Median for age: {median:.1f} cm")
        result.append(f"Difference from median: {diff:.1f} cm")
        result.append(f"Status for height: {status}")
    else:
        result.append("**Height:** Data unavailable for that age range.")
    return result

def calculate_bmi_zscore(L, M, S, bmi):
  
    if L == 0:
        z = np.log(bmi / M) / S
    else:
        z = ((bmi / M) ** L - 1) / (L * S)
    return z

def child_bmi_summary(age, gender, height_cm, weight_kgs):
    bmi = weight_kgs / ((height_cm / 100) ** 2)
    gender_code = 1 if gender == "male" else 2
    agemos = age * 12
    bmi_data["Agemos"] = pd.to_numeric(bmi_data["Agemos"],errors="coerce")
    agemos = float(age * 12)

    row = bmi_data[
    (bmi_data["Sex"] == gender_code) &
    (bmi_data["Agemos"] >= agemos - 0.5) &
    (bmi_data["Agemos"] <= agemos + 0.5)
]
   
    if row.empty:
       
        if bmi < 18.5:
            bmi_status = "Underweight"
        elif bmi < 25:
            bmi_status = "Healthy weight"
        elif bmi < 30:
            bmi_status = "Overweight"
        else:
            bmi_status = "Obese"
        return bmi, bmi_status

    L = row["L"].values[0]
    M = row["M"].values[0]
    S = row["S"].values[0]

    z = calculate_bmi_zscore(L, M, S, bmi)


    
    if z < -1.645:
        category = "Underweight"
    elif z < 1.036:
        category = "Healthy weight"
    elif z < 1.645:
        category = "Overweight"
    else:
        category = "Obese"

    return bmi, category

def adult_bmi_summary(height_m, weight_kgs):
 
    bmi = weight_kgs/ (height_m ** 2)
    if bmi < 18.5:
        status = "Underweight"
    elif bmi < 25:
        status = "Healthy weight"
    elif bmi < 30:
        status = "Overweight"
    else:
        status = "Obese"
    return bmi, status

def analyze_growth_trends(df):
    summary_lines = []
    if len(df) < 2:
        return summary_lines

    df_sorted = df.sort_values(by="Time")

    weight_diff = df_sorted["Weight (kgs)"].iloc[-1] - df_sorted["Weight (kgs)"].iloc[0]
    height_diff = df_sorted["Height (ft)"].iloc[-1] - df_sorted["Height (ft)"].iloc[0]

    if abs(weight_diff) < 0.1 * df_sorted["Weight (kgs)"].iloc[0]:
        summary_lines.append("Weight has remained stable.")
    elif weight_diff > 0:
        summary_lines.append("Weight has increased over time.")
    else:
        summary_lines.append("Weight has decreased over time.")

    if abs(height_diff) < 0.05:
        summary_lines.append("Height has remained stable.")
    elif height_diff > 0:
        summary_lines.append("Height has increased over time.")
    else:
        summary_lines.append("Height has decreased over time.")

    if weight_diff > 0 and height_diff > 0:
        summary_lines.append("Both height and weight are increasing, indicating expected healthy growth.")
    elif weight_diff < 0 and height_diff < 0:
        summary_lines.append("Both height and weight are decreasing, which may need attention.")
    elif weight_diff > 0 and height_diff < 0:
        summary_lines.append(
            "Your weight and height have changed. Your weight has increased which may have contributed to your height decrease"
        )
    elif weight_diff < 0 and height_diff > 0:
        summary_lines.append(
            "Your weight and height have changed. Your weight has decreased which may have contributed to your height increase"
        )

    return summary_lines

def overall_verdict(weight_status, height_status, bmi_status, gender):
    healthy_terms = ["Normal for age", "Healthy weight"]
    if weight_status is not None and height_status is not None:
        weight_ok = any(term in weight_status for term in healthy_terms)
        height_ok = any(term in height_status for term in healthy_terms)
        bmi_ok = bmi_status == "Healthy weight"

        if weight_ok and height_ok and bmi_ok:
            return f"Based on CDC data, overall growth appears healthy for a {gender.lower()} of this age."
        elif bmi_ok and (weight_ok or height_ok):
            return f"Growth is mostly within a healthy range for a {gender.lower()}, but continued monitoring is advised."
        else:
            return f"Growth pattern appears outside normal range for a {gender.lower()} — consider consulting a healthcare provider."
    else:
        return f"Insufficient data to determine overall health verdict for a {gender.lower()}."


if "history" in user_info and len(user_info["history"]) > 0:
    options = list(user_info["history"].keys())
    picked_name = st.selectbox("Which person would you like to view measurements for?:", options=options)

    if picked_name:
        st.subheader(f"Weight and Height for {picked_name}")

        database = {"Time": [], "Height (ft)": [], "Weight (kgs)": []}
        for time_str, measurements in user_info["history"][picked_name].items():
            database["Time"].append(time_str)
            database["Height (ft)"].append(measurements["height"])
            database["Weight (kgs)"].append(measurements["weight"])

        df = pd.DataFrame(database)

        df["Time"] = pd.to_datetime(df["Time"], format="%b %d, %Y - %I:%M %p", errors="coerce")
        df = df.dropna(subset=["Time"])

        df_sorted = df.sort_values("Time").reset_index(drop=True)
        df_sorted_desc = df.sort_values("Time", ascending=False).reset_index(drop=True)

        st.dataframe(df_sorted_desc, use_container_width=True)

        if len(df_sorted) > 1:
            st.markdown("### Growth Graphs")
            col_graph1, col_graph2 = st.columns(2)

            with col_graph1:
                fig_height = px.line(
                    df_sorted,
                    x="Time",
                    y="Height (ft)",
                    markers=True,
                    title="Height Over Time"
                )
                fig_height.update_xaxes(type="date")
                st.plotly_chart(fig_height, use_container_width=True)

                fig_combined = go.Figure()
                fig_combined.add_trace(
                    go.Scatter(
                        x=df_sorted["Time"],
                        y=df_sorted["Height (ft)"],
                        name="Height (ft)",
                        mode="lines+markers",
                        line=dict(color="royalblue", width=3),
                        marker=dict(size=8)
                    )
                )
                fig_combined.add_trace(
                    go.Scatter(
                        x=df_sorted["Time"],
                        y=df_sorted["Weight (kgs)"],
                        name="Weight (kgs)",
                        mode="lines+markers",
                        line=dict(color="darkorange", width=3, dash="dot"),
                        marker=dict(size=8),
                        yaxis="y2"
                    )
                )
                fig_combined.update_layout(
                    title="Height and Weight Growth Over Time",
                    xaxis=dict(title="Date", type="date"),
                    yaxis=dict(title="Height (ft)", color="royalblue"),
                    yaxis2=dict(
                        title="Weight (kgs)",
                        overlaying="y",
                        side="right",
                        color="darkorange"
                    ),
                    legend=dict(x=0.02, y=1.05, orientation="h"),
                    template="plotly_white",
                    margin=dict(l=50, r=50, t=60, b=40)
                )
                st.plotly_chart(fig_combined, use_container_width=True)

            with col_graph2:
                fig_weight = px.line(
                    df_sorted,
                    x="Time",
                    y="Weight (kgs)",
                    markers=True,
                    title="Weight Over Time"
                )
                fig_weight.update_xaxes(type="date")
                st.plotly_chart(fig_weight, use_container_width=True)

        st.subheader(f"Enter {picked_name}'s details for a health checkup:")

        gender = st.selectbox(f"Gender for {picked_name}:", ["male", "female"])
        age = st.number_input(f"Age of {picked_name}:", 2, 120)

        if st.button("Generate Report", key="checkup_summary"):
            last_row = df_sorted.iloc[-1]
            height_ft = last_row["Height (ft)"]
            weight_kgs_val = last_row["Weight (kgs)"]
            height_cm = height_ft * 30.4
            height_m=height_ft/3.281
            

            if age <= 20:
                st.subheader("CDC Current Weight And Height Analysis")
                st.write(cdc_info)

                summary = cdc_summary(age, gender, height_cm, weight_kgs_val)
                for line in summary:
                    st.write(line)

                st.subheader("BMI(Body Mass Index) Summary")
                bmi, bmi_status = child_bmi_summary(age, gender, height_cm, weight_kgs_val)
                st.write(f"**BMI:** {bmi:.1f} kg/m²")
                st.write(f"Status: {bmi_status}")

                if len(df_sorted) > 1:
                    st.subheader("Growth Trend Analysis")
                    for line in analyze_growth_trends(df_sorted):
                        st.write("- " + line)

                weight_status = summary[3].split(":")[-1].strip() if len(summary) > 3 else None
                height_status = summary[8].split(":")[-1].strip() if len(summary) > 8 else None
                verdict = overall_verdict(weight_status, height_status, bmi_status, gender)
                st.subheader("Final Health Verdict")
                st.write(verdict)

            else:
                st.subheader("Adult BMI Report")
                st.write(adult_summary)

                bmi, bmi_status = adult_bmi_summary(height_m, weight_kgs_val)
                st.write(f"**BMI:** {bmi:.1f}")
                st.write(f"Status: {bmi_status}")

                if len(df_sorted) > 1:
                    st.subheader("Growth Trend Analysis")
                    for line in analyze_growth_trends(df_sorted):
                        st.write("- " + line)

                if bmi_status == "Healthy weight":
                    verdict = f"Overall, growth and BMI appear healthy for an adult {gender.lower()}."
                elif bmi_status == "Underweight":
                    verdict = f"The BMI suggests underweight for an adult {gender.lower()}. Consider reviewing nutrition or consulting a healthcare provider."
                elif bmi_status == "Overweight":
                    verdict = f"The BMI indicates overweight for an adult {gender.lower()}. Monitoring diet and exercise may be beneficial."
                else:
                    verdict = f"The BMI indicates obesity for an adult {gender.lower()}. Medical advice is recommended."

                st.subheader("Final Health Verdict")
                st.write(verdict)
else:
    st.info("No history found for you yet.")
