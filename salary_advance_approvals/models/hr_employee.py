from odoo import models, fields


class HrEmployee(models.Model):
    _inherit = "hr.employee"

    advance_salary_history_ids = fields.One2many('advance.salary.history', 'salary_employee_id',
                                                 string="Advance Salary "
                                                        "History")
