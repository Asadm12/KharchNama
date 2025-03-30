from fpdf import FPDF
from datetime import datetime

class PDFReport(FPDF):
    def header(self):
        self.set_font("Arial", "B", 14)
        self.set_text_color(57, 255, 20)  # Neon Green
        self.cell(0, 10, "KharchNama – Monthly Budget Report", ln=True, align='C')
        self.ln(10)

    def add_summary(self, income, expenses, remaining, goal, feedback):
        self.set_font("Arial", "", 12)
        self.set_text_color(255, 255, 255)
        self.cell(0, 10, f"Date: {datetime.now().strftime('%d %B %Y')}", ln=True)
        self.ln(5)
        self.cell(0, 10, f"Monthly Income: PKR {income}", ln=True)
        self.cell(0, 10, f"Total Expenses: PKR {expenses}", ln=True)
        self.cell(0, 10, f"Remaining Budget: PKR {remaining}", ln=True)
        self.cell(0, 10, f"Savings Goal: PKR {goal}", ln=True)
        self.cell(0, 10, f"Status: {feedback}", ln=True)
        self.ln(10)

    def add_table(self, df):
        self.set_font("Arial", "B", 12)
        self.set_fill_color(57, 255, 20)
        self.set_text_color(0, 0, 0)
        self.cell(40, 10, "Date", border=1, fill=True)
        self.cell(40, 10, "Category", border=1, fill=True)
        self.cell(40, 10, "Amount", border=1, fill=True)
        self.cell(70, 10, "Note", border=1, ln=True, fill=True)

        self.set_font("Arial", "", 10)
        self.set_text_color(255, 255, 255)
        for index, row in df.iterrows():
            self.cell(40, 10, str(row['Date']), border=1)
            self.cell(40, 10, str(row['Category']), border=1)
            self.cell(40, 10, f"PKR {row['Amount (PKR)']}", border=1)
            self.cell(70, 10, str(row['Note']), border=1, ln=True)