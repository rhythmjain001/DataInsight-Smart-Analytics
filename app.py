
import streamlit as st
import pandas as pd
import plotly.express as px
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from io import BytesIO

# ---------------- PAGE CONFIG ----------------

st.set_page_config(
    page_title="DataInsight | Analytics Platform",
    page_icon="📊",
    layout="wide"
)

# ---------------- PROFESSIONAL DESIGN ----------------

st.markdown("""
<style>
.stApp {
    background-color: #F5F7FB;
}
[data-testid="stSidebar"] {
    background-color: #101B35;
}
[data-testid="stSidebar"] * {
    color: #FFFFFF !important;
}
.main-title {
    font-size: 34px;
    font-weight: 800;
    color: #172B4D;
}
.subtitle {
    color: #64748B;
    font-size: 16px;
}
.section-title {
    color: #172B4D;
    font-size: 23px;
    font-weight: 700;
}
div[data-testid="stMetric"] {
    background: white;
    border: 1px solid #E5EAF2;
    padding: 18px;
    border-radius: 12px;
    box-shadow: 0 2px 8px rgba(20,40,80,0.04);
}
.stButton > button {
    background-color: #315CF5;
    color: white;
    border-radius: 9px;
    border: none;
    padding: 9px 20px;
    font-weight: 600;
}
.stButton > button:hover {
    background-color: #2446C5;
    color: white;
}
</style>
""", unsafe_allow_html=True)

# ---------------- SIDEBAR ----------------

st.sidebar.markdown("# 📊 DataInsight")
st.sidebar.caption("SMART DATA ANALYTICS PLATFORM")

st.sidebar.divider()

page = st.sidebar.radio(
    "MAIN MENU",
    [
        "Dashboard",
        "Data Cleaning",
        "Data Analysis",
        "Visualizations",
        "Automatic Insights",
        "Business Analytics",
        "SQL Analytics",
        "Business KPI Dashboard",
        "Sales Forecasting",
        "PDF Reports"
    ]
)

st.sidebar.divider()

st.sidebar.markdown("### 📂 Upload Dataset")

uploaded_file = st.sidebar.file_uploader(
    "Upload CSV or Excel",
    type=["csv", "xlsx"]
)

st.sidebar.caption("Supported formats: CSV, XLSX")
st.sidebar.divider()
st.sidebar.markdown("**DataInsight v1.0**")
st.sidebar.caption("Built with Python, Pandas & Streamlit")

# ---------------- LOAD DATA ----------------

if uploaded_file is not None:

    try:
        if uploaded_file.name.lower().endswith(".csv"):
            raw_df = pd.read_csv(uploaded_file)
        else:
            raw_df = pd.read_excel(uploaded_file)

        if raw_df.empty:
            st.error("Your uploaded dataset is empty.")
            st.stop()

        if st.session_state.get("source_name") != uploaded_file.name:
            st.session_state["source_name"] = uploaded_file.name
            st.session_state["cleaned_df"] = raw_df.copy()

        st.session_state["raw_df"] = raw_df

    except Exception as e:
        st.error(f"Unable to read the file: {e}")
        st.stop()

# ---------------- COMMON DATA ----------------

raw_df = st.session_state.get("raw_df")
cleaned_df = st.session_state.get("cleaned_df")

# ---------------- HEADER ----------------

st.markdown(
    '<div class="main-title">DataInsight</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitle">Transform raw data into meaningful business insights.</div>',
    unsafe_allow_html=True
)

st.divider()

# ---------------- DASHBOARD ----------------

if page == "Dashboard":

    st.markdown("## 👋 Welcome to your Analytics Dashboard")

    st.write(
        "Upload your dataset from the left sidebar to begin "
        "exploring, cleaning and analysing your data."
    )

    if cleaned_df is not None:

        st.markdown("### 📊 Dataset Overview")

        c1, c2, c3, c4 = st.columns(4)

        with c1:
            st.metric("Total Records", f"{len(cleaned_df):,}")

        with c2:
            st.metric("Total Columns", len(cleaned_df.columns))

        with c3:
            st.metric(
                "Missing Values",
                int(cleaned_df.isnull().sum().sum())
            )

        with c4:
            st.metric(
                "Duplicate Rows",
                int(cleaned_df.duplicated().sum())
            )

        st.divider()

        st.markdown("### 📋 Dataset Preview")
        st.dataframe(
            cleaned_df.head(10),
            width="stretch",
            hide_index=True
        )

        numeric_cols = cleaned_df.select_dtypes(
            include="number"
        ).columns.tolist()

        if numeric_cols:
            st.markdown("### 📈 Quick Data Overview")

            selected = st.selectbox(
                "Choose a numerical column",
                numeric_cols,
                key="dashboard_column"
            )

            chart = px.histogram(
                cleaned_df,
                x=selected,
                title=f"Distribution of {selected}",
                template="plotly_white"
            )

            st.plotly_chart(chart, width="stretch")

    else:

        st.info("Upload a CSV or Excel file using the left sidebar.")

        st.markdown("### ✨ What you can do with DataInsight")

        c1, c2, c3 = st.columns(3)

        with c1:
            st.markdown("#### 🧹 Data Cleaning")
            st.write("Find missing values and remove duplicates.")

        with c2:
            st.markdown("#### 📈 Data Visualization")
            st.write("Create interactive charts and graphs.")

        with c3:
            st.markdown("#### 💡 Data Insights")
            st.write("Explore useful information from your data.")

        st.markdown("### 🚀 Your Data. Our Analytics. Better Decisions.")

# ---------------- DATA CLEANING ----------------

elif page == "Data Cleaning":

    st.markdown("## 🧹 Data Cleaning")

    if raw_df is None:
        st.warning("Please upload a dataset from the sidebar.")
    else:

        st.write("Review and clean your uploaded dataset.")

        c1, c2, c3 = st.columns(3)

        c1.metric("Original Rows", len(raw_df))
        c2.metric("Missing Cells", int(raw_df.isnull().sum().sum()))
        c3.metric("Duplicate Rows", int(raw_df.duplicated().sum()))

        st.markdown("### Missing Values by Column")

        missing_table = raw_df.isnull().sum().rename(
            "Missing Values"
        )

        st.dataframe(missing_table, width="stretch")

        method = st.selectbox(
            "Choose missing value treatment",
            [
                "Keep missing values",
                "Fill with median/mode",
                "Remove rows with missing values"
            ]
        )

        remove_duplicates = st.checkbox(
            "Remove duplicate rows",
            value=True
        )

        if st.button("✨ Clean My Dataset"):

            result = raw_df.copy()

            if method == "Fill with median/mode":

                for col in result.columns:

                    if result[col].isnull().any():

                        if pd.api.types.is_numeric_dtype(result[col]):
                            median = result[col].median()

                            if pd.notna(median):
                                result[col] = result[col].fillna(median)

                        else:
                            modes = result[col].mode()

                            if not modes.empty:
                                result[col] = result[col].fillna(
                                    modes.iloc[0]
                                )

            elif method == "Remove rows with missing values":
                result = result.dropna()

            if remove_duplicates:
                result = result.drop_duplicates()

            st.session_state["cleaned_df"] = result

            st.success("Dataset cleaned successfully!")

            st.rerun()

        current_df = st.session_state.get("cleaned_df")

        if current_df is not None:

            st.markdown("### ✅ Cleaned Dataset")

            a, b, c = st.columns(3)

            a.metric("Cleaned Rows", len(current_df))
            b.metric(
                "Remaining Missing Values",
                int(current_df.isnull().sum().sum())
            )
            c.metric(
                "Remaining Duplicates",
                int(current_df.duplicated().sum())
            )

            st.dataframe(current_df, width="stretch")

            csv_data = current_df.to_csv(
                index=False
            ).encode("utf-8")

            st.download_button(
                "⬇️ Download Cleaned CSV",
                data=csv_data,
                file_name="cleaned_dataset.csv",
                mime="text/csv"
            )
   
# ---------------- BUSINESS PERFORMANCE ----------------

elif page == "Business Analytics":

    st.markdown("## 💼 Business Performance Dashboard")

    if cleaned_df is None:
        st.warning("Please upload a dataset first.")

    else:

        st.write("Analyse sales and product performance.")

        if "Quantity" in cleaned_df.columns and "Price" in cleaned_df.columns:

            business_df = cleaned_df.copy()

            business_df["Sales"] = (
                pd.to_numeric(business_df["Quantity"], errors="coerce")
                * pd.to_numeric(business_df["Price"], errors="coerce")
            )

            total_sales = business_df["Sales"].sum()
            total_quantity = business_df["Quantity"].sum()
            average_sales = business_df["Sales"].mean()

            a, b, c = st.columns(3)

            a.metric("💰 Total Sales", f"₹{total_sales:,.2f}")
            b.metric("📦 Total Quantity", f"{total_quantity:,.0f}")
            c.metric("🛒 Average Sales", f"₹{average_sales:,.2f}")

            if "Product" in business_df.columns:

                product_sales = business_df.groupby(
                    "Product"
                )["Sales"].sum().reset_index()

                best_product = product_sales.loc[
                    product_sales["Sales"].idxmax(), "Product"
                ]

                st.success(f"🏆 Best-performing product: {best_product}")

                fig = px.bar(
                    product_sales,
                    x="Product",
                    y="Sales",
                    title="Product-wise Sales Performance",
                    template="plotly_white"
                )

                st.plotly_chart(fig, width="stretch")

            st.subheader("Sales Data")
            st.dataframe(business_df, width="stretch")

        else:
            st.info(
                "This feature requires columns named Quantity and Price."
            )
         

# ---------------- DATA ANALYSIS ----------------

elif page == "Data Analysis":
    

    st.markdown("## 📊 Statistical Data Analysis")

    if cleaned_df is None:
        st.warning("Please upload and clean a dataset first.")

    else:

        numeric_cols = cleaned_df.select_dtypes(
            include="number"
        ).columns.tolist()

        if numeric_cols:

            st.markdown("### Numerical Summary")

            st.dataframe(
                cleaned_df[numeric_cols].describe(),
                width="stretch"
            )

            selected = st.selectbox(
                "Select a numerical column",
                numeric_cols,
                key="analysis_column"
            )

            data = cleaned_df[selected].dropna()

            if not data.empty:

                a, b, c, d = st.columns(4)

                a.metric("Mean", f"{data.mean():,.2f}")
                b.metric("Median", f"{data.median():,.2f}")
                c.metric("Minimum", f"{data.min():,.2f}")
                d.metric("Maximum", f"{data.max():,.2f}")

                fig = px.histogram(
                    cleaned_df,
                    x=selected,
                    title=f"Distribution of {selected}",
                    template="plotly_white"
                )

                st.plotly_chart(fig, width="stretch")

        else:
            st.info("No numerical columns found.")

# ---------------- VISUALIZATIONS ----------------

elif page == "Visualizations":

    st.markdown("## 📈 Interactive Visualizations")

    if cleaned_df is None:
        st.warning("Please upload and clean a dataset first.")

    else:

        all_cols = cleaned_df.columns.tolist()

        numeric_cols = cleaned_df.select_dtypes(
            include="number"
        ).columns.tolist()

        st.markdown("### 1. Category-wise Bar Chart")

        if numeric_cols:

            category = st.selectbox(
                "Choose category",
                all_cols,
                key="visual_category"
            )

            value = st.selectbox(
                "Choose numerical value",
                numeric_cols,
                key="visual_value"
            )

            bar_data = cleaned_df.groupby(
                category,
                dropna=False
            )[value].sum().reset_index()

            bar_fig = px.bar(
                bar_data,
                x=category,
                y=value,
                title=f"{value} by {category}",
                template="plotly_white"
            )

            st.plotly_chart(bar_fig, width="stretch")

        else:
            st.info("No numerical columns available for a bar chart.")

        st.divider()

        st.markdown("### 2. Category Distribution")

        pie_col = st.selectbox(
            "Choose a column",
            all_cols,
            key="visual_pie"
        )

        pie_data = cleaned_df[pie_col].fillna(
            "Missing"
        ).astype(str).value_counts().reset_index()

        pie_data.columns = [pie_col, "Count"]

        pie_fig = px.pie(
            pie_data,
            names=pie_col,
            values="Count",
            title=f"Distribution of {pie_col}"
        )

        st.plotly_chart(pie_fig, width="stretch")

        st.divider()

        st.markdown("### 3. Correlation Heatmap")

        if len(numeric_cols) >= 2:

            corr = cleaned_df[numeric_cols].corr()

            heatmap = px.imshow(
                corr,
                text_auto=True,
                title="Numerical Correlation Heatmap",
                color_continuous_scale="RdBu",
                aspect="auto"
            )

            st.plotly_chart(heatmap, width="stretch")

        else:
            st.info("At least two numerical columns are needed.")

# ---------------- AUTOMATIC INSIGHTS ----------------

elif page == "Automatic Insights":

    st.markdown("## 💡 Automatic Data Insights")

    if cleaned_df is None:
        st.warning("Please upload and clean a dataset first.")

    else:

        st.markdown("### Dataset Summary")

        a, b, c = st.columns(3)

        a.metric("Total Records", len(cleaned_df))
        b.metric("Total Columns", len(cleaned_df.columns))
        c.metric(
            "Missing Values",
            int(cleaned_df.isnull().sum().sum())
        )

        st.divider()

        st.markdown("### 🔍 Data Quality")

        st.write(
            f"Duplicate records: **{cleaned_df.duplicated().sum()}**"
        )

        st.write(
            f"Complete records: **{len(cleaned_df.dropna())}**"
        )

        numeric_cols = cleaned_df.select_dtypes(
            include="number"
        ).columns.tolist()

        if numeric_cols:

            st.markdown("### 📊 Numerical Findings")

            for col in numeric_cols:

                data = cleaned_df[col].dropna()

                if not data.empty:

                    with st.expander(f"Insights for {col}"):

                        st.write(
                            f"Average: **{data.mean():,.2f}**"
                        )

                        st.write(
                            f"Highest value: **{data.max():,.2f}**"
                        )

                        st.write(
                            f"Lowest value: **{data.min():,.2f}**"
                        )

                        st.write(
                            f"Median: **{data.median():,.2f}**"
                        )

        else:
            st.info("No numerical columns available.")

        st.caption(
            "Insights are calculated from the uploaded dataset using statistical analysis."
        )
        
# ---------------- SMART BUSINESS INSIGHTS ----------------

elif page == "Smart Business Insights":

    st.markdown("## 🧠 Smart Business Insights")

    if cleaned_df is None:
        st.warning("Please upload a dataset first.")

    elif not all(col in cleaned_df.columns for col in ["Product", "Quantity", "Price"]):
        st.info("This feature requires Product, Quantity and Price columns.")

    else:
        smart_df = cleaned_df.copy()

        smart_df["Quantity"] = pd.to_numeric(
            smart_df["Quantity"], errors="coerce"
        )

        smart_df["Price"] = pd.to_numeric(
            smart_df["Price"], errors="coerce"
        )

        smart_df = smart_df.dropna(
            subset=["Product", "Quantity", "Price"]
        )

        smart_df["Sales"] = (
            smart_df["Quantity"] * smart_df["Price"]
        )

        if smart_df.empty:
            st.warning("No valid sales records found.")

        else:
            product_summary = smart_df.groupby(
                "Product"
            ).agg(
                Total_Sales=("Sales", "sum"),
                Total_Quantity=("Quantity", "sum")
            ).reset_index()

            best_product = product_summary.loc[
                product_summary["Total_Sales"].idxmax()
            ]

            popular_product = product_summary.loc[
                product_summary["Total_Quantity"].idxmax()
            ]

            st.success(
                f"🏆 Highest revenue product: {best_product['Product']} "
                f"(₹{best_product['Total_Sales']:,.2f})"
            )

            st.info(
                f"📦 Most sold product: {popular_product['Product']} "
                f"({popular_product['Total_Quantity']:,.0f} units)"
            )

            st.markdown("### 📊 Product Performance")

            st.dataframe(
                product_summary.sort_values(
                    "Total_Sales", ascending=False
                ),
                width="stretch",
                hide_index=True
            )

            st.markdown("### 💡 Business Recommendations")

            if len(product_summary) > 1:

                lowest_product = product_summary.loc[
                    product_summary["Total_Sales"].idxmin()
                ]

                st.write(
                    f"1. Review the performance of **{lowest_product['Product']}**. "
                    "Consider checking its pricing, demand and promotion."
                )

                st.write(
                    f"2. Study why **{best_product['Product']}** generates "
                    "the highest revenue."
                )

                st.write(
                    f"3. Monitor **{popular_product['Product']}** inventory "
                    "because it has the highest quantity sold."
                )

            else:
                st.write(
                    "Upload more product records to compare product performance."
                )

            st.caption(
                "Recommendations are based on observed sales data, "
                "not predictive AI."
            )
            
# ---------------- BUSINESS KPI DASHBOARD ----------------
elif page == "Business KPI Dashboard":
    st.title("📊 Business KPI Dashboard")
    st.write("Monitor important business performance indicators.")

    if cleaned_df is not None:

        required_columns = ["Product", "Quantity", "Price"]

        if all(col in cleaned_df.columns for col in required_columns):

            kpi_df = cleaned_df.copy()

            kpi_df["Revenue"] = (
                pd.to_numeric(kpi_df["Quantity"], errors="coerce")
                * pd.to_numeric(kpi_df["Price"], errors="coerce")
            )

            kpi_df = kpi_df.dropna(subset=["Revenue", "Quantity", "Price"])

            if not kpi_df.empty:

                total_revenue = kpi_df["Revenue"].sum()
                total_orders = len(kpi_df)
                total_quantity = kpi_df["Quantity"].sum()
                average_order_value = total_revenue / total_orders

                best_product = (
                    kpi_df.groupby("Product")["Revenue"]
                    .sum()
                    .idxmax()
                )

                st.subheader("📌 Key Performance Indicators")

                col1, col2, col3, col4 = st.columns(4)

                col1.metric("Total Revenue", f"₹{total_revenue:,.2f}")
                col2.metric("Total Orders", f"{total_orders:,}")
                col3.metric("Total Quantity", f"{total_quantity:,.0f}")
                col4.metric("Average Order Value", f"₹{average_order_value:,.2f}")

                st.success(f"🏆 Best Performing Product: {best_product}")

                st.divider()

                st.subheader("📈 Product-wise Revenue")

                product_revenue = (
                    kpi_df.groupby("Product")["Revenue"]
                    .sum()
                    .reset_index()
                    .sort_values("Revenue", ascending=False)
                )

                fig = px.bar(
                    product_revenue,
                    x="Product",
                    y="Revenue",
                    color="Revenue",
                    title="Revenue by Product",
                    text_auto=".2f"
                )

                st.plotly_chart(fig, width="stretch")

                st.subheader("🥧 Revenue Distribution")

                fig2 = px.pie(
                    product_revenue,
                    names="Product",
                    values="Revenue",
                    title="Product Revenue Share",
                    hole=0.4
                )

                st.plotly_chart(fig2, width="stretch")

                st.subheader("📋 Product Performance Table")
                st.dataframe(product_revenue, width="stretch")

            else:
                st.warning("No valid numeric sales data found.")

        else:
            st.warning(
                "This dashboard requires Product, Quantity and Price columns."
            )

    else:
        st.warning("Please upload a dataset first.")
        
# ---------------- SALES FORECASTING ----------------
elif page == "Sales Forecasting":
    st.title("🔮 Sales Forecasting")
    st.write("Analyze historical revenue and estimate future sales.")

    if cleaned_df is not None:

        required_columns = ["Date", "Quantity", "Price"]

        if all(col in cleaned_df.columns for col in required_columns):

            from statsmodels.tsa.holtwinters import ExponentialSmoothing

            forecast_df = cleaned_df.copy()

            forecast_df["Date"] = pd.to_datetime(
                forecast_df["Date"], errors="coerce"
            )
            forecast_df["Quantity"] = pd.to_numeric(
                forecast_df["Quantity"], errors="coerce"
            )
            forecast_df["Price"] = pd.to_numeric(
                forecast_df["Price"], errors="coerce"
            )

            forecast_df = forecast_df.dropna(
                subset=["Date", "Quantity", "Price"]
            )

            forecast_df["Revenue"] = (
                forecast_df["Quantity"] * forecast_df["Price"]
            )

            monthly_sales = (
                forecast_df.set_index("Date")["Revenue"]
                .resample("MS")
                .sum()
                .asfreq("MS", fill_value=0)
            )

            st.subheader("📊 Historical Monthly Revenue")
            st.line_chart(monthly_sales)

            if len(monthly_sales) >= 4 and (monthly_sales > 0).any():

                model = ExponentialSmoothing(
                    monthly_sales,
                    trend="add",
                    seasonal=None,
                    initialization_method="estimated"
                )

                fitted_model = model.fit()

                forecast_values = fitted_model.forecast(3)
                forecast_values = forecast_values.clip(lower=0)

                forecast_table = pd.DataFrame({
                    "Month": forecast_values.index.strftime("%B %Y"),
                    "Predicted Revenue": forecast_values.values.round(2)
                })

                st.subheader("🔮 Next 3 Months Sales Forecast")

                col1, col2 = st.columns(2)

                col1.metric(
                    "Total Forecast Revenue",
                    f"₹{forecast_values.sum():,.2f}"
                )

                col2.metric(
                    "Average Monthly Forecast",
                    f"₹{forecast_values.mean():,.2f}"
                )

                st.dataframe(forecast_table, width="stretch")

                st.subheader("📈 Actual vs Forecast Revenue")

                chart_data = pd.DataFrame({
                    "Actual Revenue": monthly_sales,
                    "Forecast Revenue": forecast_values
                })

                st.line_chart(chart_data, width="stretch")

                st.info(
                    "Forecasts are estimates based on historical revenue "
                    "using the Holt-Winters exponential smoothing method. "
                    "They are not guaranteed future sales."
                )

            else:
                st.warning(
                    "Please provide at least 4 months of historical data "
                    "with valid dates and revenue to generate a forecast."
                )

        else:
            st.warning(
                "Your dataset must contain Date, Quantity and Price columns."
            )

    else:
        st.warning("Please upload a dataset first.")




# ---------------- PDF REPORTS ----------------

elif page == "PDF Reports":

    st.markdown("## 📄 Download Analytics Report")

    if cleaned_df is None:
        st.warning("Please upload and clean a dataset first.")

    else:

        st.write(
            "Generate a PDF report containing your dataset summary "
            "and numerical statistics."
        )

        def create_pdf_report(df):

            buffer = BytesIO()

            pdf = canvas.Canvas(
                buffer,
                pagesize=letter
            )

            width, height = letter
            y = height - 55

            pdf.setTitle("DataInsight Analytics Report")

            pdf.setFont("Helvetica-Bold", 20)
            pdf.drawString(
                50, y,
                "DataInsight Analytics Report"
            )

            y -= 40

            pdf.setFont("Helvetica", 11)

            summary = [
                f"Total Rows: {len(df)}",
                f"Total Columns: {len(df.columns)}",
                f"Missing Values: {df.isnull().sum().sum()}",
                f"Duplicate Rows: {df.duplicated().sum()}"
            ]

            for line in summary:
                pdf.drawString(50, y, line)
                y -= 22

            y -= 20

            pdf.setFont("Helvetica-Bold", 14)
            pdf.drawString(50, y, "Numerical Analysis")

            y -= 28

            pdf.setFont("Helvetica", 10)

            numeric_cols = df.select_dtypes(
                include="number"
            ).columns.tolist()

            if not numeric_cols:
                pdf.drawString(
                    50, y,
                    "No numerical columns available."
                )
                y -= 20

            for col in numeric_cols:

                data = df[col].dropna()

                if data.empty:
                    continue

                lines = [
                    f"Column: {col}",
                    f"Mean: {data.mean():.2f}",
                    f"Median: {data.median():.2f}",
                    f"Minimum: {data.min():.2f}",
                    f"Maximum: {data.max():.2f}"
                ]

                for line in lines:

                    if y < 60:
                        pdf.showPage()
                        y = height - 55
                        pdf.setFont("Helvetica", 10)

                    pdf.drawString(50, y, line)
                    y -= 18

                y -= 12

            pdf.save()
            buffer.seek(0)

            return buffer

        pdf_file = create_pdf_report(cleaned_df)

        st.success("Your report is ready!")

        st.download_button(
            "📥 Download PDF Report",
            data=pdf_file,
            file_name="DataInsight_Report.pdf",
            mime="application/pdf",
            width="stretch"
        )
        # ---------------- SQL ANALYTICS ----------------


elif page == "SQL Analytics":
    st.title("🧮 SQL Analytics")
    st.write("Run SQL queries on your uploaded dataset.")

    if cleaned_df is not None:
        import duckdb

        con = duckdb.connect()
        con.register("sales", cleaned_df)

        st.subheader("Available SQL Table")
        st.info("Your dataset is available as: sales")

        query = st.text_area(
            "Write your SQL Query",
            value="SELECT * FROM sales;",
            height=150
        )

        if st.button("▶ Run SQL Query"):
            try:
                result = con.execute(query).df()
                st.success("Query executed successfully!")
                st.subheader("Query Results")
                st.dataframe(result, width="stretch")

                csv = result.to_csv(index=False).encode("utf-8")

                st.download_button(
                    "⬇ Download Results as CSV",
                    data=csv,
                    file_name="sql_results.csv",
                    mime="text/csv"
                )

            except Exception as e:
                st.error(f"SQL Error: {e}")

        st.subheader("📚 Practice SQL Queries")

        examples = {
            "Show all records": "SELECT * FROM sales;",
            "Count total records": "SELECT COUNT(*) AS Total_Records FROM sales;",
            "Find highest revenue product": """
SELECT Product, Quantity, Price,
       Quantity * Price AS Total_Sales
FROM sales
ORDER BY Total_Sales DESC
LIMIT 1;
""",
            "Find total sales": """
SELECT SUM(Quantity * Price) AS Total_Sales
FROM sales;
""",
            "Find average price": """
SELECT AVG(Price) AS Average_Price
FROM sales;
"""
        }

        selected_example = st.selectbox(
            "Choose a SQL example",
            list(examples.keys())
        )

        st.code(examples[selected_example], language="sql")

        con.close()

    else:
        st.warning("Please upload a dataset first.")


# ---------------- FOOTER ----------------

st.divider()

st.markdown(
    """
    <div style="text-align:center; color:#64748B; padding:15px;">
        <b>DataInsight</b> | Smart Data Analytics Platform<br>
        Built with Python, Pandas, Plotly and Streamlit
    </div>
    """,
    unsafe_allow_html=True
)
