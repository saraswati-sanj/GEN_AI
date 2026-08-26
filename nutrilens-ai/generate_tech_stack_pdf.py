"""
NutriLens AI — Technical Stack PDF Generator
Generates a PDF document for NutriLens AI tech stack and system architecture.
"""
import os
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable, KeepTogether
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

def generate_pdf(filename="NutriLens_AI_Tech_Stack_Specification.pdf"):
    pdf_path = os.path.abspath(filename)
    doc = SimpleDocTemplate(
        pdf_path,
        pagesize=letter,
        rightMargin=0.5 * inch,
        leftMargin=0.5 * inch,
        topMargin=0.5 * inch,
        bottomMargin=0.5 * inch
    )

    styles = getSampleStyleSheet()
    
    # Custom Palette
    primary_color = colors.HexColor("#10b981")   # Emerald
    dark_bg_color = colors.HexColor("#0b0f19")   # Dark Header
    accent_blue   = colors.HexColor("#3b82f6")   # Info Blue
    text_dark     = colors.HexColor("#1e293b")   # Slate Dark Text
    light_bg      = colors.HexColor("#f8fafc")   # Off-white card bg
    border_color  = colors.HexColor("#e2e8f0")

    # Custom Styles
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=22,
        leading=26,
        textColor=primary_color,
        spaceAfter=4
    )
    
    subtitle_style = ParagraphStyle(
        'DocSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=11,
        leading=14,
        textColor=colors.HexColor("#64748b"),
        spaceAfter=12
    )

    h2_style = ParagraphStyle(
        'SectionH2',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=14,
        leading=18,
        textColor=colors.HexColor("#0f172a"),
        spaceBefore=10,
        spaceAfter=6
    )

    body_style = ParagraphStyle(
        'BodyDark',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9.5,
        leading=13.5,
        textColor=text_dark,
        spaceAfter=6
    )

    table_header_style = ParagraphStyle(
        'TableHeader',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=9,
        leading=11,
        textColor=colors.white,
        alignment=0
    )

    table_cell_style = ParagraphStyle(
        'TableCell',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.5,
        leading=11.5,
        textColor=text_dark
    )

    table_cell_bold = ParagraphStyle(
        'TableCellBold',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8.5,
        leading=11.5,
        textColor=primary_color
    )

    story = []

    # Title & Header Banner
    story.append(Paragraph("NutriLens AI — Technical Stack & Architecture", title_style))
    story.append(Paragraph("Generative AI Food Barcode Health & RAG Risk Assessment System", subtitle_style))
    story.append(HRFlowable(width="100%", thickness=1.5, color=primary_color, spaceBefore=0, spaceAfter=10))

    # Executive Overview
    story.append(Paragraph("1. Executive System Overview", h2_style))
    overview_text = (
        "<b>NutriLens AI</b> is an intelligent, clinical-grade Generative AI web application designed to evaluate "
        "packaged food health risks using <b>product barcode recognition</b>. It retrieves real-time product ingredients "
        "and nutritional metrics from <b>OpenFoodFacts</b>, performs <b>RAG (Retrieval-Augmented Generation)</b> vector search over "
        "trusted food regulations (<b>FSSAI, WHO, ICMR 2024, USDA, PubMed</b>) stored inside <b>ChromaDB</b> using "
        "<b>BAAI/bge-small-en-v1.5 embeddings</b>, and generates personalized clinical evaluations and Health Scores (0–100) via "
        "<b>Google Gemini LLM</b> in multiple languages (English, Hindi, Kannada, Tamil)."
    )
    story.append(Paragraph(overview_text, body_style))
    story.append(Spacer(1, 8))

    # Complete Tech Stack Breakdown Table
    story.append(Paragraph("2. Technical Stack Breakdown", h2_style))

    stack_data = [
        [
            Paragraph("Component / Layer", table_header_style),
            Paragraph("Technology Stack", table_header_style),
            Paragraph("Role & Functionality in NutriLens AI", table_header_style)
        ],
        [
            Paragraph("Backend Web Framework", table_cell_bold),
            Paragraph("<b>FastAPI</b><br/>Python 3.10 (ASGI)", table_cell_style),
            Paragraph("Executes async REST APIs (/scan, /users, /history), static UI file mounting, CORS middleware, and request validation.", table_cell_style)
        ],
        [
            Paragraph("Barcode Decoder", table_cell_bold),
            Paragraph("<b>pyzbar & OpenCV</b> (Backend)<br/><b>ZXing JS</b> (Frontend)", table_cell_style),
            Paragraph("Decodes EAN-13, EAN-8, UPC-A barcodes from live web cameras or uploaded product photo files with image contrast preprocessing.", table_cell_style)
        ],
        [
            Paragraph("Food Database Integration", table_cell_bold),
            Paragraph("<b>OpenFoodFacts REST API</b>", table_cell_style),
            Paragraph("Queries OpenFoodFacts database by barcode to retrieve Product Name, Brand, Category, Ingredients, 100g Nutriments, INS Additives, Allergens, Nutri-Score, and NOVA Groups.", table_cell_style)
        ],
        [
            Paragraph("Dense Embedding Model", table_cell_bold),
            Paragraph("<b>BAAI/bge-small-en-v1.5</b><br/>(HuggingFace Transformers)", table_cell_style),
            Paragraph("Generates 384-dimensional dense vector embeddings for regulatory documents and query terms for fast semantic search.", table_cell_style)
        ],
        [
            Paragraph("Vector Database & RAG", table_cell_bold),
            Paragraph("<b>ChromaDB</b><br/>(Persistent Collection)", table_cell_style),
            Paragraph("Indexes 28 vector chunks from FSSAI, WHO, ICMR, USDA, and PubMed research studies. Performs cosine similarity retrieval.", table_cell_style)
        ],
        [
            Paragraph("Generative AI LLM", table_cell_bold),
            Paragraph("<b>Google Gemini</b><br/>(gemini-1.5-flash)", table_cell_style),
            Paragraph("Synthesizes product data, user health profiles (Age, Diabetes, BP, CKD, Pregnancy, Allergies), and RAG context into multilingual JSON analysis.", table_cell_style)
        ],
        [
            Paragraph("Relational DB & Auth", table_cell_bold),
            Paragraph("<b>SQLAlchemy 2.0</b><br/>PostgreSQL / SQLite", table_cell_style),
            Paragraph("Manages persistent user accounts, bcrypt hashed passwords, personal health conditions, and paginated scan history.", table_cell_style)
        ],
        [
            Paragraph("Frontend Web App", table_cell_bold),
            Paragraph("<b>HTML5, CSS3, JS</b><br/>(Glassmorphism Design)", table_cell_style),
            Paragraph("Features SVG radial health score gauge (0-100), dark mode UI, touch tabs, quick test barcode chips, and mobile responsiveness.", table_cell_style)
        ],
        [
            Paragraph("Deployment & DevOps", table_cell_bold),
            Paragraph("<b>Docker & Render</b><br/>(docker-compose, render.yaml)", table_cell_style),
            Paragraph("Containerized multi-service deployment setup bundling FastAPI backend, ChromaDB vector store, and static frontend.", table_cell_style)
        ],
    ]

    col_widths = [1.3 * inch, 1.8 * inch, 4.4 * inch]
    stack_table = Table(stack_data, colWidths=col_widths)
    stack_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), primary_color),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('GRID', (0, 0), (-1, -1), 0.5, border_color),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, light_bg]),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('RIGHTPADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(stack_table)
    story.append(Spacer(1, 10))

    # Architecture Execution Flow
    story.append(Paragraph("3. End-to-End System Execution Flow", h2_style))
    
    flow_steps = [
        "<b>Step 1 (Barcode Input)</b>: User scans barcode via camera stream or uploads a photo containing a food barcode.",
        "<b>Step 2 (Decoding)</b>: Frontend/Backend decodes the barcode string (e.g. <code>8901058852309</code> for Maggi Noodles).",
        "<b>Step 3 (OpenFoodFacts Query)</b>: Async API request fetches raw product facts, ingredients, nutriments per 100g, and INS codes.",
        "<b>Step 4 (RAG Vector Search)</b>: Ingredients & category query terms are embedded via BAAI BGE-small and searched in ChromaDB for matching FSSAI/WHO/ICMR guidelines.",
        "<b>Step 5 (Gemini Prompt Assembly)</b>: Product metadata + 4 retrieved vector context passages + User Health Profile are formatted into a structured prompt.",
        "<b>Step 6 (Multilingual LLM Generation)</b>: Gemini outputs a validated JSON object containing Health Score (0-100), risk assessments, and daily advice in the requested language (EN, HI, KN, TA).",
        "<b>Step 7 (UI Dashboard Rendering)</b>: Web UI renders the animated circular gauge score dial, risk badges, and interactive analysis tabs."
    ]

    for step in flow_steps:
        story.append(Paragraph(f"• {step}", body_style))

    story.append(Spacer(1, 10))
    story.append(HRFlowable(width="100%", thickness=0.8, color=border_color, spaceBefore=5, spaceAfter=8))
    
    # Document Footer
    footer_text = "NutriLens AI Specification Document — Generated automatically on local workspace."
    story.append(Paragraph(footer_text, ParagraphStyle('Footer', parent=styles['Normal'], fontName='Helvetica-Oblique', fontSize=8, textColor=colors.HexColor("#94a3b8"), alignment=1)))

    doc.build(story)
    print(f"Successfully generated PDF at: {pdf_path}")
    return pdf_path

if __name__ == "__main__":
    generate_pdf()
