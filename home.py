import streamlit as st
from datetime import datetime
from utils import calculate_monthly_payment, calculate_lease_payment, calculate_balance
from utils import calculate_taxes, generate_pdf, fill_fi_pdf, modify_stocknum
from utils import dealer_names, banks


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

def render_tab(calc_payment_func, prefix, is_lease=False):
    fc, sc, tc = st.columns([3, 3, 2])
    with fc:
        fc1, sc1 = st.columns([.6,4])
        fc1.markdown('<input class="label-input" type="text" value="Customer" disabled>', unsafe_allow_html=True)
        customer = sc1.text_input(label="Customer", key=f"{prefix}_cust", label_visibility='collapsed')
        fc1.markdown('<input class="label-input" type="text" value="Address" disabled>', unsafe_allow_html=True)
        address = sc1.text_input(label="Address", key=f"{prefix}_addr", label_visibility="collapsed")
        fc2, sc2, tc2, fr2, ft2, st2 = st.columns([.6, 2.5, .5, .5, .5, 1])
        fc2.markdown('<input class="label-input" type="text" value="City" disabled>', unsafe_allow_html=True)
        city = sc2.text_input(label="City", key=f"{prefix}_city", label_visibility="collapsed")
        tc2.markdown('<input class="label-input" type="text" value="State" disabled>', unsafe_allow_html=True)
        state = fr2.text_input(label="State", key=f"{prefix}_state", max_chars=2, label_visibility="collapsed")
        ft2.markdown('<input class="label-input" type="text" value="Zip" disabled>', unsafe_allow_html=True)
        zipcode = st2.text_input(label="Zip", key=f"{prefix}_zip", max_chars=5, label_visibility="collapsed")
        fc2.markdown('<input class="label-input" type="text" value="Email" disabled>', unsafe_allow_html=True)
        email_address = sc2.text_input(label="Email", key=f"{prefix}_emailaddress", label_visibility="collapsed")
        ft2.markdown('<input class="label-input" type="text" value="Phone" disabled>', unsafe_allow_html=True)
        phone_num = st2.text_input(label="Phone", key=f"{prefix}_phonenumber", max_chars=12, label_visibility="collapsed")
    with sc:
        fc3, sc3, tc3, fr3 = st.columns([1, 2, 1, 4])
        fc3.markdown('<input class="label-input" type="text" value="Stock #" disabled>', unsafe_allow_html=True)
        stocknum = sc3.text_input(label="Stock #", key=f"{prefix}_stock", label_visibility="collapsed")
        tc3.markdown('<input class="label-input" type="text" value="VIN" disabled>', unsafe_allow_html=True)
        vin = fr3.text_input(label="VIN", key=f"{prefix}_vin", max_chars=17, label_visibility="collapsed")
        fc4, sc4, tc4, fr4, ft4 = st.columns([1, 1, 1, 1, 2])
        newused = fc4.selectbox(label="N/U", options=["New", "Used", "CPO"], key=f"{prefix}_newused", label_visibility="collapsed")
        is_new = newused == "New"
        bos_cb_new = is_new
        mvr6tNewcb = is_new
        bos_cb_used = not is_new
        mvr6tUsedcb = not is_new
        sc4.markdown('<input class="label-input" type="text" value="Year" disabled>', unsafe_allow_html=True)
        year = tc4.text_input(label="Year", key=f"{prefix}_year", max_chars=4, label_visibility="collapsed")
        fr4.markdown('<input class="label-input" type="text" value="Make" disabled>', unsafe_allow_html=True)
        make = ft4.text_input(label="Make", key=f"{prefix}_make", label_visibility="collapsed")
        fc5, sc5, tc5, fr5, ft5, st5 = st.columns([1, 2, 1, 1.5, 1, 1.5])
        fc5.markdown('<input class="label-input" type="text" value="Model" disabled>', unsafe_allow_html=True)
        model = sc5.text_input(label="Model", key=f"{prefix}_model", label_visibility="collapsed")
        tc5.markdown('<input class="label-input" type="text" value="Trim" disabled>', unsafe_allow_html=True)
        trim = fr5.text_input(label="Trim", key=f"{prefix}_trim", max_chars=4, label_visibility="collapsed")
        ft5.markdown('<input class="label-input" type="text" value="Odometer" disabled>', unsafe_allow_html=True)
        odometer = st5.text_input(label="Odometer", key=f"{prefix}_odometer", label_visibility="collapsed")
        fc6, sc6, tc6, fr6 = st.columns(4)
        fc6.markdown('<input class="label-input" type="text" value="Cost" disabled>', unsafe_allow_html=True)
        veh_cost = sc6.number_input(label="Cost", key=f"{prefix}_veh_cost", value=0.00, label_visibility='collapsed')
        tc6.markdown('<input class="label-input" type="text" value="Book Value" disabled>', unsafe_allow_html=True)
        book_value = fr6.number_input(label="Book Value", key=f"{prefix}_book_value", value=0.00, label_visibility='collapsed')
    with tc:
        fc7, sc7 = st.columns([1.5,4])
        fc7.markdown('<input class="label-input" type="text" value="Select Dealer" disabled>', unsafe_allow_html=True)
        dealer = sc7.selectbox("Select a Dealer", dealer_names_list, key=f"{prefix}_dealer", label_visibility="collapsed")
        fc7.markdown('<input class="label-input" type="text" value="Sales Person" disabled>', unsafe_allow_html=True)
        consultant = sc7.text_input(label="Sales Person", key=f"{prefix}_consultant", label_visibility="collapsed")
        fc7.markdown('<input class="label-input" type="text" value="Sales Manager" disabled>', unsafe_allow_html=True)
        manager = sc7.text_input(label="Sales Manager", key=f"{prefix}_manager", label_visibility="collapsed")
    trade_values = [0] * 2
    trade_payoffs = [0] * 2
    trade_acvs = [0] * 2
    with st.popover("Enter Trade-in Details", use_container_width=True):
        for i in range(2):
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
    
            tt2, fc2, sc2, tc2, fr2, ft2, st2, sv2, ec2 = st.columns([1, 1, 2, 1, 2, 1, 2, 1, 4])
            fc2.markdown('<input class="label-input" type="text" value="Miles" disabled>', unsafe_allow_html=True)
            trade_miles = sc2.text_input(f"Trade-in {i+1} Miles", key=f"{prefix}_trade_miles_{i+1}", label_visibility="collapsed")
            tc2.markdown('<input class="label-input" type="text" value="Trade Value" disabled>', unsafe_allow_html=True)
            trade_values[i] = fr2.number_input(f"Trade-in {i+1} Value", key=f"{prefix}_trade_value_{i+1}", value=0.00, label_visibility="collapsed")
            ft2.markdown('<input class="label-input" type="text" value="Payoff" disabled>', unsafe_allow_html=True)
            trade_payoffs[i] = st2.number_input(f"Trade-in {i+1} Payoff", key=f"{prefix}_trade_payoff_{i+1}", value=0.00, label_visibility="collapsed")
            sv2.markdown('<input class="label-input" type="text" value="Trade ACV" disabled>', unsafe_allow_html=True)
            trade_acvs[i] = ec2.number_input(f"Trade-in {i+1} ACV", key=f"{prefix}_trade_acv_{i+1}", value=0.00, label_visibility="collapsed")
            st.divider()
    
    left_col, right_col = st.columns(2)
    with right_col:
        labels_col, inputs_col = st.columns([1, 4])
        labels_col.markdown('<input class="label-input" type="text" value="Market Value" disabled>', unsafe_allow_html=True)
        market_value = inputs_col.number_input(label="Market Value", key=f"{prefix}_market_value", value=0.00, label_visibility='collapsed')
        labels_col.markdown('<input class="label-input" type="text" value="Discount" disabled>', unsafe_allow_html=True)
        discount = inputs_col.number_input(label="Discount", key=f"{prefix}_discount", value=0.00, label_visibility='collapsed')
        labels_col.markdown('<input class="label-input" type="text" value="Rebate" disabled>', unsafe_allow_html=True)
        rebate = inputs_col.number_input(label="Rebate", key=f"{prefix}_rebate", value=0.00, label_visibility='collapsed')
        labels_col.markdown('<input class="label-input" type="text" value="Trade Value" disabled>', unsafe_allow_html=True)
        trade_value = sum(trade_values)
        inputs_col.number_input(label="Trade Value", key=f"{prefix}_trade_value", value=trade_value, label_visibility='collapsed', disabled=True)
        labels_col.markdown('<input class="label-input" type="text" value="Trade ACV" disabled>', unsafe_allow_html=True)
        trade_acv = sum(trade_acvs)
        inputs_col.number_input(label="Trade ACV", key=f"{prefix}_trade_acv", value=trade_acv, label_visibility='collapsed', disabled=True)
        labels_col.markdown('<input class="label-input" type="text" value="Trade Payoff" disabled>', unsafe_allow_html=True)
        trade_payoff = sum(trade_payoffs)
        inputs_col.number_input(label="Trade Payoff", key=f"{prefix}_trade_payoff", value=trade_payoff, label_visibility='collapsed', disabled=True)
        labels_col.markdown('<input class="label-input" type="text" value="Doc Fee" disabled>', unsafe_allow_html=True)
        doc_fee = inputs_col.number_input(label="Doc Fee", key=f"{prefix}_doc_fee", value=799.00, label_visibility='collapsed')
        taxes = calculate_taxes(state, market_value, discount, doc_fee, trade_value)
        labels_col.markdown('<input class="label-input" type="text" value="Taxes" disabled>', unsafe_allow_html=True)
        if taxes is None:
            taxes = inputs_col.number_input(label="Taxes", key=f"{prefix}_taxes", value=0.00, label_visibility='collapsed')
        else:
            inputs_col.number_input(label="Taxes", key=f"{prefix}_taxes", value=taxes, label_visibility='collapsed', disabled=True)
        labels_col.markdown('<input class="label-input" type="text" value="Non-Tax Fees" disabled>', unsafe_allow_html=True)
        non_tax_fees = inputs_col.number_input(label="Non-Tax Fees", key=f"{prefix}_non_tax_fees", value=125.00, label_visibility='collapsed')
        balance = calculate_balance(market_value, discount, rebate, trade_value, trade_payoff, taxes, doc_fee, non_tax_fees)
        labels_col.markdown('<input class="label-input" type="text" value="Balance" disabled>', unsafe_allow_html=True)
        inputs_col.text_input(label="Balance", key=f"{prefix}_balance", value=f"{balance:.2f}", label_visibility='collapsed', disabled=True)
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
        value1 = col4.number_input(label="Down Payment", key=f"{prefix}_value1", value=1000.00)
        value2 = col5.number_input(label="Down Payment", key=f"{prefix}_value2", value=2000.00)
        value3 = col6.number_input(label="Down Payment", key=f"{prefix}_value3", value=3000.00)
        down_payments = [value1, value2, value3]
        terms = []
        rates = []
        default_terms = [36, 60, 72]
        for i in range(3):
            term = col1.number_input("Term", min_value=1, value=default_terms[i], key=f'{prefix}_term_{i+1}')
            if is_lease:
                rate = col2.number_input(f"Money Factor {i+1}", min_value=0.00000, max_value=1.00000, value=0.00275, format="%.5f", key=f'{prefix}_rate_{i+1}')
            else:
                rate = col2.number_input("Rate (%)", min_value=0.0, max_value=100.0, value=14.0, format="%.2f", key=f'{prefix}_rate_{i+1}')
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
    with st.popover("Enter Finance Details", use_container_width=True):
        c1, c2, c3, c4, c5, c6, c7, c8 = st.columns([1,1,1,1,1,3,1,3])
        c1.markdown('<input class="label-input" type="text" value="Body Style" disabled>', unsafe_allow_html=True)
        bodystyle = c2.text_input(label="Body Style", key=f"{prefix}_bodystyle", label_visibility="collapsed")
        c1.markdown('<input class="label-input" type="text" value="Fuel Type" disabled>', unsafe_allow_html=True)
        fuel_type = c2.text_input(label="Fuel Type", key=f"{prefix}_fuel_type", label_visibility="collapsed")
        c3.markdown('<input class="label-input" type="text" value="Driver\'s License" disabled>', unsafe_allow_html=True)
        drivers_license = c4.text_input(label="Driver's License", key=f"{prefix}_drivers_license", label_visibility="collapsed")
        c3.markdown('<input class="label-input" type="text" value="County" disabled>', unsafe_allow_html=True)
        county = c4.text_input(label="County", key=f"{prefix}_county", label_visibility="collapsed")
        c3.markdown('<input class="label-input" type="text" value="Plate Number" disabled>', unsafe_allow_html=True)
        platenum = c4.text_input(label="License Plate Number", key=f"{prefix}_platenum", label_visibility="collapsed")
        c3.markdown('<input class="label-input" type="text" value="Plate Expire" disabled>', unsafe_allow_html=True)
        plate_exp = c4.text_input(label="Plate Expiration", key=f"{prefix}_plate_exp", label_visibility="collapsed")
        c5.markdown('<input class="label-input" type="text" value="Lienholder Name" disabled>', unsafe_allow_html=True)
        lienholder_name = c6.selectbox("Select Lienholder", bank_list, key=f"{prefix}_bank", label_visibility="collapsed")

        # Update lienholder details
        lien_address, lien_city, lien_state, lien_zip_code = update_lienholder_details(lienholder_name)

        c5.markdown('<input class="label-input" type="text" value="Lienholder Address" disabled>', unsafe_allow_html=True)
        lienholder_address = c6.text_input(label="Lienholder Address", value=lien_address, key=f"{prefix}_lienholder_address", label_visibility="collapsed")
        c5.markdown('<input class="label-input" type="text" value="Lienholder City" disabled>', unsafe_allow_html=True)
        lienholder_city = c6.text_input(label="Lienholder City", value=lien_city, key=f"{prefix}_lienholder_city", label_visibility="collapsed")
        c5.markdown('<input class="label-input" type="text" value="Lienholder State" disabled>', unsafe_allow_html=True)
        lienholder_state = c6.text_input(label="Lienholder State", value=lien_state, key=f"{prefix}_lienholder_state", label_visibility="collapsed", max_chars=2)
        c5.markdown('<input class="label-input" type="text" value="Lienholder Zip" disabled>', unsafe_allow_html=True)
        lienholder_zip = c6.text_input(label="Lienholder Zip Code", value=lien_zip_code, key=f"{prefix}_lienholder_zip", label_visibility="collapsed", max_chars=5)
        c7.markdown('<input class="label-input" type="text" value="Ins Company" disabled>', unsafe_allow_html=True)
        ins_company = c8.text_input(label="Insurance Company", key=f"{prefix}_ins_company", label_visibility="collapsed")
        c7.markdown('<input class="label-input" type="text" value="Policy #" disabled>', unsafe_allow_html=True)
        policy = c8.text_input(label="Policy #", key=f"{prefix}_policy", label_visibility="collapsed")
        submit_modal_button = c8.button("Submit", key=f"{prefix}_submit_modal")
        if submit_modal_button:
            if trade_value > 0:
                if is_new:
                    template_pdf_path = 'docs/FIDocs1T.pdf'
                else:
                    template_pdf_path = 'docs/FIDocs1TUsed.pdf'
            else:
                if is_new:
                    template_pdf_path = 'docs/FIDocs.pdf'
                else:
                    template_pdf_path = 'docs/FIDocsUsed.pdf'
            words = customer.split()
            if len(words) >= 2:
                formatted_customer = ''.join(words[:2]).lower()
            else:
                formatted_customer = customer.replace(" ", "").lower()
            output_pdf_path = f'{formatted_customer}FIDocs.pdf'
            bos_stock2 = ""
            if trade_value > 0:
                bos_stock2 = modify_stocknum(stocknum)
            data = {
                "bos_date": datetime.today().strftime('%m/%d/%Y'),
                "bos_salesperson": consultant,
                "bos_salesperson_no": "",
                "bos_salesperson2": "",
                "bos_salesperson2_no": "",
                "bos_deal_num": "",
                "bos_buyer": customer,
                "box_cobuyer": "",
                "box_address": address,
                "bos_city": city,
                "bos_state": state,
                "bos_county": county,
                "bos_zip": zipcode,
                "bos_res_phone": phone_num,
                "bos_cell": "",
                "bos_email": email_address,
                "bos_cb_new": bos_cb_new,
                "bos_cb_used": bos_cb_used,
                "bos_year": year,
                "bos_make": make,
                "bos_model": model,
                "bos_bodystyle": bodystyle,
                "bos_vin1": vin,
                "bos_stock1": stocknum,
                "bos_color": "",
                "bos_miles1": odometer,
                "bos_sls_mgr": manager,
                "bos_bus_mgr": "",
                "bos_year2": st.session_state.get(f"{prefix}_trade_year_1", ""),
                "bos_make2": st.session_state.get(f"{prefix}_trade_make_1", ""),
                "bos_model2": st.session_state.get(f"{prefix}_trade_model_1", ""),
                "bos_miles2": st.session_state.get(f"{prefix}_trade_miles_1", ""),
                "bos_vin2": st.session_state.get(f"{prefix}_trade_vin_1", ""),
                "bos_stock2": bos_stock2,
                "bos_year3": st.session_state.get(f"{prefix}_trade_year_2", ""),
                "bos_make3": st.session_state.get(f"{prefix}_trade_make_2", ""),
                "bos_model3": st.session_state.get(f"{prefix}_trade_model_2", ""),
                "bos_miles3": st.session_state.get(f"{prefix}_trade_miles_2", ""),
                "bos_vin3": st.session_state.get(f"{prefix}_trade_vin_2", ""),
                "bos_stock3": "",
                "bos_vehicle_price": "{:.2f}".format(market_value - discount),
                "bos_accessories": "",
                "bos_trade_value": "{:.2f}".format(trade_value),
                "bos_total": "{:.2f}".format(market_value - discount - trade_value),
                "bos_docfee": "{:.2f}".format(doc_fee),
                "bos_taxes": "{:.2f}".format(taxes),
                "bos_tagfees": "{:.2f}".format(non_tax_fees - 11),
                "bos_titlefee": "{:.2f}".format(11.00),
                "bos_payoff": "{:.2f}".format(trade_payoff),
                "bos_gap": "",
                "bos_vsc": "",
                "bos_vsctax": "",
                "bos_subtotal": "{:.2f}".format((market_value - discount - trade_value) + doc_fee + taxes + non_tax_fees + trade_payoff),
                "bos_downpayment": "{:.2f}".format(value1),
                "bos_rebate": "{:.2f}".format(rebate),
                "bos_balance": "{:.2f}".format((market_value - discount - trade_value) + doc_fee + taxes + non_tax_fees + trade_payoff - rebate - value1),
                "Check Box3": "",
                "Check Box4": "",
                "Check Box5": "",
                "This includes the truck trailer and load": "",
                "Check Box6": "",
                "Check Box7": "",
                "Class of License": "",
                "Check Box8": "",
                "Check Box9": "",
                "Check Box10": "",
                "List Plate Number and Expiration": f"{platenum}           {plate_exp}",
                "YEAR": year,
                "MAKE": make,
                "BODY STYLE": bodystyle,
                "SERIES MODEL": model,
                "VEHICLE IDENTIFICATION NUMBER": vin,
                "FUEL TYPE": fuel_type,
                "ODOMETER READING": odometer,
                "Owner 1 ID": drivers_license,
                "Full Legal Name of Owner 1 First Middle Last Suffix or Company Name": customer,
                "Owner 2 ID": "",
                "Full Legal Name of Owner 2 First Middle Last Suffix or Company Name": "",
                "Check Box1": "",
                "Check Box2": "",
                "Residence Address Individual Business Address Firm City and State Zip Code": f'{address}         {city}, {state}         {zipcode}',
                "Mail Address if different from above City and State Zip Code": "",
                "Vehicle Location Address if different from residence address above City and State Zip Code": "",
                "Tax County": county,
                "Account #1": "",
                "Account #2": "",
                "Text1": "",
                "Date 1": "",
                "Text2": "",
                "Date 2": "",
                "Lienholder 1 ID": "",
                "Lienholder 1 name": lienholder_name,
                "Lienholder 2 ID": "",
                "Lienholder 2 name": "",
                "Address": lienholder_address,
                "undefined": "",
                "Address_2": "",
                "City": lienholder_city,
                "State": lienholder_state,
                "Zip Code": lienholder_zip,
                "City_2": "",
                "State_2": "",
                "Zip Code_2": "",
                "Insurance Company authorized in NC": ins_company,
                "Policy Number": policy,
                "Purchase Date": datetime.today().strftime('%m/%d/%Y'),
                "From Whom Purchased Name and Address": f"{dealer}\n{dealer_names[dealer].split(',')[0].strip()}\n{dealer_names[dealer].split(',')[1].strip()} {dealer_names[dealer].split(',')[2].strip()}",
                "NC Dealer No": "",
                "No_2": True,
                "Equipment": "",
                "mvr1_cb_New": bos_cb_new,
                "mvr1_cb_Used": bos_cb_used,
                "I We would like the personal information contained in this application to be available for disclosure": "",
                "Date": "",
                "County": "",
                "State_3": "",
                "purpose stated therein and in the capacity indicated": "",
                "or Typed Name": "",
                "My Commission Expires": "",
                "mvr6tYear": year,
                "mvr6tMake": make,
                "mvr6tBodyStyle": bodystyle,
                "mvr6tModel": model,
                "mvr6tVIN": vin,
                "mvr6tFuel": fuel_type,
                "mvr6tOwner 1 ID": drivers_license,
                "mvr6tOwner 2 ID": "",
                "mvr6tFull Legal Name of Owner 1 First Middle Last Suffix or Company Name": customer,
                "mvr6tFull Legal Name of Owner 2 First Middle Last Suffix or Company Name": "",
                "mvr6tResidence Address Individual Business Address Firm": address,
                "mvr6tCityState": f'{city}     {state}',
                "mvr6tZip": zipcode,
                "mvr6tCounty": county,
                "mvr6tMail Address if different from above": "",
                "mvr6tLienDate": "",
                "mvr6tLienMaturity": "",
                "mvr6tFIRST LIEN Account  Maturity Date MH Date of Lien": "",
                "mvr6tLienholder Name": lienholder_name,
                "mvr6tLienAddress": lienholder_address,
                "mvr6tLienCity": lienholder_city,
                "mvr6tLienState": lienholder_state,
                "mvr6tDMVcb": "",
                "mvr6tOwnerState": "",
                "mvr6tLienZip": lienholder_zip,
                "mvr6tNewcb": mvr6tNewcb,
                "mvr6tUsedcb": mvr6tUsedcb,
                "mvr6tPurchase Date": "",
                "mvr6tPrevious NC Title Number": "",
                "mvr6tDealer": "",
                "mvr6tPrinted Firm Name": "",
                "mvr6tDealer_Date": "",
                "mvr6tDealer_County": "",
                "mvr6tDealerState": "NC",
                "mvr63POABuyer": customer,
                "mvr63POAVehYear": year,
                "mvr63POAVehMake": make,
                "mvr63VehBodyStyle": bodystyle,
                "mvr63VehModel": model,
                "mvr63VehVIN": vin,
                "mvr63POADealer": dealer,
                "mvr63POADay": datetime.today().strftime('%d'),
                "mvr63POAMonth": datetime.today().strftime("%B"),
                "mvr63WitYear": datetime.today().strftime("%Y"),
                "mvr180Year": year,
                "mvr180Make": make,
                "mvr180BodyStyle": bodystyle,
                "mvr180Model": model,
                "mvr180VIN": vin,
                "mvr180Odometer": odometer,
                "mvr180CertifyMiles": "",
                "mvr180Discrepancy": "",
                "mvr180SellName": dealer,
                "mvr180SellerName2": dealer,
                "mvr180SellerAddress": dealer_names[dealer].split(',')[0].strip(),
                "mvr180SellerCity": dealer_names[dealer].split(',')[1].strip(),
                "mvr180SellerState": dealer_names[dealer].split(',')[2].strip().split(' ')[0],
                "mvr180SellerZip": dealer_names[dealer].split(',')[2].strip().split(' ')[1],
                "mvr180SellerDateCert": "",
                "mvr180BuyersName": customer,
                "mvr180BuyersAddress": address,
                "mvr180BuyerCity": city,
                "mvr180BuyerState": state,
                "mvr180BuyersZip": zipcode,
                "mvr180BuyerDateCert": "",
                "mvr181Year": year,
                "mvr181Make": make,
                "mvr181BodyStyle": bodystyle,
                "mvr181VIN": vin,
                "mvr181cbCollide": True,
                "mvr181cbSalvage": True,
                "mvr181cbFlood": True,
                "mvr181cbTheft": True,
                "mvr181cbRecon": True,
                "mvr181Date": "",
                "mvr181SellerAddress": f"{dealer_names[dealer].split(',')[0].strip()}, {dealer_names[dealer].split(',')[1].strip()}, {dealer_names[dealer].split(',')[2].strip()}",
                "BUYERMVR63": customer,
                "YEARMVR63": st.session_state["finance_trade_year_1"],
                "MAKEMVR63": st.session_state["finance_trade_make_1"],
                "BODYSTYLEMVR63": "",
                "MODELMVR63": st.session_state["finance_trade_model_1"],
                "VINMVR63": st.session_state["finance_trade_vin_1"],
                "POANAMEMVR63": "",
                "DAYMVR63": datetime.today().strftime('%d'),
                "MONTHMVR63": datetime.today().strftime("%B"),
                "WITYEARMVR63": datetime.today().strftime("%Y"),
                "YEARMVR180": st.session_state["finance_trade_year_1"],
                "MAKEMVR180": st.session_state["finance_trade_make_1"],
                "BODYSTYLEMVR180": "",
                "MODELMVR180": st.session_state["finance_trade_model_1"],
                "VINMVR180": st.session_state["finance_trade_vin_1"],
                "ODOMETERMVR180": st.session_state["finance_trade_miles_1"],
                "ODOCERTCBMVR180": "",
                "ODOWARNCBMVR180": "",
                "SELLERNAMEMVR180": customer,
                "SELLERNAME2MVR180": customer,
                "SELLERADDRESSMVR180": address,
                "SELLERCITYMVR180": city,
                "SELLERSTATEMVR180": state,
                "SELLERZIPMVR180": zipcode,
                "SELLERDATEMVR180": "",
                "BUYERNAMEMVR180": dealer,
                "BUYERADDRESSMVR180": dealer_names[dealer].split(',')[0].strip(),
                "BUYERCITYMVR180": dealer_names[dealer].split(',')[1].strip(),
                "BUYERSTATEMVR180": dealer_names[dealer].split(',')[2].strip().split(' ')[0],
                "BUYERZIPMVR180": dealer_names[dealer].split(',')[2].strip().split(' ')[1],
                "BUYERDATEMVR180": "",
                "YEARMVR181": st.session_state["finance_trade_year_1"],
                "MAKEMVR181": st.session_state["finance_trade_make_1"],
                "BODYSTYLEMVR181": "",
                "VINMVR181": st.session_state["finance_trade_vin_1"],
                "DAMAGECBNOMVR181": True,
                "SALVAGECBNOMVR181": True,
                "FLOODCBNOMVR181": True,
                "THEFTCBNOMVR181": True,
                "RECONCBNOMVR181": True,
                "DATEMVR181": "",
                "SELLERADDRESSMVR181": f"{address}, {city}, {state} {zipcode}",
                "YEARMVR6TT": year,
                "MAKEMVR6TT": make,
                "BODYSTYLEMVR6TT": bodystyle,
                "MODELMVR6TT": model,
                "VINMVR6TT": vin,
                "FUELMVR6TT": fuel_type,
                "OWNERIDMVR6TT": drivers_license,
                "OWNERMVR6TT": customer,
                "OWNERADDRESSMVR6TT": address,
                "CITYSTATEMVR6TT": city,
                "ZIPMVR6TT": zipcode,
                "COUNTYMVR6TT": county,
                "LIENDATEMVR6TT": "",
                "LIENACCOUNTNOMVR6TT": "",
                "LIENHOLDERMVR6TT": lienholder_name,
                "LIENHOLDERIDMVR6TT": "",
                "LIENADDRESSMVR6TT": lienholder_address,
                "LIENCITYMVR6TT": lienholder_city,
                "LIENSTATEMVR6TT": lienholder_state,
                "LIENZIPMVR6TT": lienholder_zip,
                "BUYERDATEMVR6TT": "",
                "CAPACITYMVR6TT": "",
                "PRINCIPALSMVR6TT": "",
                "WONAME": customer,
                "WOSTKNO": stocknum,
                "WONEWUSED": newused,
                "WOADDRESS": address,
                "WOSTATE": state,
                "WOYEAR": year,
                "WOMAKE": make,
                "WOCITY": city,
                "WOZIP": zipcode,
                "WOMODEL": model,
                "WOPHONE": phone_num,
                "WOVIN": vin,
                "WOEMAIL": email_address,
                "WOSALESPERSON": consultant,
                "WODELDATE": datetime.today().strftime('%m/%d/%Y'),
                "CPDATE": datetime.today().strftime('%m/%d/%Y'),
                "CPBUYER": customer,
                "CPSALESPERSON": consultant,
                "CPINS": ins_company,
                "CPMANAGER": manager,
                "CPPOLICY": policy,
                "CPYEAR": st.session_state["finance_trade_year_1"],
                "CPMAKE": st.session_state["finance_trade_make_1"],
                "CPMODEL": st.session_state["finance_trade_model_1"],
                "CPPAYOFFAMT": str("  ${:,.2f}".format(st.session_state["finance_trade_payoff_1"])),
                "vinverifystock": stocknum,
                "vinverifyvin": vin,
                "vinverifymiles": odometer,
                "vinverifytradevin": st.session_state["finance_trade_vin_1"],
                "vinverifytrademiles": st.session_state["finance_trade_miles_1"],
                "guidemake": make,
                "guidemodel": model,
                "guideyear": year,
                "guidevin": vin,
                "guidestock": stocknum,
                "guidecb1": True,
                "guidedealer": dealer,
                "guideaddress": f"{dealer_names[dealer].split(',')[0].strip()}, {dealer_names[dealer].split(',')[1].strip()}, {dealer_names[dealer].split(',')[2].strip()}",
                "guidedate": datetime.today().strftime('%m/%d/%Y'),
                "LAWBUYER": customer,
                "LAWBUYADDRESS": f'{address}, {city}, {state} {zipcode}',
                "LAWBUYCELL": phone_num,
                "LAWBUYEMAIL": email,
                "SellerCreditor Name and Address": f"{dealer}\n{dealer_names[dealer].split(',')[0].strip()}\n{dealer_names[dealer].split(',')[1].strip()} {dealer_names[dealer].split(',')[2].strip()}",
                "LAWNEWUSED": "NEW" if is_new else "USED",
                "LAWYEAR": year,
                "LAWMAKEMODEL": f"{make} {model}",
                "LAWVIN": vin,
                "LAWRATE": f"{rates[0]:.2f}",
                "LAWFINANCECHARGE": '',
                "LAWAMTFINANCED": '',
                "LAWTOTALPAY": '',
                "LAWDOWNPAY": '',
                "LAWTOTALCOST": '',
                "LAWNUMPAYMENTS": '',
                "LAWMONTHLYPAY": '',
                "When Payments Are Due": 'Monthly',
                "LAWBEGINPAY": '',
                "LAWSALESTAX": "{:.2f}".format(taxes),
                "LAWCASHPRICE": '',
                "LAWTRADEYEAR": st.session_state["finance_trade_year_1"],
                "LAWTRADEMAKE": st.session_state["finance_trade_make_1"],
                "LAWTRADEMODEL": st.session_state["finance_trade_model_1"],
                "LAWGROSSTRADE": '',
                "Less Pay Off Made By Seller to": '',
                "LAWCASHDOWNPAY": "{:.2f}".format(value1),
            }

            fill_fi_pdf(template_pdf_path, output_pdf_path, data)
            with open(output_pdf_path, 'rb') as f:
                st.download_button('Download F&I Docs', f, file_name=output_pdf_path)

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
            if not customer:
                filename = 'quote.pdf'
            else:
                filename = f'{customer}.pdf'
            pdf_file = generate_pdf(data, filename=filename)
            with open(pdf_file, 'rb') as f:
                st.download_button('Download Quote', f, file_name=pdf_file, key=f"{prefix}_download_button")

finance, lease = st.tabs(["Finance", "Lease"])
with finance:
    render_tab(calculate_monthly_payment, prefix="finance")
with lease:
    render_tab(calculate_lease_payment, prefix="lease", is_lease=True)
