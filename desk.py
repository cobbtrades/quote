import streamlit as st
from datetime import datetime
from utils import (
    calculate_monthly_payment, calculate_lease_payment, calculate_balance,
    calculate_taxes, generate_pdf, fill_fi_pdf, modify_stocknum,
    dealer_names, banks
)
st.set_page_config(page_title="Desking App", page_icon="📝")
with open("styles.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
st.subheader("")
dealer_names_list = list(dealer_names.keys())
bank_list = list(banks.keys())
def update_lienholder_details(lienholder_name):
    if lienholder_name in banks:
        return banks[lienholder_name]["address"], banks[lienholder_name]["city"], banks[lienholder_name]["state"], banks[lienholder_name]["zip"]
    return "", "", "", ""
def text_input_with_label(col, label, key, **kwargs):
    col.markdown(f'<input class="label-input" type="text" value="{label}" disabled>', unsafe_allow_html=True)
    return col.text_input(label=label, key=key, label_visibility="collapsed", **kwargs)
def number_input_with_label(col, label, key, **kwargs):
    col.markdown(f'<input class="label-input" type="text" value="{label}" disabled>', unsafe_allow_html=True)
    return col.number_input(label=label, key=key, label_visibility="collapsed", **kwargs)
def render_tab(calc_payment_func, prefix, is_lease=False):
    fc, sc, tc = st.columns([3, 3, 2])
    with fc:
        customer = text_input_with_label(fc, "Customer", key=f"{prefix}_cust")
        address = text_input_with_label(fc, "Address", key=f"{prefix}_addr")
        city = text_input_with_label(fc, "City", key=f"{prefix}_city")
        state = text_input_with_label(fc, "State", key=f"{prefix}_state", max_chars=2)
        zipcode = text_input_with_label(fc, "Zip", key=f"{prefix}_zip", max_chars=5)
        email_address = text_input_with_label(fc, "Email", key=f"{prefix}_emailaddress")
        phone_num = text_input_with_label(fc, "Phone", key=f"{prefix}_phonenumber", max_chars=12)
    with sc:
        stocknum = text_input_with_label(sc, "Stock #", key=f"{prefix}_stock")
        vin = text_input_with_label(sc, "VIN", key=f"{prefix}_vin", max_chars=17)
        newused = sc.selectbox("N/U", ["New", "Used", "CPO"], key=f"{prefix}_newused", label_visibility="collapsed")
        year = text_input_with_label(sc, "Year", key=f"{prefix}_year", max_chars=4)
        make = text_input_with_label(sc, "Make", key=f"{prefix}_make")
        model = text_input_with_label(sc, "Model", key=f"{prefix}_model")
        trim = text_input_with_label(sc, "Trim", key=f"{prefix}_trim", max_chars=4)
        odometer = text_input_with_label(sc, "Odometer", key=f"{prefix}_odometer")
        veh_cost = number_input_with_label(sc, "Cost", key=f"{prefix}_veh_cost", value=0.00)
        book_value = number_input_with_label(sc, "Book Value", key=f"{prefix}_book_value", value=0.00)
    with tc:
        dealer = sc.selectbox("Select Dealer", dealer_names_list, key=f"{prefix}_dealer", label_visibility="collapsed")
        consultant = text_input_with_label(tc, "Sales Person", key=f"{prefix}_consultant")
        manager = text_input_with_label(tc, "Sales Manager", key=f"{prefix}_manager")
    trade_values, trade_payoffs, trade_acvs = [0] * 2, [0] * 2, [0] * 2
    with st.popover("Enter Trade-in Details", use_container_width=True):
        for i in range(2):
            col1, col2, col3, col4 = st.columns([1, 2, 1, 4])
            trade_year = text_input_with_label(col1, "Year", key=f"{prefix}_trade_year_{i+1}", max_chars=4)
            trade_make = text_input_with_label(col2, "Make", key=f"{prefix}_trade_make_{i+1}")
            trade_model = text_input_with_label(col3, "Model", key=f"{prefix}_trade_model_{i+1}")
            trade_vin = text_input_with_label(col4, "VIN", key=f"{prefix}_trade_vin_{i+1}", max_chars=17)
            trade_miles = text_input_with_label(col1, "Miles", key=f"{prefix}_trade_miles_{i+1}")
            trade_values[i] = number_input_with_label(col2, "Trade Value", key=f"{prefix}_trade_value_{i+1}", value=0.00)
            trade_payoffs[i] = number_input_with_label(col3, "Payoff", key=f"{prefix}_trade_payoff_{i+1}", value=0.00)
            trade_acvs[i] = number_input_with_label(col4, "Trade ACV", key=f"{prefix}_trade_acv_{i+1}", value=0.00)
    left_col, right_col = st.columns(2)
    with right_col:
        market_value = number_input_with_label(right_col, "Market Value", key=f"{prefix}_market_value", value=0.00)
        discount = number_input_with_label(right_col, "Discount", key=f"{prefix}_discount", value=0.00)
        rebate = number_input_with_label(right_col, "Rebate", key=f"{prefix}_rebate", value=0.00)
        trade_value = sum(trade_values)
        st.number_input(label="Trade Value", key=f"{prefix}_trade_value", value=trade_value, label_visibility='collapsed', disabled=True)
        trade_acv = sum(trade_acvs)
        st.number_input(label="Trade ACV", key=f"{prefix}_trade_acv", value=trade_acv, label_visibility='collapsed', disabled=True)
        trade_payoff = sum(trade_payoffs)
        st.number_input(label="Trade Payoff", key=f"{prefix}_trade_payoff", value=trade_payoff, label_visibility='collapsed', disabled=True)
        doc_fee = number_input_with_label(right_col, "Doc Fee", key=f"{prefix}_doc_fee", value=799.00)
        taxes = calculate_taxes(state, market_value, discount, doc_fee, trade_value)
        st.number_input(label="Taxes", key=f"{prefix}_taxes", value=taxes or 0.00, label_visibility='collapsed', disabled=True)
        non_tax_fees = number_input_with_label(right_col, "Non-Tax Fees", key=f"{prefix}_non_tax_fees", value=125.00)
        balance = calculate_balance(market_value, discount, rebate, trade_value, trade_payoff, taxes, doc_fee, non_tax_fees)
        st.text_input(label="Balance", key=f"{prefix}_balance", value=f"{balance:.2f}", label_visibility='collapsed', disabled=True)
    with left_col:
        residual_values = []
        if is_lease:
            for i in range(3):
                residual_value = number_input_with_label(left_col, f"Residual Percent {i+1}", key=f"{prefix}_residual_percent_{i+1}", value=0.70)
                residual_values.append(residual_value)
        down_payments = [
            number_input_with_label(left_col, "Down Payment", key=f"{prefix}_value1", value=1000.00),
            number_input_with_label(left_col, "Down Payment", key=f"{prefix}_value2", value=2000.00),
            number_input_with_label(left_col, "Down Payment", key=f"{prefix}_value3", value=3000.00)
        ]
        terms = []
        rates = []
        default_terms = [36, 60, 72]
        for i in range(3):
            term = number_input_with_label(left_col, "Term", key=f"{prefix}_term_{i+1}", value=default_terms[i], min_value=1)
            rate = number_input_with_label(left_col, "Rate (%)" if not is_lease else f"Money Factor {i+1}", key=f"{prefix}_rate_{i+1}", value=14.0 if not is_lease else 0.00275, min_value=0.0, max_value=100.0)
            terms.append(term)
            rates.append(rate)
        for i in range(3):
            for j in range(3):
                monthly_payment = 0 if market_value == 0 else (
                    calculate_lease_payment(market_value, doc_fee, non_tax_fees, 0, down_payments[j], 0, rates[i], terms[i], residual_values[i], trade_value, trade_payoff, discount)
                    if is_lease else calc_payment_func(balance, down_payments[j], rates[i], terms[i])
                )
                col = left_col if j == 0 else right_col if j == 1 else st
                col.markdown(f'<div class="centered-metric"><div class="stMetric">{monthly_payment}</div></div>', unsafe_allow_html=True)
        ltv1 = ((balance - down_payments[0]) / book_value) * 100 if book_value else 0
        ltv2 = ((balance - down_payments[1]) / book_value) * 100 if book_value else 0
        ltv3 = ((balance - down_payments[2]) / book_value) * 100 if book_value else 0
        right_col.markdown(f'<div class="centered-metric"><div class="stMetric"><span style="font-size: 14px;">{ltv1:.2f}%</span></div></div>', unsafe_allow_html=True)
        right_col.markdown(f'<div class="centered-metric"><div class="stMetric"><span style="font-size: 14px;">{ltv2:.2f}%</span></div></div>', unsafe_allow_html=True)
        right_col.markdown(f'<div class="centered-metric"><div class="stMetric"><span style="font-size: 14px;">{ltv3:.2f}%</span></div></div>', unsafe_allow_html=True)
        gross_profit = market_value - discount - veh_cost + (trade_acv - trade_value)
        color = "green" if gross_profit > 0 else "red" if gross_profit < 0 else "white"
        right_col.markdown(f"<p style='color:{color}; font-size:24px; text-align:center'>Front Gross ${gross_profit:.2f}</p>", unsafe_allow_html=True)
    with st.popover("Enter Finance Details", use_container_width=True):
        col1, col2, col3, col4 = st.columns([1, 1, 1, 3])
        bodystyle = text_input_with_label(col1, "Body Style", key=f"{prefix}_bodystyle")
        fuel_type = text_input_with_label(col1, "Fuel Type", key=f"{prefix}_fuel_type")
        drivers_license = text_input_with_label(col2, "Driver's License", key=f"{prefix}_drivers_license")
        county = text_input_with_label(col2, "County", key=f"{prefix}_county")
        platenum = text_input_with_label(col3, "License Plate Number", key=f"{prefix}_platenum")
        plate_exp = text_input_with_label(col3, "Plate Expiration", key=f"{prefix}_plate_exp")
        lienholder_name = st.selectbox("Select Lienholder", bank_list, key=f"{prefix}_bank", label_visibility="collapsed")
        lien_address, lien_city, lien_state, lien_zip_code = update_lienholder_details(lienholder_name)
        lienholder_address = text_input_with_label(col4, "Lienholder Address", key=f"{prefix}_lienholder_address", value=lien_address)
        lienholder_city = text_input_with_label(col4, "Lienholder City", key=f"{prefix}_lienholder_city", value=lien_city)
        lienholder_state = text_input_with_label(col4, "Lienholder State", key=f"{prefix}_lienholder_state", value=lien_state, max_chars=2)
        lienholder_zip = text_input_with_label(col4, "Lienholder Zip Code", key=f"{prefix}_lienholder_zip", value=lien_zip_code, max_chars=5)
        ins_company = text_input_with_label(col4, "Insurance Company", key=f"{prefix}_ins_company")
        policy = text_input_with_label(col4, "Policy #", key=f"{prefix}_policy")
        if st.button("Submit", key=f"{prefix}_submit_modal"):
            process_submission(
                calc_payment_func, prefix, is_lease, customer, address, city, state, zipcode,
                email_address, phone_num, stocknum, vin, newused, year, make, model, trim,
                odometer, veh_cost, book_value, trade_values, trade_payoffs, trade_acvs,
                market_value, discount, rebate, doc_fee, taxes, non_tax_fees, balance,
                dealer, consultant, manager, bodystyle, fuel_type, drivers_license, county,
                platenum, plate_exp, lienholder_name, lienholder_address, lienholder_city,
                lienholder_state, lienholder_zip, ins_company, policy
            )
    if st.button("Generate Quote", key=f"{prefix}_submit_button"):
        quotes = generate_quotes(
            calc_payment_func, market_value, doc_fee, non_tax_fees, down_payments, rates, terms,
            residual_values, trade_value, trade_payoff, discount, balance, is_lease
        )
        generate_and_download_pdf(quotes, dealer, consultant, manager, customer, address, city, state,
                                  zipcode, phone_num, email_address, newused, year, make, model, trim,
                                  stocknum, vin, odometer, trade_values, trade_acvs, trade_payoffs,
                                  market_value, discount, rebate, doc_fee, taxes, non_tax_fees, balance)
def process_submission(
    calc_payment_func, prefix, is_lease, customer, address, city, state, zipcode,
    email_address, phone_num, stocknum, vin, newused, year, make, model, trim,
    odometer, veh_cost, book_value, trade_values, trade_payoffs, trade_acvs,
    market_value, discount, rebate, doc_fee, taxes, non_tax_fees, balance,
    dealer, consultant, manager, bodystyle, fuel_type, drivers_license, county,
    platenum, plate_exp, lienholder_name, lienholder_address, lienholder_city,
    lienholder_state, lienholder_zip, ins_company, policy
):
    trade_value = sum(trade_values)
    trade_acv = sum(trade_acvs)
    trade_payoff = sum(trade_payoffs)
    balance = calculate_balance(market_value, discount, rebate, trade_value, trade_payoff, taxes, doc_fee, non_tax_fees)
    # Generate quotes
    quotes = generate_quotes(
        calc_payment_func, market_value, doc_fee, non_tax_fees, [1000.00, 2000.00, 3000.00], [14.0, 14.0, 14.0], [36, 60, 72],
        [0.70, 0.70, 0.70], trade_value, trade_payoff, discount, balance, is_lease
    )
    # Prepare data for PDF
    words = customer.split()
    formatted_customer = ''.join(words[:2]).lower() if len(words) >= 2 else customer.replace(" ", "").lower()
    output_pdf_path = f'{formatted_customer}FIDocs.pdf'
    data = {
        "bos_date": datetime.today().strftime('%m/%d/%Y'),
        "bos_salesperson": consultant,
        "bos_buyer": customer,
        "box_address": address,
        "bos_city": city,
        "bos_state": state,
        "bos_zip": zipcode,
        "bos_res_phone": phone_num,
        "bos_email": email_address,
        "bos_cb_new": newused == "New",
        "bos_cb_used": newused != "New",
        "bos_year": year,
        "bos_make": make,
        "bos_model": model,
        "bos_vin1": vin,
        "bos_stock1": stocknum,
        "bos_miles1": odometer,
        "bos_sls_mgr": manager,
        "bos_trade_value": "{:.2f}".format(trade_value),
        "bos_total": "{:.2f}".format(market_value - discount - trade_value),
        "bos_docfee": "{:.2f}".format(doc_fee),
        "bos_taxes": "{:.2f}".format(taxes),
        "bos_tagfees": "{:.2f}".format(non_tax_fees - 11),
        "bos_titlefee": "{:.2f}".format(11.00),
        "bos_payoff": "{:.2f}".format(trade_payoff),
        "bos_downpayment": "{:.2f}".format(1000.00),
        "bos_rebate": "{:.2f}".format(rebate),
        "bos_balance": "{:.2f}".format(balance),
        "Check Box3": "",
        "Check Box4": "",
        "Check Box5": "",
        "Check Box6": "",
        "Check Box7": "",
        "Check Box8": "",
        "Check Box9": "",
        "Check Box10": "",
        "YEAR": year,
        "MAKE": make,
        "BODY STYLE": bodystyle,
        "SERIES MODEL": model,
        "VEHICLE IDENTIFICATION NUMBER": vin,
        "FUEL TYPE": fuel_type,
        "ODOMETER READING": odometer,
        "Owner 1 ID": drivers_license,
        "Full Legal Name of Owner 1 First Middle Last Suffix or Company Name": customer,
        "Residence Address Individual Business Address Firm City and State Zip Code": f'{address}         {city}, {state}         {zipcode}',
        "Vehicle Location Address if different from residence address above City and State Zip Code": "",
        "Tax County": county,
        "Lienholder 1 name": lienholder_name,
        "Address": lienholder_address,
        "City": lienholder_city,
        "State": lienholder_state,
        "Zip Code": lienholder_zip,
        "Insurance Company authorized in NC": ins_company,
        "Policy Number": policy,
        "From Whom Purchased Name and Address": f"{dealer}\n{dealer_names[dealer].split(',')[0].strip()}\n{dealer_names[dealer].split(',')[1].strip()} {dealer_names[dealer].split(',')[2].strip()}",
    }
    # Generate and download PDF
    template_pdf_path = 'docs/FIDocs1T.pdf' if trade_value > 0 else 'docs/FIDocs.pdf'
    fill_fi_pdf(template_pdf_path, output_pdf_path, data)
    with open(output_pdf_path, 'rb') as f:
        st.download_button('Download F&I Docs', f, file_name=output_pdf_path)
def generate_quotes(calc_payment_func, market_value, doc_fee, non_tax_fees, down_payments, rates, terms, residual_values, trade_value, trade_payoff, discount, balance, is_lease):
    quotes = {}
    for i in range(3):
        term_payments = {}
        for j in range(3):
            monthly_payment = 0 if market_value == 0 else (
                calculate_lease_payment(market_value, doc_fee, non_tax_fees, 0, down_payments[j], 0, rates[i], terms[i], residual_values[i], trade_value, trade_payoff, discount)
                if is_lease else calc_payment_func(balance, down_payments[j], rates[i], terms[i])
            )
            term_payments[down_payments[j]] = round(float(monthly_payment), 2)
        quotes[terms[i]] = term_payments
    return quotes
def generate_and_download_pdf(quotes, dealer, consultant, manager, customer, address, city, state, zipcode, phone_num, email_address, newused, year, make, model, trim, stocknum, vin, odometer, trade_values, trade_acvs, trade_payoffs, market_value, discount, rebate, doc_fee, taxes, non_tax_fees, balance):
    data = {
        'date': datetime.today().strftime('%m/%d/%Y'),
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
        'trade_year': st.session_state.get("finance_trade_year_1", ""),
        'trade_make': st.session_state.get("finance_trade_make_1", ""),
        'trade_model': st.session_state.get("finance_trade_model_1", ""),
        'trade_vin': st.session_state.get("finance_trade_vin_1", ""),
        'trade_miles': st.session_state.get("finance_trade_miles_1", ""),
        'trade_value': sum(trade_values),
        'trade_payoff': sum(trade_payoffs),
        'trade_acv': sum(trade_acvs),
        'trade_year_2': st.session_state.get("finance_trade_year_2", ""),
        'trade_make_2': st.session_state.get("finance_trade_make_2", ""),
        'trade_model_2': st.session_state.get("finance_trade_model_2", ""),
        'trade_vin_2': st.session_state.get("finance_trade_vin_2", ""),
        'trade_miles_2': st.session_state.get("finance_trade_miles_2", ""),
        'sale_price': market_value,
        'discount': discount,
        'rebate': rebate,
        'doc_fee': doc_fee,
        'sales_tax': taxes,
        'non_tax_fees': non_tax_fees,
        'balance': balance,
        'quotes': quotes,
    }
    filename = f'{customer}.pdf' if customer else 'quote.pdf'
    pdf_file = generate_pdf(data, filename=filename)
    with open(pdf_file, 'rb') as f:
        st.download_button('Download Quote', f, file_name=pdf_file, key="download_quote_button")
finance, lease = st.tabs(["Finance", "Lease"])
with finance:
    render_tab(calculate_monthly_payment, prefix="finance")
with lease:
    render_tab(calculate_lease_payment, prefix="lease", is_lease=True)
