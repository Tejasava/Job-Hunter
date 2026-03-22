"""
PDF Resume Builder
Generates professional PDF resumes from data
"""

import logging
import os
from typing import Dict, Any
from datetime import datetime

logger = logging.getLogger(__name__)


class PDFResumeBuilder:
    """Generates professional PDF resumes"""

    def __init__(self):
        self.try_reportlab()
        self.try_pdfkit()

    def try_reportlab(self):
        """Try to import reportlab"""
        try:
            from reportlab.lib.pagesizes import letter, A4
            from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            from reportlab.lib.units import inch

            self.reportlab_available = True
            self.letter = letter
            self.A4 = A4
            self.SimpleDocTemplate = SimpleDocTemplate
            self.Paragraph = Paragraph
            self.Spacer = Spacer
            self.Table = Table
            self.getSampleStyleSheet = getSampleStyleSheet
            self.ParagraphStyle = ParagraphStyle
            self.inch = inch
        except ImportError:
            self.reportlab_available = False
            logger.warning("ReportLab not installed")

    def try_pdfkit(self):
        """Try to import pdfkit"""
        try:
            import pdfkit

            self.pdfkit_available = True
            self.pdfkit = pdfkit
        except ImportError:
            self.pdfkit_available = False
            logger.warning("pdfkit not installed")

    def generate_pdf(
        self, resume_data: Dict[str, Any], output_path: str
    ) -> bool:
        """
        Generate PDF resume
        
        Args:
            resume_data: Resume content data
            output_path: Path to save PDF
        
        Returns:
            True if successful
        """
        try:
            if self.reportlab_available:
                return self._generate_with_reportlab(resume_data, output_path)
            else:
                return self._generate_with_html_to_pdf(resume_data, output_path)
        except Exception as e:
            logger.error(f"Error generating PDF: {e}")
            return False

    def _generate_with_reportlab(
        self, resume_data: Dict[str, Any], output_path: str
    ) -> bool:
        """Generate PDF using ReportLab"""
        try:
            # Create output directory if needed
            os.makedirs(os.path.dirname(output_path), exist_ok=True)

            doc = self.SimpleDocTemplate(output_path, pagesize=self.A4)
            elements = []

            styles = self.getSampleStyleSheet()
            title_style = self.ParagraphStyle(
                "CustomTitle",
                parent=styles["Heading1"],
                fontSize=24,
                textColor="000000",
                spaceAfter=10,
                alignment=1,  # Center
            )

            heading_style = self.ParagraphStyle(
                "CustomHeading",
                parent=styles["Heading2"],
                fontSize=14,
                textColor="000000",
                spaceAfter=6,
                spaceBefore=6,
            )

            # Title
            name = f"{resume_data.get('first_name', '')} {resume_data.get('last_name', '')}"
            elements.append(self.Paragraph(name, title_style))

            # Contact info
            contact = f"{resume_data.get('email', '')} | {resume_data.get('phone', '')}"
            elements.append(self.Paragraph(contact, styles["Normal"]))
            elements.append(self.Spacer(1, 0.2 * self.inch))

            # Summary
            if resume_data.get("summary"):
                elements.append(self.Paragraph("PROFESSIONAL SUMMARY", heading_style))
                elements.append(
                    self.Paragraph(resume_data["summary"], styles["Normal"])
                )
                elements.append(self.Spacer(1, 0.15 * self.inch))

            # Experience
            if resume_data.get("experience"):
                elements.append(self.Paragraph("EXPERIENCE", heading_style))
                for exp in resume_data["experience"]:
                    exp_text = f"""
                    <b>{exp.get('title', '')}</b> at {exp.get('company', '')}<br/>
                    {exp.get('duration', '')}<br/>
                    {exp.get('description', '')}
                    """
                    elements.append(self.Paragraph(exp_text, styles["Normal"]))
                    elements.append(self.Spacer(1, 0.1 * self.inch))

            # Education
            if resume_data.get("education"):
                elements.append(self.Paragraph("EDUCATION", heading_style))
                for edu in resume_data["education"]:
                    edu_text = f"""
                    <b>{edu.get('degree', '')}</b> from {edu.get('school', '')}<br/>
                    {edu.get('year', '')}
                    """
                    elements.append(self.Paragraph(edu_text, styles["Normal"]))
                    elements.append(self.Spacer(1, 0.1 * self.inch))

            # Skills
            if resume_data.get("skills"):
                elements.append(self.Paragraph("SKILLS", heading_style))
                skills_text = ", ".join(resume_data["skills"])
                elements.append(self.Paragraph(skills_text, styles["Normal"]))

            # Build PDF
            doc.build(elements)
            logger.info(f"PDF resume generated: {output_path}")
            return True

        except Exception as e:
            logger.error(f"Error generating with ReportLab: {e}")
            return False

    def _generate_with_html_to_pdf(
        self, resume_data: Dict[str, Any], output_path: str
    ) -> bool:
        """Generate PDF using HTML to PDF conversion"""
        try:
            html_content = self._build_html_resume(resume_data)

            if self.pdfkit_available:
                # Save HTML first, then convert
                html_path = output_path.replace(".pdf", ".html")
                with open(html_path, "w") as f:
                    f.write(html_content)

                self.pdfkit.from_file(html_path, output_path)
                os.remove(html_path)
                logger.info(f"PDF resume generated: {output_path}")
                return True

        except Exception as e:
            logger.error(f"Error generating with pdfkit: {e}")

        return False

    def _build_html_resume(self, resume_data: Dict[str, Any]) -> str:
        """Build HTML resume template"""
        name = f"{resume_data.get('first_name', '')} {resume_data.get('last_name', '')}"

        html = f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                h1 {{ text-align: center; font-size: 24px; }}
                h2 {{ font-size: 14px; border-bottom: 2px solid #000; margin-top: 15px; }}
                .contact {{ text-align: center; margin-bottom: 20px; }}
                .section {{ margin-bottom: 15px; }}
                .job {{ margin-left: 20px; margin-bottom: 10px; }}
            </style>
        </head>
        <body>
            <h1>{name}</h1>
            <div class="contact">
                {resume_data.get('email', '')} | {resume_data.get('phone', '')}
            </div>

            <div class="section">
                <h2>PROFESSIONAL SUMMARY</h2>
                <p>{resume_data.get('summary', '')}</p>
            </div>

            <div class="section">
                <h2>EXPERIENCE</h2>
                {"".join([f'<div class="job"><b>{exp.get("title", "")}</b> at {exp.get("company", "")}<br/>{exp.get("duration", "")}<br/>{exp.get("description", "")}</div>' for exp in resume_data.get('experience', [])])}
            </div>

            <div class="section">
                <h2>EDUCATION</h2>
                {"".join([f'<div class="job"><b>{edu.get("degree", "")}</b> from {edu.get("school", "")}<br/>{edu.get("year", "")}</div>' for edu in resume_data.get('education', [])])}
            </div>

            <div class="section">
                <h2>SKILLS</h2>
                <p>{", ".join(resume_data.get('skills', []))}</p>
            </div>
        </body>
        </html>
        """

        return html
