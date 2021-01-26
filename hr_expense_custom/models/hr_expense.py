from odoo import api, fields, models, _
import datetime


class HrExpense(models.Model):
    _inherit = "hr.expense"

    product_id = fields.Many2one('product.product', string='Expense Type', readonly=True,
                                 states={'draft': [('readonly', False)], 'reported': [('readonly', False)],
                                         'refused': [('readonly', False)]},
                                 domain="[('can_be_expensed', '=', True), '|', ('company_id', '=', False), ('company_id', '=', company_id)]",
                                 ondelete='restrict')

    def _create_sheet_from_expenses(self):
        sheet = super(HrExpense, self)._create_sheet_from_expenses()
        sheet._onchange_expense_settings_id()
        return sheet
