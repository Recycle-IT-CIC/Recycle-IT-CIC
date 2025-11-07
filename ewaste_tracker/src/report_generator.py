"""
Final Compliance Report Generator
Creates comprehensive PDF reports for client records
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
    from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False

try:
    from .config import (
        ORGANISATION, ORGANISATION_ADDRESS, ORGANISATION_EMAIL,
        CLIENT_NAME, CLIENT_VIA, JOB_TYPE, COMPLIANCE_STANDARDS,
        ITEM_TYPES, REPORTS_DIR, get_current_date, get_file_timestamp
    )
except ImportError:
    from config import (
        ORGANISATION, ORGANISATION_ADDRESS, ORGANISATION_EMAIL,
        CLIENT_NAME, CLIENT_VIA, JOB_TYPE, COMPLIANCE_STANDARDS,
        ITEM_TYPES, REPORTS_DIR, get_current_date, get_file_timestamp
    )


class ReportGenerator:
    """Generates final compliance reports"""

    def __init__(self):
        if not REPORTLAB_AVAILABLE:
            raise ImportError("reportlab library is required for PDF generation")

        self.reports_dir = REPORTS_DIR
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()

    def _setup_custom_styles(self):
        """Setup custom paragraph styles"""

        self.styles.add(ParagraphStyle(
            name='ReportTitle',
            parent=self.styles['Heading1'],
            fontSize=22,
            textColor=colors.HexColor('#1a5490'),
            spaceAfter=20,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        ))

        self.styles.add(ParagraphStyle(
            name='ReportHeading',
            parent=self.styles['Heading2'],
            fontSize=14,
            textColor=colors.HexColor('#1a5490'),
            spaceAfter=10,
            spaceBefore=15,
            fontName='Helvetica-Bold'
        ))

        self.styles.add(ParagraphStyle(
            name='SubHeading',
            parent=self.styles['Heading3'],
            fontSize=12,
            textColor=colors.HexColor('#2c5aa0'),
            spaceAfter=8,
            spaceBefore=10,
            fontName='Helvetica-Bold'
        ))

        self.styles.add(ParagraphStyle(
            name='BodyJustify',
            parent=self.styles['Normal'],
            fontSize=10,
            alignment=TA_JUSTIFY,
            spaceAfter=8
        ))

    def _create_cover_page(self, story: List):
        """Create report cover page"""

        story.append(Spacer(1, 3 * cm))

        # Main title
        title = Paragraph(
            "E-WASTE DESTRUCTION & COMPLIANCE REPORT",
            self.styles['ReportTitle']
        )
        story.append(title)
        story.append(Spacer(1, 1 * cm))

        # Client and org info
        info_style = ParagraphStyle(
            'CoverInfo',
            parent=self.styles['Normal'],
            fontSize=12,
            alignment=TA_CENTER,
            spaceAfter=10
        )

        story.append(Paragraph(f"<b>Client:</b> {CLIENT_NAME}", info_style))
        story.append(Paragraph(f"<b>Via:</b> {CLIENT_VIA}", info_style))
        story.append(Spacer(1, 0.5 * cm))
        story.append(Paragraph(f"<b>Service Provider:</b> {ORGANISATION}", info_style))
        story.append(Paragraph(f"{ORGANISATION_ADDRESS}", info_style))
        story.append(Spacer(1, 1 * cm))

        # Date and job type
        story.append(Paragraph(f"<b>Report Date:</b> {get_current_date()}", info_style))
        story.append(Paragraph(f"<b>Service Type:</b> {JOB_TYPE}", info_style))
        story.append(Spacer(1, 2 * cm))

        # Compliance badges
        compliance_text = "<b>Compliant with:</b><br/>" + "<br/>".join(COMPLIANCE_STANDARDS)
        story.append(Paragraph(compliance_text, info_style))

        story.append(PageBreak())

    def _create_executive_summary(self, story: List, stats: Dict):
        """Create executive summary section"""

        story.append(Paragraph("Executive Summary", self.styles['ReportHeading']))

        summary_text = (
            f"{ORGANISATION} has successfully completed the secure destruction and recycling service "
            f"for {stats['total_items']} items of electronic waste on behalf of {CLIENT_NAME}. "
            "All items have been processed in accordance with ISO 9001:2015, WEEE Regulations 2013, "
            "and UK GDPR 2018 requirements. This report provides comprehensive documentation of all "
            "processing activities, destruction methods, and compliance measures taken."
        )

        story.append(Paragraph(summary_text, self.styles['BodyJustify']))
        story.append(Spacer(1, 0.5 * cm))

        # Key statistics table
        key_stats_data = [
            ['Total Items Processed:', str(stats['total_items'])],
            ['Data Wipe Operations:', str(stats.get('data_wipe_completed', 0))],
            ['Label Removal Operations:', str(stats.get('label_removal_completed', 0))],
            ['Destruction Certificates Issued:', str(stats['certificates_issued'])],
            ['Photo Evidence Files:', str(stats.get('photo_count', 0))],
        ]

        stats_table = Table(key_stats_data, colWidths=[10 * cm, 6 * cm])
        stats_table.setStyle(TableStyle([
            ('FONT', (0, 0), (0, -1), 'Helvetica-Bold', 10),
            ('FONT', (1, 0), (1, -1), 'Helvetica', 10),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#e8f4f8')),
        ]))

        story.append(stats_table)
        story.append(Spacer(1, 0.5 * cm))

    def _create_item_breakdown(self, story: List, stats: Dict):
        """Create detailed item breakdown section"""

        story.append(Paragraph("Item Breakdown", self.styles['ReportHeading']))

        breakdown_text = (
            "The following table provides a detailed breakdown of all items processed, "
            "categorised by type and showing expected versus actual quantities."
        )
        story.append(Paragraph(breakdown_text, self.styles['BodyJustify']))
        story.append(Spacer(1, 0.3 * cm))

        # Build item breakdown table
        table_data = [['Item Type', 'Expected Qty', 'Processed Qty', 'Status']]

        for item_code, config in ITEM_TYPES.items():
            expected = config['expected_quantity']
            processed = stats['by_type'].get(config['name'], 0)

            if expected > 0:
                if processed == expected:
                    status = '✓ Complete'
                elif processed < expected:
                    status = f'⚠ {processed}/{expected}'
                else:
                    status = f'✓ {processed} (over)'
            else:
                status = '✓ Complete' if processed > 0 else 'N/A'

            table_data.append([
                config['name'],
                str(expected) if expected > 0 else 'Variable',
                str(processed),
                status
            ])

        breakdown_table = Table(table_data, colWidths=[7 * cm, 3 * cm, 3 * cm, 3 * cm])
        breakdown_table.setStyle(TableStyle([
            ('FONT', (0, 0), (-1, 0), 'Helvetica-Bold', 10),
            ('FONT', (0, 1), (-1, -1), 'Helvetica', 9),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a5490')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ]))

        story.append(breakdown_table)
        story.append(Spacer(1, 0.5 * cm))

    def _create_compliance_section(self, story: List, stats: Dict):
        """Create compliance and methodology section"""

        story.append(Paragraph("Compliance & Methodology", self.styles['ReportHeading']))

        # ISO 9001
        story.append(Paragraph("ISO 9001:2015 Quality Management", self.styles['SubHeading']))
        iso_text = (
            "All processes have been conducted in accordance with our ISO 9001:2015 certified "
            "quality management system. This includes documented procedures, traceability of all "
            "items, and comprehensive record-keeping throughout the destruction process."
        )
        story.append(Paragraph(iso_text, self.styles['BodyJustify']))

        # WEEE
        story.append(Paragraph("WEEE Regulations 2013", self.styles['SubHeading']))
        weee_text = (
            "All electronic waste has been processed in compliance with the Waste Electrical and "
            "Electronic Equipment Regulations 2013. Materials have been segregated appropriately "
            "for recycling, and hazardous components have been handled by certified facilities."
        )
        story.append(Paragraph(weee_text, self.styles['BodyJustify']))

        # GDPR
        story.append(Paragraph("UK GDPR 2018", self.styles['SubHeading']))
        gdpr_text = (
            f"Data-bearing devices (n={stats.get('data_wipe_completed', 0)}) have undergone "
            "secure data sanitisation using industry-standard methods to ensure complete data "
            "destruction. All processes comply with UK GDPR requirements for secure data disposal."
        )
        story.append(Paragraph(gdpr_text, self.styles['BodyJustify']))

        story.append(Spacer(1, 0.5 * cm))

    def _create_destruction_methods(self, story: List, destruction_methods: Dict):
        """Create section detailing destruction methods used"""

        story.append(Paragraph("Destruction Methods", self.styles['ReportHeading']))

        methods_text = (
            "The following destruction methods were employed based on item type and client requirements:"
        )
        story.append(Paragraph(methods_text, self.styles['BodyJustify']))
        story.append(Spacer(1, 0.3 * cm))

        if destruction_methods:
            method_data = [['Method', 'Items Processed']]
            for method, count in sorted(destruction_methods.items()):
                if method:  # Skip empty methods
                    method_data.append([method, str(count)])

            if len(method_data) > 1:  # More than just header
                method_table = Table(method_data, colWidths=[10 * cm, 6 * cm])
                method_table.setStyle(TableStyle([
                    ('FONT', (0, 0), (-1, 0), 'Helvetica-Bold', 10),
                    ('FONT', (0, 1), (-1, -1), 'Helvetica', 9),
                    ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#f5f5f5')),
                    ('ALIGN', (1, 0), (1, -1), 'CENTER'),
                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                    ('TOPPADDING', (0, 0), (-1, -1), 6),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                ]))
                story.append(method_table)
            else:
                story.append(Paragraph("<i>Destruction methods to be recorded during processing.</i>",
                                      self.styles['Normal']))
        else:
            story.append(Paragraph("<i>Destruction methods to be recorded during processing.</i>",
                                  self.styles['Normal']))

        story.append(Spacer(1, 0.5 * cm))

    def _create_evidence_section(self, story: List, photo_inventory: Dict, cert_list: List[str]):
        """Create section about evidence and documentation"""

        story.append(Paragraph("Evidence & Documentation", self.styles['ReportHeading']))

        # Photo evidence
        story.append(Paragraph("Photographic Evidence", self.styles['SubHeading']))
        if photo_inventory and photo_inventory.get('total_photos', 0) > 0:
            photo_text = (
                f"A total of {photo_inventory['total_photos']} photographs have been taken "
                "documenting the destruction process. Photos are organised by item type and "
                f"stored in: <i>{photo_inventory.get('job_folder', 'photo_evidence/')}</i>"
            )
            story.append(Paragraph(photo_text, self.styles['BodyJustify']))

            if photo_inventory.get('by_item_type'):
                story.append(Spacer(1, 0.3 * cm))
                photo_data = [['Item Type', 'Photo Count']]
                for item_type, count in sorted(photo_inventory['by_item_type'].items()):
                    photo_data.append([item_type, str(count)])

                photo_table = Table(photo_data, colWidths=[10 * cm, 6 * cm])
                photo_table.setStyle(TableStyle([
                    ('FONT', (0, 0), (-1, 0), 'Helvetica-Bold', 9),
                    ('FONT', (0, 1), (-1, -1), 'Helvetica', 8),
                    ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#f5f5f5')),
                    ('ALIGN', (1, 0), (1, -1), 'CENTER'),
                    ('TOPPADDING', (0, 0), (-1, -1), 4),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
                ]))
                story.append(photo_table)
        else:
            story.append(Paragraph(
                "<i>Photographic evidence to be compiled during processing.</i>",
                self.styles['Normal']
            ))

        story.append(Spacer(1, 0.3 * cm))

        # Certificates
        story.append(Paragraph("Destruction Certificates", self.styles['SubHeading']))
        if cert_list:
            cert_text = (
                f"{len(cert_list)} destruction certificates have been generated and are included "
                "with this report. Each certificate provides detailed information about the items "
                "destroyed, methods used, and technician certification."
            )
            story.append(Paragraph(cert_text, self.styles['BodyJustify']))
        else:
            story.append(Paragraph(
                "<i>Destruction certificates to be generated upon completion of processing.</i>",
                self.styles['Normal']
            ))

        story.append(Spacer(1, 0.5 * cm))

    def generate_final_report(self,
                            asset_records: List[Dict],
                            photo_inventory: Optional[Dict] = None,
                            cert_list: Optional[List[str]] = None,
                            report_name: str = "LBQ_Final_Report") -> Path:
        """Generate comprehensive final compliance report"""

        timestamp = get_file_timestamp()
        filename = f"{report_name}_{timestamp}.pdf"
        filepath = self.reports_dir / filename

        # Calculate statistics
        stats = self._calculate_stats(asset_records)

        # Gather destruction methods
        destruction_methods = {}
        for record in asset_records:
            method = record.get('Destruction Method', '')
            if method:
                destruction_methods[method] = destruction_methods.get(method, 0) + 1

        # Add photo count to stats
        if photo_inventory:
            stats['photo_count'] = photo_inventory.get('total_photos', 0)

        # Create PDF
        doc = SimpleDocTemplate(str(filepath), pagesize=A4,
                               topMargin=2 * cm, bottomMargin=2 * cm,
                               leftMargin=2.5 * cm, rightMargin=2.5 * cm)

        story = []

        # Build report sections
        self._create_cover_page(story)
        self._create_executive_summary(story, stats)
        self._create_item_breakdown(story, stats)
        self._create_compliance_section(story, stats)
        self._create_destruction_methods(story, destruction_methods)
        self._create_evidence_section(story, photo_inventory or {}, cert_list or [])

        # Footer
        story.append(Spacer(1, 1 * cm))
        footer_text = (
            f"<i>This report was generated by {ORGANISATION} on {get_current_date()}. "
            f"For queries, please contact {ORGANISATION_EMAIL}</i>"
        )
        story.append(Paragraph(footer_text, self.styles['Normal']))

        # Build PDF
        doc.build(story)

        print(f"\n✓ Final compliance report generated: {filename}")
        print(f"  Location: {filepath}")
        print(f"  Total items: {stats['total_items']}")
        return filepath

    def _calculate_stats(self, records: List[Dict]) -> Dict:
        """Calculate comprehensive statistics"""

        stats = {
            "total_items": len(records),
            "by_type": {},
            "by_condition": {},
            "label_removal_completed": 0,
            "data_wipe_completed": 0,
            "destruction_completed": 0,
            "certificates_issued": 0
        }

        for record in records:
            # Count by type
            item_type = record['Item Type']
            stats["by_type"][item_type] = stats["by_type"].get(item_type, 0) + 1

            # Count by condition
            condition = record['Condition']
            stats["by_condition"][condition] = stats["by_condition"].get(condition, 0) + 1

            # Count completed tasks
            if record["Label Removal Completed"] == "Yes":
                stats["label_removal_completed"] += 1

            if record["Data Wipe Date"]:
                stats["data_wipe_completed"] += 1

            if record["Destruction Date"]:
                stats["destruction_completed"] += 1

            if record["Certificate Issued"] == "Yes":
                stats["certificates_issued"] += 1

        return stats

    def list_reports(self) -> List[str]:
        """List all generated reports"""
        reports = sorted(self.reports_dir.glob("*.pdf"), reverse=True)
        return [r.name for r in reports]
