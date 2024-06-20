def generate_pdf(data, filename='quote.pdf'):
    doc = SimpleDocTemplate(filename, pagesize=letter, topMargin=30)
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
    elements.append(Spacer(1, 20))  # Reduced spacing here
    
    # Detailed breakdown table
    breakdown_data = [
        ["Sales Price", f"${data['sale_price']:.2f}"],
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
    
    elements.append(breakdown_table)
    elements.append(Spacer(1, 20))  # Reduced spacing here
    
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
    
    grid_table = Table(grid_data, colWidths=[70] + [70]*len(data['quotes'][list(data['quotes'].keys())[0]].keys()))
    grid_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
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
    elements.append(Spacer(1, 20))  # Reduced spacing here
    
    # Leasing quotes header
    elements.append(Paragraph("Monthly Payments (Lease)", styles['Normal']))
    elements.append(Spacer(1, 10))
    
    # Grid data for lease quotes
    lease_grid_data = [["Term"] + [f"${dp:.2f}" for dp in data['lease_quotes'][list(data['lease_quotes'].keys())[0]].keys()]]
    for term, payments in data['lease_quotes'].items():
        row = [term]
        for dp, payment in payments.items():
            row.append(f"${payment:.2f}")
        lease_grid_data.append(row)
    
    lease_grid_table = Table(lease_grid_data, colWidths=[70] + [70]*len(data['lease_quotes'][list(data['lease_quotes'].keys())[0]].keys()))
    lease_grid_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.whitesmoke),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))
    
    elements.append(lease_grid_table)
    elements.append(Spacer(1, 20))  # Reduced spacing here

    # Calculate residual value
    residual_value = data['sale_price'] * (data['residual_percent'] / 100)
    
    # Add residual value below the lease payments grid
    residual_data = [["Residual Value", f"${residual_value:.2f}"]]
    residual_table = Table(residual_data, colWidths=[150, 100])
    residual_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.whitesmoke),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))
    
    elements.append(residual_table)
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
