import streamlit as st
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import pandas as pd
import numpy as np

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
    
    y = height - 160
    for i, (down_payment, terms) in enumerate(data['quotes'].items()):
        c.drawString(100, y, f"Down Payment Option {i+1}: ${down_payment}")
        y -= 20
        for term, payment in terms.items():
            c.drawString(120, y, f"Term: {term} years at {data['rates'][term]}% - Monthly Payment: ${payment:.2f}")
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
    for dp in down_payments:
        taxable_amount = sale_price - trade_value + DOC_FEE
        sales_tax = taxable_amount * SALES_TAX_RATE
        total_loan_amount = taxable_amount + sales_tax + NON_TAX_FEE - dp
        
        term_payments = {}
        for term in terms:
            monthly_payment = calculate_monthly_payment(total_loan_amount, rates[term], term)
            term_payments[term] = monthly_payment
        quotes[dp] = term_payments
    
    data = {
        'sale_price': sale_price,
        'trade_value': trade_value,
        'quotes': quotes,
        'rates': rates
    }
    
    # Display the quotes in a grid
    grid_data = []
    for dp, terms in quotes.items():
        for term, payment in terms.items():
            grid_data.append({
                'Down Payment': dp,
                'Term (years)': term,
                'Rate (%)': rates[term],
                'Monthly Payment': round(payment, 2)
            })
    
    df = pd.DataFrame(grid_data)
    st.dataframe(df)
    
    pdf_file = generate_pdf(data)
    
    st.success("Quote generated successfully!")
    with open(pdf_file, 'rb') as f:
        st.download_button('Download PDF Quote', f, file_name=pdf_file)
