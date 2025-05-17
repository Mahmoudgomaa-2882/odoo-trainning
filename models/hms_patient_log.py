from odoo import models, fields, api
from odoo.exceptions import ValidationError
import logging

_logger = logging.getLogger(__name__)

class HmsPatientLog(models.Model):
    _name = 'hms.patient.log'

    patient_id = fields.Many2one('hms.patient', string="Patient")
    created_by = fields.Many2one('res.users', string='Created By')
    date = fields.Datetime('Date', default=fields.Datetime.now)
    description = fields.Text('Description')
    info = fields.Text("OSD Info")