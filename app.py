from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Spacer, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.enums import TA_CENTER
from reportlab.lib import colors
import pandas as pd
import streamlit as st
from datetime import datetime

# Constants for fees
NON_TAX_FEE = 106.75
SALES_TAX_RATE_NC = 0.03

# Function to calculate monthly payments
def calculate_monthly_payment(principal, annual_rate, term_months):
    monthly_rate = annual_rate / 100 / 12
    if monthly_rate == 0:
        return principal / term_months
    return principal * monthly_rate / (1 - (1 + monthly_rate) ** -term_months)

# Function to calculate lease payments
def calculate_lease_payment(sale_price, residual_percent, money_factor, term_months, down_payment):
    residual_value = sale_price * (residual_percent / 100)
    depreciation_fee = (sale_price - residual_value) / term_months
    finance_fee = (sale_price + residual_value) * money_factor
    monthly_payment = depreciation_fee + finance_fee
    total_payment = monthly_payment - down_payment / term_months
    return total_payment

def generate_pdf(data, filename='quote.pdf'):
    doc = SimpleDocTemplate(filename, pagesize=letter, topMargin=30, leftMargin=30, rightMargin=30, bottomMargin=30)
    elements = []
    styles = getSampleStyleSheet()
    
    # Header
    header_data = [
        [data['dealership_name']],
    ]
    header_table = Table(header_data, colWidths=[400])
    header_table.setStyle(TableStyle([
        ('SPAN', (0, 0), (-1, -1)),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 14),
    ]))
    elements.append(header_table)
    elements.append(Spacer(1, 8))  # Reduced spacing here
    
    # Customer and vehicle details
    details_data = [
        ["DATE", data['date'], "SALES", data['salesperson']],
        ["BUYER", data['buyer'], "", ""],
        ["ADDR", data['address'], "", ""],
        ["CITY", data['city'], "STATE", data['state']],
        ["ZIP", data['zip'], "PHONE", data['cell_phone']],
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
    elements.append(Spacer(1, 20))  # Reduced spacing here
    
    # Vehicle selection and trade-in details
    selection_data = [
        ["SELECTION:", "", "", "", ""],
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
    elements.append(Spacer(1, 15))  # Reduced spacing here
    
    # Detailed breakdown table
    breakdown_data = [
        ["Retail Price", f"${data['retail_price']:.2f}"],
        ["Sale Price", f"${data['sale_price']:.2f}"],
        ["Discount", f"${data['discount']:.2f}"],
        ["Rebate", f"${data['rebate']:.2f}"],
        ["Trade Value", f"${data['trade_value']:.2f}"],
        ["Trade Payoff", f"${data['trade_payoff']:.2f}"],
        ["Dealer Service Fee", f"${data['doc_fee']:.2f}"],
        ["Sales Tax", f"${data['sales_tax']:.2f}"],
        ["Non Tax Fees", f"${NON_TAX_FEE:.2f}"],
        ["Balance", f"${data['balance']:.2f}"],
    ]
    breakdown_table = Table(breakdown_data, colWidths=[150, 100])
    breakdown_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.whitesmoke),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))
    
    # Financing quotes header
    elements.append(Paragraph("Monthly Payments (Purchase)", styles['Normal']))
    elements.append(Spacer(1, 10))
    
    # Grid data for purchase quotes
    grid_data = [["Term"] + [f"${dp:.2f}" for dp in data['quotes'][list(data['quotes'].keys())[0]].keys()]]
    for term, payments in data['quotes'].items():
        row = [term]
        for dp, payment in payments.items():
            row.append(f"${payment:.2f}")
        grid_data.append(row)
    
    # Add disclaimer text
    grid_data.append([f"* A.P.R Subject to equity and credit requirements."] + [None]*(len(grid_data[0]) - 1))
    
    # Add blank lines
    grid_data.append([None]*len(grid_data[0]))
    grid_data.append([None]*len(grid_data[0]))

    # Grid data for lease quotes
    lease_grid_data = [["Term"] + [f"${dp:.2f}" for dp in data['lease_quotes'][list(data['lease_quotes'].keys())[0]].keys()]]
    for term, payments in data['lease_quotes'].items():
        row = [term]
        for dp, payment in payments.items():
            row.append(f"${payment:.2f}")
        lease_grid_data.append(row)
    
    # Combine purchase and lease quotes
    combined_data = grid_data + lease_grid_data
    
    combined_table = Table(combined_data, colWidths=[70] + [70]*len(data['quotes'][list(data['quotes'].keys())[0]].keys()))
    combined_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.whitesmoke),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))
    
    # Table for side-by-side layout
    side_by_side_data = [
        [breakdown_table, combined_table]
    ]
    side_by_side_table = Table(side_by_side_data, colWidths=[200, 400])
    side_by_side_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ]))
    
    elements.append(side_by_side_table)
    elements.append(Spacer(1, 3))  # Reduced spacing here

    # Calculate residual value
    residual_value = data['sale_price'] * (data.get('residual_percent', 0) / 100)
    
    # Add residual value as a centered paragraph below the lease payments grid
    residual_text = f"Residual Value: ${residual_value:.2f}"
    residual_paragraph_style = styles['Normal']
    residual_paragraph_style.alignment = TA_CENTER
    elements.append(Paragraph(residual_text, residual_paragraph_style))
    elements.append(Spacer(1, 20))  # Reduced spacing here
    
    # Add signature lines
    signature_data = [
        ["Customer Approval: ", "_________________________", "Management Approval: ", "_________________________"]
    ]
    signature_table = Table(signature_data, colWidths=[150, 100, 150, 100])
    signature_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
    ]))
    elements.append(signature_table)

    # Add paragraph
    paragraph_text = "By signing this authorization form, you certify that the above personal information is correct and accurate, and authorize the release of credit and employment information. By signing above, I provide to the dealership and its affiliates consent to communicate with me about my vehicle or any future vehicles using electronic, verbal and written communications including but not limited to email, text messaging, SMS, phone calls and direct mail. Terms and Conditions subject to credit approval. For Information Only. This is not an offer or contract for sale."
    paragraph_style = styles["Normal"]
    paragraph_style.fontSize = 6
    paragraph = Paragraph(paragraph_text, paragraph_style)
    
    elements.append(paragraph)
    
    doc.build(elements)
    return filename

st.set_page_config(layout="wide", page_title="Quote Generator", page_icon="📝")
st.title("Quote Generator")

# Form to input deal details
with st.form(key='deal_form'):
    col1, col2, col3, col4, col5, col6 = st.columns([1, 1, 1, 1, 1, 1])
    
    with col1:
        dealership_name = st.text_input("Dealership Name", key='dealership_name')
        date = st.date_input("Date", key='date', value=datetime.today())
        salesperson = st.text_input("Sales Person", key='salesperson')
        buyer = st.text_input("Buyer", key='buyer')
        address = st.text_input("Address", key='address')
        city = st.text_input("City", key='city')
    
    with col2:
        zip_code = st.text_input("ZIP", key='zip')
        cell_phone = st.text_input("Phone", key='cell_phone')
        year = st.text_input("Vehicle Year", key='year')
        make = st.text_input("Vehicle Make", key='make')
    
    with col3:
        model = st.text_input("Vehicle Model", key='model')
        stock_no = st.text_input("Stock No.", key='stock_no')
        color = st.text_input("Vehicle Color", key='color')
        cost_of_vehicle = st.number_input("Cost of Vehicle", min_value=0.0, format="%.2f", key='cost_of_vehicle')
        doc_fee = st.number_input("Dealer Service Fee", min_value=0.0, value=799.0, format="%.2f", key='doc_fee')
    
    with col4:
        retail_price = st.number_input("Retail Price of Vehicle", min_value=0.0, format="%.2f", key='retail_price')
        rebate = st.number_input("Rebate", min_value=0.0, format="%.2f", key='rebate')
        sale_price = st.number_input("Sale Price of Vehicle", min_value=0.0, format="%.2f", key='sale_price')
        trade_value = st.number_input("Trade Value", min_value=0.0, format="%.2f", key='trade_value')
        acv_of_trade = st.number_input("ACV of Trade", min_value=0.0, format="%.2f", key='acv_of_trade')
        trade_payoff = st.number_input("Trade Payoff", min_value=0.0, format="%.2f", key='trade_payoff')
    
    with col5:
        down_payments = []
        default_down_payments = [1000.0, 2000.0, 3000.0]
        for i in range(3):
            down_payments.append(st.number_input(f"Down Payment Option {i+1}", min_value=0.0, value=default_down_payments[i], format="%.2f", key=f'down_payment_{i+1}'))
        
        terms = []
        rates = {}
        for i in range(1, 4):
            term = st.number_input(f"Loan Term {i} (months)", min_value=1, value=[60, 66, 72][i-1], key=f'term_{i}')
            rate = st.number_input(f"Rate for Term {i} (%)", min_value=0.0, max_value=100.0, value=14.0, format="%.2f", key=f'rate_{i}')
            terms.append(term)
            rates[term] = rate
    
    with col6:
        lease_term = st.number_input("Lease Term (months)", min_value=1, value=36, key='lease_term')
        residual_percent = st.number_input("Residual Percent", min_value=0.0, max_value=100.0, value=50.0, format="%.2f", key='residual_percent')
        money_factor = st.number_input("Money Factor", min_value=0.0, max_value=1.0, value=0.0025, format="%.5f", key='money_factor')
    
    use_custom_tax = st.checkbox("Use Custom Sales Tax Amount")
    if use_custom_tax:
        custom_sales_tax = st.number_input("Custom Sales Tax Amount", min_value=0.0, format="%.2f", key='custom_sales_tax')
    else:
        sales_tax_rate = st.number_input("Sales Tax Rate (%)", min_value=0.0, max_value=100.0, value=3.0, format="%.2f", key='sales_tax_rate') / 100
    
    submit_button = st.form_submit_button(label='Generate Quote')

if submit_button:
    # Calculate discount
    discount = retail_price - sale_price
    
    # Calculate sales tax
    taxable_amount = sale_price - trade_value + doc_fee
    if use_custom_tax:
        sales_tax = custom_sales_tax
    else:
        sales_tax = taxable_amount * sales_tax_rate

    # Calculate monthly payments for each combination of down payment and term
    quotes = {}
    for term in terms:
        term_payments = {}
        for dp in down_payments:
            total_loan_amount = taxable_amount + sales_tax + NON_TAX_FEE + trade_payoff - dp
            monthly_payment = calculate_monthly_payment(total_loan_amount, rates[term], term)
            term_payments[dp] = round(monthly_payment, 2)
        quotes[term] = term_payments
    
    balance = sale_price - trade_value + doc_fee - rebate + sales_tax + NON_TAX_FEE + trade_payoff
    gross_profit = sale_price - cost_of_vehicle + (acv_of_trade - trade_value)  # Corrected calculation

    # Calculate lease payments for each down payment
    lease_quotes = {}
    term_payments = {}
    for dp in down_payments:
        monthly_payment = calculate_lease_payment(sale_price, residual_percent, money_factor, lease_term, dp)
        term_payments[dp] = round(monthly_payment, 2)
    lease_quotes[lease_term] = term_payments

    data = {
        'dealership_name': dealership_name,
        'date': date.strftime("%Y-%m-%d"),
        'salesperson': salesperson,
        'buyer': buyer,
        'address': address,
        'city': city,
        'state': 'NC',
        'zip': zip_code,
        'cell_phone': cell_phone,
        'year': year,
        'make': make,
        'model': model,
        'stock_no': stock_no,
        'color': color,
        'retail_price': retail_price,
        'sale_price': sale_price,
        'discount': discount,
        'rebate': rebate,
        'trade_value': trade_value,
        'trade_payoff': trade_payoff,
        'doc_fee': doc_fee,
        'sales_tax': sales_tax,
        'balance': balance,
        'quotes': quotes,
        'lease_quotes': lease_quotes,
        'rates': rates,
        'residual_percent': residual_percent
    }
    
    # Display the purchase quotes in a grid format
    st.write("### Monthly Payments Grid (Purchase)")
    grid_data = []
    for term, payments in quotes.items():
        row = {'Term': term}
        for dp, payment in payments.items():
            row[f'${dp}'] = round(payment, 2)
        grid_data.append(row)
    
    df = pd.DataFrame(grid_data)
    st.dataframe(df, hide_index=True)

    # Display the lease quotes in a grid format
    st.write("### Monthly Payments Grid (Lease)")
    lease_grid_data = []
    for term, payments in lease_quotes.items():
        row = {'Term': term}
        for dp, payment in payments.items():
            row[f'${dp}'] = round(payment, 2)
        lease_grid_data.append(row)
    
    lease_df = pd.DataFrame(lease_grid_data)
    st.dataframe(lease_df, hide_index=True)

    # Display the gross profit
    color = "lightgreen" if gross_profit > 0 else "red" if gross_profit < 0 else "white"
    st.markdown(f"<p style='color:{color}; font-size:24px;'>Front Gross ${gross_profit:.2f}</p>", unsafe_allow_html=True)
    
    pdf_file = generate_pdf(data)
    
    with open(pdf_file, 'rb') as f:
        st.download_button('Download PDF Quote', f, file_name=pdf_file)
