# -*- coding: utf-8 -*-
import base64
import tempfile
import subprocess
import os

from odoo import api, fields, models, _
from odoo.exceptions import UserError


class MedicalLabResult(models.Model):
    _name = 'medical.lab.result'
    _description = 'Medical Lab Result'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'create_date desc'

    encounter_id = fields.Many2one(
        'medical.encounter',
        string='Encounter',
        required=True,
        ondelete='cascade',
        index=True,
        tracking=True,
    )

    patient_id = fields.Many2one(related='encounter_id.patient_id', store=True, readonly=True)
    doctor_user_id = fields.Many2one(related='encounter_id.doctor_user_id', store=True, readonly=True)

    ref = fields.Char(string='Lab Folio', readonly=True, copy=False, default=lambda self: _('New'), index=True)
    study_name = fields.Char(string='Study / Panel', required=True, tracking=True)
    result_date = fields.Datetime(string='Result Date', default=fields.Datetime.now, tracking=True)

    state = fields.Selection([
        ('draft', 'Draft'),
        ('validated', 'Validated'),
        ('cancelled', 'Cancelled'),
    ], default='draft', tracking=True)

    result_pdf = fields.Binary(string='Result PDF', attachment=True)
    result_pdf_filename = fields.Char(string='PDF Filename')

    preview_image = fields.Image(string='Preview', max_width=512, max_height=512, attachment=True)
    notes = fields.Text(string='Notes')

    @api.model_create_multi
    def create(self, vals_list):
        seq = self.env['ir.sequence']
        records = super().create([
            dict(vals, ref=(seq.next_by_code('medical.lab.result') if vals.get('ref', _('New')) == _('New') else vals.get('ref')))
            for vals in vals_list
        ])
        # generar preview si viene PDF
        for rec, vals in zip(records, vals_list):
            if vals.get('result_pdf'):
                rec._generate_preview_from_pdf()
        return records

    def write(self, vals):
        res = super().write(vals)
        if 'result_pdf' in vals:
            for rec in self:
                if rec.result_pdf:
                    rec._generate_preview_from_pdf()
                else:
                    rec.preview_image = False
        return res

    def _generate_preview_from_pdf(self):
        """
        Genera preview PNG (primera página) desde result_pdf usando pdftoppm.
        Requiere poppler-utils instalado en el contenedor.
        """
        self.ensure_one()
        if not self.result_pdf:
            return

        pdf_bytes = base64.b64decode(self.result_pdf)

        with tempfile.TemporaryDirectory() as tmpdir:
            pdf_path = os.path.join(tmpdir, 'input.pdf')
            out_prefix = os.path.join(tmpdir, 'preview')  # pdftoppm produce preview-1.png

            with open(pdf_path, 'wb') as f:
                f.write(pdf_bytes)

            try:
                # -png: salida png, -f 1 -l 1: solo primera página, -singlefile: preview.png (sin -1)
                cmd = ['pdftoppm', '-png', '-f', '1', '-l', '1', '-singlefile', pdf_path, out_prefix]
                subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            except FileNotFoundError:
                raise UserError(_("pdftoppm not found. Install 'poppler-utils' in the Odoo container."))
            except subprocess.CalledProcessError as e:
                raise UserError(_("Failed generating preview from PDF:\n%s") % (e.stderr.decode('utf-8', errors='ignore') or str(e)))

            png_path = out_prefix + '.png'
            if not os.path.exists(png_path):
                raise UserError(_("Preview PNG was not generated."))

            with open(png_path, 'rb') as img:
                self.preview_image = base64.b64encode(img.read())

    # -------------------------
    # Acción para abrir PDF en nueva pestaña del navegador
    # -------------------------
    def action_open_result_pdf_new_tab(self):
        self.ensure_one()
        if not self.result_pdf:
            raise UserError(_("No PDF uploaded."))

        return {
            "type": "ir.actions.act_url",
            "url": f"/web/content/{self._name}/{self.id}/result_pdf?download=false",
            "target": "new",
        }

    # -------------------------
    # Acción para abrir PDF en visor embebido (iframe) dentro de un wizard
    # (requiere que el PDF esté guardado como attachment relacionado para que el iframe pueda acceder a él)
    # -------------------------
    def action_open_result_pdf(self):
        self.ensure_one()
        if not self.result_pdf:
            raise UserError(_("No PDF uploaded."))

        attachment = self.env["ir.attachment"].sudo().search([
            ("res_model", "=", self._name),
            ("res_id", "=", self.id),
            ("res_field", "=", "result_pdf"),
        ], order="id desc", limit=1)

        if not attachment:
            raise UserError(_("Attachment not found for this PDF."))

        return {
            "type": "ir.actions.act_window",
            "name": _("PDF Preview"),
            "res_model": "medical.lab.result.pdf.preview.wizard",
            "view_mode": "form",
            "target": "new",
            "context": {
                "default_attachment_id": attachment.id,
            },
        }