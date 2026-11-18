import os
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

class AssessmentPDFGenerator:
    """
    Generates a professional Insurance Claim Assessment PDF Report using ReportLab.
    """
    def generate_pdf(self, claim_data: dict, output_path: str) -> str:
        doc = SimpleDocTemplate(
            output_path,
            pagesize=letter,
            rightMargin=36,
            leftMargin=36,
            topMargin=36,
            bottomMargin=36
        )

        styles = getSampleStyleSheet()
        
        # Custom Styles
        title_style = ParagraphStyle(
            'DocTitle',
            parent=styles['Heading1'],
            fontSize=20,
            leading=24,
            textColor=colors.HexColor("#1e293b"),
            fontName="Helvetica-Bold"
        )
        subtitle_style = ParagraphStyle(
            'DocSubTitle',
            parent=styles['Normal'],
            fontSize=10,
            leading=14,
            textColor=colors.HexColor("#64748b")
        )
        heading_style = ParagraphStyle(
            'SectionHeader',
            parent=styles['Heading2'],
            fontSize=13,
            leading=16,
            textColor=colors.HexColor("#0f172a"),
            fontName="Helvetica-Bold",
            spaceBefore=10,
            spaceAfter=6
        )
        normal_style = ParagraphStyle(
            'Body',
            parent=styles['Normal'],
            fontSize=9,
            leading=13,
            textColor=colors.HexColor("#334155")
        )
        reason_style = ParagraphStyle(
            'ReasonText',
            parent=styles['Normal'],
            fontSize=9,
            leading=12,
            textColor=colors.HexColor("#991b1b")
        )

        story = []

        # 1. Header Section
        story.append(Paragraph("AI VEHICLE INSURANCE ASSESSMENT REPORT", title_style))
        story.append(Paragraph(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | Reference: {claim_data.get('claim_id', 'CLM-2026-9021')}", subtitle_style))
        story.append(Spacer(1, 10))
        story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#0284c7"), spaceAfter=12))

        # 2. Vehicle Verification Section
        story.append(Paragraph("1. Vehicle & Claim Identification", heading_style))
        veh_ver = claim_data.get("vehicle_verification", {})
        claimed = veh_ver.get("claimed", {})
        detected = veh_ver.get("detected", {})
        conf = veh_ver.get("confidences", {})

        veh_table_data = [
            ["Claimed Make/Model:", f"{claimed.get('brand', 'N/A')} {claimed.get('model', 'N/A')}", "Verification Status:", "VERIFIED" if veh_ver.get("is_verified") else "MISMATCH"],
            ["AI Detected Make/Model:", f"{detected.get('brand', 'N/A')} {detected.get('model', 'N/A')}", "Overall Confidence:", f"{conf.get('overall', 0)*100:.0f}%"],
            ["Badge OCR Detected:", detected.get('badge_ocr', 'N/A'), "Logo Confidence:", f"{conf.get('logo', 0)*100:.0f}%"]
        ]

        t_veh = Table(veh_table_data, colWidths=[120, 160, 120, 140])
        t_veh.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#f8fafc")),
            ('TEXTCOLOR', (0,0), (-1,-1), colors.HexColor("#334155")),
            ('FONTNAME', (0,0), (-1,-1), 'Helvetica'),
            ('FONTSIZE', (0,0), (-1,-1), 9),
            ('BOTTOMPADDING', (0,0), (-1,-1), 4),
            ('TOPPADDING', (0,0), (-1,-1), 4),
            ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#e2e8f0"))
        ]))
        story.append(t_veh)
        story.append(Spacer(1, 12))

        # 3. Damage Inventory & Cost Estimation Table
        story.append(Paragraph("2. Part-by-Part Damage Inventory & Cost Estimate", heading_style))
        cost_data = claim_data.get("cost_estimate", {})
        line_items = cost_data.get("line_items", [])

        if not line_items:
            story.append(Paragraph("<b>NO VEHICLE DAMAGE DETECTED</b> — All uploaded photos exhibit smooth body panels and pristine condition.", ParagraphStyle('CleanNotice', parent=normal_style, textColor=colors.HexColor("#15803d"), fontName="Helvetica-Bold", fontSize=10)))
            story.append(Spacer(1, 4))
            dmg_rows = [
                ["Part", "Action", "Part Cost (INR)", "Labor Cost (INR)", "Subtotal (INR)"],
                ["Pristine Vehicle Condition", "No Action Required", "INR 0", "INR 0", "INR 0"],
                ["TOTAL ESTIMATED REPAIR COST", "", "", "", "INR 0"]
            ]
        else:
            dmg_headers = ["Part", "Action", "Part Cost (INR)", "Labor Cost (INR)", "Subtotal (INR)"]
            dmg_rows = [dmg_headers]

            for item in line_items:
                dmg_rows.append([
                    item.get("part", ""),
                    item.get("decision", ""),
                    f"INR {item.get('part_cost', 0):,}",
                    f"INR {item.get('labor_cost', 0):,}",
                    f"INR {item.get('subtotal', 0):,}"
                ])

            dmg_rows.append([
                "TOTAL ESTIMATED REPAIR COST", "", "", "", f"INR {cost_data.get('grand_total', 0):,}"
            ])

        t_dmg = Table(dmg_rows, colWidths=[140, 100, 100, 100, 100])
        t_dmg.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#0f172a")),
            ('TEXTCOLOR', (0,0), (-1,0), colors.white),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('FONTSIZE', (0,0), (-1,-1), 9),
            ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#cbd5e1")),
            ('BACKGROUND', (0,-1), (-1,-1), colors.HexColor("#f1f5f9")),
            ('FONTNAME', (0,-1), (-1,-1), 'Helvetica-Bold'),
            ('TEXTCOLOR', (0,-1), (-1,-1), colors.HexColor("#0f172a")),
            ('TOPPADDING', (0,0), (-1,-1), 5),
            ('BOTTOMPADDING', (0,0), (-1,-1), 5)
        ]))
        story.append(t_dmg)
        story.append(Spacer(1, 12))

        # 4. Explainable Fraud Assessment
        story.append(Paragraph("3. Explainable Fraud Risk Assessment", heading_style))
        fraud = claim_data.get("fraud_assessment", {})
        score = fraud.get("fraud_score", 0)
        risk = fraud.get("risk_tier", "Low Risk")

        bg_color = colors.HexColor("#fef2f2") if score >= 50 else (colors.HexColor("#fffbebf1") if score >= 25 else colors.HexColor("#f0fdf4"))
        border_color = colors.HexColor("#ef4444") if score >= 50 else (colors.HexColor("#f59e0b") if score >= 25 else colors.HexColor("#22c55e"))

        fraud_table_data = [
            ["Fraud Risk Score:", f"{score} / 100", "Risk Level:", risk],
            ["Recommendation:", Paragraph(fraud.get("recommendation", ""), normal_style), "", ""]
        ]
        t_fraud = Table(fraud_table_data, colWidths=[120, 140, 100, 180])
        t_fraud.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), bg_color),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('TEXTCOLOR', (0,0), (-1,-1), colors.HexColor("#1e293b")),
            ('GRID', (0,0), (-1,-1), 1, border_color),
            ('SPAN', (1,1), (3,1))
        ]))
        story.append(t_fraud)
        story.append(Spacer(1, 8))

        story.append(Paragraph("Evidence & Explanation Audit Trail:", ParagraphStyle('Sub', parent=normal_style, fontName='Helvetica-Bold')))
        for r in fraud.get("explanation_reasons", []):
            story.append(Paragraph(f"• {r}", reason_style if score >= 25 else normal_style))

        story.append(Spacer(1, 20))
        story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#cbd5e1"), spaceAfter=10))
        story.append(Paragraph("Certified by AI Assessment Pipeline | Confidential Insurance Document", subtitle_style))

        doc.build(story)
        return output_path
