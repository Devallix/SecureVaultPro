"""Report generation service for SecureVault Pro."""

from __future__ import annotations

import csv
from datetime import datetime

from app.logging.logger import get_logger

logger = get_logger(__name__)


class ReportService:
    """Service for generating exportable reports."""

    def generate_passwords_csv(
        self, vault_id: str, output_path: str, password_service,
        mask_passwords: bool = True,
    ) -> str:
        """Export all passwords to a CSV file.

        Args:
            vault_id: The vault ID.
            output_path: Destination file path.
            password_service: PasswordService instance.
            mask_passwords: If True, replaces password values with '********'.

        Returns:
            Output path on success.
        """
        passwords = password_service.get_all_passwords(vault_id)
        fieldnames = [
            "title", "username", "password", "url", "notes",
            "is_favourite", "created_at", "updated_at",
        ]
        with open(output_path, "w", newline="", encoding="utf-8") as fh:
            writer = csv.DictWriter(fh, fieldnames=fieldnames)
            writer.writeheader()
            for pw in passwords:
                writer.writerow({
                    "title": pw.get("title", ""),
                    "username": pw.get("username", ""),
                    "password": "********" if mask_passwords else pw.get("password", ""),
                    "url": pw.get("url", ""),
                    "notes": pw.get("notes", ""),
                    "is_favourite": pw.get("is_favourite", False),
                    "created_at": pw.get("created_at", ""),
                    "updated_at": pw.get("updated_at", ""),
                })
        logger.info("Passwords CSV exported: {path}", path=output_path)
        return output_path

    def generate_passwords_excel(
        self, vault_id: str, output_path: str, password_service,
        mask_passwords: bool = True,
    ) -> str:
        """Export all passwords to an Excel workbook using openpyxl.

        Args:
            vault_id: The vault ID.
            output_path: Destination file path.
            password_service: PasswordService instance.
            mask_passwords: If True, replaces password values with '********'.

        Returns:
            Output path on success.
        """
        from openpyxl import Workbook
        from openpyxl.styles import Font, PatternFill

        passwords = password_service.get_all_passwords(vault_id)
        wb = Workbook()
        ws = wb.active
        ws.title = "Passwords"

        headers = [
            "Title", "Username", "Password", "URL", "Notes",
            "Favourite", "Created", "Updated",
        ]
        header_font = Font(bold=True, color="FFFFFF")
        header_fill = PatternFill(start_color="64B4FF", end_color="64B4FF", fill_type="solid")
        for col, header in enumerate(headers, 1):
            cell = ws.cell(row=1, column=col, value=header)
            cell.font = header_font
            cell.fill = header_fill

        for row_idx, pw in enumerate(passwords, 2):
            ws.cell(row=row_idx, column=1, value=pw.get("title", ""))
            ws.cell(row=row_idx, column=2, value=pw.get("username", ""))
            ws.cell(row=row_idx, column=3, value="********" if mask_passwords else pw.get("password", ""))
            ws.cell(row=row_idx, column=4, value=pw.get("url", ""))
            ws.cell(row=row_idx, column=5, value=pw.get("notes", ""))
            ws.cell(row=row_idx, column=6, value=pw.get("is_favourite", False))
            ws.cell(row=row_idx, column=7, value=str(pw.get("created_at", ""))[:19])
            ws.cell(row=row_idx, column=8, value=str(pw.get("updated_at", ""))[:19])

        for col in ws.columns:
            max_len = max(len(str(cell.value or "")) for cell in col)
            ws.column_dimensions[col[0].column_letter].width = min(max_len + 4, 50)

        wb.save(output_path)
        logger.info("Passwords Excel exported: {path}", path=output_path)
        return output_path

    def generate_passwords_pdf(
        self, vault_id: str, output_path: str, password_service
    ) -> str:
        """Export all passwords to a PDF document using reportlab.

        Args:
            vault_id: The vault ID.
            output_path: Destination file path.
            password_service: PasswordService instance.

        Returns:
            Output path on success.
        """
        from reportlab.lib import colors
        from reportlab.lib.pagesizes import A4, landscape
        from reportlab.lib.styles import getSampleStyleSheet
        from reportlab.lib.units import inch
        from reportlab.platypus import (
            Paragraph,
            SimpleDocTemplate,
            Spacer,
            Table,
            TableStyle,
        )

        passwords = password_service.get_all_passwords(vault_id)
        doc = SimpleDocTemplate(output_path, pagesize=landscape(A4))
        styles = getSampleStyleSheet()
        elements: list = []

        elements.append(Paragraph("Password Export Report", styles["Title"]))
        elements.append(
            Paragraph(
                f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                styles["Normal"],
            )
        )
        elements.append(Spacer(1, 0.3 * inch))

        headers = ["Title", "Username", "URL", "Favourite"]
        data = [headers]
        for pw in passwords:
            data.append([
                pw.get("title", ""),
                pw.get("username", ""),
                pw.get("url", ""),
                "Yes" if pw.get("is_favourite") else "No",
            ])

        table = Table(data, repeatRows=1)
        table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#64B4FF")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 9),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F0F0F0")]),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("LEFTPADDING", (0, 0), (-1, -1), 6),
            ("RIGHTPADDING", (0, 0), (-1, -1), 6),
            ("TOPPADDING", (0, 0), (-1, -1), 4),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ]))
        elements.append(table)
        elements.append(Spacer(1, 0.2 * inch))
        elements.append(Paragraph(f"Total entries: {len(passwords)}", styles["Normal"]))

        doc.build(elements)
        logger.info("Passwords PDF exported: {path}", path=output_path)
        return output_path

    def generate_audit_csv(
        self, vault_id: str, output_path: str, audit_service
    ) -> str:
        """Export the audit log to a CSV file.

        Args:
            vault_id: The vault ID.
            output_path: Destination file path.
            audit_service: AuditService instance.

        Returns:
            Output path on success.
        """
        entries = audit_service.get_all(vault_id, limit=10000)
        fieldnames = ["timestamp", "action", "entity_type", "entity_id"]
        with open(output_path, "w", newline="", encoding="utf-8") as fh:
            writer = csv.DictWriter(fh, fieldnames=fieldnames)
            writer.writeheader()
            for entry in entries:
                writer.writerow({
                    "timestamp": entry.get("created_at", ""),
                    "action": entry.get("action", ""),
                    "entity_type": entry.get("entity_type", ""),
                    "entity_id": entry.get("entity_id", ""),
                })
        logger.info("Audit CSV exported: {path}", path=output_path)
        return output_path

    def generate_security_report_pdf(
        self, vault_id: str, output_path: str, analysis_service
    ) -> str:
        from reportlab.lib import colors
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.styles import getSampleStyleSheet
        from reportlab.lib.units import inch
        from reportlab.platypus import (
            Paragraph,
            SimpleDocTemplate,
            Spacer,
            Table,
            TableStyle,
        )

        result = analysis_service.analyse_vault(vault_id)
        doc = SimpleDocTemplate(output_path, pagesize=A4)
        styles = getSampleStyleSheet()
        elements: list = []

        elements.append(Paragraph("Security Analysis Report", styles["Title"]))
        elements.append(
            Paragraph(
                f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                styles["Normal"],
            )
        )
        elements.append(Spacer(1, 0.3 * inch))

        health = result.get("health_score", 0)

        summary_data = [
            ["Metric", "Value"],
            ["Total Passwords", str(result.get("total_passwords", 0))],
            ["Health Score", f"{health}/100"],
            ["Weak Passwords", str(len(result.get("weak_passwords", [])))],
            ["Old Passwords (>90 days)", str(len(result.get("old_passwords", [])))],
            ["Duplicate Passwords", str(len(result.get("duplicate_passwords", [])))],
        ]
        summary_table = Table(summary_data, colWidths=[3 * inch, 2 * inch])
        summary_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#64B4FF")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F0F0F0")]),
            ("FONTSIZE", (0, 0), (-1, -1), 10),
            ("LEFTPADDING", (0, 0), (-1, -1), 8),
            ("TOPPADDING", (0, 0), (-1, -1), 4),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ]))
        elements.append(summary_table)
        elements.append(Spacer(1, 0.3 * inch))

        weak = result.get("weak_passwords", [])
        if weak:
            elements.append(Paragraph("Weak Passwords", styles["Heading2"]))
            weak_data = [["Title", "Score", "Entropy"]]
            for wp in weak:
                s = wp.get("strength", {})
                weak_data.append([
                    wp.get("title", ""),
                    f"{s.get('score', 0)}/{s.get('max_score', 7)}",
                    str(s.get("entropy", 0)),
                ])
            weak_table = Table(weak_data, repeatRows=1)
            weak_table.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#EF4444")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                ("FONTSIZE", (0, 0), (-1, -1), 9),
                ("LEFTPADDING", (0, 0), (-1, -1), 6),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ]))
            elements.append(weak_table)
            elements.append(Spacer(1, 0.2 * inch))

        recommendations = result.get("recommendations", [])
        if recommendations:
            elements.append(Paragraph("Recommendations", styles["Heading2"]))
            for rec in recommendations:
                elements.append(Paragraph(f"&#8226; {rec}", styles["Normal"]))
            elements.append(Spacer(1, 0.2 * inch))

        doc.build(elements)
        logger.info("Security report PDF exported: {path}", path=output_path)
        return output_path

    def generate_ssh_keys_csv(
        self, vault_id: str, output_path: str, ssh_key_repo, vault_key: bytes
    ) -> str:
        """Export all SSH keys to a CSV file.

        Args:
            vault_id: The vault ID.
            output_path: Destination file path.
            ssh_key_repo: SSHKeyRepository instance.
            vault_key: The vault encryption key for decrypting fields.

        Returns:
            Output path on success.
        """
        from app.security.crypto_engine import CryptoEngine

        crypto = CryptoEngine()
        entries = ssh_key_repo.get_by_vault(vault_id)
        fieldnames = [
            "name", "key_type", "fingerprint", "public_key", "private_key",
            "last_used_at", "created_at", "updated_at",
        ]
        with open(output_path, "w", newline="", encoding="utf-8") as fh:
            writer = csv.DictWriter(fh, fieldnames=fieldnames)
            writer.writeheader()
            for e in entries:
                writer.writerow({
                    "name": crypto.decrypt_field(vault_key, e.name_enc),
                    "key_type": e.key_type,
                    "fingerprint": e.fingerprint,
                    "public_key": crypto.decrypt_field(vault_key, e.public_key_enc),
                    "private_key": crypto.decrypt_field(vault_key, e.private_key_enc),
                    "last_used_at": e.last_used_at or "",
                    "created_at": str(e.created_at)[:19] if e.created_at else "",
                    "updated_at": str(e.updated_at)[:19] if e.updated_at else "",
                })
        logger.info("SSH keys CSV exported: {path}", path=output_path)
        return output_path

    def generate_api_keys_csv(
        self, vault_id: str, output_path: str, api_key_repo, vault_key: bytes
    ) -> str:
        """Export all API keys to a CSV file.

        Args:
            vault_id: The vault ID.
            output_path: Destination file path.
            api_key_repo: APIKeyRepository instance.
            vault_key: The vault encryption key for decrypting fields.

        Returns:
            Output path on success.
        """
        from app.security.crypto_engine import CryptoEngine

        crypto = CryptoEngine()
        entries = api_key_repo.get_by_vault(vault_id)
        fieldnames = [
            "name", "service", "key_value", "expires_at", "last_used_at",
            "created_at", "updated_at",
        ]
        with open(output_path, "w", newline="", encoding="utf-8") as fh:
            writer = csv.DictWriter(fh, fieldnames=fieldnames)
            writer.writeheader()
            for e in entries:
                writer.writerow({
                    "name": crypto.decrypt_field(vault_key, e.name_enc),
                    "service": crypto.decrypt_field(vault_key, e.service_enc) if e.service_enc else "",
                    "key_value": crypto.decrypt_field(vault_key, e.key_value_enc),
                    "expires_at": str(e.expires_at)[:10] if e.expires_at else "",
                    "last_used_at": str(e.last_used_at)[:19] if e.last_used_at else "",
                    "created_at": str(e.created_at)[:19] if e.created_at else "",
                    "updated_at": str(e.updated_at)[:19] if e.updated_at else "",
                })
        logger.info("API keys CSV exported: {path}", path=output_path)
        return output_path

    def generate_licences_csv(
        self, vault_id: str, output_path: str, licence_repo, vault_key: bytes
    ) -> str:
        """Export all software licences to a CSV file.

        Args:
            vault_id: The vault ID.
            output_path: Destination file path.
            licence_repo: SoftwareLicenceRepository instance.
            vault_key: The vault encryption key for decrypting fields.

        Returns:
            Output path on success.
        """
        from app.security.crypto_engine import CryptoEngine

        crypto = CryptoEngine()
        entries = licence_repo.get_by_vault(vault_id)
        fieldnames = [
            "name", "publisher", "licence_key", "expires_at",
            "created_at", "updated_at",
        ]
        with open(output_path, "w", newline="", encoding="utf-8") as fh:
            writer = csv.DictWriter(fh, fieldnames=fieldnames)
            writer.writeheader()
            for e in entries:
                writer.writerow({
                    "name": crypto.decrypt_field(vault_key, e.name_enc),
                    "publisher": crypto.decrypt_field(vault_key, e.publisher_enc) if e.publisher_enc else "",
                    "licence_key": crypto.decrypt_field(vault_key, e.licence_key_enc),
                    "expires_at": str(e.expires_at)[:10] if e.expires_at else "",
                    "created_at": str(e.created_at)[:19] if e.created_at else "",
                    "updated_at": str(e.updated_at)[:19] if e.updated_at else "",
                })
        logger.info("Software licences CSV exported: {path}", path=output_path)
        return output_path
