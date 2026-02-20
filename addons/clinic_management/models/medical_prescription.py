# -*- coding: utf-8 -*-
from odoo import api, fields, models, _

class MedicalPrescription(models.Model):
    _name = "medical.prescription"
    _description = "Medical Prescription"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "create_date desc"
    _rec_name = "ref"

    ref = fields.Char(string="Prescription Folio", readonly=True, copy=False, default=lambda self: _("New"), index=True)

    encounter_id = fields.Many2one(
        "medical.encounter",
        string="Encounter",
        required=True,
        ondelete="cascade",
        index=True,
        tracking=True,
    )

    patient_id = fields.Many2one(related="encounter_id.patient_id", store=True, readonly=True)
    doctor_user_id = fields.Many2one(related="encounter_id.doctor_user_id", store=True, readonly=True)
    prescription_date = fields.Datetime(default=fields.Datetime.now, tracking=True)

    diagnosis = fields.Char(string="Diagnosis", tracking=True)
    indications = fields.Text(string="Indications / Notes", tracking=True)

    line_ids = fields.One2many("medical.prescription.line", "prescription_id", string="Medicines")

    company_id = fields.Many2one(
        "res.company",
        string="Company",
        default=lambda self: self.env.company,
        readonly=True,
    )


    @api.model_create_multi
    def create(self, vals_list):
        seq = self.env["ir.sequence"]
        for vals in vals_list:
            if vals.get("ref", _("New")) == _("New"):
                vals["ref"] = seq.next_by_code("medical.prescription") or _("New")
        return super().create(vals_list)
    
    def action_print_prescription(self):
        self.ensure_one()
        # Trabajamos con un "encounter" que puede escribir aunque vengamos desde Patients
        encounter = self.encounter_id.with_context(
            bypass_readonly_from_patient=True,  # permite el write en medical.encounter.write()
            readonly_from_patient=False,        # por si viene arrastrado desde el paciente
        )
        # 1) Si por alguna razón el encounter está en draft, lo pasamos a in_progress
        if encounter and encounter.state == 'draft':
            encounter.write({'state': 'in_progress'})
        # 2) Al imprimir receta: finalizar encounter
        if encounter and encounter.state != 'done':
            encounter.write({'state': 'done'})
        # 3) Disparar el PDF (mismo reporte que ya tienes)
        return self.env.ref('clinic_management.action_report_medical_prescription').report_action(self)


class MedicalPrescriptionLine(models.Model):
    _name = "medical.prescription.line"
    _description = "Medical Prescription Line"
    _order = "sequence, id"

    prescription_id = fields.Many2one("medical.prescription", required=True, ondelete="cascade")
    sequence = fields.Integer(default=10)

    medicine = fields.Char(required=True)
    dose = fields.Char(string="Dose")             # ej: 500 mg
    frequency = fields.Char(string="Frequency")   # ej: c/8h
    duration = fields.Char(string="Duration")     # ej: 7 días
    route = fields.Char(string="Route")           # ej: VO
    notes = fields.Char(string="Notes")
