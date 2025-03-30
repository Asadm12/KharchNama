import streamlit as st
import datetime
import pandas as pd
import plotly.express as px
from fpdf import FPDF
from PIL import Image

# Custom PDF Report Class
class PDFReport(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 16)
        self.set_text_color(57, 255, 20)  # Neon green color
        self.cell(0, 10, 'KharchNama - Budget Report', 0, 1, 'C')
        self.ln(10)
    
    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.set_text_color(57, 255, 20)
        self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')
    
    def add_summary(self, income, expenses, remaining, goal, feedback):
        # Remove emojis from feedback for PDF
        clean_feedback = feedback.encode('latin-1', 'replace').decode('latin-1')
        
        self.set_font('Arial', 'B', 12)
        self.set_text_color(57, 255, 20)
        self.cell(0, 10, 'Budget Summary', 0, 1)
        self.ln(5)
        
        self.set_font('Arial', '', 10)
        self.set_text_color(224, 224, 224)  # Light gray text
        
        self.cell(0, 10, f'Total Income: PKR {income}', 0, 1)
        self.cell(0, 10, f'Total Expenses: PKR {expenses}', 0, 1)
        self.cell(0, 10, f'Remaining Budget: PKR {remaining}', 0, 1)
        self.cell(0, 10, f'Savings Goal: PKR {goal}', 0, 1)
        self.ln(5)
        
        self.set_font('Arial', 'B', 12)
        self.cell(0, 10, clean_feedback, 0, 1)
        self.ln(10)
    
    def add_table(self, data):
        self.set_font('Arial', 'B', 12)
        self.set_text_color(57, 255, 20)
        self.cell(0, 10, 'Expense Details', 0, 1)
        self.ln(5)
        
        # Table header
        self.set_fill_color(34, 34, 34)  # Dark gray for header
        self.set_text_color(57, 255, 20)
        self.set_font('Arial', 'B', 10)
        for col in data.columns:
            self.cell(40, 10, str(col), 1, 0, 'C', 1)
        self.ln()
        
        # Table rows
        self.set_font('Arial', '', 10)
        self.set_text_color(224, 224, 224)
        for _, row in data.iterrows():
            for col in data.columns:
                # Ensure all data is properly encoded
                cell_content = str(row[col]).encode('latin-1', 'replace').decode('latin-1')
                self.cell(40, 10, cell_content, 1, 0, 'C')
            self.ln()

# Initialize session state variables
if 'income' not in st.session_state:
    st.session_state.income = 0
if 'goal' not in st.session_state:
    st.session_state.goal = 0
if 'expenses' not in st.session_state:
    st.session_state.expenses = pd.DataFrame(columns=['Date', 'Category', 'Amount (PKR)', 'Note'])
if 'current_tab' not in st.session_state:
    st.session_state.current_tab = "Budget"

# Calculator button helper functions
def add_digit(digit, target_key):
    # Handle the digit input like a calculator
    current_value = st.session_state.get(target_key, 0)
    if current_value == 0:
        st.session_state[target_key] = digit
    else:
        st.session_state[target_key] = int(str(current_value) + str(digit))

def clear_input(target_key):
    st.session_state[target_key] = 0

# Page setup
st.set_page_config(
    page_title="KharchNama",
    layout="wide",
    page_icon="💸"
)

st.markdown("""
<style>
    /* ========== 🌑 GENERAL APP STYLES ========== */
    .main {
        background-color: #111111;
        color: #E0E0E0;
    }

    /* ========== 🟢 HEADINGS ========== */
    h1 {
        color: #39FF14;
        text-shadow: 0 0 10px #39FF14;
    }

    /* Center all heading levels */
    h1, h2, h3, h4, h5, h6 {
        text-align: center !important;
    }

    /* ========== 🔡 INPUT FIELDS ========== */
    .stTextInput > div > div > input,
    .stNumberInput > div > input {
        background-color: #222222;
        color: #39FF14;
    }

    /* ========== 🟢 BUTTONS ========== */
    .stButton button {
        background-color: #39FF14;
        color: black;
        border-radius: 10px;
        font-weight: bold;
    }

    /* ========== 🧩 TABS STYLING ========== */
    .stTabs [data-baseweb="tab-list"] {
        gap: 24px;
    }

    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: pre-wrap;
        background-color: #222222;
        border-radius: 4px 4px 0px 0px;
        padding-top: 10px;
        padding-bottom: 10px;
    }

    .stTabs [aria-selected="true"] {
        background-color: #39FF14 !important;
        color: black !important;
    }
</style>
""", unsafe_allow_html=True)


# ===== Enhanced Styling =====
st.markdown("""
<style>
    .header-container {
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin-bottom: 5px;
    }

    .left-section {
        color: #a1a1a1;
        font-size: 16px;
    }

    .center-section {
        display: flex;
        align-items: center;
        gap: 20px;
        justify-content: center;
        flex-grow: 1;
    }

    .app-title {
        font-size: 48px;
        font-weight: bold;
        color: #39FF14;
        text-shadow: 0 0 10px #39FF14;
        margin: 0;
        animation: glow-pulse 2s infinite alternate;
    }

    @keyframes glow-pulse {
        from { text-shadow: 0 0 5px #39FF14; }
        to { text-shadow: 0 0 15px #39FF14, 0 0 20px #39FF14; }
    }

    .slogan-strip {
        background: rgba(0, 212, 255, 0.1);
        padding: 8px 0;
        margin: 10px 0;
        overflow: hidden;
        white-space: nowrap;
    }

    .slogan-text {
        display: inline-block;
        color: #a1f0ff;
        font-size: 18px;
        letter-spacing: 0.5px;
        padding-left: 100%;
        animation: marquee 15s linear infinite;
    }

    @keyframes marquee {
        0% { transform: translateX(0); }
        100% { transform: translateX(-100%); }
    }

    .divider-line {
        border-top: 2px solid #00d4ff;
        box-shadow: 0 0 8px #00d4ff;
        margin: 15px 0 10px 0;
    }

    /* Enhanced tab styling */
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        font-size: 16px;
        padding: 0 20px;
        transition: all 0.3s ease;
    }

    .stTabs [aria-selected="true"] {
        background-color: rgba(156, 39, 176, 0.7) !important;
        color: white !important;
    }

    .stTabs [aria-selected="false"] {
        background-color: #2a2a2a !important;
        color: #a1a1a1 !important;
    }

    .stTabs [data-baseweb="tab"]:hover {
        opacity: 0.8;
    }
</style>
""", unsafe_allow_html=True)

# Header layout with columns
col1, col2, col3 = st.columns([1, 4, 2])


with col2:
    with st.container():
        col_img, col_title = st.columns([1, 4])
        with col_img:
            st.image("data/Screenshot 2025-03-30 202342.png", use_container_width=True)  # Changed from use_column_width to use_container_width
        with col_title:
            st.markdown("<h1 class='app-title'>KharachNama – Apna Budget, Apni Marzi</h1>", unsafe_allow_html=True)

# Slogan strip
st.markdown("""
<div class="slogan-strip">
    <span class="slogan-text">
        Plan your budget • Save smart • Live better. • 
        Plan your budget • Save smart • Live better. • Plan your budget • Save smart • Live better. •
    </span>
</div>
<div class="divider-line"></div>
""", unsafe_allow_html=True)


# === Tabs ===
tab1, tab2 = st.tabs([
    "💰 Budget Manager", 
    "📊 Expense Report"
])

# === Styles ===
st.markdown("""
<style>
    .budget-container {
        background-color: #1a1a1a;
        padding: 20px;
        border-radius: 15px;
        box-shadow: 0 0 10px #2dd4bf;
        margin-bottom: 30px;
    }
    .stButton>button {
        border: 1px solid #2dd4bf;
        color: white;
        background-color: #1a1a1a;
        margin-top: 5px;
    }
    .stButton>button:hover {
        background-color: #2dd4bf;
        color: black;
    }
    .input-box {
        background-color: #1a1a1a;
        padding: 20px;
        border-radius: 15px;
        box-shadow: 0 0 15px #60a5fa;
        border: 1px solid #3b82f6;
        margin-bottom: 30px;
    }
    .input-title {
        color: #3b82f6;
        margin-bottom: 15px;
    }
    .stNumberInput input {
        color: white !important;
    }
</style>
""", unsafe_allow_html=True)

with tab1:
    st.markdown("<div style='text-align: center; font-size: 32px; margin-bottom: 30px; color: #ffffff;'>🔧 Setup Your Monthly Budget</div>", unsafe_allow_html=True)
    col1, col2 = st.columns(2)

    # Initialize session state
    if 'income' not in st.session_state:
        st.session_state['income'] = 0
    if 'goal' not in st.session_state:
        st.session_state['goal'] = 0

    def backspace(field):
        if field in st.session_state:
            current = str(st.session_state[field])
            if len(current) > 1:
                st.session_state[field] = int(current[:-1])
            elif len(current) == 1:
                st.session_state[field] = 0

    def add_digit(digit, field):
        if field in st.session_state:
            current = str(st.session_state[field])
            if current == "0":
                st.session_state[field] = digit
            else:
                st.session_state[field] = int(current + str(digit))

    # === Column 1: Income Input ===
    with col1:
        st.markdown("<h4 class='input-title'>💵 Enter your monthly income (PKR)</h4>", unsafe_allow_html=True)
        income = st.number_input(
            " ", 
            value=st.session_state.income, 
            key="income_input",
            label_visibility="collapsed",
            on_change=lambda: setattr(st.session_state, 'income', st.session_state.income_input)
        )

        rows = [
            ["1", "2", "3"],
            ["4", "5", "6"],
            ["7", "8", "9"],
            ["0", "00", "⌫"]
        ]
        for row in rows:
            r1, r2, r3 = st.columns(3)
            if r1.button(row[0], key=f"income_{row[0]}", use_container_width=True):
                add_digit(0 if row[0] == "00" else int(row[0]), "income") if row[0] != "⌫" else backspace("income")
            if r2.button(row[1], key=f"income_{row[1]}", use_container_width=True):
                add_digit(0 if row[1] == "00" else int(row[1]), "income") if row[1] != "⌫" else backspace("income")
            if r3.button(row[2], key=f"income_{row[2]}", use_container_width=True):
                add_digit(0 if row[2] == "00" else int(row[2]), "income") if row[2] != "⌫" else backspace("income")
        st.markdown("</div>", unsafe_allow_html=True)

    # === Column 2: Savings Goal Input ===
    with col2:
        st.markdown("<h4 class='input-title'>🎯 Set your monthly savings goal (PKR)</h4>", unsafe_allow_html=True)
        goal = st.number_input(
            "  ", 
            value=st.session_state.goal, 
            key="goal_input",
            label_visibility="collapsed",
            on_change=lambda: setattr(st.session_state, 'goal', st.session_state.goal_input)
        )

        for row in rows:
            r1, r2, r3 = st.columns(3)
            if r1.button(row[0], key=f"goal_{row[0]}", use_container_width=True):
                add_digit(0 if row[0] == "00" else int(row[0]), "goal") if row[0] != "⌫" else backspace("goal")
            if r2.button(row[1], key=f"goal_{row[1]}", use_container_width=True):
                add_digit(0 if row[1] == "00" else int(row[1]), "goal") if row[1] != "⌫" else backspace("goal")
            if r3.button(row[2], key=f"goal_{row[2]}", use_container_width=True):
                add_digit(0 if row[2] == "00" else int(row[2]), "goal") if row[2] != "⌫" else backspace("goal")
        st.markdown("</div>", unsafe_allow_html=True)


    # Divider
    st.markdown("---")

    st.markdown("<h2 style='text-align: center;'>💳 Add Your Expenses</h2>", unsafe_allow_html=True)

    # === Expense Input Form ===
    with st.form("expense_form", clear_on_submit=True):
        col1, col2, col3 = st.columns(3)

        with col1:
            expense_date = st.date_input("📅 Date", value=datetime.date.today())
        
        with col2:
            category = st.selectbox("📂 Category", ["Food", "Transport", "Stationery", "Utilities", "Leisure", "Other"])
        
        with col3:
            amount = st.number_input("💸 Amount (PKR)", min_value=0, step=50)

        note = st.text_input("📝 Optional Note")

        submitted = st.form_submit_button("➕ Add Expense")
        if submitted and amount > 0:
            new_expense = {
                "Date": expense_date,
                "Category": category,
                "Amount (PKR)": amount,
                "Note": note
            }
            st.session_state.expenses = pd.concat([
                st.session_state.expenses,
                pd.DataFrame([new_expense])
            ], ignore_index=True)
            st.success("Expense added!")

    # === Show Table of Expenses ===
    st.markdown("<h3 style='text-align: center;'>📋 Expense Log</h3>", unsafe_allow_html=True)
    st.dataframe(st.session_state.expenses, use_container_width=True)

    st.markdown("<h2 style='text-align: center;'>📊 Budget Dashboard</h2>", unsafe_allow_html=True)

    expenses_df = st.session_state.expenses.copy()

    # ==== PIE CHART: Expense by Category ====
    if not expenses_df.empty:
        category_chart = expenses_df.groupby("Category")["Amount (PKR)"].sum().reset_index()
        fig = px.pie(category_chart,
                    names="Category",
                    values="Amount (PKR)",
                    title="💡 Expense Breakdown by Category",
                    color_discrete_sequence=px.colors.sequential.RdPu)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No expenses to visualize yet.")

    # ==== SUMMARY STATS ====
    total_income = st.session_state.income
    savings_goal = st.session_state.goal
    total_expense = expenses_df["Amount (PKR)"].sum() if not expenses_df.empty else 0
    remaining = total_income - total_expense
    savings_achieved = max(0, total_income - total_expense)
    progress = int((savings_achieved / savings_goal) * 100) if savings_goal else 0

    # ==== Progress Bar ====
    st.markdown("<h3 style='text-align: center;'>🎯 Savings Progress</h3>", unsafe_allow_html=True)
    st.progress(min(progress, 100))

    # ==== Summary Metrics ====
    col1, col2, col3 = st.columns(3)
    col1.metric("💰 Total Income", f"PKR {total_income}")
    col2.metric("🧾 Total Expenses", f"PKR {total_expense}")
    col3.metric("📉 Remaining Budget", f"PKR {remaining}")

    # ==== Emoji Feedback ====
    st.markdown("<h3 style='text-align: center;'>💬 Financial Status</h3>", unsafe_allow_html=True)

    if total_expense > total_income:
        st.error("🔴 You're overspending! Tighten your belt. 💸")
    elif total_expense > total_income * 0.8:
        st.warning("🟡 Caution: You've spent over 80% of your income.")
    else:
        st.success("💚 You're managing well. Keep saving!")

with tab2:
    st.markdown("<h2 style='text-align: center;'>📑 Detailed Expense Report</h2>", unsafe_allow_html=True)
    
    expenses_df = st.session_state.expenses.copy()
    
    # Summary stats for the report tab
    if not expenses_df.empty:
        # Display summary stats in a nice grid
        st.markdown("<div style='background-color: #222; padding: 20px; border-radius: 10px;'>", unsafe_allow_html=True)
        summary_col1, summary_col2 = st.columns(2)
        
        with summary_col1:
            st.markdown("<h3 style='text-align: center;'>📈 Expense Summary</h3>", unsafe_allow_html=True)
            st.metric("Total Expenses", f"PKR {total_expense}")
            st.metric("Largest Expense", f"PKR {expenses_df['Amount (PKR)'].max()}" if len(expenses_df) > 0 else "N/A")
            st.metric("Average Expense", f"PKR {round(expenses_df['Amount (PKR)'].mean(), 2)}" if len(expenses_df) > 0 else "N/A")
        
        with summary_col2:
            st.markdown("<h3 style='text-align: center;'>📊 Category Analysis</h3>", unsafe_allow_html=True)
            if not expenses_df.empty:
                top_category = expenses_df.groupby('Category')['Amount (PKR)'].sum().idxmax()
                top_category_amount = expenses_df.groupby('Category')['Amount (PKR)'].sum().max()
                st.metric("Top Expense Category", top_category)
                st.metric("Amount Spent on " + top_category, f"PKR {top_category_amount}")
                st.metric("Percentage of Total", f"{round((top_category_amount/total_expense)*100, 1)}%")
        
        st.markdown("</div>", unsafe_allow_html=True)
        
        # Time-based analysis
        st.markdown("<h3 style='text-align: center;'>🕒 Expense Over Time</h3>", unsafe_allow_html=True)
        
        # Convert date to datetime for proper plotting
        expenses_df['Date'] = pd.to_datetime(expenses_df['Date'])
        expenses_by_date = expenses_df.groupby(expenses_df['Date'].dt.date)['Amount (PKR)'].sum().reset_index()
        
        # Line chart of expenses over time
        fig_time = px.line(
            expenses_by_date, 
            x='Date', 
            y='Amount (PKR)',
            title='Daily Expenses',
            markers=True,
            color_discrete_sequence=['#39FF14']
        )
        fig_time.update_layout(
            plot_bgcolor='rgba(17, 17, 17, 0.8)',
            paper_bgcolor='rgba(17, 17, 17, 0.8)',
            font_color='#E0E0E0',
            xaxis_title="Date",
            yaxis_title="Amount (PKR)"
        )
        st.plotly_chart(fig_time, use_container_width=True)
        
        # Heatmap of expenses by category and time
        if len(expenses_df['Category'].unique()) > 1 and len(expenses_df['Date'].dt.date.unique()) > 1:
            st.markdown("<h3 style='text-align: center;'>🔥 Expense Heatmap</h3>", unsafe_allow_html=True)
            pivot_data = expenses_df.pivot_table(
                index='Category', 
                columns=expenses_df['Date'].dt.date,
                values='Amount (PKR)', 
                aggfunc='sum',
                fill_value=0
            )
            
            fig_heatmap = px.imshow(
                pivot_data,
                color_continuous_scale='Viridis',
                labels=dict(x="Date", y="Category", color="Amount (PKR)")
            )
            fig_heatmap.update_layout(
                plot_bgcolor='rgba(17, 17, 17, 0.8)',
                paper_bgcolor='rgba(17, 17, 17, 0.8)',
                font_color='#E0E0E0'
            )
            st.plotly_chart(fig_heatmap, use_container_width=True)
    else:
        st.info("No expense data to generate a report. Add some expenses to see detailed analytics!")
    
    # ==== Report Generation ====
    st.markdown("---")
    st.markdown("<h3 style='text-align: center;'>📑 Export Report</h3>", unsafe_allow_html=True)

    # Improved report aesthetics description
    st.markdown("""
    <div style='background-color: #222; padding: 15px; border-radius: 8px; margin-bottom: 20px;'>
        <p style='color: #39FF14;'>⭐ The PDF report includes:</p>
        <ul style='color: #E0E0E0;'>
            <li>Complete budget summary with income and expenses</li>
            <li>Detailed breakdown of all expenses by category</li>
            <li>Financial status assessment</li>
            <li>Stylish neon-themed design matching the app</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

    # Center the button with columns
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("Generate PDF Report", use_container_width=True):
            try:
                # Generate status feedback
                if total_expense > total_income:
                    feedback = "You're overspending! Tighten your belt. [🔴]"
                elif total_expense > total_income * 0.8:
                    feedback = "Caution: You've spent over 80% of your income. [🟡]"
                else:
                    feedback = "You're managing well. Keep saving! [💚]"
                    
                # Create PDF report
                pdf = PDFReport()
                # Set page color to dark
                pdf.set_fill_color(17, 17, 17)  # Dark background matching the app
                pdf.add_page()
                pdf.rect(0, 0, 210, 297, 'F')  # Fill page with dark background
                
                pdf.add_summary(total_income, total_expense, remaining, savings_goal, feedback)
                
                if not expenses_df.empty:
                    pdf.add_table(expenses_df)
                
                # Save PDF to a temporary file
                temp_file = "total_budget_report.pdf"
                pdf.output(temp_file)
                
                # Provide download link
                with open(temp_file, "rb") as file:
                    st.download_button(
                        label="⬇️ Download PDF Report",
                        data=file,
                        file_name="KharchNama_Report.pdf",
                        mime="application/pdf",
                        use_container_width=True
                    )
                st.success("✅ Report generated successfully!")
            except Exception as e:
                st.error(f"❌ Error generating report: {e}")