# -*- coding: utf-8 -*-

from odoo import models, fields


class PaymentPlans(models.Model):
    _name = 'payment.plans'
    _description = 'Payment Plans'

    housing_loan_history_id = fields.Many2one('housing.loan', string='Employee Name')
    approval_request_id = fields.Many2one('approval.request', string='Approval Request Name')
    pay_year = fields.Char(string='Pay Year')
    pay_month = fields.Char(string="Pay month")
    start_date = fields.Date(string='Start Date')
    end_date = fields.Date(string='End Date')
    loan_balance = fields.Float(string='Loan balance')
    payment = fields.Float(string='Payment')
    loan_repayment = fields.Float(string='Loan RePayment')
    reg_repayment = fields.Float(string='Reg RePayment')

    def name_get(self):
        """
        :Author:Nimesh Jadav TechUltra Solutions
        :Date:16/10/2020
        :Func:this method use for the add name in name the field
        :Return:list with name and
        """
        result = []
        for employee in self:
            if employee.housing_loan_history_id:
                name = employee.housing_loan_history_id.employee_name.name
                result.append((employee.id, name))
        return result
