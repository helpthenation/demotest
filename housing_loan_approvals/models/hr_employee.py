from odoo import models, fields


class HrEmployee(models.Model):
    _inherit = "hr.employee"

    housing_history_ids = fields.One2many('housing.loan', 'employee_name', string="Employee Housing history")


