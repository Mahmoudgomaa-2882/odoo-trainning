from odoo import models, fields, api
from odoo.exceptions import ValidationError
import logging



class HmsDoctor(models.Model):
    _name = 'hms.doctor'


    name = fields.Char()
    last_name = fields.Char()
    image = fields.Binary()

