import streamlit as st
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
import pandas as pd

# Constants for fees
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
    
    # Header
    header_data = [
        ["MODERN AUTOMOTIVE"],
    ]
    header_table = Table(header_data, colWidths=[400])
    header_table.setStyle(TableStyle([
        ('SPAN', (0, 0), (-1, -1)),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 14),
    ]))
    elements.append(header_table)
    elements.append(Spacer(1, 12))
    
    # Customer and vehicle details
    details_data = [
        ["DATE", data['date'], "SALES", data['salesperson']],
        ["BUYER", data['buyer'], "", ""],
        ["ADDR", data['address'], "", ""],
        ["CITY", data['city'], "STATE", data['state']],
        ["ZIP", data['zip'], "CELL PHONE", data['cell_phone']],
    ]
    details_table = Table(details_data, colWidths=[50, 200, 80, 200])
    details_table.setStyle(TableStyle([
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
    ]))
    elements.append(details_table)
    elements.append(Spacer(1, 12))
    
    # Vehicle selection and trade-in details
    selection_data = [
        ["SELECTION:", "NEW", "", "CAR", "", "DEMO"],
        ["YEAR", "MAKE", "MODEL", "STOCK NO.", "COLOR"],
        [data['year'], data['make'], data['model'], data['stock_no'], data['color']]
    ]
    selection_table = Table(selection_data, colWidths=[80, 60, 80, 80, 80, 80])
    selection_table.setStyle(TableStyle([
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
    ]))
    elements.append(selection_table)
    elements.append(Spacer(1, 12))
    
    # Detailed breakdown table
    breakdown_data = [
        ["Sales Price", f"${data['sale_price']}"],
        ["Trade Value", f"${data['trade_value']}"],
        ["Trade Payoff", f"${data['trade_payoff']}"],
        ["Dealer Service Fee", f"${data['doc_fee']}"],
        ["Sales Tax", f"${data['sales_tax']:.2f}"],
        ["Non Tax Fees", f"${NON_TAX_FEE}"],
        ["Balance", f"${data['balance']:.2f}"],
    ]
    breakdown_table = Table(breakdown_data, colWidths=[150, 100])
    breakdown_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))
    
    elements.append(breakdown_table)
    elements.append(Spacer(1, 12))
    
    # Grid data
    grid_data = [["Term"] + [f"${dp}" for dp in data['quotes'][list(data['quotes'].keys())[0]].keys()]]
    for term, payments in data['quotes'].items():
        row = [term]
        for dp, payment in payments.items():
            row.append(f"${payment:.2f}")
        grid_data.append(row)
    
    grid_table = Table(grid_data, colWidths=[70] + [70]*len(data['quotes'][list(data['quotes'].keys())[0]].keys()))
    grid_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))
    
    elements.append(grid_table)
    
    doc.build(elements)
    return filename

st.title("Quote Generator")

# Form to input deal details
with st.form(key='deal_form'):
    date = st.date_input("Date", key='date')
    salesperson = st.text_input("Sales Person", key='salesperson')
    buyer = st.text_input("Buyer", key='buyer')
    address = st.text_input("Address", key='address')
    city = st.text_input("City", key='city')
    state = st.text_input("State", key='state')
    zip_code = st.text_input("ZIP", key='zip')
    cell_phone = st.text_input("Cell Phone", key='cell_phone')
    
    year = st.text_input("Vehicle Year", key='year')
    make = st.text_input("Vehicle Make", key='make')
    model = st.text_input("Vehicle Model", key='model')
    stock_no = st.text_input("Stock No.", key='stock_no')
    color = st.text_input("Vehicle Color", key='color')
    
    sale_price = st.number_input("Sale Price of Vehicle", min_value=0, key='sale_price')
    trade_value = st.number_input("Trade Value", min_value=0, key='trade_value')
    trade_payoff = st.number_input("Trade Payoff", min_value=0, key='trade_payoff')
    doc_fee = st.number_input("Dealer Service Fee", min_value=0, value=799, key='doc_fee')
    
    down_payments = []
    default_down_payments = [1000, 2000, 3000]
    for i in range(3):
        down_payments.append(st.number_input(f"Down Payment Option {i+1}", min_value=0, value=default_down_payments[i], key=f'down_payment_{i+1}'))
    
    terms = []
    rates = {}
    for i in range(1, 4):
        term = st.number_input(f"Loan Term {i} (months)", min_value=1, value=[60, 66, 72][i-1], key=f'term_{i}')
        rate = st.number_input(f"Rate for Term {i} (%)", min_value=0.0, max_value=100.0, value=14.0, key=f'rate_{i}')
        terms.append(term)
        rates[term] = rate
    
    submit_button = st.form_submit_button(label='Generate Quote')

if submit_button:
    # Calculate monthly payments for each combination of down payment and term
    quotes = {}
    for term in terms:
        term_payments = {}
        for dp in down_payments:
            taxable_amount = sale_price - trade_value + doc_fee
            sales_tax = taxable_amount * SALES_TAX_RATE
            total_loan_amount = taxable_amount + sales_tax + NON_TAX_FEE + trade_payoff - dp
            monthly_payment = calculate_monthly_payment(total_loan_amount, rates[term], term)
            term_payments[dp] = round(monthly_payment, 2)
        quotes[term] = term_payments
    
    balance = sale_price - trade_value + doc_fee + sales_tax + NON_TAX_FEE + trade_payoff
    data = {
        'date': date,
        'salesperson': salesperson,
        'buyer': buyer,
        'address': address,
        'city': city,
        'state': state,
        'zip': zip_code,
        'cell_phone': cell_phone,
        'year': year,
        'make': make,
        'model': model,
        'stock_no': stock_no,
        'color': color,
        'sale_price': sale_price,
        'trade_value': trade_value,
        'trade_payoff': trade_payoff,
        'doc_fee': doc_fee,
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
    st.write(f"**Dealer Service Fee:** ${doc_fee}")
    st.write(f"**Sales Tax:** ${sales_tax:.2f}")
    st.write(f"**Non Tax Fees:** ${NON_TAX_FEE}")
    st.write(f"**Balance:** ${balance:.2f}")
    
    # Display the quotes in a grid format
    grid_data = []
    for term, payments in quotes.items():
        row = {'Term': term}
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
