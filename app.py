# app.py
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from io import BytesIO

sns.set(style="whitegrid")
st.set_page_config(page_title="AI Data Visualizer", layout="wide")

# ------------------- HEADER -------------------
st.title("📊 AI Data Visualizer (Enhanced Edition)")
st.markdown("Upload your Excel or CSV file and explore interactive visualizations and auto insights.")

# ------------------- FILE UPLOAD -------------------
uploaded_file = st.file_uploader("Upload your dataset", type=["xlsx", "csv"])

if uploaded_file is not None:
    try:
        if uploaded_file.name.endswith(".csv"):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)
        st.success(f"Loaded file: {uploaded_file.name}")
    except Exception as e:
        st.error(f"Error reading file: {e}")
        st.stop()
else:
    st.info("Please upload a file to begin.")
    st.stop()

# ------------------- COLUMN DETECTION -------------------
st.subheader("📄 Data Preview")
st.dataframe(df.head(200))

categorical_cols = df.select_dtypes(include=["object", "category"]).columns.tolist()
numeric_cols = df.select_dtypes(include=["number"]).columns.tolist()
datetime_cols = df.select_dtypes(include=["datetime64[ns]", "datetime"]).columns.tolist()

st.write("**Detected Columns:**")
st.write(f"- Categorical: {categorical_cols}")
st.write(f"- Numeric: {numeric_cols}")
st.write(f"- Datetime: {datetime_cols}")

# ------------------- SIDEBAR -------------------
st.sidebar.header("🧭 Visualization Controls")

theme_choice = st.sidebar.radio("Select Theme", ["Whitegrid", "Darkgrid", "Ticks"])
sns.set(style=theme_choice.lower())

vis_type = st.sidebar.selectbox(
    "Select Visualization Type",
    ["Pie Chart", "Bar Chart", "Histogram", "Line Chart", "Correlation Heatmap"]
)

# ------------------- FILTERING -------------------
if categorical_cols:
    st.sidebar.markdown("### 🔍 Filter Data (Optional)")
    filter_col = st.sidebar.selectbox("Select Categorical Column to Filter", ["None"] + categorical_cols)
    if filter_col != "None":
        unique_vals = df[filter_col].dropna().unique().tolist()
        selected_val = st.sidebar.selectbox(f"Select Value from {filter_col}", unique_vals)
        df = df[df[filter_col] == selected_val]
        st.info(f"Filtered by {filter_col} = {selected_val}")

# ------------------- SUMMARY STATISTICS -------------------
if st.sidebar.checkbox("🧮 Show Summary Statistics"):
    st.subheader("Summary Statistics")
    num_select = st.multiselect("Select Numeric Columns", numeric_cols, default=numeric_cols[:1])
    if num_select:
        st.write(df[num_select].describe().T)

# ------------------- COLUMN SELECTION -------------------
if vis_type in ["Pie Chart", "Bar Chart"]:
    cat_col = st.sidebar.selectbox("Select Categorical Column (X-axis / Group)", categorical_cols)
    num_cols_selected = st.sidebar.multiselect("Select Numeric Column(s) (Y-axis / Value)", numeric_cols, default=numeric_cols[:1])
elif vis_type == "Histogram":
    num_cols_selected = st.sidebar.multiselect("Select Numeric Column(s)", numeric_cols, default=numeric_cols[:1])
elif vis_type == "Line Chart":
    if datetime_cols:
        dt_col = st.sidebar.selectbox("Select Datetime Column (X-axis)", datetime_cols)
    else:
        dt_col = None
        st.warning("No datetime columns detected.")
    num_cols_selected = st.sidebar.multiselect("Select Numeric Column(s)", numeric_cols, default=numeric_cols[:1])
elif vis_type == "Correlation Heatmap":
    num_cols_selected = numeric_cols

# ------------------- GENERATE VISUALIZATION -------------------
if st.sidebar.button("Generate Visualization"):
    st.subheader(f"📈 Visualization: {vis_type}")

    fig, ax = plt.subplots(figsize=(8,5))

    # PIE
    if vis_type == "Pie Chart":
        for num_col in num_cols_selected:
            grouping = df.groupby(cat_col)[num_col].sum().dropna()
            fig, ax = plt.subplots(figsize=(5,5))
            grouping.plot(kind='pie', autopct='%1.1f%%', startangle=90, ax=ax)
            ax.set_ylabel('')
            ax.set_title(f"{num_col} distribution across {cat_col}")
            st.pyplot(fig)

    # BAR
    elif vis_type == "Bar Chart":
        for num_col in num_cols_selected:
            grouping = df.groupby(cat_col)[num_col].sum().sort_values(ascending=False).dropna()
            fig, ax = plt.subplots(figsize=(8,4))
            grouping.plot(kind='bar', ax=ax)
            ax.set_title(f"{num_col} sum by {cat_col}")
            ax.set_xlabel(cat_col)
            ax.set_ylabel(f"Sum of {num_col}")
            st.pyplot(fig)

    # HISTOGRAM
    elif vis_type == "Histogram":
        for num_col in num_cols_selected:
            fig, ax = plt.subplots(figsize=(6,4))
            df[num_col].dropna().plot(kind='hist', bins=20, ax=ax)
            ax.set_title(f"Histogram of {num_col}")
            st.pyplot(fig)

    # LINE
    elif vis_type == "Line Chart":
        if dt_col is not None:
            df_sorted = df.sort_values(by=dt_col)
            for num_col in num_cols_selected:
                fig, ax = plt.subplots(figsize=(8,4))
                ax.plot(df_sorted[dt_col], df_sorted[num_col], marker='o', linestyle='-')
                ax.set_title(f"{num_col} over time ({dt_col})")
                ax.set_xlabel(dt_col)
                ax.set_ylabel(num_col)
                st.pyplot(fig)
        else:
            st.warning("No valid datetime column selected.")

    # CORRELATION HEATMAP
    elif vis_type == "Correlation Heatmap":
        corr = df[num_cols_selected].corr()
        fig, ax = plt.subplots(figsize=(8,6))
        sns.heatmap(corr, annot=True, cmap="coolwarm", ax=ax)
        ax.set_title("Correlation Heatmap")
        st.pyplot(fig)

    # ------------------- DOWNLOAD CHART -------------------
    buf = BytesIO()
    fig.savefig(buf, format="png", bbox_inches="tight")
    st.download_button("📤 Download Chart as PNG", data=buf.getvalue(), file_name="chart.png", mime="image/png")

    # ------------------- AUTO INSIGHT GENERATOR -------------------
    st.markdown("### 🪄 Auto Insight Generator")
    if vis_type in ["Bar Chart", "Line Chart", "Histogram"]:
        for num_col in num_cols_selected:
            desc = df[num_col].describe()
            trend = "increasing" if desc["mean"] > desc["50%"] else "stable"
            st.info(
                f"For **{num_col}**, average value is **{desc['mean']:.2f}**, "
                f"median is **{desc['50%']:.2f}**, data shows a **{trend} trend** overall."
            )
    elif vis_type == "Pie Chart":
        st.info(f"Pie chart shows proportional distribution of {num_cols_selected[0]} across {cat_col}.")
    elif vis_type == "Correlation Heatmap":
        st.info("This heatmap highlights relationships between numeric features. Values near +1 or -1 show strong correlations.")

    st.success("✅ Visualization and insights generated successfully!")
