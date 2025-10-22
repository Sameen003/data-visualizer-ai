# app.py
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from io import BytesIO

sns.set(style="whitegrid")
st.set_page_config(page_title="AI Data Visualizer", layout="wide")

st.title("📊 AI Data Visualizer (Interactive)")

st.markdown(
    """
    Upload an Excel (.xlsx) or CSV file and select your desired visualization type and columns.
    """
)

uploaded_file = st.file_uploader("Upload your dataset", type=["xlsx", "csv"])

# Optional sample dataset button
if st.button("Load sample dataset (penguins)"):
    df = sns.load_dataset("penguins")
    st.success("Loaded sample: penguins")
else:
    df = None

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

if df is not None:
    st.subheader("Data Preview")
    st.dataframe(df.head(200))

    # Detect column types
    categorical_cols = df.select_dtypes(include=["object", "category"]).columns.tolist()
    numeric_cols = df.select_dtypes(include=["number"]).columns.tolist()
    datetime_cols = df.select_dtypes(include=["datetime64[ns]", "datetime"]).columns.tolist()

    st.write("**Detected columns:**")
    st.write(f"- Categorical: {categorical_cols}")
    st.write(f"- Numeric: {numeric_cols}")
    st.write(f"- Datetime: {datetime_cols}")

    # Sidebar controls
    st.sidebar.header("Visualization Controls")
    vis_type = st.sidebar.selectbox(
        "Select Visualization Type",
        ["Pie Chart", "Bar Chart", "Histogram", "Line Chart"]
    )

    # Depending on visualization type, show relevant column pickers
    if vis_type in ["Pie Chart", "Bar Chart"]:
        cat_col = st.sidebar.selectbox("Select Categorical Column (X-axis / Group)", categorical_cols)
        num_col = st.sidebar.selectbox("Select Numeric Column (Y-axis / Value)", numeric_cols)
    elif vis_type == "Histogram":
        num_col = st.sidebar.selectbox("Select Numeric Column", numeric_cols)
    elif vis_type == "Line Chart":
        if datetime_cols:
            dt_col = st.sidebar.selectbox("Select Datetime Column (X-axis)", datetime_cols)
        else:
            dt_col = None
            st.warning("No datetime columns detected.")
        num_col = st.sidebar.selectbox("Select Numeric Column (Y-axis)", numeric_cols)
    else:
        st.warning("Select a valid visualization type.")
        st.stop()

    # Visualization button
    if st.sidebar.button("Generate Visualization"):
        st.subheader(f"Visualization: {vis_type}")

        if vis_type == "Pie Chart":
            grouping = df.groupby(cat_col)[num_col].sum().dropna()
            fig, ax = plt.subplots(figsize=(5,5))
            grouping.plot(kind='pie', autopct='%1.1f%%', startangle=90, ax=ax)
            ax.set_ylabel('')
            ax.set_title(f"{num_col} distribution across {cat_col}")
            st.pyplot(fig)

        elif vis_type == "Bar Chart":
            grouping = df.groupby(cat_col)[num_col].sum().sort_values(ascending=False).dropna()
            fig, ax = plt.subplots(figsize=(8,4))
            grouping.plot(kind='bar', ax=ax)
            ax.set_title(f"{num_col} sum by {cat_col}")
            ax.set_xlabel(cat_col)
            ax.set_ylabel(f"Sum of {num_col}")
            st.pyplot(fig)

        elif vis_type == "Histogram":
            fig, ax = plt.subplots(figsize=(6,4))
            df[num_col].dropna().plot(kind='hist', bins=20, ax=ax)
            ax.set_title(f"Histogram of {num_col}")
            st.pyplot(fig)

        elif vis_type == "Line Chart":
            if dt_col is not None:
                df_sorted = df.sort_values(by=dt_col)
                fig, ax = plt.subplots(figsize=(8,4))
                ax.plot(df_sorted[dt_col], df_sorted[num_col], marker='o', linestyle='-')
                ax.set_title(f"{num_col} over time ({dt_col})")
                ax.set_xlabel(dt_col)
                ax.set_ylabel(num_col)
                st.pyplot(fig)
            else:
                st.warning("No valid datetime column selected.")

        st.success("Visualization generated successfully!")

else:
    st.info("Upload a file or click the sample dataset button to start.")
