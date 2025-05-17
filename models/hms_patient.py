from odoo import models, fields, api
from odoo.exceptions import ValidationError, UserError
import logging
import re

_logger = logging.getLogger(__name__)


class HmsPatient(models.Model):
    _name = 'hms.patient'
    _description = 'Hospitals Management System'

    first_name = fields.Char(required=True)
    last_name = fields.Char(required=True)
    birth_date = fields.Date()
    history = fields.Html(string='History')
    cr_ratio = fields.Float(string='CR Ratio')
    blood_type = fields.Selection([
        ('a', 'A'), ('b', 'B'), ('o-positive', 'O-POSITIVE'),
        ('0-negative', 'O-NEGATIVE'), ('ab', 'AB')
    ])
    pcr = fields.Boolean()
    image = fields.Binary()
    address = fields.Text()
    age = fields.Integer(compute='_compute_age', store=True)
    department_id = fields.Many2one('hms.department', string='Department')
    doctor_id = fields.Many2one('hms.doctor', string='Doctor')
    state = fields.Selection([
        ('undetermined', 'Undetermined'),
        ('good', 'Good'),
        ('fair', 'Fair'),
        ('serious', 'Serious')
    ], string='State', default='undetermined')
    email = fields.Char(string='Email', unique=True)
    department_capacity = fields.Integer(related='department_id.capacity', string="Department Capacity")
    log_ids= fields.One2many('hms.patient.log', 'patient_id', string="Patient Log History")

    @api.depends('birth_date')
    def _compute_age(self):
        for record in self:
            if record.birth_date:
                today = fields.Date.today()
                birth_date = fields.Date.from_string(record.birth_date)
                record.age = today.year - birth_date.year - (
                            (today.month, today.day) < (birth_date.month, birth_date.day))

    @api.onchange('age')
    def _onchange_age(self):
        if self.age < 30:
            self.pcr = True
            _logger.info(
                f"PCR has been automatically checked for patient {self.first_name} {self.last_name} due to age being below 30.")

    @api.model
    def create(self, vals):
        department = self.env['hms.department'].browse(vals.get('department_id'))
        if department and not department.is_opened:
            raise ValidationError("Cannot assign patient to a closed department.")

        record = super(HmsPatient, self).create(vals)
        self._create_state_change_log(record, "Patient created")
        return record

    def write(self, vals):
        if 'department_id' in vals:
            department = self.env['hms.department'].browse(vals['department_id'])
            if department and not department.is_opened:
                raise ValidationError("Cannot assign patient to a closed department.")

        if 'state' in vals:
            state = vals['state']
            self._create_state_change_log(self, state)

        return super(HmsPatient, self).write(vals)

    def _create_state_change_log(self, patient, new_state):
        self.env['hms.patient.log'].create({
            'patient_id': patient.id,
            'created_by': self.env.user.id,
            'date': fields.Datetime.now(),
            'description': f"Patient state changed to {new_state}.",
        })
        _logger.info(f"State for patient {patient.first_name} {patient.last_name} changed to {new_state}.")

    def action_create_patient_log(self):
        for patient in self:
            self.env['hms.patient.log'].create({
                'patient_id': patient.id,
                'created_by': self.env.user.id,
                'date': fields.Datetime.now(),
                'description': 'Initial log entry for the patient.',
            })
            _logger.info(f"Log created for patient {patient.first_name} {patient.last_name} by {self.env.user.name}")

    @api.constrains('email')
    def _check_email(self):
        for record in self:

            if record.email and not re.match(r"[^@]+@[^@]+\.[^@]+", record.email):
                raise ValidationError("Please provide a valid email address.")
            existing_patient = self.env['hms.patient'].search([('email', '=', record.email)])
            if existing_patient and existing_patient.id != record.id:
                raise ValidationError("This email address is already linked to another patient.")

    @api.depends('birth_date')
    def _compute_age(self):
        for record in self:
            if record.birth_date:
                today = date.today()
                birth_date = fields.Date.from_string(record.birth_date)
                record.age = today.year - birth_date.year - (
                            (today.month, today.day) < (birth_date.month, birth_date.day))
            else:
                record.age = 0




