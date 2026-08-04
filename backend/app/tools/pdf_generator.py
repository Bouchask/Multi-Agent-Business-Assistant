import os
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.colors import HexColor

class PDFGeneratorTool:
    @staticmethod
    def create_report(filename: str, title: str, content: str) -> str:
        os.makedirs("./data/reports", exist_ok=True)
        file_path = f"./data/reports/{filename}"
        
        doc = SimpleDocTemplate(file_path, pagesize=letter, rightMargin=54, leftMargin=54, topMargin=54, bottomMargin=54)
        styles = getSampleStyleSheet()
        
        title_style = ParagraphStyle(
            'ReportTitle',
            parent=styles['Heading1'],
            fontName='Helvetica-Bold',
            fontSize=22,
            textColor=HexColor('#1A365D'),
            spaceAfter=12
        )
        body_style = ParagraphStyle(
            'ReportBody',
            parent=styles['Normal'],
            fontName='Helvetica',
            fontSize=11,
            textColor=HexColor('#2D3748'),
            leading=16
        )

        story = [
            Paragraph(title, title_style),
            Spacer(1, 12)
        ]
        for line in content.split("\n"):
            if line.strip():
                story.append(Paragraph(line.strip(), body_style))
                story.append(Spacer(1, 6))

        doc.build(story)
        return os.path.abspath(file_path)
