from odoo import models, fields, api
from odoo.exceptions import ValidationError


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    related_patient_id = fields.Many2one('hms.patient', string='Related Patient', help="Link the customer to a patient")
    tax_id = fields.Char(string='Tax ID', required=True)
    discount = fields.Float(string="Discount")
    total_quantities = fields.Float(compute='_compute_quantities', store=True)

    def action_change_state(self):
        for rec in self:
            if rec.state == 'draft':
                rec.action_confirm()

    @api.onchange('partner_id')
    def _customer_filter_partner_id(self):
        return {
            'domain': {
                'partner_id': [('partner_type', '=', 'customer')]
            }
        }

    @api.depends('order_line.product_uom_qty')
    def _compute_quantities(self):
        for record in self:
            record.total_quantities = sum(record.order_line.mapped('product_uom_qty')) if record.order_line else 0


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    sale_discount = fields.Float()
    volume_discount = fields.Float()
    cash_discount = fields.Float()
    total_discount = fields.Float()

    @api.onchange('discount')
    def _check_discount_limit(self):
        for record in self:
            max_discount = self.env.user.discount or 0
            if record.discount > max_discount:
                raise ValidationError(f"You cannot give more than {max_discount}% discount.")


class ResPartner(models.Model):
    _inherit = 'res.partner'

    partner_type = fields.Selection([
        ('vendor', 'Vendor'),
        ('customer', 'Customer')],
        string="Partner Type",
        default='customer'
    )
    international_number = fields.Char(
        string="International Number",
        size=20,
        required=True,
    )

    _sql_constraints = [
        ('unique_international_number', 'unique (international_number)', 'The international number must be unique!')
    ]

    @api.constrains('international_number')
    def _check_international_number(self):
        for record in self:
            if record.international_number and len(record.international_number) > 15:
                raise ValidationError("The international number must be at most 15 digits.")