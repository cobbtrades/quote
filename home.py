import streamlit as st
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
import pandas as pd

# Constants for fees
DOC_FEE = 799
NON_TAX_FEE = 106.75
SALES_TAX_RATE = 0.03

# Function to calculate monthly payments
def calculate_monthly_payment(principal, rate, term):
    rate_monthly = rate / 100 / 12
    term_months = term * 12
    if rate_monthly == 0:
        return principal / term_months
    return principal * rate_monthly / (1 - (1 + rate_monthly) ** -term_months)

# Function to generate PDF
def generate_pdf(data, filename='quote.pdf'):
    doc = SimpleDocTemplate(filename, pagesize=letter)
    elements = []
    styles = getSampleStyleSheet()
    
    # Detailed breakdown table
    breakdown_data = [
        ["SALE PRICE", f"${data['sale_price']}"],
        ["TRADE VALUE", f"${data['trade_value']}"],
        ["TRADE PAYOFF", f"${data['trade_payoff']}"],
        ["DEALER SERVICE FEE", f"${DOC_FEE}"],
        ["SALES TAX", f"${data['sales_tax']:.2f}"],
        ["NON TAX FEES", f"${NON_TAX_FEE}"],
        ["BALANCE", f"${data['balance']:.2f}"],
    ]
    breakdown_table = Table(breakdown_data, colWidths=[200, 100])
    breakdown_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))
    
    # Grid data
    grid_data = [["TERM (MONTHS)"] + [f"DOWN PAYMENT ${dp}" for dp in data['quotes'][list(data['quotes'].keys())[0]].keys()]]
    for term, payments in data['quotes'].items():
        row = [f"{term * 12}"]
        for dp, payment in payments.items():
            row.append(f"${payment:.2f}")
        grid_data.append(row)
    
    grid_table = Table(grid_data, colWidths=[100] + [100] * len(data['quotes'][list(data['quotes'].keys())[0]].keys()))
    grid_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))

    # Adding header and form details
    header = Paragraph("Quote Details", styles['Title'])
    form_details = [
        ["Buyer", "The Bancorp Bank"],
        ["Address", "2127 Espey Ct, Crofton, MD 21114"],
        ["Year", "2024"],
        ["Make", "Nissan"],
        ["Model", "Frontier"],
        ["VIN", "1N6ED1CL7RN654531"],
        ["Salesperson", "Mike Smith"],
    ]
    form_table = Table(form_details, colWidths=[100, 300])
    form_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))

    elements.append(header)
    elements.append(form_table)
    elements.append(breakdown_table)
    elements.append(grid_table)
    doc.build(elements)
    return filename

st.title("Quote Generator")

# Form to input deal details
with st.form(key='deal_form'):
    sale_price = st.number_input("Sale Price of Vehicle", min_value=0, key='sale_price')
    trade_value = st.number_input("Trade Value", min_value=0, key='trade_value')
    trade_payoff = st.number_input("Trade Payoff", min_value=0, key='trade_payoff')
    
    down_payments = []
    for i in range(1, 4):
        down_payments.append(st.number_input(f"Down Payment Option {i}", min_value=0, key=f'down_payment_{i}'))
    
    terms = []
    rates = {}
    for i in range(1, 4):
        term = st.number_input(f"Loan Term {i} (years)", min_value=1, key=f'term_{i}')
        rate = st.number_input(f"Rate for Term {i} (years) (%)", min_value=0.0, max_value=100.0, key=f'rate_{i}')
        terms.append(term)
        rates[term] = rate
    
    submit_button = st.form_submit_button(label='Generate Quote')

if submit_button:
    # Calculate monthly payments for each combination of down payment and term
    quotes = {}
    for term in terms:
        term_payments = {}
        for dp in down_payments:
            taxable_amount = sale_price - trade_value + DOC_FEE
            sales_tax = taxable_amount * SALES_TAX_RATE
            total_loan_amount = taxable_amount + sales_tax + NON_TAX_FEE + trade_payoff - dp
            monthly_payment = calculate_monthly_payment(total_loan_amount, rates[term], term)
            term_payments[dp] = round(monthly_payment, 2)
        quotes[term] = term_payments
    
    balance = sale_price - trade_value + DOC_FEE + sales_tax + NON_TAX_FEE + trade_payoff
    data = {
        'sale_price': sale_price,
        'trade_value': trade_value,
        'trade_payoff': trade_payoff,
        'sales_tax': sales_tax,
        'balance': balance,
        'quotes': quotes,
        'rates': rates
    }
    
    # Display the detailed breakdown
    st.write("### Detailed Breakdown")
    st.write(f"**Sales Price:** ${sale_price}")
    st.write(f"**Trade Value:** ${trade_value}")
    st.write(f"**Trade Payoff:** ${trade_payoff}")
    st.write(f"**Dealer Service Fee:** ${DOC_FEE}")
    st.write(f"**Sales Tax:** ${sales_tax:.2f}")
    st.write(f"**Non Tax Fees:** ${NON_TAX_FEE}")
    st.write(f"**Balance:** ${balance:.2f}")
    
    # Display the quotes in a grid format
    grid_data = []
    for term, payments in quotes.items():
        row = {'Term (months)': term}
        for dp, payment in payments.items():
            row[f'${dp}'] = round(payment, 2)
        grid_data.append(row)
    
    df = pd.DataFrame(grid_data)
    st.write("### Monthly Payments Grid")
    st.dataframe(df, hide_index=True)
    
    pdf_file = generate_pdf(data)
    
    st.success("Quote generated successfully!")
    with open(pdf_file, 'rb') as f:
        st.download_button('Download PDF Quote', f, file_name=pdf_file)
