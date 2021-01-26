# -*- coding: utf-8 -*-
from odoo import models


class HrPayslip(models.Model):
    _inherit = 'hr.payslip'

    def get_housing_loan_repayment(self, payslip):
        """
        This method will calculate repayment of the housing loan and for employee
        :param payslip: dict of payslip
        :return: repayment amount
        Nimesh Jadav : 2 Dec 2020
        """
        if payslip.dict:
            if payslip.dict.date_to and payslip.dict.date_from:
                repayment = self.env['payment.plans'].search(
                    [('housing_loan_history_id.employee_name', '=', payslip.employee_id),
                     ('start_date', '<=', payslip.dict.date_to), ('start_date', '>=', payslip.dict.date_from)], limit=1)
                return - repayment.loan_repayment
            else:
                return 0.0
