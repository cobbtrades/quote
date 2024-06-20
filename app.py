from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Spacer, Paragraph, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
import pandas as pd, streamlit as st

# Constants for fees
NON_TAX_FEE = 106.75
SALES_TAX_RATE = 0.03

# Function to calculate monthly payments
def calculate_monthly_payment(principal, annual_rate, term_months):
    monthly_rate = annual_rate / 100 / 12
    if monthly_rate == 0:
        return principal / term_months
    return principal * monthly_rate / (1 - (1 + monthly_rate) ** -term_months)

# Function to generate PDF
def generate_pdf(data, filename='quote.pdf'):
    doc = SimpleDocTemplate(filename, pagesize=letter, topMargin=20)
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
    elements.append(Spacer(1, 8))  # Reduced spacing here
    
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
    elements.append(Spacer(1, 8))  # Reduced spacing here
    
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
    elements.append(Spacer(1, 8))  # Reduced spacing here
    
    # Detailed breakdown table
    breakdown_data = [
        ["Sales Price", f"${data['sale_price']}"],
        ["Rebate", f"${data['rebate']}"],
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
    elements.append(Spacer(1, 8))  # Reduced spacing here
    
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
    elements.append(Spacer(1, 16))  # Reduced spacing here
    
    # Add signature lines
    signature_data = [
        ["Customer Signature", "Date"],
        ["_________________________", "_________________"]
    ]
    signature_table = Table(signature_data, colWidths=[150, 100, 150, 100])
    signature_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
    ]))
    elements.append(signature_table)

    # Add privacy notice header and line
    privacy_notice_header = Paragraph("<b>PRIVACY NOTICE</b>", styles['Normal'])
    elements.append(Spacer(1, 12))
    elements.append(privacy_notice_header)
    elements.append(HRFlowable(width="100%", thickness=1, lineCap='round', color=colors.black, spaceBefore=1, spaceAfter=1, hAlign='CENTER', vAlign='BOTTOM', dash=None))
    elements.append(Spacer(1, 8))  # Reduced spacing here
    
    # Add privacy notice with numbered items on their own lines and centered heading
    privacy_notice = """
    <ol>
        <li>We collect nonpublic information about you from the following sources:</li>
            <ul>
                <li>Information we receive from you on application or other forms;</li>
                <li>Information about your transactions with us, our affiliates or others; and</li>
                <li>Information we receive from a consumer reporting agency.</li>
            </ul>
        <li>We may disclose some or all of the information that we collect, as described above, to companies that perform services or other functions on our behalf to other financial institutions with whom we have dealer agreements. We may make such disclosures about you as a consumer, customer, or former customer.</li>
        <li>We may also disclose nonpublic personal information about you as a consumer, customer, or former customer, to non-affiliated third parties as permitted by law.</li>
        <li>We restrict access to nonpublic personal information about you to those employees who need to know that information to provide products or services to you. We maintain physical, electronic, and procedural safeguards that comply with federal regulations to guard your nonpublic personal information.</li>
    </ol>
    """
    
    privacy_style = ParagraphStyle(
        'PrivacyNotice',
        fontSize=6,
        leading=8,
        spaceBefore=8,
        spaceAfter=8,
        textColor=colors.black
    )

    privacy_paragraph = Paragraph(privacy_notice, privacy_style)
    elements.append(privacy_paragraph)
    
    doc.build(elements)
    return filename

st.set_page_config(layout="wide")
st.title("Quote Generator")

# Form to input deal details
with st.form(key='deal_form'):
    col1, col2, col3, col4, col5 = st.columns([1, 1, 1, 1, 1])
    
    with col1:
        date = st.date_input("Date", key='date')
        salesperson = st.text_input("Sales Person", key='salesperson')
        buyer = st.text_input("Buyer", key='buyer')
        address = st.text_input("Address", key='address')
        city = st.text_input("City", key='city')
    
    with col2:
        state = st.text_input("State", key='state')
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
    # Calculate monthly payments for each combination of down payment and term
    quotes = {}
    for term in terms:
        term_payments = {}
        for dp in down_payments:
            taxable_amount = sale_price - trade_value + doc_fee - rebate
            sales_tax = taxable_amount * SALES_TAX_RATE
            total_loan_amount = taxable_amount + sales_tax + NON_TAX_FEE + trade_payoff - dp
            monthly_payment = calculate_monthly_payment(total_loan_amount, rates[term], term)
            term_payments[dp] = round(monthly_payment, 2)
        quotes[term] = term_payments
    
    balance = sale_price - trade_value + doc_fee - rebate + sales_tax + NON_TAX_FEE + trade_payoff
    gross_profit = sale_price - cost_of_vehicle + (acv_of_trade - trade_value)  # Corrected calculation

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
