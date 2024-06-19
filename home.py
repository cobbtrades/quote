import streamlit as st
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import pandas as pd

# Constants for fees
DOC_FEE = 799
NON_TAX_FEE = 106.75
SALES_TAX_RATE = 0.03

# Function to calculate monthly payments
def calculate_monthly_payment(principal, rate, term):
    rate_monthly = rate / 100 / 12
    term_months = term * 12
    payment = principal * rate_monthly / (1 - (1 + rate_monthly) ** -term_months)
    return payment

# Function to generate PDF
def generate_pdf(data, filename='quote.pdf'):
    c = canvas.Canvas(filename, pagesize=letter)
    width, height = letter
    
    c.drawString(100, height - 100, "Vehicle Sale Quote")
    c.drawString(100, height - 120, f"Sale Price: ${data['sale_price']}")
    c.drawString(100, height - 140, f"Trade Value: ${data['trade_value']}")
    c.drawString(100, height - 160, f"Dealer Service Fee: ${DOC_FEE}")
    c.drawString(100, height - 180, f"Sales Tax: ${data['sales_tax']:.2f}")
    c.drawString(100, height - 200, f"TTL: ${NON_TAX_FEE}")
    c.drawString(100, height - 220, f"Balance: ${data['balance']:.2f}")
    
    y = height - 260
    for i, (term, payments) in enumerate(data['quotes'].items()):
        c.drawString(100, y, f"Term: {term} years")
        y -= 20
        for dp, payment in payments.items():
            c.drawString(120, y, f"Down Payment: ${dp} - Monthly Payment: ${payment:.2f}")
            y -= 20
        y -= 20
    
    c.save()
    return filename

st.title("Car Deal Quote Generator")

# Form to input deal details
with st.form(key='deal_form'):
    sale_price = st.number_input("Sale Price of Vehicle", min_value=0, key='sale_price')
    trade_value = st.number_input("Trade Value", min_value=0, key='trade_value')
    
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
            total_loan_amount = taxable_amount + sales_tax + NON_TAX_FEE - dp
            monthly_payment = calculate_monthly_payment(total_loan_amount, rates[term], term)
            term_payments[dp] = monthly_payment
        quotes[term] = term_payments
    
    balance = sale_price - trade_value + DOC_FEE + sales_tax + NON_TAX_FEE
    data = {
        'sale_price': sale_price,
        'trade_value': trade_value,
        'sales_tax': sales_tax,
        'balance': balance,
        'quotes': quotes,
        'rates': rates
    }
    
    # Display the detailed breakdown
    st.write("### Detailed Breakdown")
    st.write(f"**Sales Price:** ${sale_price}")
    st.write(f"**Trade Value:** ${trade_value}")
    st.write(f"**Dealer Service Fee:** ${DOC_FEE}")
    st.write(f"**Sales Tax:** ${sales_tax:.2f}")
    st.write(f"**TTL:** ${NON_TAX_FEE}")
    st.write(f"**Balance:** ${balance:.2f}")
    
    # Display the quotes in a grid format
    grid_data = []
    for term, payments in quotes.items():
        row = {'Term (years)': term}
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
