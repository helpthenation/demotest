# -*- coding: utf-8 -*-
from odoo import models, api


class HrPayslip(models.Model):
    _inherit = 'hr.payslip'

    def remain_leaves_for_encash_rule_applicable_condition(self, payslip):
        date_from_month = payslip.date_from.strftime("%m")
        date_to_month = payslip.date_to.strftime("%m")
        if date_from_month == date_to_month:
            end_of_service_record = self.env['end.of.service'].search_read(
                [('employee_id', '=', payslip.employee_id), ('last_working_month_for_payslip', '=', date_to_month),
                 ('request_status', '=', 'approved')], ['id'])
            if end_of_service_record:
                return True
            else:
                return False
        else:
            return False

    def get_remain_leaves_encashment_amount(self, payslip):
        date_to_month = payslip.date_to.strftime("%m")
        end_of_service_record = self.env['end.of.service'].search(
            [('employee_id', '=', payslip.employee_id), ('last_working_month_for_payslip', '=', date_to_month),
             ('request_status', '=', 'approved')])
        if end_of_service_record:
            leaves_encashment_amount = end_of_service_record.leave_encashment
        return round(leaves_encashment_amount, 2)

    def notice_pay_rule_applicable_condition_allowance(self, payslip):
        date_from_month = payslip.date_from.strftime("%m")
        date_to_month = payslip.date_to.strftime("%m")
        if date_from_month == date_to_month:
            end_of_service_record = self.env['end.of.service'].search_read(
                [('employee_id', '=', payslip.employee_id), ('last_working_month_for_payslip', '=', date_to_month),
                 ('request_status', '=', 'approved')], ['id'])
            if end_of_service_record:
                return True
            else:
                return False
        else:
            return False

    def get_eos_notice_pay_amount_allowance(self, payslip):
        notice_pay_amount = 0.0
        date_to_month = payslip.date_to.strftime("%m")
        end_of_service_record = self.env['end.of.service'].search(
            [('employee_id', '=', payslip.employee_id), ('last_working_month_for_payslip', '=', date_to_month),
             ('request_status', '=', 'approved')])
        if end_of_service_record:
            notice_pay_amount = end_of_service_record.notice_pay_amount
        return round(notice_pay_amount)

    def gratuity_pay_rule_applicable_condition_allowance(self, payslip):
        date_from_month = payslip.date_from.strftime("%m")
        date_to_month = payslip.date_to.strftime("%m")
        if date_from_month == date_to_month:
            end_of_service_record = self.env['end.of.service'].search_read(
                [('employee_id', '=', payslip.employee_id), ('last_working_month_for_payslip', '=', date_to_month),
                 ('request_status', '=', 'approved')], ['id'])
            if end_of_service_record:
                return True
            else:
                return False
        else:
            return False

    def get_eos_gratuity_pay_amount_allowance(self, payslip):
        gratuity_pay_amount = 0.0
        date_to_month = payslip.date_to.strftime("%m")
        end_of_service_record = self.env['end.of.service'].search(
            [('employee_id', '=', payslip.employee_id), ('last_working_month_for_payslip', '=', date_to_month),
             ('request_status', '=', 'approved')])
        if end_of_service_record:
            gratuity_pay_amount = end_of_service_record.gratuity_payments_amount
        return round(gratuity_pay_amount)
