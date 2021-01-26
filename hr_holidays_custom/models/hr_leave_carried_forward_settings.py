from odoo.exceptions import Warning
from odoo import fields, models, api


class CarriedForwardSettings(models.Model):
    _name = "carried.forward.settings"
    _description = "Hr Leave Carried Forward Settings"

    name = fields.Char(string="Name")

    apply_for_all_employee = fields.Boolean(string="Apply For All Employee", default=False)
    employee_ids = fields.Many2many('hr.employee', string='Employees')
    carry_forward = fields.Selection([('all', 'All'),
                                      ('specific_number', 'Specific Number')
                                      ], string="Carry Forward", default='all', required=True)
    num_of_leave_for_carry_forward = fields.Float(string="Number of Leave for Carry Forward")
    encashment = fields.Selection([('all_remaining', 'All Remaining'),
                                   ('specific_number_of_remaining', 'Specific Number of Remaining'),
                                   ('percentage_of_remaining', 'Percentage of Remaining')
                                   ], string="Encashment", default="all_remaining", required=True)
    encashment_number = fields.Float(string="Encashment Number")
    encashment_percentage = fields.Float(string="Encashment Percentage")
