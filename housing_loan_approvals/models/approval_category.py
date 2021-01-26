# -*- coding: utf-8 -*-

from odoo import models, fields, api, _

CATEGORY_SELECTION = [
    ('required', 'Required'),
    ('optional', 'Optional'),
    ('no', 'None')]


class ApprovalCategory(models.Model):
    _inherit = 'approval.category'

    is_housing_loan_request = fields.Selection([
        ('yes', 'Yes'),
        ('no', 'No')], string="Is Housing Loan Request", default="no", required=True)

    has_e_name = fields.Selection(CATEGORY_SELECTION, string="Employee Name", default="no", required=True)
    has_employee_id = fields.Selection(CATEGORY_SELECTION, string="Employee Id", default="no", required=True)
    has_job_title_id = fields.Selection(CATEGORY_SELECTION, string="Job Title", default="no", required=True)
    has_department_id = fields.Selection(CATEGORY_SELECTION, string="Dept/Section", default="no", required=True)
    has_grade_id = fields.Selection(CATEGORY_SELECTION, string="Grade", default="no", required=True)
    has_date_of_join = fields.Selection(CATEGORY_SELECTION, string="Date of Joining", default="no", required=True)
    has_monthly_housing_allowance = fields.Selection(CATEGORY_SELECTION, string="Monthly housing Allowance",
                                                     default="no", required=True)
    has_yearly_housing_allowance = fields.Selection(CATEGORY_SELECTION, string="Yearly housing Allowance",
                                                    default="no", required=True)
    has_loan_amount = fields.Selection(CATEGORY_SELECTION, string="Loan Amount", default="no", required=True)
    has_mode_of_payment = fields.Selection(CATEGORY_SELECTION, string="Mode of Payment", default="no", required=True)
    has_remarks = fields.Selection(CATEGORY_SELECTION, string="Remarks", default="no", required=True)
    has_currency_id = fields.Selection(CATEGORY_SELECTION, string="Currency", default="no", required=True)
    has_rental_period = fields.Selection(CATEGORY_SELECTION, string="Rental Period", default="no", required=True)

    has_tenancy_contract = fields.Selection(CATEGORY_SELECTION, string="Tenancy Contract", default="no", required=True)
    has_rental_amount = fields.Selection(CATEGORY_SELECTION, string="Rental Amount", default="no", required=True)
    has_tenancy_contract_start_date = fields.Selection(CATEGORY_SELECTION, string="Start Date", default="no",
                                                       required=True)
    has_tenancy_contract_end_date = fields.Selection(CATEGORY_SELECTION, string="End Date", default="no", required=True)

    has_emirate_id = fields.Selection(CATEGORY_SELECTION, string="Emirate", default="no", required=True)
    has_town = fields.Selection(CATEGORY_SELECTION, string="Town", default="no", required=True)
    has_street = fields.Selection(CATEGORY_SELECTION, string="Street", default="no", required=True)
    has_build_no = fields.Selection(CATEGORY_SELECTION, string="Building/No", default="no", required=True)
    has_flat_vila_no = fields.Selection(CATEGORY_SELECTION, string="Flat/Villa No", default="no", required=True)
    has_tel_no = fields.Selection(CATEGORY_SELECTION, string="Tel.No", default="no", required=True)
    has_mobile_no = fields.Selection(CATEGORY_SELECTION, string="Mobile Number", default="no", required=True)

    # has_signature = fields.Selection(CATEGORY_SELECTION, string="Signature", default="no", required=True)
    # has_sign_date = fields.Selection(CATEGORY_SELECTION, string="Date", default="no", required=True)

    has_utility_bill = fields.Selection(CATEGORY_SELECTION, string="Utility Bill", default="no", required=True)
    has_tenancy_contract_file = fields.Selection(CATEGORY_SELECTION, string="Tenancy Contract", default="no",
                                                 required=True)
    has_security_cheque = fields.Selection(CATEGORY_SELECTION, string="Security Cheque", default="no", required=True)
    has_my_company = fields.Selection(CATEGORY_SELECTION, string="My Company", default="no", required=True)
    has_housing_effective_month_year = fields.Selection(CATEGORY_SELECTION, string="Effective Month/Year", default="no",
                                                        required=True)
