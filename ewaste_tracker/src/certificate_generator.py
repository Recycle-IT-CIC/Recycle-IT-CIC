"""
Certificate Generator
Creates destruction certificates and compliance documentation in PDF format
"""

from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime

try:
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import cm
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
    from reportlab.platypus import Image as RLImage
    from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False
    print("Warning: reportlab not installed. PDF generation will not work.")
    print("Install with: pip install reportlab")

try:
    from .config import (
        ORGANISATION, ORGANISATION_ADDRESS, ORGANISATION_EMAIL,
        CLIENT_NAME, CLIENT_VIA, COMPLIANCE_STANDARDS,
        CERTIFICATES_DIR, get_current_date, get_file_timestamp
    )
except ImportError:
    from config import (
        ORGANISATION, ORGANISATION_ADDRESS, ORGANISATION_EMAIL,
        CLIENT_NAME, CLIENT_VIA, COMPLIANCE_STANDARDS,
        CERTIFICATES_DIR, get_current_date, get_file_timestamp
    )


class CertificateGenerator:
    """Generates PDF certificates for destruction and compliance"""

    def __init__(self):
        if not REPORTLAB_AVAILABLE:
            raise ImportError("reportlab library is required for PDF generation")

        self.certificates_dir = CERTIFICATES_DIR
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()

    def _setup_custom_styles(self):
        """Setup custom paragraph styles"""

        # Title style
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#1a5490'),
            spaceAfter=30,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        ))

        # Heading style
        self.styles.add(ParagraphStyle(
            name='CustomHeading',
            parent=self.styles['Heading2'],
            fontSize=14,
            textColor=colors.HexColor('#1a5490'),
            spaceAfter=12,
            spaceBefore=12,
            fontName='Helvetica-Bold'
        ))

        # Certificate number style
        self.styles.add(ParagraphStyle(
            name='CertNumber',
            parent=self.styles['Normal'],
            fontSize=10,
            alignment=TA_RIGHT,
            textColor=colors.grey
        ))

    def _create_header(self, story: List, cert_number: str):
        """Create certificate header with branding"""

        # Organisation name
        org_title = Paragraph(f"<b>{ORGANISATION}</b>", self.styles['CustomTitle'])
        story.append(org_title)

        # Certificate type
        cert_type = Paragraph(
            "CERTIFICATE OF SECURE DESTRUCTION",
            ParagraphStyle(
                'CertType',
                parent=self.styles['Normal'],
                fontSize=16,
                alignment=TA_CENTER,
                textColor=colors.HexColor('#d32f2f'),
                spaceAfter=20
            )
        )
        story.append(cert_type)

        # Certificate number
        cert_num_text = Paragraph(
            f"Certificate No: <b>{cert_number}</b>",
            self.styles['CertNumber']
        )
        story.append(cert_num_text)
        story.append(Spacer(1, 0.5 * cm))

        # Header info table
        header_data = [
            ['Date of Issue:', get_current_date()],
            ['Issued To:', CLIENT_NAME],
            ['Via:', CLIENT_VIA],
            ['Service Provider:', f"{ORGANISATION}, {ORGANISATION_ADDRESS}"],
        ]

        header_table = Table(header_data, colWidths=[4 * cm, 12 * cm])
        header_table.setStyle(TableStyle([
            ('FONT', (0, 0), (0, -1), 'Helvetica-Bold', 10),
            ('FONT', (1, 0), (1, -1), 'Helvetica', 10),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ]))

        story.append(header_table)
        story.append(Spacer(1, 0.8 * cm))

    def _create_compliance_section(self, story: List):
        """Add compliance standards section"""

        story.append(Paragraph("Compliance Standards", self.styles['CustomHeading']))

        compliance_text = "This destruction service has been performed in accordance with:"
        story.append(Paragraph(compliance_text, self.styles['Normal']))
        story.append(Spacer(1, 0.3 * cm))

        for standard in COMPLIANCE_STANDARDS:
            bullet = Paragraph(f"• {standard}", self.styles['Normal'])
            story.append(bullet)

        story.append(Spacer(1, 0.5 * cm))

    def _create_signature_section(self, story: List):
        """Add signature section"""

        story.append(Spacer(1, 1 * cm))
        story.append(Paragraph("Certification", self.styles['CustomHeading']))

        cert_text = (
            "I certify that the items listed in this certificate have been securely destroyed "
            "in accordance with the specified methods and that all data storage devices have been "
            "rendered permanently unrecoverable."
        )
        story.append(Paragraph(cert_text, self.styles['Normal']))
        story.append(Spacer(1, 1 * cm))

        # Signature fields
        sig_data = [
            ['Technician Signature:', '_' * 40, 'Date:', '_' * 20],
            ['', '', '', ''],
            ['Technician Name:', '_' * 40, '', ''],
        ]

        sig_table = Table(sig_data, colWidths=[4 * cm, 6 * cm, 2 * cm, 4 * cm])
        sig_table.setStyle(TableStyle([
            ('FONT', (0, 0), (-1, -1), 'Helvetica', 10),
            ('VALIGN', (0, 0), (-1, -1), 'BOTTOM'),
        ]))

        story.append(sig_table)
        story.append(Spacer(1, 0.5 * cm))

    def _create_footer(self, story: List):
        """Add certificate footer"""

        footer_text = f"<i>{ORGANISATION} | {ORGANISATION_EMAIL}</i>"
        footer = Paragraph(
            footer_text,
            ParagraphStyle(
                'Footer',
                parent=self.styles['Normal'],
                fontSize=8,
                alignment=TA_CENTER,
                textColor=colors.grey
            )
        )
        story.append(Spacer(1, 0.5 * cm))
        story.append(footer)

    def generate_individual_certificate(self,
                                       asset_record: Dict,
                                       cert_number: Optional[str] = None) -> Path:
        """Generate certificate for a single asset"""

        if cert_number is None:
            cert_number = f"CERT-{asset_record['Asset ID']}"

        filename = f"{cert_number}.pdf"
        filepath = self.certificates_dir / filename

        # Create PDF
        doc = SimpleDocTemplate(str(filepath), pagesize=A4,
                               topMargin=2 * cm, bottomMargin=2 * cm,
                               leftMargin=2 * cm, rightMargin=2 * cm)

        story = []

        # Header
        self._create_header(story, cert_number)

        # Asset details
        story.append(Paragraph("Asset Details", self.styles['CustomHeading']))

        asset_data = [
            ['Asset ID:', asset_record['Asset ID']],
            ['Item Type:', asset_record['Item Type']],
            ['Serial Number:', asset_record['Serial Number'] or 'N/A'],
            ['Condition:', asset_record['Condition']],
            ['Intake Date:', asset_record['Intake Date']],
        ]

        asset_table = Table(asset_data, colWidths=[4 * cm, 12 * cm])
        asset_table.setStyle(TableStyle([
            ('FONT', (0, 0), (0, -1), 'Helvetica-Bold', 10),
            ('FONT', (1, 0), (1, -1), 'Helvetica', 10),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f5f5f5')),
        ]))

        story.append(asset_table)
        story.append(Spacer(1, 0.5 * cm))

        # Destruction details
        if asset_record['Destruction Date']:
            story.append(Paragraph("Destruction Details", self.styles['CustomHeading']))

            destruction_data = [
                ['Destruction Date:', asset_record['Destruction Date']],
                ['Destruction Method:', asset_record['Destruction Method']],
                ['Technician:', asset_record['Destruction Technician']],
            ]

            # Add data wipe info if applicable
            if asset_record['Data Wipe Date']:
                destruction_data.extend([
                    ['Data Wipe Method:', asset_record['Data Wipe Method']],
                    ['Data Wipe Date:', asset_record['Data Wipe Date']],
                    ['Data Wipe Technician:', asset_record['Data Wipe Technician']],
                ])

            destruction_table = Table(destruction_data, colWidths=[4 * cm, 12 * cm])
            destruction_table.setStyle(TableStyle([
                ('FONT', (0, 0), (0, -1), 'Helvetica-Bold', 10),
                ('FONT', (1, 0), (1, -1), 'Helvetica', 10),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('TOPPADDING', (0, 0), (-1, -1), 8),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
                ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f5f5f5')),
            ]))

            story.append(destruction_table)
            story.append(Spacer(1, 0.5 * cm))

        # Photo evidence reference
        if asset_record['Photo Evidence Path']:
            photo_ref = Paragraph(
                f"<b>Photo Evidence:</b> {asset_record['Photo Evidence Path']}",
                self.styles['Normal']
            )
            story.append(photo_ref)
            story.append(Spacer(1, 0.5 * cm))

        # Compliance section
        self._create_compliance_section(story)

        # Signature section
        self._create_signature_section(story)

        # Footer
        self._create_footer(story)

        # Build PDF
        doc.build(story)

        print(f"✓ Certificate generated: {filename}")
        return filepath

    def generate_batch_certificate(self,
                                   asset_records: List[Dict],
                                   batch_name: str = "LBQ_Batch") -> Path:
        """Generate a single certificate for multiple assets"""

        cert_number = f"CERT-BATCH-{get_file_timestamp()}"
        filename = f"{batch_name}_{cert_number}.pdf"
        filepath = self.certificates_dir / filename

        # Create PDF
        doc = SimpleDocTemplate(str(filepath), pagesize=A4,
                               topMargin=2 * cm, bottomMargin=2 * cm,
                               leftMargin=2 * cm, rightMargin=2 * cm)

        story = []

        # Header
        self._create_header(story, cert_number)

        # Summary
        story.append(Paragraph("Batch Summary", self.styles['CustomHeading']))
        summary_text = f"This certificate covers the secure destruction of <b>{len(asset_records)}</b> items."
        story.append(Paragraph(summary_text, self.styles['Normal']))
        story.append(Spacer(1, 0.5 * cm))

        # Count by type
        type_counts = {}
        for record in asset_records:
            item_type = record['Item Type']
            type_counts[item_type] = type_counts.get(item_type, 0) + 1

        type_data = [['Item Type', 'Quantity']]
        for item_type, count in sorted(type_counts.items()):
            type_data.append([item_type, str(count)])

        type_table = Table(type_data, colWidths=[12 * cm, 4 * cm])
        type_table.setStyle(TableStyle([
            ('FONT', (0, 0), (-1, 0), 'Helvetica-Bold', 11),
            ('FONT', (0, 1), (-1, -1), 'Helvetica', 10),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a5490')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (1, 0), (1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ]))

        story.append(type_table)
        story.append(Spacer(1, 0.8 * cm))

        # Asset list (first page only - if too many, just show count)
        story.append(Paragraph("Assets Included", self.styles['CustomHeading']))

        if len(asset_records) <= 50:
            # Show all assets
            asset_data = [['Asset ID', 'Item Type', 'Destruction Date']]
            for record in asset_records:
                asset_data.append([
                    record['Asset ID'],
                    record['Item Type'],
                    record['Destruction Date'] or 'Pending'
                ])

            asset_table = Table(asset_data, colWidths=[5 * cm, 7 * cm, 4 * cm])
            asset_table.setStyle(TableStyle([
                ('FONT', (0, 0), (-1, 0), 'Helvetica-Bold', 9),
                ('FONT', (0, 1), (-1, -1), 'Helvetica', 8),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#f5f5f5')),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('TOPPADDING', (0, 0), (-1, -1), 4),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
            ]))

            story.append(asset_table)
        else:
            # Too many assets - refer to intake log
            note = Paragraph(
                f"<i>Due to large quantity ({len(asset_records)} items), "
                "please refer to the intake log CSV for complete asset listing.</i>",
                self.styles['Normal']
            )
            story.append(note)

        story.append(Spacer(1, 0.8 * cm))

        # Compliance section
        self._create_compliance_section(story)

        # Signature section
        self._create_signature_section(story)

        # Footer
        self._create_footer(story)

        # Build PDF
        doc.build(story)

        print(f"✓ Batch certificate generated: {filename}")
        print(f"  Contains {len(asset_records)} assets")
        return filepath

    def list_certificates(self) -> List[str]:
        """List all generated certificates"""
        certs = sorted(self.certificates_dir.glob("*.pdf"), reverse=True)
        return [c.name for c in certs]
