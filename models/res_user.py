from odoo import models, fields

class ResUsers(models.Model):
    _inherit = 'res.users'

    discount = fields.Float(string="Discount")
    max_discount = fields.Float(string="Maximum Discount Allowed", default=40.0)
