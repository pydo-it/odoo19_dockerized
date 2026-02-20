# -*- coding: utf-8 -*-
from odoo import api, fields, models, _

class MedicalLabResultPdfPreviewWizard(models.TransientModel):
    _name = "medical.lab.result.pdf.preview.wizard"
    _description = "Medical Lab Result PDF Preview"

    attachment_id = fields.Many2one("ir.attachment", string="Attachment", readonly=True)
    viewer_html = fields.Html(string="PDF", readonly=True, sanitize=False)

    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)
        att_id = self.env.context.get("default_attachment_id")
        if att_id:
            res["attachment_id"] = att_id
            # iframe al contenido del attachment
            res["viewer_html"] = (
                f'<iframe src="/web/content/{att_id}?download=false" '
                f'style="width:100%; height:80vh; border:0;"></iframe>'
            )
        return res