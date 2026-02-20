# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError


class MedicalEncounter(models.Model):
    _name = 'medical.encounter'
    _description = 'Medical Encounter'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'encounter_date desc, id desc'
    _rec_name = 'ref'

    # Identificación
    ref = fields.Char(
        string='Encounter Folio',
        readonly=True,
        copy=False,
        index=True,
        default=lambda self: _('New'),
        tracking=True,
    )

    patient_id = fields.Many2one(
        'medical.patients',
        string='Patient',
        required=True,
        index=True,
        ondelete='cascade',
        tracking=True,
    )

    encounter_date = fields.Datetime(
        string='Date',
        required=True,
        default=fields.Datetime.now,
        tracking=True,
    )

    doctor_user_id = fields.Many2one(
        'res.users',
        string='Doctor',
        required=True,
        default=lambda self: self.env.user,
        tracking=True,
    )

    # Nota clínica (mínimo serio)
    chief_complaint = fields.Text(string='Chief Complaint')
    present_illness = fields.Text(string='History of Present Illness')
    physical_exam = fields.Text(string='Physical Exam')
    diagnosis = fields.Text(string='Diagnosis')
    plan = fields.Text(string='Plan / Treatment')
    notes = fields.Text(string='Additional Notes')

    # Signos vitales
    bp_systolic = fields.Integer(string='BP Systolic (mmHg)')
    bp_diastolic = fields.Integer(string='BP Diastolic (mmHg)')
    heart_rate = fields.Integer(string='Heart Rate (bpm)')
    resp_rate = fields.Integer(string='Respiratory Rate (rpm)')
    temperature = fields.Float(string='Temperature (°C)', digits=(3, 1))
    spo2 = fields.Integer(string='SpO2 (%)')

    weight = fields.Float(string='Weight (kg)', digits=(6, 2))
    height = fields.Float(string='Height (m)', digits=(4, 2))
    bmi = fields.Float(string='BMI', digits=(6, 2), compute='_compute_bmi', store=True)

    # Lab Results
    lab_result_ids = fields.One2many(
        'medical.lab.result', 'encounter_id', string='Lab Results'
    )

    prescription_ids = fields.One2many(
        'medical.prescription',
        'encounter_id',
        string='Prescriptions'
    )
    prescription_count = fields.Integer(compute='_compute_prescription_count')

    state = fields.Selection([
        ("in_progress", "In progress"),
        ("done", "Finalized"),
    ], default="in_progress", required=True, tracking=True)

    @api.depends('weight', 'height')
    def _compute_bmi(self):
        for rec in self:
            if rec.weight and rec.height and rec.height > 0:
                rec.bmi = rec.weight / (rec.height * rec.height)
            else:
                rec.bmi = 0.0

    @api.model_create_multi
    def create(self, vals_list):
        seq = self.env['ir.sequence']
        for vals in vals_list:
            if vals.get('ref', _('New')) == _('New'):
                vals['ref'] = seq.next_by_code('medical.encounter') or _('New')
        return super().create(vals_list)


    def write(self, vals):
        # Bloquear edición desde Patient, excepto si se manda un bypass explícito
        if self.env.context.get('readonly_from_patient') and not self.env.context.get('bypass_readonly_from_patient'):
            raise UserError(
                "You cannot edit a medical encounter from the Patient record. "
                "Please open it from the Encounters menu."
            )
        return super().write(vals)


    # Botones de estado (opcional pero útil)
    def action_confirm(self):
        self.write({'state': 'in_progress'})

    def action_close(self):
        self.write({'state': 'done'})

    def _compute_prescription_count(self):
        for rec in self:
            rec.prescription_count = len(rec.prescription_ids)