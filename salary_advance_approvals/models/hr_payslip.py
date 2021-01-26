# -*- coding: utf-8 -*-
from odoo import models, api


class HrPayslip(models.Model):
    _inherit = 'hr.payslip'

    def get_advance_salary_amount_allowance(self, payslip):
        """
        @Author:Bhavesh Jadav TechUltra Solutions Pvt. Ltd.
        @Date:02/12/2020
        @Func:this method use for add advance salary amount payslip
        @return: advance salary amount
        """
        date_from_month = payslip.date_from.strftime("%m")
        date_from_year = payslip.date_from.strftime("%Y")
        employee_id = self.env['hr.employee'].browse(payslip.employee_id)
        advance_salary_line = employee_id.advance_salary_history_ids.filtered(
            lambda line: line.request_month == str(int(date_from_month) + 1) and line.request_year == str(
                date_from_year))
        if advance_salary_line:
            return round(advance_salary_line.request_amount, 2)
        else:
            return 0.0

    def rule_applicable_condition_allowance(self, payslip):
        """
        @Author: Bhavesh Jadav TechUltra Solutions Pvt. Ltd.
        @Date:02/12/2020
        @Func:this method use for the check advance rule applicable for that employee or not
        @return: true or false
        """
        date_from_month = payslip.date_from.strftime("%m")
        date_to_month = payslip.date_to.strftime("%m")
        date_from_year = payslip.date_from.strftime("%Y")
        if date_from_month == date_to_month:
            employee_id = self.env['hr.employee'].browse(payslip.employee_id)
            record = employee_id.advance_salary_history_ids.filtered(
                lambda line: line.request_month == str(int(date_from_month) + 1) and line.request_year == str(
                    date_from_year))
            if record:
                return True
            else:
                return False
        else:
            return False

    def rule_applicable_condition_deduction(self, payslip):
        """
        @Author:Bhavesh Jadav TechUltra Solutions Pvt. Ltd.
        @Date:02/12/2020
        @Func:this method use for the check advance rule applicable for that employee or not
        @return: true or false
        """
        date_from_month = payslip.date_from.strftime("%m")
        date_to_month = payslip.date_to.strftime("%m")
        date_from_year = payslip.date_from.strftime("%Y")
        if date_from_month == date_to_month:
            employee_id = self.env['hr.employee'].browse(payslip.employee_id)
            record = employee_id.advance_salary_history_ids.filtered(
                lambda line: line.request_month == date_from_month and line.request_year == line.request_year == str(
                    str(date_from_year)))
            if record:
                return True
            else:
                return False
        else:
            return False

    def get_advance_salary_amount_deduction(self, payslip):
        """
        @Author:Bhavesh Jadav TechUltra Solutions Pvt. Ltd.
        @Date:02/12/2020
        @Func:this method use for deduction advance salary amount payslip
        @return: advance salary amount
        """
        date_from_month = payslip.date_from.strftime("%m")
        date_from_year = payslip.date_from.strftime("%Y")
        employee_id = self.env['hr.employee'].browse(payslip.employee_id)
        advance_salary_line = employee_id.advance_salary_history_ids.filtered(
            lambda line: line.request_month == date_from_month and line.request_year == str(date_from_year))
        if advance_salary_line:
            return - round(advance_salary_line.request_amount, 2)
        else:
            return 0.0
