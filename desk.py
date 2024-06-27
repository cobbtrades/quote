import streamlit as st, logging
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Spacer, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from pdfrw import PdfReader, PdfWriter, PdfName, PdfString, PdfDict, PdfArray, PdfObject
from func import calculate_monthly_payment, calculate_lease_payment, calculate_balance, calculate_taxes, generate_pdf

st.set_page_config(page_title="Desking App", page_icon="📝")

with open("styles.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

st.subheader("")

def set_appearance(annotation, value, max_font_size):
    lines = value.split('\n')
    max_length = max(len(line) for line in lines)
    field_width = annotation['/Rect'][2] - annotation['/Rect'][0]
    field_height = annotation['/Rect'][3] - annotation['/Rect'][1]

    # Calculate the font size based on the width and height of the field
    font_size = max_font_size
    while font_size > 1:
        text_width = font_size * 0.6 * max_length
        text_height = font_size * len(lines)
        if text_width <= field_width and text_height <= field_height:
            break
        font_size -= 1

    # Split the value into lines
    line_height = font_size + 2
    box_height = line_height * len(lines)

    # Create the appearance stream for multiline text
    appearance_stream = f"""
    q
    1 0 0 1 0 0 cm
    /Tx BMC
    BT
    /F1 {font_size} Tf
    0 g
    2 {box_height - font_size} Td
    """

    for line in lines:
        appearance_stream += f"({line}) Tj\nT* "
    
    appearance_stream += """
    ET
    EMC
    Q
    """
    
    appearance = PdfDict(
        Type=PdfName('XObject'),
        Subtype=PdfName('Form'),
        BBox=PdfArray([0, 0, field_width, box_height]),
        Resources=PdfDict(
            Font=PdfDict(
                F1=PdfDict(
                    Type=PdfName('Font'),
                    Subtype=PdfName('Type1'),
                    BaseFont=PdfName('Helvetica')
                )
            )
        ),
        FormType=1,
        Length=len(appearance_stream),
        stream=appearance_stream
    )

    annotation.update({
        PdfName('AP'): PdfDict(N=appearance),
        PdfName('V'): PdfString(value)
    })

def fill_pdf(input_pdf_path, output_pdf_path, data_dict, max_font_size=10):
    template_pdf = PdfReader(input_pdf_path)
    for page in template_pdf.pages:
        annotations = page['/Annots']
        if annotations:
            for annotation in annotations:
                if annotation['/Subtype'] == '/Widget' and annotation['/T']:
                    key = annotation['/T'][1:-1]  # Remove the parentheses around the key
                    if key in data_dict:
                        annotation.update({
                            PdfName('/V'): PdfString(data_dict[key]),
                            PdfName('/Ff'): 1,  # Make the field read-only
                        })
                        set_appearance(annotation, data_dict[key], max_font_size)
    PdfWriter().write(output_pdf_path, template_pdf)

def render_tab(calc_payment_func, prefix, is_lease=False):
    fc, sc, tc = st.columns([3, 3, 2])
    
    with fc:
        fc1, sc1 = st.columns([.6,4])
        fc1.markdown('<input class="label-input" type="text" value="Customer" disabled>', unsafe_allow_html=True)
        customer = sc1.text_input(label="Customer", key=f"{prefix}_cust", label_visibility='collapsed', help="Customer")
        fc1.markdown('<input class="label-input" type="text" value="Address" disabled>', unsafe_allow_html=True)
        address = sc1.text_input(label="Address", key=f"{prefix}_addr", label_visibility="collapsed", help="Address")

        
        fc2, sc2, tc2, fr2, ft2, st2 = st.columns([.6, 2.5, .5, .5, .5, 1])
        fc2.markdown('<input class="label-input" type="text" value="City" disabled>', unsafe_allow_html=True)
        city = sc2.text_input(label="City", key=f"{prefix}_city", label_visibility="collapsed", help="City")
        tc2.markdown('<input class="label-input" type="text" value="State" disabled>', unsafe_allow_html=True)
        state = fr2.text_input(label="State", key=f"{prefix}_state", max_chars=2, label_visibility="collapsed", help="State")
        ft2.markdown('<input class="label-input" type="text" value="Zip" disabled>', unsafe_allow_html=True)
        zipcode = st2.text_input(label="Zip", key=f"{prefix}_zip", max_chars=5, label_visibility="collapsed", help="Zip")
        fc2.markdown('<input class="label-input" type="text" value="Email" disabled>', unsafe_allow_html=True)
        email_address = sc2.text_input(label="Email", key=f"{prefix}_emailaddress", label_visibility="collapsed", help="Email")
        ft2.markdown('<input class="label-input" type="text" value="Phone" disabled>', unsafe_allow_html=True)
        phone_num = st2.text_input(label="Phone", key=f"{prefix}_phonenumber", max_chars=12, label_visibility="collapsed", help="Phone")
    
    with sc:
        fc3, sc3, tc3, fr3 = st.columns([1, 2, 1, 4])
        fc3.markdown('<input class="label-input" type="text" value="Stock #" disabled>', unsafe_allow_html=True)
        stocknum = sc3.text_input(label="Stock #", key=f"{prefix}_stock", label_visibility="collapsed", help="Stock #")
        tc3.markdown('<input class="label-input" type="text" value="VIN" disabled>', unsafe_allow_html=True)
        vin = fr3.text_input(label="VIN", key=f"{prefix}_vin", max_chars=17, label_visibility="collapsed", help="VIN")
        fc4, sc4, tc4, fr4, ft4 = st.columns([1, 1, 1, 1, 2])
        newused = fc4.selectbox(label="N/U", options=["New", "Used", "CPO"], key=f"{prefix}_newused", label_visibility="collapsed", help="N/U")
        sc4.markdown('<input class="label-input" type="text" value="Year" disabled>', unsafe_allow_html=True)
        year = tc4.text_input(label="Year", key=f"{prefix}_year", max_chars=4, label_visibility="collapsed", help="Year")
        fr4.markdown('<input class="label-input" type="text" value="Make" disabled>', unsafe_allow_html=True)
        make = ft4.text_input(label="Make", key=f"{prefix}_make", label_visibility="collapsed", help="Make")
        fc5, sc5, tc5, fr5, ft5, st5 = st.columns([1, 2, 1, 1.5, 1, 1.5])
        fc5.markdown('<input class="label-input" type="text" value="Model" disabled>', unsafe_allow_html=True)
        model = sc5.text_input(label="Model", key=f"{prefix}_model", label_visibility="collapsed", help="Model")
        tc5.markdown('<input class="label-input" type="text" value="Trim" disabled>', unsafe_allow_html=True)
        trim = fr5.text_input(label="Trim", key=f"{prefix}_trim", max_chars=4, label_visibility="collapsed", help="Trim")
        ft5.markdown('<input class="label-input" type="text" value="Odometer" disabled>', unsafe_allow_html=True)
        odometer = st5.text_input(label="Odometer", key=f"{prefix}_odometer", label_visibility="collapsed", help="Odometer")
        fc6, sc6, tc6, fr6 = st.columns(4)
        fc6.markdown('<input class="label-input" type="text" value="Cost" disabled>', unsafe_allow_html=True)
        veh_cost = sc6.number_input(label="Cost", key=f"{prefix}_veh_cost", value=0, label_visibility='collapsed', help="Cost")
        tc6.markdown('<input class="label-input" type="text" value="Book Value" disabled>', unsafe_allow_html=True)
        book_value = fr6.number_input(label="Book Value", key=f"{prefix}_book_value", value=0, label_visibility='collapsed', help="Book Value")
    
    with tc:
        fc7, sc7 = st.columns([1.5,4])
        fc7.markdown('<input class="label-input" type="text" value="Dealer" disabled>', unsafe_allow_html=True)
        dealer = sc7.text_input(label="Dealership", key=f"{prefix}_dealer", label_visibility="collapsed", help="Dealership")
        fc7.markdown('<input class="label-input" type="text" value="Sales Person" disabled>', unsafe_allow_html=True)
        consultant = sc7.text_input(label="Sales Person", key=f"{prefix}_consultant", label_visibility="collapsed", help="Sales Person")
        fc7.markdown('<input class="label-input" type="text" value="Sales Manager" disabled>', unsafe_allow_html=True)
        manager = sc7.text_input(label="Sales Manager", key=f"{prefix}_manager", label_visibility="collapsed", help="Sales Manager")

    trade_values = [0] * 2
    trade_payoffs = [0] * 2
    trade_acvs = [0] * 2
    with st.popover("Enter Trade-in Details", use_container_width=True):
        for i in range(2):  # For up to 2 trades
            # First row of trade-in details
            tt1, fc1, sc1, tc1, fr1, ft1, st1, sv1, ec1 = st.columns([1, 1, 2, 1, 2, 1, 2, 1, 4])
            col_data = f"Trade-in {i+1}"
            tt1.markdown(f'<input class="label-input" type="text" value="{col_data}" disabled>', unsafe_allow_html=True)
            fc1.markdown('<input class="label-input" type="text" value="Year" disabled>', unsafe_allow_html=True)
            trade_year = sc1.text_input(f"Trade-in {i+1} Year", key=f"{prefix}_trade_year_{i+1}", label_visibility="collapsed", max_chars=4)
            tc1.markdown('<input class="label-input" type="text" value="Make" disabled>', unsafe_allow_html=True)
            trade_make = fr1.text_input(f"Trade-in {i+1} Make", key=f"{prefix}_trade_make_{i+1}", label_visibility="collapsed")
            ft1.markdown('<input class="label-input" type="text" value="Model" disabled>', unsafe_allow_html=True)
            trade_model = st1.text_input(f"Trade-in {i+1} Model", key=f"{prefix}_trade_model_{i+1}", label_visibility="collapsed")
            sv1.markdown('<input class="label-input" type="text" value="VIN" disabled>', unsafe_allow_html=True)
            trade_vin = ec1.text_input(f"Trade-in {i+1} VIN", key=f"{prefix}_trade_vin_{i+1}", label_visibility="collapsed", max_chars=17)
    
            # Second row of trade-in details
            tt2, fc2, sc2, tc2, fr2, ft2, st2, sv2, ec2 = st.columns([1, 1, 2, 1, 2, 1, 2, 1, 4])
            fc2.markdown('<input class="label-input" type="text" value="Miles" disabled>', unsafe_allow_html=True)
            trade_miles = sc2.text_input(f"Trade-in {i+1} Miles", key=f"{prefix}_trade_miles_{i+1}", label_visibility="collapsed")
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
                        monthly_payment = calculate_lease_payment(market_value, doc_fee, non_tax_fees, 0, down_payments[j], 0, rates[i], terms[i], residual_values[i], trade_value, trade_payoff, discount)
                    else:
                        monthly_payment = calc_payment_func(balance, down_payments[j], rates[i], terms[i])
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
        market_value = market_value or 0
        discount = discount or 0
        veh_cost = veh_cost or 0
        trade_acv = trade_acv or 0
        trade_value = trade_value or 0
        gross_profit = market_value - discount - veh_cost + (trade_acv - trade_value)
        color = "green" if gross_profit > 0 else "red" if gross_profit < 0 else "white"
        col6.markdown(f"<p style='color:{color}; font-size:24px; text-align:center'>Front Gross ${gross_profit:.2f}</p>", unsafe_allow_html=True)

    lbc, blankbc = st.columns([2, 10])
    with blankbc:
        # Generate MRV-1 button and logic
            if st.button("Generate MRV-1", key=f"{prefix}_generate_mvr1"):
                # Mapping Streamlit form data to the PDF fields
                pdf_data = {
                    "List Plate Number and Expiration": "",
                    "YEAR": year,
                    "MAKE": make,
                    "BODY STYLE": "",
                    "SERIES MODEL": model,
                    "VEHICLE IDENTIFICATION NUMBER": vin,
                    "FUEL TYPE": "",
                    "ODOMETER READING": odometer,
                    "Owner 1 ID": "",
                    "Full Legal Name of Owner 1 First Middle Last Suffix or Company Name": customer,
                    "Owner 2 ID": "",
                    "Full Legal Name of Owner 2 First Middle Last Suffix or Company Name": "",
                    "Residence Address Individual Business Address Firm City and State Zip Code": f'{address}, {city}, {state}, {zipcode}',
                    "Mail Address if different from above City and State Zip Code": "",
                    "Vehicle Location Address if different from residence address above City and State Zip Code": "",
                    "Tax County": "",
                    "Date 1": "",
                    "Lienholder 1 ID": "",
                    "Lienholder 1 name": "",
                    "Address": "",
                    "City": "",
                    "State": "",
                    "Zip Code": "",
                    "Insurance Company authorized in NC": "",
                    "Policy Number": "",
                    "From Whom Purchased Name and Address": "",
                    "New": newused,
                    "Used": newused
                }

                # Fill the PDF form
                pdf_template_path = 'MVR-1.pdf'
                filled_pdf_path = 'output_form_filled.pdf'
                fill_pdf(pdf_template_path, filled_pdf_path, pdf_data, 10)
                
                # Provide download link for filled MRV-1 PDF
                with open(filled_pdf_path, 'rb') as f:
                    st.download_button('Download MVR-1', f, file_name=filled_pdf_path, key=f"{prefix}_download_mvr1_button")
    with lbc:
        submit_button = st.button(label="Generate Quote", key=f"{prefix}_submit_button")
        
        if submit_button:
            quotes = {}
            for i in range(3):
                term_payments = {}
                for j in range(3):
                    if is_lease:
                        residual_value = market_value * residual_values[i]
                        monthly_payment = calculate_lease_payment(market_value, doc_fee, non_tax_fees, 0, down_payments[j], 0, rates[i], terms[i], residual_values[i], trade_value, trade_payoff, discount)
                    else:
                        monthly_payment = calc_payment_func(balance, down_payments[j], rates[i], terms[i])
                    term_payments[down_payments[j]] = round(float(monthly_payment), 2)
                quotes[terms[i]] = term_payments
            
            data = {
                'date': datetime.today().strftime('%B %d, %Y').upper(),
                'dealer': dealer,
                'salesperson': consultant,
                'manager': manager,
                'buyer': customer,
                'address': address,
                'city': city,
                'state': state,
                'zip': zipcode,
                'cell_phone': phone_num,
                'email_add': email_address,
                'newused': newused,
                'year': year,
                'make': make,
                'model': model,
                'trim': trim,
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

finance, lease = st.tabs(["Finance", "Lease"])

with finance:
    render_tab(calculate_monthly_payment, prefix="finance")

with lease:
    render_tab(calculate_lease_payment, prefix="lease", is_lease=True)
