# -*- coding: utf-8 -*-

from odoo import models, fields


# class HrCompensationPayComponent(models.Model):
#     _inherit = 'hr.compensation.pay.component'
#
#     # is_housing = fields.Boolean(string='Is Housing')


class HousingLoan(models.Model):
    _name = 'housing.loan'
    _description = 'Housing Loan'

    related_approval_hl = fields.Many2one('approval.request', 'Approval Request')
    employee_name = fields.Many2one('hr.employee', string="Employee Name", readonly=1)
    employee_id = fields.Char(related='employee_name.company_employee_id', string="Employee Id")
    job_title_id = fields.Many2one(related='employee_name.contract_id.job_title', string="Job Title")
    department_id = fields.Many2one(related='employee_name.department_id', string="Dept/Section")
    grade_id = fields.Many2one(related='employee_name.contract_id.job_grade', string="Grade")
    date_of_join = fields.Date(related='employee_name.contract_id.date_start', string="Date of joining")
    monthly_housing_allowance = fields.Float(string="Monthly Housing Allowance", readonly=1)
    yearly_housing_allowance = fields.Float(string='Yearly Housing Allowance', readonly=1)

    loan_amount = fields.Float(string='Loan Amount', readonly=1)
    mode_of_payment = fields.Selection(
        [('Cheque', 'Cheque'), ('Bank Transfer to Salary Account', 'Bank Transfer to Salary Account')],
        string="Mode of Payment", readonly=1)
    remarks = fields.Char(string="Remarks", readonly=1)
    currency_id = fields.Many2one('res.currency', 'Currency', default=lambda x: x.env.company.currency_id)
    rental_period = fields.Selection([('6 months', '6 months'), ('1 year', '1 year'), ('Other', 'Other')],
                                     string='Rental period', default='1 year', readonly=1)

    tenancy_contract = fields.Selection([('Renewal of contract', 'Renewal of contract'),
                                         ('Renting a new accommodation', 'Renting a new accommodation')],
                                        string='Tenancy Contract', readonly=1)
    rental_amount = fields.Float(string='Rental Amount', readonly=1)
    tenancy_contract_start_date = fields.Date(string='Start Date', readonly=1)
    tenancy_contract_end_date = fields.Date(string='End Date', readonly=1)
    effective_month_year = fields.Char('Effective Month/Year', store=True)

    emirate_id = fields.Many2one('res.country.state', string='Emirate', readonly=1)
    town = fields.Char(string='Town', readonly=1)
    street = fields.Char(string="Street", readonly=1)
    build_no = fields.Char(string='Building', readonly=1)
    flat_vila_no = fields.Char(string='Flat/Villa No', readonly=1)
    tel_no = fields.Char(string='Tel. No', readonly=1)
    mobile_no = fields.Char(string='Mobile No', readonly=1)
    # signature = fields.Char(string='Signature', readonly=1)
    # sign_date = fields.Date(string='Date', readonly=1)
    utility_bill = fields.Binary(string='Utility Bill', readonly=1)
    tenancy_contract_file = fields.Binary(string="Tenancy Contract", readonly=1)
    security_cheque = fields.Binary(string="Security Cheque", readonly=1)

    # Payment Plans
    payment_plans_ids = fields.One2many('payment.plans', 'housing_loan_history_id', string='Payment Plans')

    current_account_number = fields.Char(string='Current Account Number',
                                         readonly=True)
    current_bank_name = fields.Many2one('res.bank', string='Current Bank Name', readonly=True)
    current_iban = fields.Char(string="Current IBAN NO.", readonly=True)

    def name_get(self):
        """
        :Author:Nimesh Jadav TechUltra Solutions
        :Date:07/10/2020
        :Func:this method use for the add name in name the field
        :Return:list with name and
        """
        result = []
        for employee in self:
            if employee.employee_name:
                name = employee.employee_name.name
                result.append((employee.id, name))
        return result
