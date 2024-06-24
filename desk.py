import streamlit as st
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Spacer, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors

st.set_page_config(page_title="Desking App", page_icon="📝")

with open("styles.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

st.header("")

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

def calculate_lease_payment(market_value, doc_fee, non_tax_fees, doc, down_payment, rebate, money_factor, term_months, residual_percentage, trade_value, trade_payoff):
    if market_value == 0:
        return 0
    else:
        residual_value = market_value * residual_percentage
        gross_cap_cost = market_value - discount + doc_fee + non_tax_fees + doc
        cap_cost_reduction = down_payment + rebate + (trade_value - trade_payoff)
        adjusted_cap_cost = gross_cap_cost - cap_cost_reduction
        monthly_depreciation = (adjusted_cap_cost - residual_value) / term_months
        monthly_rent_charge = (adjusted_cap_cost + residual_value) * money_factor
        monthly_tax = (monthly_depreciation + monthly_rent_charge) * 0.03
        total_monthly_lease_payment = monthly_depreciation + monthly_rent_charge + monthly_tax
        return "{:.2f}".format(total_monthly_lease_payment)

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
        [data['trade_year'], data['trade_make'], data['trade_model'], "", data['trade_vin'], data['trade_miles']],
        ["TRADE-IN 2", "", "", "", ""],
        ["YEAR", "MAKE", "MODEL", "", "VIN", "MILES"],
        [data['trade_year_2'], data['trade_make_2'], data['trade_model_2'], "", data['trade_vin_2'], data['trade_miles_2']]
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
        ('FONTNAME', (0, 3), (-1, 3), 'Helvetica-Bold'),
        ('BACKGROUND', (0, 6), (-1, 6), colors.grey),  # This line styles the "TRADE-IN 2:" row
        ('TEXTCOLOR', (0, 6), (-1, 6), colors.white),
        ('FONTNAME', (0, 6), (-1, 6), 'Helvetica-Bold')
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

def render_tab(calc_payment_func, prefix, is_lease=False):
    fc, sc, tc = st.columns([3, 3, 2])
    
    with fc:
        customer = st.text_input(label="Customer", key=f"{prefix}_cust", placeholder="Customer", label_visibility='collapsed', help="Customer")
        address = st.text_input(label="Address", key=f"{prefix}_addr", placeholder="Address", label_visibility="collapsed", help="Address")
        fc2, sc2, tc2 = st.columns([3, 1, 2])
        city = fc2.text_input(label="City", key=f"{prefix}_city", placeholder="City", label_visibility="collapsed", help="City")
        state = sc2.text_input(label="State", key=f"{prefix}_state", placeholder="State", max_chars=2, label_visibility="collapsed", help="State")
        zipcode = tc2.text_input(label="Zip", key=f"{prefix}_zip", placeholder="Zip", max_chars=5, label_visibility="collapsed", help="Zip")
        email_address = fc2.text_input(label="Email", key=f"{prefix}_emailaddress", placeholder="Email", label_visibility="collapsed", help="Email")
        phone_num = tc2.text_input(label="Phone", key=f"{prefix}_phonenumber", placeholder="Phone", max_chars=12, label_visibility="collapsed", help="Phone")
    
    with sc:
        fc3, sc3 = st.columns([2, 4])
        stocknum = fc3.text_input(label="Stock #", key=f"{prefix}_stock", placeholder="Stock #", label_visibility="collapsed", help="Stock #")
        vin = sc3.text_input(label="VIN", key=f"{prefix}_vin", placeholder="VIN", max_chars=17, label_visibility="collapsed", help="VIN")
        fc4, sc4, tc4 = st.columns([1, 2, 3])
        newused = fc4.selectbox(label="N/U", options=["New", "Used", "CPO"], key=f"{prefix}_newused", label_visibility="collapsed", help="N/U")
        year = sc4.text_input(label="Year", key=f"{prefix}_year", placeholder="Year", max_chars=4, label_visibility="collapsed", help="Year")
        make = tc4.text_input(label="Make", key=f"{prefix}_make", placeholder="Make", label_visibility="collapsed", help="Make")
        fc5, sc5, tc5 = st.columns([3, 1.5, 1.5])
        model = fc5.text_input(label="Model", key=f"{prefix}_model", placeholder="Model", label_visibility="collapsed", help="Model")
        trim = sc5.text_input(label="Trim", key=f"{prefix}_trim", placeholder="Trim", label_visibility="collapsed", help="Trim")
        odometer = tc5.text_input(label="Odometer", key=f"{prefix}_odometer", placeholder="Odometer", label_visibility="collapsed", help="Odometer")
        fc6, sc6, tc6, fr6 = st.columns(4)
        fc6.markdown('<input class="label-input" type="text" value="Cost" disabled>', unsafe_allow_html=True)
        veh_cost = sc6.number_input(label="Cost", key=f"{prefix}_veh_cost", value=0, label_visibility='collapsed', help="Cost")
        tc6.markdown('<input class="label-input" type="text" value="Book Value" disabled>', unsafe_allow_html=True)
        book_value = fr6.number_input(label="Book Value", key=f"{prefix}_book_value", value=0, label_visibility='collapsed', help="Book Value")
    
    with tc:
        dealer = st.text_input(label="Dealership", key=f"{prefix}_dealer", placeholder="Dealership", label_visibility="collapsed", help="Dealership")
        consultant = st.text_input(label="Sales Person", key=f"{prefix}_consultant", placeholder="Sales Person", label_visibility="collapsed", help="Sales Person")
        manager = st.text_input(label="Sales Manager", key=f"{prefix}_manager", placeholder="Sales Manager", label_visibility="collapsed", help="Sales Manager")

    trade_values = [0] * 2
    trade_payoffs = [0] * 2
    trade_acvs = [0] * 2
    with st.expander("Enter Trade-in Details"):
        for i in range(2):  # For up to 2 trades
            # First row of trade-in details
            tt1, fc1, sc1, tc1, fr1, ft1, st1, sv1, ec1 = st.columns([1, 1, 2, 1, 2, 1, 2, 1, 4])
            col_data = f"Trade-in {i+1}"
            tt1.markdown(f'<input class="label-input" type="text" value="{col_data}" disabled>', unsafe_allow_html=True)
            fc1.markdown('<input class="label-input" type="text" value="Year" disabled>', unsafe_allow_html=True)
            trade_year = sc1.text_input(f"Trade-in {i+1} Year", key=f"{prefix}_trade_year_{i+1}", placeholder="Year", label_visibility="collapsed", max_chars=4)
            tc1.markdown('<input class="label-input" type="text" value="Make" disabled>', unsafe_allow_html=True)
            trade_make = fr1.text_input(f"Trade-in {i+1} Make", key=f"{prefix}_trade_make_{i+1}", placeholder="Make", label_visibility="collapsed")
            ft1.markdown('<input class="label-input" type="text" value="Model" disabled>', unsafe_allow_html=True)
            trade_model = st1.text_input(f"Trade-in {i+1} Model", key=f"{prefix}_trade_model_{i+1}", placeholder="Model", label_visibility="collapsed")
            sv1.markdown('<input class="label-input" type="text" value="VIN" disabled>', unsafe_allow_html=True)
            trade_vin = ec1.text_input(f"Trade-in {i+1} VIN", key=f"{prefix}_trade_vin_{i+1}", placeholder="VIN", label_visibility="collapsed", max_chars=17)
    
            # Second row of trade-in details
            tt2, fc2, sc2, tc2, fr2, ft2, st2, sv2, ec2 = st.columns([1, 1, 2, 1, 2, 1, 2, 1, 4])
            fc2.markdown('<input class="label-input" type="text" value="Miles" disabled>', unsafe_allow_html=True)
            trade_miles = sc2.text_input(f"Trade-in {i+1} Miles", key=f"{prefix}_trade_miles_{i+1}", placeholder="Miles", label_visibility="collapsed")
            tc2.markdown('<input class="label-input" type="text" value="Trade Value" disabled>', unsafe_allow_html=True)
            trade_values[i] = fr2.number_input(f"Trade-in {i+1} Value", key=f"{prefix}_trade_value_{i+1}", value=0, label_visibility="collapsed")
            ft2.markdown('<input class="label-input" type="text" value="Payoff" disabled>', unsafe_allow_html=True)
            trade_payoffs[i] = st2.number_input(f"Trade-in {i+1} Payoff", key=f"{prefix}_trade_payoff_{i+1}", value=0, label_visibility="collapsed")
            sv2.markdown('<input class="label-input" type="text" value="Trade ACV" disabled>', unsafe_allow_html=True)
            trade_acvs[i] = ec2.number_input(f"Trade-in {i+1} ACV", key=f"{prefix}_trade_acv_{i+1}", value=0, label_visibility="collapsed")
            st.divider()
    
    left_col, right_col = st.columns(2)
    
    with right_col:
        labels_col, inputs_col = st.columns([1, 4])
        
        labels_col.markdown('<input class="label-input" type="text" value="Market Value" disabled>', unsafe_allow_html=True)
        market_value = inputs_col.number_input(label="Market Value", key=f"{prefix}_market_value", value=0, label_visibility='collapsed', help="Market Value")
        
        labels_col.markdown('<input class="label-input" type="text" value="Discount" disabled>', unsafe_allow_html=True)
        discount = inputs_col.number_input(label="Discount", key=f"{prefix}_discount", value=0, label_visibility='collapsed', help="Discount")
        
        labels_col.markdown('<input class="label-input" type="text" value="Rebate" disabled>', unsafe_allow_html=True)
        rebate = inputs_col.number_input(label="Rebate", key=f"{prefix}_rebate", value=0, label_visibility='collapsed', help="Rebate")
        
        labels_col.markdown('<input class="label-input" type="text" value="Trade Value" disabled>', unsafe_allow_html=True)
        trade_value = sum(trade_values)
        inputs_col.text_input(label="Trade Value", key=f"{prefix}_trade_value", value=f"{trade_value:.2f}", label_visibility='collapsed', help="Trade Value", disabled=True)
        
        labels_col.markdown('<input class="label-input" type="text" value="Trade ACV" disabled>', unsafe_allow_html=True)
        trade_acv = sum(trade_acvs)
        inputs_col.text_input(label="Trade ACV", key=f"{prefix}_trade_acv", value=f"{trade_acv:.2f}", label_visibility='collapsed', help="Trade ACV", disabled=True)
        
        labels_col.markdown('<input class="label-input" type="text" value="Trade Payoff" disabled>', unsafe_allow_html=True)
        trade_payoff = sum(trade_payoffs)
        inputs_col.text_input(label="Trade Payoff", key=f"{prefix}_trade_payoff", value=f"{trade_payoff:.2f}", label_visibility='collapsed', help="Trade Payoff", disabled=True)
        
        labels_col.markdown('<input class="label-input" type="text" value="Doc Fee" disabled>', unsafe_allow_html=True)
        doc_fee = inputs_col.number_input(label="Doc Fee", key=f"{prefix}_doc_fee", value=799, label_visibility='collapsed', help="Doc Fee")
        
        taxes = calculate_taxes(state, market_value, discount, doc_fee, trade_value)
        labels_col.markdown('<input class="label-input" type="text" value="Taxes" disabled>', unsafe_allow_html=True)
        inputs_col.text_input(label="Taxes", key=f"{prefix}_taxes", value=f"{taxes:.2f}", label_visibility='collapsed', help="Taxes", disabled=True)
        
        labels_col.markdown('<input class="label-input" type="text" value="Non-Tax Fees" disabled>', unsafe_allow_html=True)
        non_tax_fees = inputs_col.number_input(label="Non-Tax Fees", key=f"{prefix}_non_tax_fees", value=106.75, label_visibility='collapsed', help="Non-Tax Fees")
        
        balance = calculate_balance(
            market_value, discount, rebate, trade_value, trade_payoff, taxes, doc_fee, non_tax_fees
        )
        labels_col.markdown('<input class="label-input" type="text" value="Balance" disabled>', unsafe_allow_html=True)
        inputs_col.text_input(label="Balance", key=f"{prefix}_balance", value=f"{balance:.2f}", label_visibility='collapsed', help="Balance", disabled=True)
    
    with left_col:
        col1, col2, col3, col4, col5, col6 = st.columns([.5,1.5,1,1.5,1.5,1.5])
    
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
        col3.text("")
        col3.text("")
        col3.text("")
        col3.text("")
        col3.text("")

        residual_values = []
        if is_lease:
            for i in range(3):
                residual_value = col3.number_input(label=f"Residual Percent {i+1}", key=f"{prefix}_residual_percent_{i+1}", value=0.70)
                residual_values.append(residual_value)
        # Input values
        value1 = col4.number_input(label="Down Payment", key=f"{prefix}_value1", value=1000)
        value2 = col5.number_input(label="Down Payment", key=f"{prefix}_value2", value=2000)
        value3 = col6.number_input(label="Down Payment", key=f"{prefix}_value3", value=3000)
        down_payments = [value1, value2, value3]
    
        terms = []
        rates = []
        default_terms = [36, 48, 60]  # Changed to typical lease terms
        for i in range(3):
            term = col1.number_input(f"Term {i+1}", min_value=1, value=default_terms[i], key=f'{prefix}_term_{i+1}')
            if is_lease:
                rate = col2.number_input(f"Money Factor {i+1}", min_value=0.00000, max_value=1.00000, value=0.00275, format="%.5f", key=f'{prefix}_rate_{i+1}')
            else:
                rate = col2.number_input(f"Rate {i+1} (%)", min_value=0.0, max_value=100.0, value=14.0, format="%.2f", key=f'{prefix}_rate_{i+1}')
            terms.append(term)
            rates.append(rate)
    
        for i in range(3):
            for j in range(3):
                if market_value == 0:
                    monthly_payment = 0
                else:
                    if is_lease:
                        residual_value = market_value * residual_values[i]
                        monthly_payment = calc_payment_func(market_value, market_value, 0, down_payments[j], 0, rates[i], terms[i], residual_value, taxes)
                    else:
                        monthly_payment = calc_payment_func(balance, down_payments[j], rates[i], terms[i])
                ltv = ((balance - down_payments[j]) / book_value) * 100 if book_value else 0
                if j == 0:
                    col4.markdown(f'<div class="centered-metric"><div class="stMetric">{monthly_payment}</div></div>', unsafe_allow_html=True)
                elif j == 1:
                    col5.markdown(f'<div class="centered-metric"><div class="stMetric">{monthly_payment}</div></div>', unsafe_allow_html=True)
                elif j == 2:
                    col6.markdown(f'<div class="centered-metric"><div class="stMetric">{monthly_payment}</div></div>', unsafe_allow_html=True)
        
        # Display LTV percentages under each column
        ltv1 = ((balance - down_payments[0]) / book_value) * 100 if book_value else 0
        ltv2 = ((balance - down_payments[1]) / book_value) * 100 if book_value else 0
        ltv3 = ((balance - down_payments[2]) / book_value) * 100 if book_value else 0
        
        col4.markdown(f'<div class="centered-metric"><div class="stMetric"><span style="font-size: 14px;">{ltv1:.2f}%</span></div></div>', unsafe_allow_html=True)
        col5.markdown(f'<div class="centered-metric"><div class="stMetric"><span style="font-size: 14px;">{ltv2:.2f}%</span></div></div>', unsafe_allow_html=True)
        col6.markdown(f'<div class="centered-metric"><div class="stMetric"><span style="font-size: 14px;">{ltv3:.2f}%</span></div></div>', unsafe_allow_html=True)

    lbc, rbc, blankbc = st.columns([2, 3, 10])
    with lbc:
        submit_button = st.button(label="Generate Quote", key=f"{prefix}_submit_button")
        
        if submit_button:
            quotes = {}
            for i in range(3):
                term_payments = {}
                for j in range(3):
                    if is_lease:
                        residual_value = market_value * residual_values[i]
                        monthly_payment = calc_payment_func(market_value, market_value, 0, down_payments[j], 0, rates[i], terms[i], residual_value, taxes)
                    else:
                        monthly_payment = calc_payment_func(balance, down_payments[j], rates[i], terms[i])
                    term_payments[down_payments[j]] = round(float(monthly_payment), 2)
                quotes[terms[i]] = term_payments
            
            data = {
                'date': datetime.today().strftime('%B %d, %Y').upper(),
                'salesperson': consultant,
                'buyer': customer,
                'address': address,
                'city': city,
                'state': state,
                'zip': zipcode,
                'cell_phone': phone_num,
                'email_add': email_address,
                'year': year,
                'make': make,
                'model': model,
                'stock_no': stocknum,
                'vin': vin,
                'miles': odometer,
                'trade_year': st.session_state.get(f"{prefix}_trade_year_1", ""),
                'trade_make': st.session_state.get(f"{prefix}_trade_make_1", ""),
                'trade_model': st.session_state.get(f"{prefix}_trade_model_1", ""),
                'trade_vin': st.session_state.get(f"{prefix}_trade_vin_1", ""),
                'trade_miles': st.session_state.get(f"{prefix}_trade_miles_1", ""),
                'trade_value': sum(trade_values),
                'trade_payoff': sum(trade_payoffs),
                'trade_acv': sum(trade_acvs),
                'trade_year_2': st.session_state.get(f"{prefix}_trade_year_2", ""),
                'trade_make_2': st.session_state.get(f"{prefix}_trade_make_2", ""),
                'trade_model_2': st.session_state.get(f"{prefix}_trade_model_2", ""),
                'trade_vin_2': st.session_state.get(f"{prefix}_trade_vin_2", ""),
                'trade_miles_2': st.session_state.get(f"{prefix}_trade_miles_2", ""),
                'sale_price': market_value,
                'discount': discount,
                'rebate': rebate,
                'doc_fee': doc_fee,
                'sales_tax': taxes,
                'non_tax_fees': non_tax_fees,
                'balance': balance,
                'quotes': quotes,
            }
            
            pdf_file = generate_pdf(data)
            with open(pdf_file, 'rb') as f:
                st.download_button('Download Quote', f, file_name=pdf_file, key=f"{prefix}_download_button")
        with rbc:
            market_value = market_value or 0
            discount = discount or 0
            veh_cost = veh_cost or 0
            trade_acv = trade_acv or 0
            trade_value = trade_value or 0
            gross_profit = market_value - discount - veh_cost + (trade_acv - trade_value)
            color = "green" if gross_profit > 0 else "red" if gross_profit < 0 else "white"
            st.markdown(f"<p style='color:{color}; font-size:24px;'>Front Gross ${gross_profit:.2f}</p>", unsafe_allow_html=True)

finance, lease = st.tabs(["Finance", "Lease"])

with finance:
    render_tab(calculate_monthly_payment, prefix="finance")

with lease:
    render_tab(calculate_lease_payment, prefix="lease", is_lease=True)
