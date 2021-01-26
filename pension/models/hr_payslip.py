# -*- coding: utf-8 -*-
from odoo import models, api


class HrPayslip(models.Model):
    _inherit = 'hr.payslip'

    def get_pension(self, contract):
        """
        This method will calculate pension for the different country and different employment types
        :param contract: contract id of the employee
        :return: pension amount
        Nimesh Jadav : 11 Nov 2020
        """
        total_amount = 0.0
        if contract.employment_status != "contractor":
            pension_rule = self.env['pension.rule'].search([('country_id', '=', contract.employee_id.country_id.id), (
                'contract_subgroups_id', '=', contract.contract_subgroup.id)], limit=1)
            for line in pension_rule.lines_ids.filtered(lambda pl: pl.share == 'employee'):
                rec = contract.related_compensation.filtered(lambda c: c.code == line.component.code)
                if rec:
                    amount = ((rec.amount / 100) * line.component_percentage / 100) * line.percentage
                    total_amount += amount
                elif line.detail == "fixed_amount":
                    total_amount += line.fixed_amount
                elif line.detail == "total_salary":
                    amount = ((contract.wage / 100) * line.component_percentage / 100) * line.percentage
                    total_amount += amount
            return - round(total_amount, 2)

    @api.model
    def get_basic(self, contract):
        """
            This method will use to calculate basic for the pension report
            :param contract: contract id
            :return: basic amount
            Nimesh Jadav : 11 Nov 2020
        """

        if contract.related_compensation:
            for line in contract.related_compensation:
                if line.code == '1000':
                    return round(line.amount, 2)

    @api.model
    def get_housing(self, contract):
        """
            This method will use to calculate housing for the pension report
            :param contract: contract id
            :return: company amount
            Nimesh Jadav : 11 Nov 2020
        """
        if contract.related_compensation:
            for line in contract.related_compensation:
                if line.code == '1001':
                    return round(line.amount, 2) if contract.employee_id.country_id.code != 'OM' else round(
                        (line.amount / 100) * 75, 2)

    @api.model
    def get_company_share(self, contract):
        """
            This method will use to calculate company share for the pension report
            :param contract: contract id
            :return: housing amount
            Nimesh Jadav : 11 Nov 2020
        """
        total_amount = 0.0
        if contract.employment_status != "contractor":
            pension_rule = self.env['pension.rule'].search([('country_id', '=', contract.employee_id.country_id.id), (
                'contract_subgroups_id', '=', contract.contract_subgroup.id)], limit=1)
            for line in pension_rule.lines_ids.filtered(lambda pl: pl.share == 'company'):
                rec = contract.related_compensation.filtered(lambda c: c.code == line.component.code)
                if rec:
                    amount = ((rec.amount / 100) * line.component_percentage / 100) * line.percentage
                    total_amount += amount
                elif line.detail == "fixed_amount":
                    total_amount += line.fixed_amount
                elif line.detail == "total_salary":
                    amount = ((contract.wage / 100) * line.component_percentage / 100) * line.percentage
                    total_amount += amount

        return round(total_amount, 2)

    @api.model
    def get_total_contribution(self, contract):
        """
            This method will use to calculate housing for the pension report
            :param contract: contract id
            :return: company amount
            Nimesh Jadav : 11 Nov 2020
        """
        amount = self.get_pension(contract)
        amount = amount * -1
        amount += self.get_company_share(contract)
        return round(amount, 2)
