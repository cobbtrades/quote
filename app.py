from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Spacer, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
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

# Function to generate PDF
def generate_pdf(data, filename='quote.pdf'):
    doc = SimpleDocTemplate(filename, pagesize=letter, topMargin=50)
    elements = []
    styles = getSampleStyleSheet()
    
    # Header
    header_data = [["MODERN AUTOMOTIVE"]]
    header_table = Table(header_data, colWidths=[400])
    header_table.setStyle(TableStyle([
        ('SPAN', (0, 0), (-1, -1)),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 14),
    ]))
    elements.append(header_table)
    elements.append(Spacer(1, 8))
    
    # Customer and vehicle details
    details_data = [
        ["DATE", data['date'], "SALES", data['salesperson']],
        ["BUYER", data['buyer'], "", ""],
        ["ADDRESS", data['address'], "EMAIL", data['email_add']],
        ["CITY", data['city'], "STATE", data['state']],
        ["ZIP", data['zip'], "PHONE", data['cell_phone']]
    ]
    details_table = Table(details_data, colWidths=[80, 150, 60, 180])
    details_table.setStyle(TableStyle([
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('BACKGROUND', (0, 0), (-1, 0), colors.whitesmoke),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica'),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
    ]))
    elements.append(details_table)
    elements.append(Spacer(1, 20))
    
    # Vehicle selection and trade-in details
    selection_data = [
        ["SELECTION", "", "", "", "", ""],
        ["YEAR", "MAKE", "MODEL", "STOCK NO.", "VIN", "MILES"],
        [data['year'], data['make'], data['model'], data['stock_no'], data['vin'], data['miles']],
        ["TRADE-IN", "", "", "", ""],
        ["YEAR", "MAKE", "MODEL", "", "VIN", "MILES"],
        [data['trade_year'], data['trade_make'], data['trade_model'], "", data['trade_vin'], data['trade_miles']]
    ]
    selection_table = Table(selection_data, colWidths=[65, 60, 80, 80, 115, 80])
    selection_table.setStyle(TableStyle([
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('BACKGROUND', (0, 3), (-1, 3), colors.grey),  # This line styles the "TRADE-IN:" row
        ('TEXTCOLOR', (0, 3), (-1, 3), colors.whitesmoke),
        ('FONTNAME', (0, 3), (-1, 3), 'Helvetica-Bold')
    ]))
    elements.append(selection_table)
    elements.append(Spacer(1, 20))
    
    # Detailed breakdown table
    breakdown_data = [
        ["Sales Price", f"${data['sale_price']:.2f}"] if data['sale_price'] != 0 else None,
        ["Rebate", f"${data['rebate']:.2f}"] if data['rebate'] != 0 else None,
        ["Trade Value", f"${data['trade_value']:.2f}"] if data['trade_value'] != 0 else None,
        ["Trade Payoff", f"${data['trade_payoff']:.2f}"] if data['trade_payoff'] != 0 else None,
        ["Dealer Service Fee", f"${data['doc_fee']:.2f}"] if data['doc_fee'] != 0 else None,
        ["Sales Tax", f"${data['sales_tax']:.2f}"] if data['sales_tax'] != 0 else None,
        ["Non Tax Fees", f"${NON_TAX_FEE:.2f}"] if NON_TAX_FEE != 0 else None,
        ["Balance", f"${data['balance']:.2f}"] if data['balance'] != 0 else None,
    ]
    # Filter out None values
    breakdown_data = [row for row in breakdown_data if row is not None]
    
    breakdown_table = Table(breakdown_data, colWidths=[150, 100])
    breakdown_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 6),
        ('BACKGROUND', (0, 1), (-1, -1), colors.whitesmoke),
    ]))
    
    # Add underlines to the values
    for row_idx in range(len(breakdown_data)):
        breakdown_table.setStyle(TableStyle([
            ('LINEBELOW', (1, row_idx), (1, row_idx), 1, colors.black)
        ]))
    
    elements.append(breakdown_table)
    elements.append(Spacer(1, 20))
    
    # Grid data
    grid_data = [["Term"] + [f"${dp:.2f}" for dp in data['quotes'][list(data['quotes'].keys())[0]].keys()]]
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
        ('BOTTOMPADDING', (0, 0), (-1, 0), 6),
        ('BACKGROUND', (0, 1), (-1, -1), colors.whitesmoke),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))
    
    elements.append(grid_table)
    disclaimer_line = Table([["* A.P.R Subject to equity and credit requirements."]], colWidths=[sum([70]*len(data['quotes'][list(data['quotes'].keys())[0]].keys())) + 70])
    disclaimer_line.setStyle(TableStyle([
        ('SPAN', (0, 0), (-1, -1)),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
    ]))
    elements.append(disclaimer_line)
    elements.append(Spacer(1, 20))

    # Add signature lines
    signature_data = [
        ["Customer Approval: ", "_________________________ ", "Management Approval: ", "_________________________"]
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
    col1, col2, col3, col4, col5 = st.columns([1, 1, 1, 1, 1])
    
    with col1:
        salesperson = st.text_input("Sales Person", key='salesperson')
        buyer = st.text_input("Buyer", key='buyer')
        address = st.text_input("Address", key='address')
        city = st.text_input("City", key='city')
        state = st.text_input("State", key='state')  # Added state field
        zip_code = st.text_input("ZIP", key='zip')
        cell_phone = st.text_input("Phone", key='cell_phone')
        email_add = st.text_input("Email", key='email_add')
        doc_fee = st.number_input("Dealer Service Fee", min_value=0.0, value=799.0, format="%.2f", key='doc_fee')
    
    with col2:
        stock_no = st.text_input("Stock No.", key='stock_no')
        year = st.text_input("Vehicle Year", key='year')
        make = st.text_input("Vehicle Make", key='make')
        model = st.text_input("Vehicle Model", key='model')
        vin = st.text_input("VIN", key='vin')
        miles = st.text_input("Vehicle Miles", key='miles')
        cost_of_vehicle = st.number_input("Cost of Vehicle", min_value=0.0, format="%.2f", key='cost_of_vehicle')
    
    with col3:
        trade_year = st.text_input("Trade Vehicle Year", key='trade_year')
        trade_make = st.text_input("Trade Vehicle Make", key='trade_make')
        trade_model = st.text_input("Trade Vehicle Model", key='trade_model')
        trade_vin = st.text_input("Trade Vehicle VIN", key='trade_vin')
        trade_miles = st.text_input("Trade Vehicle Miles", key='trade_miles')
    
    with col4:
        sale_price = st.number_input("Sale Price of Vehicle", min_value=0.0, format="%.2f", key='sale_price')
        rebate = st.number_input("Rebate", min_value=0.0, format="%.2f", key='rebate')
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
    
    submit_button = st.form_submit_button(label='Generate Quote')

if submit_button:
    # Calculate sales tax
    taxable_amount = sale_price - trade_value + doc_fee
    sales_tax = taxable_amount * SALES_TAX_RATE_NC

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
    gross_profit = sale_price - cost_of_vehicle + (acv_of_trade - trade_value)

    data = {
        'date': datetime.today().strftime('%B %d, %Y').upper(),
        'salesperson': salesperson,
        'buyer': buyer,
        'address': address,
        'city': city,
        'state': state,
        'zip': zip_code,
        'cell_phone': cell_phone,
        'email_add': email_add,
        'year': year,
        'make': make,
        'model': model,
        'stock_no': stock_no,
        'vin': vin,
        'miles': miles,
        'trade_year': trade_year,
        'trade_make': trade_make,
        'trade_model': trade_model,
        'trade_vin': trade_vin,
        'trade_miles': trade_miles,
        'sale_price': sale_price,
        'rebate': rebate,
        'trade_value': trade_value,
        'trade_payoff': trade_payoff,
        'doc_fee': doc_fee,
        'sales_tax': sales_tax,
        'balance': balance,
        'quotes': quotes,
        'rates': rates
    }
    
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

    # Display the gross profit
    color = "lightgreen" if gross_profit > 0 else "red" if gross_profit < 0 else "white"
    st.markdown(f"<p style='color:{color}; font-size:24px;'>Front Gross ${gross_profit:.2f}</p>", unsafe_allow_html=True)
    
    pdf_file = generate_pdf(data)
    
    with open(pdf_file, 'rb') as f:
        st.download_button('Download PDF Quote', f, file_name=pdf_file)
