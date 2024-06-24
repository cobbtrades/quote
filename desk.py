import streamlit as st

st.set_page_config(page_title="Desking App")

with open("styles.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Page title
st.title("Desking App")

def calculate_monthly_payment(principal, down_payment, annual_rate, term_months):
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
        col1, col2, col3, col4, col5 = st.columns(5)

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
        
        # 3x3 grid displaying some calculations based on input values and balance
        term1 = col1.number_input(label="Term 1", key="term1", value=60)
        rate1 = col2.number_input(label="Rate 1", key="rate1", value=14.00, )
        grid1 = col3.markdown(f'<div class="centered-metric"><div class="stMetric">{calculate_monthly_payment(balance, value1, rate1, term1)}</div></div>', unsafe_allow_html=True)
        grid2 = col4.markdown(f'<div class="centered-metric"><div class="stMetric">{calculate_monthly_payment(balance, value2, rate1, term1)}</div></div>', unsafe_allow_html=True)
        grid3 = col5.markdown(f'<div class="centered-metric"><div class="stMetric">{calculate_monthly_payment(balance, value3, rate1, term1)}</div></div>', unsafe_allow_html=True)
        
        term2 = col1.number_input(label="Term 2", key="term2", value=66)
        rate2 = col2.number_input(label="Rate 2", key="rate2", value=14.00)
        grid4 = col3.markdown(f'<div class="centered-metric"><div class="stMetric">{calculate_monthly_payment(balance, value1, rate2, term2)}</div></div>', unsafe_allow_html=True)
        grid5 = col4.markdown(f'<div class="centered-metric"><div class="stMetric">{calculate_monthly_payment(balance, value2, rate2, term2)}</div></div>', unsafe_allow_html=True)
        grid6 = col5.markdown(f'<div class="centered-metric"><div class="stMetric">{calculate_monthly_payment(balance, value3, rate2, term2)}</div></div>', unsafe_allow_html=True)
        
        term3 = col1.number_input(label="Term 3", key="term3", value=72)
        rate3 = col2.number_input(label="Rate 3", key="rate3", value=14.00)
        grid7 = col3.markdown(f'<div class="centered-metric"><div class="stMetric">{calculate_monthly_payment(balance, value1, rate3, term3)}</div></div>', unsafe_allow_html=True)
        grid8 = col4.markdown(f'<div class="centered-metric"><div class="stMetric">{calculate_monthly_payment(balance, value2, rate3, term3)}</div></div>', unsafe_allow_html=True)
        grid9 = col5.markdown(f'<div class="centered-metric"><div class="stMetric">{calculate_monthly_payment(balance, value3, rate3, term3)}</div></div>', unsafe_allow_html=True)
    


