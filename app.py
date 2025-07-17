import streamlit as st
import pandas as pd
import plotly.express as px
import sqlite3
import os
from io import BytesIO
from sklearn.preprocessing import LabelEncoder, StandardScaler



st.set_page_config(page_title="DataTool", layout="wide")
st.title("📊 Data Preparation & Visualization Tool")

uploaded_file = st.file_uploader("Upload a file (CSV, Excel, SQLite)", type=["csv", "xlsx", "xls", "sqlite", "db"])
df = None

if uploaded_file:
    filename = uploaded_file.name
    if filename.endswith(".csv"):
        df = pd.read_csv(uploaded_file)
    elif filename.endswith((".xlsx", ".xls")):
        df = pd.read_excel(uploaded_file)
    elif filename.endswith((".sqlite", ".db")):
        with open("temp_db.sqlite", "wb") as f:
            f.write(uploaded_file.read())
        conn = sqlite3.connect("temp_db.sqlite")
        tables = pd.read_sql("SELECT name FROM sqlite_master WHERE type='table'", conn)
        selected_table = st.selectbox("Choose table", tables["name"])
        df = pd.read_sql(f"SELECT * FROM {selected_table}", conn)
        conn.close()
        os.remove("temp_db.sqlite")

if df is not None:
    st.success(f"✅ Loaded {df.shape[0]} rows × {df.shape[1]} columns")

    st.subheader("🔍 Basic Information")
    st.write("**Shape:**", df.shape)
    st.dataframe(df.dtypes.astype(str).reset_index().rename(columns={'index': 'Column', 0: 'Type'}))
    st.dataframe(df.describe(include='all').transpose())

    st.subheader("📊 Correlation Heatmap")
    st.plotly_chart(px.imshow(df.corr(numeric_only=True), text_auto=True), use_container_width=True, key="heatmap1")

    st.subheader("🧼 Handle Missing Values")
    method = st.selectbox("Fill method", ["None", "Drop rows", "Fill 0", "Mean", "Median", "Custom value"])
    if method == "Drop rows":
        df = df.dropna()
    elif method == "Fill 0":
        df = df.fillna(0)
    elif method == "Mean":
        df = df.fillna(df.mean(numeric_only=True))
    elif method == "Median":
        df = df.fillna(df.median(numeric_only=True))
    elif method == "Custom value":
        val = st.text_input("Enter custom fill value")
        if val:
            df = df.fillna(val)

    st.subheader("🔠 Label Encoding")
    obj_cols = df.select_dtypes(include='object').columns.tolist()
    if obj_cols:
        encode_cols = st.multiselect("Select columns to encode", obj_cols)
        for col in encode_cols:
            df[col] = LabelEncoder().fit_transform(df[col].astype(str))

    st.subheader("📐 Feature Scaling")
    num_cols = df.select_dtypes(include=['int64', 'float64']).columns.tolist()
    if num_cols:
        scale_cols = st.multiselect("Select columns to scale", num_cols)
        if scale_cols:
            scaler = StandardScaler()
            df[scale_cols] = scaler.fit_transform(df[scale_cols])
            st.success("✅ Scaling applied.")

    st.subheader("📝 Edit DataFrame")
    df = st.data_editor(df, use_container_width=True, num_rows="dynamic")

    with st.expander("🎨 Choose Plot Type", expanded=False):
        chart_type = st.radio("Select Visualization Type", [
            "None", "Histogram", "Box", "Pie", "Scatter", "Heatmap", "Pair Plot"
        ])

    if chart_type == "Histogram":
        col = st.selectbox("Select numeric column", num_cols)
        st.plotly_chart(px.histogram(df, x=col), use_container_width=True)
    elif chart_type == "Box":
        col = st.selectbox("Select column", num_cols)
        st.plotly_chart(px.box(df, y=col), use_container_width=True)
    elif chart_type == "Pie":
        col = st.selectbox("Select categorical column", obj_cols)
        st.plotly_chart(px.pie(df, names=col), use_container_width=True)
    elif chart_type == "Scatter":
        x = st.selectbox("X-axis", num_cols)
        y = st.selectbox("Y-axis", num_cols, index=1 if len(num_cols) > 1 else 0)
        st.plotly_chart(px.scatter(df, x=x, y=y), use_container_width=True)
    elif chart_type == "Heatmap":
        st.plotly_chart(px.imshow(df.corr(numeric_only=True), text_auto=True), use_container_width=True, key="heatmap2")
    elif chart_type == "Pair Plot":
        pair_cols = st.multiselect("Select numeric columns for Pair Plot", num_cols, default=num_cols[:3])
        if len(pair_cols) >= 2:
            fig = px.scatter_matrix(df, dimensions=pair_cols, title="Pair Plot", height=600)
            st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")
    st.subheader("🧠 Python Console (df only)")
    py_code = st.text_area("Code using 'df'", "# Example: df = df.drop_duplicates()")
    if st.button("▶️ Run df code"):
        try:
            local_env = {"df": df}
            exec(py_code, {}, local_env)
            df = local_env["df"]
            st.success("Code executed successfully.")
        except Exception as e:
            st.error(f"Python Error: {e}")

    st.subheader("🖥️ CMD Python Console")
    cmd_code = st.text_input(">>>", placeholder="Type Python expression here...")
    if st.button("Run CMD"):
        try:
            result = eval(cmd_code)
            st.code(result)
        except Exception as e:
            st.error(f"CMD Error: {e}")

    st.subheader("📥 Download Processed Data")
    st.download_button("⬇️ CSV", df.to_csv(index=False).encode(), "processed.csv", "text/csv")

    out_excel = BytesIO()
    with pd.ExcelWriter(out_excel, engine="xlsxwriter") as writer:
        df.to_excel(writer, index=False, sheet_name="Sheet1")
    st.download_button("⬇️ Excel", out_excel.getvalue(), "processed.xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

    st.download_button("⬇️ JSON", df.to_json(orient="records"), "processed.json", "application/json")

    def get_sqlite_bytes(df):
        temp_db = "output.sqlite"
        conn = sqlite3.connect(temp_db)
        df.to_sql("cleaned_data", conn, if_exists="replace", index=False)
        conn.close()
        with open(temp_db, "rb") as f:
            data = f.read()
        os.remove(temp_db)
        return data

    db_data = get_sqlite_bytes(df)
    st.download_button("⬇️ SQLite", db_data, "processed.sqlite", "application/octet-stream")
