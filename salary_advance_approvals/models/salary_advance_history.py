from odoo import models, fields, api, _
from datetime import datetime as datetime

Year_Selection_Value = [('2015', '2015'), ('2016', '2016'), ('2017', '2017'), ('2018', '2018'), ('2019', '2019'),
                        ('2020', '2020'), ('2021', '2021'), ('2022', '2022'), ('2023', '2023'), ('2024', '2024'),
                        ('2025', '2025'), ('2026', '2026'), ('2027', '2027'), ('2028', '2028'), ('2029', '2029'),
                        ('2030', '2030'), ('2031', '2031'), ('2032', '2032'), ('2033', '2033'), ('2034', '2034'),
                        ('2035', '2035'), ('2036', '2036'), ('2037', '2037'), ('2038', '2038'), ('2039', '2039'),
                        ('2040', '2040'), ('2041', '2041'), ('2042', '2042'), ('2043', '2043'), ('2044', '2044'),
                        ('2045', '2045'), ('2046', '2046'), ('2047', '2047'), ('2048', '2048'), ('2049', '2049'),
                        ('2050', '2050')]

Month_Selection_Value = [('01', 'January'), ('02', 'February'), ('03', 'March'), ('04', 'April'),
                         ('05', 'May'), ('06', 'June'), ('07', 'July'), ('08', 'August'),
                         ('09', 'September'), ('10', 'October'), ('11', 'November'),
                         ('12', 'December')]


class AdvanceSalaryHistory(models.Model):
    _name = 'advance.salary.history'
    _description = "Employee Salary Advance Request History"

    advance_salary_request_id = fields.Many2one('approval.request', 'Advance Salary Request')
    salary_employee_id = fields.Many2one('hr.employee', string="Employee", readonly=1)
    system_id = fields.Char(related='salary_employee_id.system_id', readonly=1)
    job_title = fields.Many2one(related='salary_employee_id.contract_id.job_title', readonly=1)
    job_grade = fields.Many2one(related='salary_employee_id.contract_id.job_grade', readonly=1)
    currency_id = fields.Many2one('res.currency', string='Currency',
                                  default=lambda x: x.env.company.currency_id, readonly=1)
    total_monthly_salary = fields.Monetary(string="Total Monthly Salary", currency_field='currency_id', readonly=1)
    request_year = fields.Selection(string="Request Year", selection=Year_Selection_Value,
                                    default=datetime.today().strftime("%Y"), readonly=1)
    request_month = fields.Selection(string='Request Month', selection=Month_Selection_Value,
                                     default=datetime.today().strftime("%m"), readonly=1)

    # approved_year = fields.Selection(string='Approved Year', selection=Year_Selection_Value, readonly=1)
    request_amount = fields.Monetary(string="Request Amount", currency_field='currency_id', readonly=1)
    # approved_amount = fields.Monetary(string="Approved Amount", currency_field='currency_id', readonly=1)
    # approved_month = fields.Selection(string='Approved Month', selection=Month_Selection_Value, readonly=1)
    salary_advance_reason = fields.Text(string="Request Reason", readonly=1)
    salary_advance_ref = fields.Char(string="Reference Number", readonly=1)

    def name_get(self):
        """
        :Author:Bhavesh Jadav TechUltra Solutions
        :Date:09/10/2020
        :Func:this method use for the add name in name the field
        :Return:list with name and
        """
        result = []
        for employee in self:
            if employee.salary_employee_id:
                name = employee.salary_employee_id.name
                result.append((employee.id, name))
        return result
