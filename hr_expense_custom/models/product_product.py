from odoo import models, fields, api, _, SUPERUSER_ID
from odoo.exceptions import UserError


class ProductProduct(models.Model):
    _inherit = 'product.product'

    expense_type = fields.Many2many('expense.type', string="Expense Category")
