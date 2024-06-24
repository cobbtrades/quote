import streamlit as st
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Spacer, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors

st.set_page_config(page_title="Desking App")

with open("styles.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Page title
st.title("Desking App")

def calculate_monthly_payment(principal, down_payment, annual_rate, term_months):
    if principal == 0:
        return 0
    else:
        principal = principal - down_payment
        monthly_rate = annual_rate / 100 / 12
        if monthly_rate == 0:
            payment = principal / term_months
        else:
            payment = principal * monthly_rate / (1 - (1 + monthly_rate) ** -term_months)
        return "{:.2f}".format(payment)

def calculate_balance(market_value, discount, rebate, trade_value, trade_payoff, taxes, doc_fee, non_tax_fees):
    market_value = market_value or 0
    discount = discount or 0
    rebate = rebate or 0
    trade_value = trade_value or 0
    trade_payoff = trade_payoff or 0
    taxes = taxes or 0
    doc_fee = doc_fee or 0
    non_tax_fees = non_tax_fees or 0
    balance = market_value - discount - rebate - trade_value + trade_payoff + taxes + doc_fee + non_tax_fees
    return balance

def calculate_taxes(state, market_value, discount, doc_fee, trade_value):
    market_value = market_value or 0
    discount = discount or 0
    doc_fee = doc_fee or 0
    trade_value = trade_value or 0
    taxable_amount = market_value - discount - trade_value + doc_fee
    if state == "NC":
        return taxable_amount * 0.03
    elif state == "SC":
        return 500.00
    else:
        return 0.00

def generate_pdf(data, filename='quote.pdf'):
    doc = SimpleDocTemplate(filename, pagesize=letter, topMargin=50, leftMargin=36, rightMargin=36)
    elements = []
    styles = getSampleStyleSheet()
    
    # Header
    header_data_left = [["MODERN AUTOMOTIVE"]]
    header_table_left = Table(header_data_left, colWidths=[200])
    header_table_left.setStyle(TableStyle([
        ('SPAN', (0, 0), (-1, -1)),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 14),
    ]))
    
    header_data_right = [
        ["Date:", data['date']],
        ["Salesperson:", data['salesperson']]
    ]
    header_table_right = Table(header_data_right, colWidths=[80, 150])
    header_table_right.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
    ]))
    spacer = Spacer(width=100, height=0)
    combined_header_data = [
        [header_table_left, spacer, header_table_right]
    ]
    combined_header_table = Table(combined_header_data, colWidths=[200, 100, 260])
    combined_header_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP')
    ]))
    elements.append(combined_header_table)
    elements.append(Spacer(1, 8))
    
    # Customer and vehicle details
    details_data = [
        ["CUSTOMER", data['buyer'], "", ""],
        ["", data['address'], "", ""],
        ["", f"{data['city']}, {data['state']} {data['zip']}", "", ""],
        ["EMAIL", data['email_add'], "PHONE", data['cell_phone']]
    ]
    details_table = Table(details_data, colWidths=[70, 230, 55, 160])
    details_table.setStyle(TableStyle([
        ('GRID', (0, 0), (-1, -1), 1, colors.white),
        ('BACKGROUND', (0, 0), (-1, 0), colors.white),
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
    selection_table = Table(selection_data, colWidths=[65, 65, 90, 80, 135, 80])
    selection_table.setStyle(TableStyle([
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('BACKGROUND', (0, 3), (-1, 3), colors.grey),  # This line styles the "TRADE-IN:" row
        ('TEXTCOLOR', (0, 3), (-1, 3), colors.white),
        ('FONTNAME', (0, 3), (-1, 3), 'Helvetica-Bold')
    ]))
    elements.append(selection_table)
    elements.append(Spacer(1, 20))

    # Payment Grid Data
    grid_data = [["Term"] + [f"${dp:.2f}" for dp in data['quotes'][list(data['quotes'].keys())[0]].keys()]]
    for term, payments in data['quotes'].items():
        row = [term]
        for dp, payment in payments.items():
            row.append(f"${payment:.2f}")
        grid_data.append(row)
    
    grid_table = Table(grid_data, colWidths=[75] + [75]*len(data['quotes'][list(data['quotes'].keys())[0]].keys()))
    grid_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-BoldOblique'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 6),
        ('FONTSIZE', (0, 0), (-1, 0), 12),  # Increase font size for the header row
        ('FONTSIZE', (0, 1), (-1, -1), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.white),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))

    # Detailed breakdown table
    breakdown_data = [
        ["Market Value", f"${data['sale_price']:.2f}"] if data['sale_price'] != 0 else None,
        ["Savings", f"${data['rebate'] + data['discount']:.2f}"] if data['rebate'] + data['discount'] != 0 else None,
        ["Trade Value", f"${data['trade_value']:.2f}"] if data['trade_value'] != 0 else None,
        ["Trade Payoff", f"${data['trade_payoff']:.2f}"] if data['trade_payoff'] != 0 else None,
        ["Doc Fee", f"${data['doc_fee']:.2f}"] if data['doc_fee'] != 0 else None,
        ["Sales Tax", f"${data['sales_tax']:.2f}"] if data['sales_tax'] != 0 else None,
        ["Non Tax Fees", f"${data['non_tax_fees']:.2f}"] if data['non_tax_fees'] != 0 else None,
        ["Balance", f"${data['balance']:.2f}"] if data['balance'] != 0 else None,
    ]
    # Filter out None values
    breakdown_data = [row for row in breakdown_data if row is not None]
    
    breakdown_table = Table(breakdown_data, colWidths=[100, 80])
    breakdown_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (0, -1), 'LEFT'),
        ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 6),
        ('BACKGROUND', (0, 1), (-1, -1), colors.white),
        ('VALIGN', (0, 0), (-1, -1), 'TOP')  # Align to the top
    ]))
    
    # Add underlines to the values
    for row_idx in range(len(breakdown_data)):
        breakdown_table.setStyle(TableStyle([
            ('LINEBELOW', (1, row_idx), (1, row_idx), 1, colors.black)
        ]))

    spacer = Spacer(width=20, height=0)

    # Combine the payment grid and breakdown tables side by side with spacer
    combined_data = [
        [grid_table, spacer, breakdown_table]
    ]
    
    combined_table = Table(combined_data, colWidths=[300, 20, 220], rowHeights=None, hAlign='LEFT')
    combined_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP')  # Align to the top
    ]))

    elements.append(combined_table)
    elements.append(Spacer(1, 20))
    
    disclaimer_line = Table([["* A.P.R Subject to equity and credit requirements."]], colWidths=[470])
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

finance, cash, lease = st.tabs(["Finance", "Cash", "Lease"])

with finance:
    fc, sc, tc = st.columns([3, 3, 2])
    
    with fc:
        customer = st.text_input(label="Customer", key="cust", placeholder="Customer", label_visibility='collapsed', help="Customer")
        address = st.text_input(label="Address", key="addr", placeholder="Address", label_visibility="collapsed", help="Address")
        fc2, sc2, tc2 = st.columns([3, 1, 2])
        city = fc2.text_input(label="City", key="city", placeholder="City", label_visibility="collapsed", help="City")
        state = sc2.text_input(label="State", key="state", placeholder="State", max_chars=2, label_visibility="collapsed", help="State")
        zipcode = tc2.text_input(label="Zip", key="zip", placeholder="Zip", max_chars=5, label_visibility="collapsed", help="Zip")
        email_address = fc2.text_input(label="Email", key="emailaddress", placeholder="Email", label_visibility="collapsed", help="Email")
        phone_num = tc2.text_input(label="Phone", key="phonenumber", placeholder="Phone", max_chars=12, label_visibility="collapsed", help="Phone")
    
    with sc:
        fc3, sc3 = st.columns([2, 4])
        stocknum = fc3.text_input(label="Stock #", key="stock", placeholder="Stock #", label_visibility="collapsed", help="Stock #")
        vin = sc3.text_input(label="VIN", key="vin", placeholder="VIN", max_chars=17, label_visibility="collapsed", help="VIN")
        fc4, sc4, tc4 = st.columns([1, 2, 3])
        newused = fc4.selectbox(label="N/U", options=["New", "Used", "CPO"], label_visibility="collapsed", help="N/U")
        year = sc4.text_input(label="Year", key="year", placeholder="Year", max_chars=4, label_visibility="collapsed", help="Year")
        make = tc4.text_input(label="Make", key="make", placeholder="Make", label_visibility="collapsed", help="Make")
        fc5, sc5, tc5 = st.columns([3, 1.5, 1.5])
        model = fc5.text_input(label="Model", key="model", placeholder="Model", label_visibility="collapsed", help="Model")
        trim = sc5.text_input(label="Trim", key="trim", placeholder="Trim", label_visibility="collapsed", help="Trim")
        odometer = tc5.text_input(label="Odometer", key="odometer", placeholder="Odometer", label_visibility="collapsed", help="Odometer")
    
    with tc:
        dealer = st.text_input(label="Dealership", key="dealer", placeholder="Dealership", label_visibility="collapsed", help="Dealership")
        consultant = st.text_input(label="Sales Person", key="consultant", placeholder="Sales Person", label_visibility="collapsed", help="Sales Person")
        manager = st.text_input(label="Sales Manager", key="manager", placeholder="Sales Manager", label_visibility="collapsed", help="Sales Manager")

    left_col, right_col = st.columns(2)

    with right_col:
        market_value = st.number_input(label="Market Value", key="market_value", value = None, placeholder="Market Value", label_visibility='collapsed', help="Market Value")
        discount = st.number_input(label="Discount", key="discount", value = None, placeholder="Discount", label_visibility='collapsed', help="Discount")
        rebate = st.number_input(label="Rebate", key="rebate", value = None, placeholder="Rebate", label_visibility='collapsed', help="Rebate")
        trade_value = st.number_input(label="Trade Value", key="trade_value", value = None, placeholder="Trade Value", label_visibility='collapsed', help="Trade Value")
        trade_acv = st.number_input(label="Trade ACV", key="trade_acv", value = None, placeholder="Trade ACV", label_visibility='collapsed', help="Trade ACV")
        trade_payoff = st.number_input(label="Trade Payoff", key="trade_payoff", value = None, placeholder="Trade Payoff", label_visibility='collapsed', help="Trade Payoff")
        doc_fee = st.number_input(label="Doc Fee", key="doc_fee", value = None, placeholder="Doc Fee", label_visibility='collapsed', help="Doc Fee")
        taxes = calculate_taxes(state, market_value, discount, doc_fee, trade_value)
        st.text_input(label="Taxes", key="taxes", value=f"{taxes:.2f}", label_visibility='collapsed', help="taxes")
        non_tax_fees = st.number_input(label="Non-Tax Fees", key="non_tax_fees", value = None, placeholder="Non-Tax Fees", label_visibility='collapsed', help="Non-Tax Fees")
        balance = calculate_balance(
            market_value, discount, rebate, trade_value, trade_payoff, taxes, doc_fee, non_tax_fees
        )
        st.text_input(label="Balance", key="balance", value=f"{balance:.2f}", label_visibility='collapsed', help="Balance", disabled=True)

    with left_col:
        col1, col2, col3, col4, col5 = st.columns([1,1,2,2,2])

        col1.text("")
        col1.text("")
        col1.text("")
        col1.text("")
        col1.text("")
        col2.text("")
        col2.text("")
        col2.text("")
        col2.text("")
        col2.text("")

        # Input values
        value1 = col3.number_input(label="Down Payment", key="value1", value=1000)
        value2 = col4.number_input(label="Down Payment", key="value2", value=2000)
        value3 = col5.number_input(label="Down Payment", key="value3", value=3000)
        down_payments = [value1, value2, value3]

        terms = []
        rates = []
        default_terms = [60, 66, 72]
        for i in range(3):
            term = col1.number_input(f"Term {i+1}", min_value=1, value=default_terms[i], key=f'term_{i+1}')
            rate = col2.number_input(f"Rate {i+1} (%)", min_value=0.0, max_value=100.0, value=14.0, format="%.2f", key=f'rate_{i+1}')
            terms.append(term)
            rates.append(rate)

        for i in range(3):
            for j in range(3):
                monthly_payment = calculate_monthly_payment(balance, down_payments[j], rates[i], terms[i])
                if j == 0:
                    col3.markdown(f'<div class="centered-metric"><div class="stMetric">{monthly_payment}</div></div>', unsafe_allow_html=True)
                elif j == 1:
                    col4.markdown(f'<div class="centered-metric"><div class="stMetric">{monthly_payment}</div></div>', unsafe_allow_html=True)
                elif j == 2:
                    col5.markdown(f'<div class="centered-metric"><div class="stMetric">{monthly_payment}</div></div>', unsafe_allow_html=True)
submit_button = st.button(label="Generate Quote")

if submit_button:
    quotes = {}
    for term in terms:
        term_payments = {}
        for dp in down_payments:
            monthly_payment = calculate_monthly_payment(balance, rates[term], term)
            term_payments[dp] = round(monthly_payment, 2)
        quotes[term] = term_payments
    data = {
        'date': datetime.today().strftime('%B %d, %Y').upper(),
        'salesperson': consultant,
        'buyer': customer,
        'address': address,
        'city': city,
        'state': state,
        'zip': zipcode,
        'phone_num': phone_num,
        'email_add': email_address,
        'year': year,
        'make': make,
        'model': model,
        'stock_no': stock_no,
        'vin': vin,
        'miles': odometer,
        'trade_year': trade_year,
        'trade_make': trade_make,
        'trade_model': trade_model,
        'trade_vin': trade_vin,
        'trade_miles': trade_miles,
        'sale_price': sale_price,
        'discount': discount,
        'rebate': rebate,
        'trade_value': trade_value,
        'trade_payoff': trade_payoff,
        'doc_fee': doc_fee,
        'sales_tax': taxes,
        'balance': balance,
        'quotes': quotes,
        'rates': rates
    }
    pdf_file = generate_pdf(data)
    with open(pdf_file, 'rb') as f:
        st.download_button('Download PDF Quote', f, file_name=pdf_file)
