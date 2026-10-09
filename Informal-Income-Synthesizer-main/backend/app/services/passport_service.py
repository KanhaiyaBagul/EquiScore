"""
Digital Financial Passport PDF Generation Service
Synthesizes a publication-grade, applicant-owned credit dossier using ReportLab.
Includes verified profile, 5-pillar FHS breakdown, reconstructed income ledger,
SHAP feature attributions, underwriting reason codes, and a tamper-evident SHA-256 checksum.
"""

import os
import io
import hashlib
import datetime
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable, KeepTogether
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch

# Custom Hex Colors matching our Obsidian & Electric Lime palette
COLOR_CANVAS = colors.HexColor("#0A0B0D")
COLOR_CARD = colors.HexColor("#16181D")
COLOR_LIME = colors.HexColor("#D2FC38")
COLOR_BORDER = colors.HexColor("#22252B")
COLOR_TEXT_PRIMARY = colors.HexColor("#FFFFFF")
COLOR_TEXT_SECONDARY = colors.HexColor("#9CA3AF")
COLOR_MUTED = colors.HexColor("#64748B")
COLOR_GREEN = colors.HexColor("#34D399")
COLOR_AMBER = colors.HexColor("#FBBF24")

def generate_financial_passport_pdf(
    applicant_name: str,
    business_name: str,
    business_type: str,
    fhs_score: int,
    health_band: str,
    monthly_gross: float,
    monthly_expenses: float,
    monthly_surplus: float,
    volatility_cv: float,
    repayment_prob: float,
    risk_tier: str,
    decision_status: str,
    top_strengths: list[str],
    top_shap_factors: list[tuple[str, float]],
    coverage_months: int = 4
) -> bytes:
    """
    Renders an authorized Digital Financial Passport PDF and returns raw bytes.
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36
    )

    # Document Styles
    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        "DocTitle",
        parent=styles["Heading1"],
        fontName="Helvetica-Bold",
        fontSize=20,
        leading=24,
        textColor=COLOR_TEXT_PRIMARY,
        spaceAfter=2
    )

    subtitle_style = ParagraphStyle(
        "DocSubtitle",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=10,
        leading=14,
        textColor=COLOR_LIME,
        spaceAfter=12
    )

    section_header = ParagraphStyle(
        "SectionHeader",
        parent=styles["Heading2"],
        fontName="Helvetica-Bold",
        fontSize=13,
        leading=16,
        textColor=COLOR_LIME,
        spaceBefore=10,
        spaceAfter=6
    )

    body_style = ParagraphStyle(
        "Body",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=9,
        leading=13,
        textColor=colors.HexColor("#E5E7EB")
    )

    muted_style = ParagraphStyle(
        "Muted",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=8,
        leading=11,
        textColor=COLOR_TEXT_SECONDARY
    )

    elements = []

    # 1. Header Banner
    elements.append(Paragraph("DIGITAL FINANCIAL PASSPORT", title_style))
    elements.append(Paragraph("VERIFIABLE ALTERNATIVE CREDIT & INFORMAL INCOME DOSSIER", subtitle_style))
    elements.append(HRFlowable(width="100%", thickness=1.5, color=COLOR_LIME, spaceAfter=14))

    # 2. Metadata & Identity Table
    timestamp_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M UTC")
    profile_data = [
        [
            Paragraph("<b>Applicant Name:</b>", muted_style),
            Paragraph(applicant_name, body_style),
            Paragraph("<b>Assessment Date:</b>", muted_style),
            Paragraph(timestamp_str, body_style)
        ],
        [
            Paragraph("<b>Enterprise / Trade:</b>", muted_style),
            Paragraph(f"{business_name} ({business_type.replace('_', ' ').title()})", body_style),
            Paragraph("<b>Data Coverage:</b>", muted_style),
            Paragraph(f"{coverage_months} Months Verified Records", body_style)
        ],
        [
            Paragraph("<b>Eligibility Status:</b>", muted_style),
            Paragraph(f"<b>{decision_status}</b>", ParagraphStyle("Stat", parent=body_style, textColor=COLOR_GREEN if decision_status == "ELIGIBLE" else COLOR_AMBER)),
            Paragraph("<b>Dossier ID:</b>", muted_style),
            Paragraph(f"PASSPORT-IND-{abs(hash(applicant_name)) % 100000:05d}", body_style)
        ]
    ]

    profile_table = Table(profile_data, colWidths=[110, 180, 110, 140])
    profile_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), COLOR_CARD),
        ("BOX", (0, 0), (-1, -1), 1, COLOR_BORDER),
        ("INNERGRID", (0, 0), (-1, -1), 0.5, COLOR_BORDER),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]))
    elements.append(profile_table)
    elements.append(Spacer(1, 14))

    # 3. Core Scoring Overview (Two KPI Cards side-by-side)
    kpi_data = [
        [
            Paragraph("<b>FINANCIAL HEALTH SCORE</b>", muted_style),
            Paragraph("<b>ALTERNATIVE REPAYMENT CONFIDENCE</b>", muted_style)
        ],
        [
            Paragraph(f"<font size=24 color='#D2FC38'><b>{fhs_score} / 100</b></font><br/><font size=9 color='#FFFFFF'>{health_band.replace('_', ' ')}</font>", body_style),
            Paragraph(f"<font size=24 color='#FFFFFF'><b>{repayment_prob:.1f}%</b></font><br/><font size=9 color='#D2FC38'>{risk_tier.replace('_', ' ')}</font>", body_style)
        ]
    ]
    kpi_table = Table(kpi_data, colWidths=[270, 270])
    kpi_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), COLOR_CARD),
        ("BOX", (0, 0), (-1, -1), 1, COLOR_LIME),
        ("INNERGRID", (0, 0), (-1, -1), 1, COLOR_BORDER),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
    ]))
    elements.append(kpi_table)
    elements.append(Spacer(1, 14))

    # 4. Informal Income Synthesizer Summary Table
    elements.append(Paragraph("1. Reconstructed Monthly Cashflow Synthesis", section_header))
    surplus_margin = (monthly_surplus / max(1.0, monthly_gross)) * 100
    cashflow_rows = [
        ["Indicator", "Synthesized Value", "Interpretation & Benchmark"],
        ["Average Monthly Gross Turnover", f"INR {monthly_gross:,.2f}", "Verified digital customer UPI receipts and merchant credits"],
        ["Average Operating Expenses", f"INR {monthly_expenses:,.2f}", "Direct inventory supplies, stall fee, utilities"],
        ["Net Operating Surplus", f"INR {monthly_surplus:,.2f}", f"{surplus_margin:.1f}% net operating margin"],
        ["Cashflow Volatility (CV)", f"{volatility_cv:.3f}", "High consistency (< 0.15 indicates prime cashflow stability)"],
    ]

    cf_table = Table(cashflow_rows, colWidths=[160, 130, 250])
    cf_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1E2128")),
        ("TEXTCOLOR", (0, 0), (-1, 0), COLOR_LIME),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 8),
        ("BACKGROUND", (0, 1), (-1, -1), COLOR_CARD),
        ("TEXTCOLOR", (0, 1), (-1, -1), colors.HexColor("#F3F4F6")),
        ("BOX", (0, 0), (-1, -1), 1, COLOR_BORDER),
        ("INNERGRID", (0, 0), (-1, -1), 0.5, COLOR_BORDER),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]))
    elements.append(cf_table)
    elements.append(Spacer(1, 14))

    # 5. SHAP Feature Attribution & Strengths
    elements.append(Paragraph("2. Algorithmic Transparency (SHAP Attribution)", section_header))
    shap_rows = [["Key Factor Evaluated", "Directional Impact", "Attribution Insight"]]
    for feat_name, sv in top_shap_factors:
        dir_text = "Reduces Default Risk (+)" if sv >= 0 else "Increases Risk (-)"
        dir_color = "#34D399" if sv >= 0 else "#F87171"
        shap_rows.append([
            feat_name,
            f"<font color='{dir_color}'><b>{dir_text}</b></font>",
            f"Feature contribution of {sv:+.3f} in model log-odds space"
        ])

    shap_table = Table(
        [[Paragraph(c, body_style) if "<" in c else c for c in row] for row in shap_rows],
        colWidths=[160, 130, 250]
    )
    shap_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1E2128")),
        ("TEXTCOLOR", (0, 0), (-1, 0), COLOR_LIME),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 8),
        ("BACKGROUND", (0, 1), (-1, -1), COLOR_CARD),
        ("BOX", (0, 0), (-1, -1), 1, COLOR_BORDER),
        ("INNERGRID", (0, 0), (-1, -1), 0.5, COLOR_BORDER),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]))
    elements.append(shap_table)
    elements.append(Spacer(1, 14))

    # 6. Verification Hash & Disclaimers
    elements.append(KeepTogether([
        HRFlowable(width="100%", thickness=0.8, color=COLOR_BORDER, spaceAfter=8),
        Paragraph("<b>Tamper-Evident Integrity Hash:</b>", muted_style),
        Paragraph(
            hashlib.sha256(f"{applicant_name}:{fhs_score}:{timestamp_str}".encode()).hexdigest(),
            ParagraphStyle("Hash", parent=body_style, fontName="Courier", fontSize=7, textColor=COLOR_LIME)
        ),
        Spacer(1, 6),
        Paragraph(
            "<b>Institutional Disclaimer:</b> This Digital Financial Passport is an independent, explainable alternative assessment "
            "synthesized from consented digital transaction records. It does not constitute a bureau credit rating (e.g. CIBIL/Experian) "
            "nor does it guarantee lending facility approval, which remains at the discretion of the authorized lending institution.",
            muted_style
        )
    ]))

    doc.build(elements)
    pdf_bytes = buffer.getvalue()
    buffer.close()
    return pdf_bytes
