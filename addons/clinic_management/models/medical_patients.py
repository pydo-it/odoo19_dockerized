# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError



class MedicalPatient(models.Model):
    _name = 'medical.patients'
    _description = 'Medical Patients'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'create_date desc'

    # -------------------------
    # Core fields
    # -------------------------
    partner_id = fields.Many2one(
        'res.partner',
        string='Contact',
        readonly=True,
        copy=False,
        ondelete='restrict',
    )

    name = fields.Char(string='Patient Name', required=True, tracking=True)
    ref = fields.Char(
        string='Patient Folio',
        readonly=True,
        copy=False,
        index=True,
        default=lambda self: _('New'),
        tracking=True,
    )

    country_id = fields.Many2one('res.country', string='Country')
    phone = fields.Char(string='Phone')
    email = fields.Char(string='Email')

    # Identificadores (opcionales)
    curp = fields.Char(string='CURP', index=True)
    rfc = fields.Char(string='RFC', index=True)
    id_type = fields.Selection([
        ('passport', 'Passport'),
        ('national_id', 'National ID'),
        ('other', 'Other'),
    ], string="ID Type")
    id_number = fields.Char(string="ID Number", index=True)

    birthdate = fields.Date(string='Birthdate')
    age = fields.Integer(string='Age', compute='_compute_age', store=True)

    gender = fields.Selection(
        [('male', 'Male'), ('female', 'Female'), ('other', 'Other')],
        string='Gender'
    )

    # Historial clínico
    encounter_ids = fields.One2many(
        'medical.encounter',
        'patient_id',
        string='Encounters',
    )

    encounter_count = fields.Integer(
        string='Encounters',
        compute='_compute_encounter_count',
    )

    active = fields.Boolean(default=True)

    @api.depends('ref', 'name')
    def _compute_display_name(self):
        for rec in self:
            if rec.ref and rec.ref != _('New'):
                rec.display_name = f"[{rec.ref}] {rec.name or ''}".strip()
            else:
                rec.display_name = rec.name or ''

    def name_get(self):
        res = []
        for rec in self:
            nm = rec.name or ''
            if rec.ref and rec.ref != _('New'):
                nm = f"[{rec.ref}] {nm}"
            res.append((rec.id, nm))
        return res

    @api.model
    def name_search(self, name='', args=None, operator='ilike', limit=100):
        """Buscar por Folio, Nombre, Teléfono o Email (más usable en clínica)."""
        args = args or []
        domain = []
        if name:
            domain = ['|', '|', '|',
                    ('ref', operator, name),
                    ('name', operator, name),
                    ('phone', operator, name),
                    ('email', operator, name)]
        return self.search(domain + args, limit=limit).name_get()

    # -------------------------
    # Normalization utilities
    # -------------------------
    def _normalize_phone(self, phone):
        """Keep digits only to compare numbers reliably."""
        return ''.join(ch for ch in (phone or '') if ch.isdigit())

    @api.model
    def _normalize_vals(self, vals):
        """Normalize identifiers before create/write."""
        if 'curp' in vals and vals.get('curp'):
            vals['curp'] = vals['curp'].strip().upper()
        if 'rfc' in vals and vals.get('rfc'):
            vals['rfc'] = vals['rfc'].strip().upper()
        if 'id_number' in vals and vals.get('id_number'):
            vals['id_number'] = vals['id_number'].strip().upper()
        if 'email' in vals and vals.get('email'):
            vals['email'] = vals['email'].strip().lower()
        if 'phone' in vals and vals.get('phone'):
            vals['phone'] = vals['phone'].strip()
        return vals

    # -------------------------
    # Duplicate detection
    # -------------------------
    @api.model
    def _find_existing_patient(self, vals, exclude_id=None):
        """Find possible existing patient using strong -> medium -> soft keys."""
        exclude_domain = [('id', '!=', exclude_id)] if exclude_id else []

        # 1) CURP (fuerte)
        curp = (vals.get('curp') or '').strip().upper()
        if curp:
            patient = self.search(exclude_domain + [('curp', '=', curp)], limit=1)
            if patient:
                return patient

        # 2) RFC (fuerte)
        rfc = (vals.get('rfc') or '').strip().upper()
        if rfc:
            patient = self.search(exclude_domain + [('rfc', '=', rfc)], limit=1)
            if patient:
                return patient

        # 3) ID externo (fuerte)
        id_type = vals.get('id_type')
        id_number = (vals.get('id_number') or '').strip().upper()
        if id_type and id_number:
            patient = self.search(exclude_domain + [('id_type', '=', id_type), ('id_number', '=', id_number)], limit=1)
            if patient:
                return patient

        # 4) Email (medio) -> solo sugerencia, no necesariamente único
        email = (vals.get('email') or '').strip().lower()
        if email:
            patient = self.search(exclude_domain + [('email', '=', email)], limit=1)
            if patient:
                return patient

        # 5) Phone (medio) -> comparación aproximada (últimos 7 dígitos)
        phone_digits = self._normalize_phone(vals.get('phone'))
        if phone_digits and len(phone_digits) >= 7:
            last7 = phone_digits[-7:]
            patient = self.search(exclude_domain + [('phone', 'ilike', last7)], limit=1)
            if patient:
                return patient

        # 6) Nombre + birthdate (suave)
        name = (vals.get('name') or '').strip()
        birthdate = vals.get('birthdate')
        if name and birthdate:
            patient = self.search(exclude_domain + [('name', '=', name), ('birthdate', '=', birthdate)], limit=1)
            if patient:
                return patient

        return self.browse()

    # -------------------------
    # Constraints (run on create/write)
    # -------------------------
    @api.constrains('curp', 'rfc', 'id_type', 'id_number')
    def _check_unique_identifiers(self):
        """Block duplicates for strong identifiers."""
        for rec in self:
            # CURP
            if rec.curp:
                curp = rec.curp.strip().upper()
                dup = self.search([('id', '!=', rec.id), ('curp', '=', curp)], limit=1)
                if dup:
                    raise ValidationError(_("CURP already exists for patient: %s") % dup.display_name)

            # RFC
            if rec.rfc:
                rfc = rec.rfc.strip().upper()
                dup = self.search([('id', '!=', rec.id), ('rfc', '=', rfc)], limit=1)
                if dup:
                    raise ValidationError(_("RFC already exists for patient: %s") % dup.display_name)

            # External ID
            if rec.id_type and rec.id_number:
                id_number = rec.id_number.strip().upper()
                dup = self.search([
                    ('id', '!=', rec.id),
                    ('id_type', '=', rec.id_type),
                    ('id_number', '=', id_number),
                ], limit=1)
                if dup:
                    raise ValidationError(_("ID already exists for patient: %s") % dup.display_name)

    # -------------------------
    # Create / Write
    # -------------------------
    @api.model_create_multi
    def create(self, vals_list):
        partner = self.env['res.partner']
        sequence = self.env['ir.sequence']

        cleaned_vals_list = []
        for vals in vals_list:
            vals = dict(vals or {})
            vals = self._normalize_vals(vals)

            # Duplicate check (create)
            existing = self._find_existing_patient(vals)
            if existing:
                raise ValidationError(
                    _("Possible duplicate patient detected:\n%s\nUse the existing patient record instead.")
                    % (existing.display_name,)
                )

            # Folio
            if vals.get('ref', _('New')) == _('New'):
                vals['ref'] = sequence.next_by_code('medical.patients') or _('New')

            # Create partner if missing
            if not vals.get('partner_id'):
                partner_vals = {
                    'name': vals.get('name'),
                    'phone': vals.get('phone'),
                    'email': vals.get('email'),
                    'country_id': vals.get('country_id') or False,
                    'company_type': 'person',
                }
                partner = partner.create(partner_vals)
                vals['partner_id'] = partner.id

            cleaned_vals_list.append(vals)

        return super().create(cleaned_vals_list)

    def write(self, vals):
        vals = dict(vals or {})
        vals = self._normalize_vals(vals)

        # Duplicate check (write) only if key fields are being modified
        key_fields = {'curp', 'rfc', 'id_type', 'id_number', 'email', 'phone', 'name', 'birthdate'}
        if key_fields.intersection(vals.keys()):
            for rec in self:
                candidate_vals = {
                    'curp': vals.get('curp', rec.curp),
                    'rfc': vals.get('rfc', rec.rfc),
                    'id_type': vals.get('id_type', rec.id_type),
                    'id_number': vals.get('id_number', rec.id_number),
                    'email': vals.get('email', rec.email),
                    'phone': vals.get('phone', rec.phone),
                    'name': vals.get('name', rec.name),
                    'birthdate': vals.get('birthdate', rec.birthdate),
                }
                existing = self._find_existing_patient(candidate_vals, exclude_id=rec.id)
                # Bloqueamos solo si coincide por identificadores fuertes
                if existing and (
                    (candidate_vals.get('curp') and existing.curp == (candidate_vals['curp'] or '').strip().upper())
                    or (candidate_vals.get('rfc') and existing.rfc == (candidate_vals['rfc'] or '').strip().upper())
                    or (candidate_vals.get('id_type') and candidate_vals.get('id_number')
                        and existing.id_type == candidate_vals['id_type']
                        and existing.id_number == (candidate_vals['id_number'] or '').strip().upper())
                ):
                    raise ValidationError(
                        _("This update would create a duplicate patient:\n%s") % existing.display_name
                    )

        res = super().write(vals)

        # Sync fields to partner
        sync_fields = {'name': 'name', 'phone': 'phone', 'email': 'email', 'country_id': 'country_id'}
        for rec in self:
            if rec.partner_id:
                pvals = {}
                for k, pk in sync_fields.items():
                    if k in vals:
                        pvals[pk] = rec[k].id if k == 'country_id' else rec[k]
                if pvals:
                    rec.partner_id.write(pvals)

        return res

    # -------------------------
    # UX: phone prefix on country change
    # -------------------------
    @api.onchange('country_id', 'phone')
    def _onchange_phone_prefix(self):
        for rec in self:
            dial = rec.country_id.phone_code if rec.country_id else False  # int in Odoo
            if dial and rec.phone and not rec.phone.strip().startswith('+'):
                rec.phone = f"+{dial} {rec.phone.strip()}"

    # -------------------------
    # Unlink override to handle partner cleanup
    # -------------------------
    def unlink(self):
        # 1) Guardamos partners antes de borrar pacientes
        partners = self.mapped('partner_id')

        # 2) Borramos pacientes primero
        res = super().unlink()

        # 3) Borramos partners solo si ya no están usados por otros pacientes
        if partners:
            # Partners que todavía siguen ligados a algún paciente (después del delete)
            remaining_partner_ids = self.env['medical.patients'].sudo().search([
                ('partner_id', 'in', partners.ids)
            ]).mapped('partner_id').ids

            # Partners que ya no están ligados a ningún paciente
            partners_to_delete = partners.filtered(lambda p: p.id not in remaining_partner_ids)

            # (Opcional) aquí podrías evitar borrar partners "serios" (facturas, ventas, etc.)
            # por ahora lo dejamos directo:
            if partners_to_delete:
                partners_to_delete.sudo().unlink()

        return res
    
    # -------------------------
    # Compute method for encounter count
    # -------------------------
    @api.depends('encounter_ids')
    def _compute_encounter_count(self):
        encounter = self.env['medical.encounter']
        for rec in self:
            rec.encounter_count = encounter.search_count([('patient_id', '=', rec.id)])

    # -------------------------
    # Compute method for age
    # -------------------------
    @api.depends('birthdate')
    def _compute_age(self):
        today = fields.Date.today()
        for rec in self:
            if rec.birthdate:
                rec.age = today.year - rec.birthdate.year - (
                    (today.month, today.day) < (rec.birthdate.month, rec.birthdate.day)
                )
            else:
                rec.age = 0