import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime
import calendar
import streamlit as st

# Set page configuration
st.set_page_config(
    page_title="Personal Expense Tracker Dashboard",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Add title and description
st.title("Personal Expense Tracker Dashboard")
st.markdown("### Expense and Income Analysis from November 2021- March 2022")
st.markdown("---")

# Load data
@st.cache_data
def load_data():
    # For the actual app, you would use:
    # data = pd.read_csv('expense_data_1.csv')
    
    # For this example, we're using the data from the context
    data = pd.read_csv('expense_data_1.csv')
    
    # Convert Date to datetime
    data['Date'] = pd.to_datetime(data['Date'], format='%m/%d/%Y %H:%M')
    
    # Create new fields (calculated fields)
    data['Year'] = data['Date'].dt.year
    data['Month'] = data['Date'].dt.month
    data['Month_Name'] = data['Date'].dt.strftime('%b')
    data['Day'] = data['Date'].dt.day
    data['Weekday'] = data['Date'].dt.weekday
    data['Weekday_Name'] = data['Date'].dt.strftime('%a')
    
    # Calculate transaction amount (considering Income/Expense)
    data['Transaction_Amount'] = data.apply(
        lambda row: row['Amount'] if row['Income/Expense'] == 'Income' else -row['Amount'], 
        axis=1
    )
    
    # Create a new field for simplified categories
    data['Main_Category'] = data['Category'].fillna('Uncategorized')
    
    # Calculate running balance
    data = data.sort_values('Date')
    data['Running_Balance'] = data['Transaction_Amount'].cumsum()
    
    # Create Month-Year field for better grouping
    data['Month_Year'] = data['Date'].dt.strftime('%b-%Y')
    
    # Order months chronologically
    month_order = ['Nov-2021', 'Dec-2021', 'Jan-2022', 'Feb-2022', 'Mar-2022']
    data['Month_Year_Ordered'] = pd.Categorical(
        data['Month_Year'],
        categories=month_order,
        ordered=True
    )
    
    return data

# Load the data
try:
    data = load_data()
    # Debug: Print column names to verify
    st.sidebar.markdown("### Debug Information")
    with st.sidebar.expander("Show Data Information"):
        st.write("Data columns:", data.columns.tolist())
        st.write("Income/Expense values:", data['Income/Expense'].unique())
        data_sample = data.head(3)
        st.write("Sample data:", data_sample)
except Exception as e:
    st.error(f"Error loading data: {e}")
    st.stop()

# Sidebar for filters
st.sidebar.header("Filters")

# Date range filter
min_date = data['Date'].min().date()
max_date = data['Date'].max().date()
date_range = st.sidebar.date_input(
    "Select Date Range",
    [min_date, max_date],
    min_value=min_date,
    max_value=max_date
)

# Category filter
all_categories = sorted(data['Category'].dropna().unique())
# เป็น (แบบที่ 1 - ใช้ลิสต์ว่าง)
selected_categories = st.sidebar.multiselect(
    "Select Categories",
    options=all_categories,
    default=[]  # เริ่มต้นไม่มีหมวดหมู่ที่เลือก
)

# Filter data based on selections
if len(date_range) == 2:
    start_date, end_date = date_range
    filtered_data = data[(data['Date'].dt.date >= start_date) & 
                         (data['Date'].dt.date <= end_date)]
else:
    filtered_data = data

if selected_categories:
    filtered_data = filtered_data[filtered_data['Category'].isin(selected_categories)]
else:
    # เมื่อไม่มีหมวดหมู่ถูกเลือก ให้แสดงข้อมูลทั้งหมด (ไม่ต้องทำอะไรเพิ่ม)
    pass

# Key metrics
st.header("Key Financial Metrics")

# Calculate metrics
total_income = filtered_data[filtered_data['Income/Expense'] == 'Income']['Amount'].sum()
total_expense = filtered_data[filtered_data['Income/Expense'] == 'Expense']['Amount'].sum()
net_savings = total_income - total_expense
savings_rate = (net_savings / total_income * 100) if total_income > 0 else 0

# Display metrics in columns
col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Income", f"₹{total_income:,.2f}")
col2.metric("Total Expenses", f"₹{total_expense:,.2f}")
col3.metric("Net Savings", f"₹{net_savings:,.2f}")
col4.metric("Savings Rate", f"{savings_rate:.1f}%")

st.markdown("---")

# Create row for first set of visualizations
viz_row1 = st.columns(2)

# VISUALIZATION 1: Monthly Income vs Expenses
with viz_row1[0]:
    st.subheader("Monthly Income vs Expenses")
    
    # Prepare data - Convert Month_Year_Ordered to string to avoid categorical issues
    monthly_summary = filtered_data.groupby(['Month_Year', 'Income/Expense'])['Amount'].sum().reset_index()
    
    # Create a pivot table without using categorical column
    monthly_pivot = monthly_summary.pivot(
        index='Month_Year', 
        columns='Income/Expense', 
        values='Amount'
    ).reset_index().fillna(0)
    
    # Now map the month order for plotting
    month_order = ['Nov-2021', 'Dec-2021', 'Jan-2022', 'Feb-2022', 'Mar-2022']
    monthly_pivot['Month_Order'] = pd.Categorical(
        monthly_pivot['Month_Year'],
        categories=month_order,
        ordered=True
    )
    
    # Sort by the ordered column
    monthly_pivot = monthly_pivot.sort_values('Month_Order')
    
    # Ensure both Income and Expense columns exist
    if 'Income' not in monthly_pivot.columns:
        monthly_pivot['Income'] = 0
    if 'Expense' not in monthly_pivot.columns:
        monthly_pivot['Expense'] = 0
    
    # Calculate net savings
    monthly_pivot['Net'] = monthly_pivot['Income'] - monthly_pivot['Expense']
    
    # Create Plotly figure
    fig = go.Figure()
    
    # Add bar for income
    fig.add_trace(go.Bar(
        x=monthly_pivot['Month_Year'],
        y=monthly_pivot['Income'],
        name='Income',
        marker_color='#2ecc71'
    ))
    
    # Add bar for expense
    fig.add_trace(go.Bar(
        x=monthly_pivot['Month_Year'],
        y=monthly_pivot['Expense'],
        name='Expense',
        marker_color='#e74c3c'
    ))
    
    # Add line for net
    fig.add_trace(go.Scatter(
        x=monthly_pivot['Month_Year'],
        y=monthly_pivot['Net'],
        name='Net Savings',
        line=dict(color='#3498db', width=3),
        mode='lines+markers'
    ))
    
    # Update layout
    fig.update_layout(
        barmode='group',
        xaxis_title='Month',
        yaxis_title='Amount (₹)',
        legend_title='Type',
        hovermode='x unified',
        height=400,
        margin=dict(l=10, r=10, t=10, b=10)
    )
    
    st.plotly_chart(fig, use_container_width=True)

# VISUALIZATION 2: Expense Distribution by Category
with viz_row1[1]:
    st.subheader("Expense Distribution by Category")
    
    # Filter for expenses only
    expense_data = filtered_data[filtered_data['Income/Expense'] == 'Expense']
    
    # Group by category
    category_expenses = expense_data.groupby('Category')['Amount'].sum().reset_index()
    category_expenses = category_expenses.sort_values('Amount', ascending=False)
    
    # Create figure
    fig = px.pie(
        category_expenses,
        values='Amount',
        names='Category',
        title='',
        hole=0.4,
        color_discrete_sequence=px.colors.qualitative.Pastel
    )
    
    # Update layout
    fig.update_layout(
        legend_title='Category',
        height=400,
        margin=dict(l=10, r=10, t=10, b=10)
    )
    
    # Add total in the center
    fig.add_annotation(
        text=f"₹{expense_data['Amount'].sum():,.0f}",
        x=0.5, y=0.5,
        font_size=20,
        showarrow=False
    )
    
    st.plotly_chart(fig, use_container_width=True)

# Create row for second set of visualizations
viz_row2 = st.columns(2)

# VISUALIZATION 3: Daily Spending Pattern
with viz_row2[0]:
    st.subheader("Daily Spending Pattern")
    
    # Group by weekday
    weekday_expenses = expense_data.groupby('Weekday_Name')['Amount'].agg(['sum', 'mean', 'count']).reset_index()
    
    # Order by weekday
    weekday_order = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
    weekday_expenses['Weekday_Name'] = pd.Categorical(
        weekday_expenses['Weekday_Name'],
        categories=weekday_order,
        ordered=True
    )
    weekday_expenses = weekday_expenses.sort_values('Weekday_Name')
    
    # Create subplot with dual y-axis
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    
    # Add bars for total amount
    fig.add_trace(
        go.Bar(
            x=weekday_expenses['Weekday_Name'],
            y=weekday_expenses['sum'],
            name='Total Spent',
            marker_color='#3498db'
        ),
        secondary_y=False
    )
    
    # Add line for transaction count
    fig.add_trace(
        go.Scatter(
            x=weekday_expenses['Weekday_Name'],
            y=weekday_expenses['count'],
            name='Transaction Count',
            line=dict(color='#e67e22', width=3),
            mode='lines+markers'
        ),
        secondary_y=True
    )
    
    # Update layout
    fig.update_layout(
        xaxis_title='Day of Week',
        hovermode='x unified',
        legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1),
        height=400,
        margin=dict(l=10, r=10, t=30, b=10)
    )
    
    # Update y-axes
    fig.update_yaxes(title_text="Total Amount (₹)", secondary_y=False)
    fig.update_yaxes(title_text="Transaction Count", secondary_y=True)
    
    st.plotly_chart(fig, use_container_width=True)
    
# VISUALIZATION 4: Running Balance Over Time
with viz_row2[1]:
    st.subheader("Running Balance Over Time")
    
    # Create figure
    fig = px.line(
        filtered_data,
        x='Date',
        y='Running_Balance',
        title='',
        color_discrete_sequence=['#3498db']
    )
    
    # Add markers for significant changes
    significant_changes = []
    threshold = filtered_data['Transaction_Amount'].std() * 2
    
    for i in range(1, len(filtered_data)):
        if abs(filtered_data['Transaction_Amount'].iloc[i]) > threshold:
            significant_changes.append(i)
    
    # Add markers
    if significant_changes:  # Check if list is not empty
        fig.add_trace(
            go.Scatter(
                x=filtered_data.iloc[significant_changes]['Date'],
                y=filtered_data.iloc[significant_changes]['Running_Balance'],
                mode='markers',
                marker=dict(size=8, color='#e74c3c'),
                name='Significant Transaction'
            )
        )
    
    # Update layout
    fig.update_layout(
        xaxis_title='Date',
        yaxis_title='Balance (₹)',
        hovermode='x unified',
        height=400,
        margin=dict(l=10, r=10, t=10, b=10)
    )
    
    st.plotly_chart(fig, use_container_width=True)

# Create row for third set of visualizations
viz_row3 = st.columns(2)

# VISUALIZATION 5: Top 10 Expense Items
with viz_row3[0]:
    st.subheader("Top Expense Transactions")
    
    # Get top expenses
    top_expenses = expense_data.sort_values('Amount', ascending=False).head(10)
    
    # Handle empty Note field
    top_expenses['Note'] = top_expenses['Note'].fillna('Unlabeled Transaction')
    
    # Create horizontal bar chart
    fig = px.bar(
        top_expenses,
        y='Note',
        x='Amount',
        orientation='h',
        color='Category',
        text='Amount',
        title='',
        color_discrete_sequence=px.colors.qualitative.Pastel
    )
    
    # Update layout
    fig.update_layout(
        xaxis_title='Amount (₹)',
        yaxis_title='',
        height=400,
        margin=dict(l=10, r=10, t=10, b=10)
    )
    
    # Format text labels
    fig.update_traces(texttemplate='₹%{x:.0f}', textposition='outside')
    
    st.plotly_chart(fig, use_container_width=True)

# VISUALIZATION 6: Income Sources - Fixed version
with viz_row3[1]:
    st.subheader("Income Sources")
    
    # Debug information
    with st.expander("Debug Income Data"):
        st.write(f"Total records in filtered data: {len(filtered_data)}")
        st.write(f"Income/Expense column values: {filtered_data['Income/Expense'].unique()}")
    
    # Filter for income only - using case insensitive comparison
    income_data = filtered_data[filtered_data['Income/Expense'].str.strip().str.upper() == 'INCOME']
    
    # Debug information
    with st.expander("Income Data Details"):
        st.write(f"Records matching 'Income': {len(income_data)}")
        if not income_data.empty:
            st.write("Sample income data:", income_data.head(3))
    
    # Check if income data exists
    if not income_data.empty:
        # Group by source (using Note field)
        income_data['Note'] = income_data['Note'].fillna('Other Income')
        income_sources = income_data.groupby('Note')['Amount'].sum().reset_index()
        income_sources = income_sources.sort_values('Amount', ascending=False)
        
        # Debug group results
        with st.expander("Income Sources Grouped"):
            st.write(f"Number of income sources: {len(income_sources)}")
            st.write("Income sources:", income_sources)
        
        # Get top sources and combine the rest
        if len(income_sources) > 5:
            top_sources = income_sources.head(5)
            other_sources = pd.DataFrame({
                'Note': ['Other'],
                'Amount': [income_sources.iloc[5:]['Amount'].sum()]
            })
            plot_data = pd.concat([top_sources, other_sources]).reset_index(drop=True)
        else:
            plot_data = income_sources
        
        # Create both treemap and bar chart for comparison
        tab1, tab2 = st.tabs(["Treemap", "Bar Chart"])
        
        with tab1:
            try:
                # Create treemap
                fig = px.treemap(
                    plot_data,
                    path=['Note'],
                    values='Amount',
                    title='',
                    color_discrete_sequence=px.colors.sequential.Viridis
                )
                
                # Update layout
                fig.update_layout(
                    height=400,
                    margin=dict(l=10, r=10, t=10, b=10)
                )
                
                # Format text
                fig.update_traces(texttemplate='%{label}<br>₹%{value:,.0f}')
                
                st.plotly_chart(fig, use_container_width=True)
            except Exception as e:
                st.error(f"Error creating treemap: {e}")
                st.write("Trying fallback visualization...")
                st.bar_chart(plot_data.set_index('Note')['Amount'])
                
        with tab2:
            # Backup visualization using Streamlit's native bar chart
            st.bar_chart(plot_data.set_index('Note')['Amount'])
    else:
        st.info("No income data available for the selected period. Please check that your data contains 'Income' entries.")

# Create row for fourth set of visualizations
viz_row4 = st.columns(2)

# VISUALIZATION 7: Monthly Category Breakdown
with viz_row4[0]:
    st.subheader("Monthly Category Breakdown")
    
    # Filter expense data
    if not expense_data.empty:
        # Use Month_Year instead of Month_Year_Ordered to avoid categorical issues
        expense_month_cat = expense_data.groupby(['Month_Year', 'Category'])['Amount'].sum().reset_index()
        
        # Add ordered category for proper month ordering
        month_order = ['Nov-2021', 'Dec-2021', 'Jan-2022', 'Feb-2022', 'Mar-2022']
        expense_month_cat['Month_Order'] = pd.Categorical(
            expense_month_cat['Month_Year'],
            categories=month_order,
            ordered=True
        )
        
        # Sort by the ordered column
        expense_month_cat = expense_month_cat.sort_values('Month_Order')
        
        # Create stacked bar chart
        fig = px.bar(
            expense_month_cat,
            x='Month_Year',
            y='Amount',
            color='Category',
            title='',
            color_discrete_sequence=px.colors.qualitative.Pastel,
            category_orders={"Month_Year": month_order}
        )
        
        # Update layout
        fig.update_layout(
            xaxis_title='Month',
            yaxis_title='Amount (₹)',
            legend_title='Category',
            hovermode='x unified',
            height=400,
            margin=dict(l=10, r=10, t=10, b=10)
        )
        
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No expense data available for the selected period.")

# VISUALIZATION 8: Expense Heatmap
with viz_row4[1]:
    st.subheader("Expense Heatmap (Day of Week × Hour)")
    
    # Check if expense data exists
    if not expense_data.empty:
        # Extract hour from Date
        expense_data['Hour'] = expense_data['Date'].dt.hour
        
        # Create heatmap data
        heatmap_data = expense_data.groupby(['Weekday', 'Hour'])['Amount'].sum().reset_index()
        
        # Check if we have enough data for a meaningful heatmap
        if not heatmap_data.empty and heatmap_data['Hour'].nunique() > 1:
            # Create pivot table
            heatmap_pivot = heatmap_data.pivot_table(
                index='Weekday',
                columns='Hour',
                values='Amount',
                aggfunc='sum'
            ).fillna(0)
            
            # Make sure the index is complete
            full_index = pd.Index(range(7))
            heatmap_pivot = heatmap_pivot.reindex(full_index, fill_value=0)
            
            # Convert weekday numbers to names
            weekday_names = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
            
            # Create heatmap
            fig = px.imshow(
                heatmap_pivot,
                labels=dict(x="Hour of Day", y="Day of Week", color="Amount (₹)"),
                x=heatmap_pivot.columns,
                y=weekday_names,
                color_continuous_scale='Viridis',
                aspect="auto"
            )
            
            # Update layout
            fig.update_layout(
                height=400,
                margin=dict(l=10, r=10, t=10, b=10)
            )
            
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Not enough time-based expense data to create a meaningful heatmap.")
    else:
        st.info("No expense data available for the selected period.")

# Additional insights section
st.markdown("---")
st.header("Key Financial Insights")

# Calculate insights
insights_col1, insights_col2 = st.columns(2)

with insights_col1:
    if not expense_data.empty and 'category_expenses' in locals() and not category_expenses.empty:
        # Top spending category
        top_category = category_expenses.iloc[0]['Category']
        top_category_amount = category_expenses.iloc[0]['Amount']
        top_category_pct = (top_category_amount / total_expense) * 100 if total_expense > 0 else 0
        
        st.info(f"💡 **Top spending category** is **{top_category}** at ₹{top_category_amount:,.2f} ({top_category_pct:.1f}% of total expenses)")
    
    if 'weekday_expenses' in locals() and not weekday_expenses.empty:
        # Highest spending day
        highest_day = weekday_expenses.loc[weekday_expenses['sum'].idxmax()]['Weekday_Name']
        highest_day_amount = weekday_expenses['sum'].max()
        
        st.info(f"💡 **Highest spending day** is **{highest_day}** with an average of ₹{highest_day_amount:,.2f}")
    
    if not expense_data.empty:
        # Largest single expense
        largest_expense = expense_data.loc[expense_data['Amount'].idxmax()]
        largest_expense_amount = largest_expense['Amount']
        largest_expense_note = largest_expense['Note'] if pd.notna(largest_expense['Note']) else 'Unlabeled Transaction'
        largest_expense_date = largest_expense['Date'].strftime('%d %b, %Y')
        
        st.info(f"💡 **Largest single expense** was ₹{largest_expense_amount:,.2f} for **{largest_expense_note}** on {largest_expense_date}")

with insights_col2:
    if not expense_data.empty:
        # Most common transaction
        expense_data['Note'] = expense_data['Note'].fillna('Unlabeled Transaction')
        common_notes = expense_data['Note'].value_counts().reset_index()
        common_notes.columns = ['Note', 'Count']
        
        if not common_notes.empty:
            top_note = common_notes.iloc[0]['Note']
            top_note_count = common_notes.iloc[0]['Count']
            
            st.info(f"💡 **Most frequent expense** is **{top_note}** with {top_note_count} transactions")
        
        # Average daily spending
        avg_daily = expense_data.groupby(expense_data['Date'].dt.date)['Amount'].sum().mean()
        
        st.info(f"💡 **Average daily spending** is ₹{avg_daily:.2f}")
    
    # Trend analysis
    if 'monthly_pivot' in locals() and len(monthly_pivot) > 1:
        if 'Expense' in monthly_pivot.columns and monthly_pivot['Expense'].iloc[0] > 0:
            trend_percentage = ((monthly_pivot['Expense'].iloc[-1] - monthly_pivot['Expense'].iloc[0]) / 
                          monthly_pivot['Expense'].iloc[0] * 100)
            trend_direction = "increased" if trend_percentage > 0 else "decreased"
            
            st.info(f"💡 **Monthly expenses** have {trend_direction} by {abs(trend_percentage):.1f}% from {monthly_pivot['Month_Year'].iloc[0]} to {monthly_pivot['Month_Year'].iloc[-1]}")

# Add explanation section
st.markdown("---")
st.header("Personal Finance Analysis")
st.markdown("""
            
แดชบอร์ดนี้วิเคราะห์การเงินส่วนบุคคลระหว่างเดือนพฤศจิกายน 2021 ถึงมีนาคม 2022 การแสดงผลข้อมูลแสดงให้เห็นรูปแบบการใช้จ่าย แหล่งที่มาของรายได้ และแนวโน้มทางการเงินตลอดช่วงเวลานี้


**ข้อสังเกตที่สำคัญ:**
1. ค่าใช้จ่ายด้านอาหารเป็นหมวดหมู่การใช้จ่ายที่ใหญ่ที่สุด
2. รายได้ไม่สม่ำเสมอ โดยมีเงินสนับสนุนส่วนใหญ่มาจากผู้ปกครอง
3. วันหยุดสุดสัปดาห์มีการใช้จ่ายสูงกว่าวันธรรมดา
4. ค่าใช้จ่ายหลักประกอบด้วยค่าเช่าและกิจกรรมทางสังคม


**คำแนะนำ:**
- กำหนดงบประมาณรายเดือนสำหรับค่าใช้จ่ายด้านอาหาร
- ติดตามค่าใช้จ่ายด้านการขนส่งซึ่งแตกต่างกันอย่างมาก
- วางแผนสำหรับค่าใช้จ่ายก้อนใหญ่ที่ไม่สม่ำเสมอ
- ติดตามแนวโน้มยอดคงเหลือเพื่อให้มั่นใจถึงเสถียรภาพทางการเงิน

""")

# Add download capability
st.markdown("---")
st.subheader("Download Analysis Report")

# Create CSV data export option
@st.cache_data
def convert_df_to_csv(df):
    return df.to_csv(index=False).encode('utf-8')

csv = convert_df_to_csv(filtered_data)
st.download_button(
    "Download Data as CSV",
    csv,
    "expense_analysis.csv",
    "text/csv",
    key='download-csv'
)

# Footer
st.markdown("---")
st.markdown("**Personal Expense Tracker Dashboard** | สร้างมาเพื่อโปรเจคต์ในรายวิชา 968-253 Data Visualization และให้เครดิตกับ Username @tharunprabu จาก Kaggle สำหรับ Dataset.")
st.markdown("**https://www.kaggle.com/datasets/tharunprabu/my-expenses-data**")
st.markdown("**คำเตือน:** แดชบอร์ดนี้มีวัตถุประสงค์เพื่อการศึกษาเท่านั้น และไม่ควรถือว่าเป็นคำแนะนำทางการเงิน")