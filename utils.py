import pdfrw, logging
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Spacer, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors

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

def calculate_lease_payment(market_value, doc_fee, non_tax_fees, doc, down_payment, rebate, money_factor, term_months, residual_percentage, trade_value, trade_payoff, discount):
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
    if state == "NC" or state == "nc":
        return taxable_amount * 0.03
    elif state == "SC" or state == 'sc':
        return 500.00
    else:
        return 0.00

def generate_pdf(data, filename='quote.pdf'):
    try:
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
            ["Date:", data.get('date', '')],
            ["Sales Person:", data.get('salesperson', '')],
            ["Manager:", data.get('manager', '')]
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
            ["Customer", data.get('buyer', ''), "", ""],
            ["", data.get('address', ''), "", ""],
            ["", f"{data.get('city', '')}, {data.get('state', '')} {data.get('zip', '')}", "", ""],
            ["Email", data.get('email_add', ''), "Phone", data.get('cell_phone', '')]
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
        elements.append(Spacer(1, 40))

        # Vehicle selection and trade-in details
        selection_data = [
            ["VEHICLE", "", "", "", "", ""],
            ["YEAR", "MAKE", "MODEL", "STOCK NO.", "VIN", "MILES"],
            [
                data.get('year', ''),
                data.get('make', ''),
                f"{data.get('model', '')} {data.get('trim', '')}".strip(),  # Concatenating model and trim
                data.get('stock_no', ''),
                data.get('vin', ''),
                data.get('miles', '')
            ]
        ]
        if data.get('trade_vin'):
            selection_data.append(["TRADE-IN", "", "", "", ""])
            selection_data.append(["YEAR", "MAKE", "MODEL", "", "VIN", "MILES"])
            selection_data.append([
                data.get('trade_year', ''),
                data.get('trade_make', ''),
                f"{data.get('trade_model', '')} {data.get('trade_trim', '')}".strip(),  # Concatenating trade model and trade trim
                "",
                data.get('trade_vin', ''),
                data.get('trade_miles', '')
            ])
        if data.get('trade_vin_2'):
            selection_data.append(["TRADE-IN 2", "", "", "", ""])
            selection_data.append(["YEAR", "MAKE", "MODEL", "", "VIN", "MILES"])
            selection_data.append([
                data.get('trade_year_2', ''),
                data.get('trade_make_2', ''),
                f"{data.get('trade_model_2', '')} {data.get('trade_trim_2', '')}".strip(),  # Concatenating trade model 2 and trade trim 2
                "",
                data.get('trade_vin_2', ''),
                data.get('trade_miles_2', '')
            ])
        selection_table = Table(selection_data, colWidths=[55, 65, 100, 80, 135, 80])
        selection_table.setStyle(TableStyle([
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('BACKGROUND', (0, 0), (-1, 0), colors.black),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER')
        ]))

        if data.get('trade_vin'):
            selection_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 3), (-1, 3), colors.black),
                ('TEXTCOLOR', (0, 3), (-1, 3), colors.white),
                ('FONTNAME', (0, 3), (-1, 3), 'Helvetica-Bold')
            ]))
        if data.get('trade_vin_2'):
            selection_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 6), (-1, 6), colors.black),
                ('TEXTCOLOR', (0, 6), (-1, 6), colors.white),
                ('FONTNAME', (0, 6), (-1, 6), 'Helvetica-Bold')
            ]))

        elements.append(selection_table)
        elements.append(Spacer(1, 20))

        # Payment grid data (without creating a table yet)
        grid_data = [["Term"] + [f"${dp:.2f}" for dp in data['quotes'][list(data['quotes'].keys())[0]].keys()]]
        for term, payments in data['quotes'].items():
            row = [term]
            for dp, payment in payments.items():
                row.append(f"${payment:.2f}")
            grid_data.append(row)

        # Detailed breakdown table
        market_value = data.get('sale_price', 0)
        savings = data.get('rebate', 0) + data.get('discount', 0)
        sales_price = market_value - savings

        breakdown_data = [
            ["Market Value", f"${market_value:.2f}"] if market_value != 0 else None,
            ["Savings", f"${savings:.2f}"] if savings != 0 else None,
            ["Sales Price", f"${sales_price:.2f}"] if market_value != 0 else None,
            ["Trade Value", f"${data.get('trade_value', 0):.2f}"] if data.get('trade_value', 0) != 0 else None,
            ["Trade Payoff", f"${data.get('trade_payoff', 0):.2f}"] if data.get('trade_payoff', 0) != 0 else None,
            ["Doc Fee", f"${data.get('doc_fee', 0):.2f}"] if data.get('doc_fee', 0) != 0 else None,
            ["Sales Tax", f"${data.get('sales_tax', 0):.2f}"] if data.get('sales_tax', 0) != 0 else None,
            ["Non Tax Fees", f"${data.get('non_tax_fees', 0):.2f}"] if data.get('non_tax_fees', 0) != 0 else None,
            ["Balance", f"${data.get('balance', 0):.2f}"] if data.get('balance', 0) != 0 else None,
        ]
        breakdown_data = [row for row in breakdown_data if row is not None]

        breakdown_table = Table(breakdown_data, colWidths=[100, 80])
        breakdown_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 6),
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('VALIGN', (0, 0), (-1, -1), 'TOP')
        ]))
        
        for row_idx in range(len(breakdown_data)):
            breakdown_table.setStyle(TableStyle([
                ('LINEBELOW', (1, row_idx), (1, row_idx), 1, colors.black)
            ]))

        elements.append(Spacer(1, 30))

        # Create the payment grid table and combine it with the breakdown table
        grid_table = Table(grid_data, colWidths=[75] + [75]*len(data['quotes'][list(data['quotes'].keys())[0]].keys()))
        grid_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.black),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-BoldOblique'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 6),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica-Oblique'),
            ('FONTSIZE', (0, 1), (-1, -1), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))

        combined_data = [
            [grid_table, spacer, breakdown_table]
        ]

        combined_table = Table(combined_data, colWidths=[300, 20, 220], rowHeights=None, hAlign='LEFT')
        combined_table.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'TOP')
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
    except Exception as e:
        logging.error(f"Failed to generate PDF: {e}")
        return None

def fill_pdf(template_pdf_path, output_pdf_path, data):
    template_pdf = pdfrw.PdfReader(template_pdf_path)
    for page in template_pdf.pages:
        annotations = page['/Annots']
        if annotations:
            for annotation in annotations:
                if annotation['/Subtype'] == '/Widget':
                    field = annotation.get('/T')
                    if field:
                        field_name = field[1:-1]
                        if field_name in data:
                            annotation.update(
                                pdfrw.PdfDict(
                                    V=pdfrw.PdfString.encode(data[field_name]),
                                    AP=''
                                )
                            )
                            annotation.update(pdfrw.PdfDict(AS=pdfrw.PdfName('Yes')))
    pdfrw.PdfWriter().write(output_pdf_path, template_pdf)
