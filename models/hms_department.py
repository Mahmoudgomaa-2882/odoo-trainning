from odoo import models, fields, api
from odoo.exceptions import ValidationError
import logging

_logger = logging.getLogger(__name__)

_logger = logging.getLogger(__name__)

class HmsDepartment(models.Model):
    _name = 'hms.department'
    _description = 'Department'

    name = fields.Char(string='Department Name', required=True)
    capacity = fields.Integer(string='Capacity')
    is_opened = fields.Boolean(string='Is Opened')
    patient = fields.Many2one('hms.patient', string='Patient')
    patient_ids = fields.One2many('hms.patient', 'department_id', string="Patients")


