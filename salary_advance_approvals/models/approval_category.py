from odoo import models, fields, api, _

CATEGORY_SELECTION = [
    ('required', 'Required'),
    ('optional', 'Optional'),
    ('no', 'None')]


class ApprovalCategory(models.Model):
    _inherit = 'approval.category'

    is_salary_advance = fields.Selection([
        ('yes', 'Yes'),
        ('no', 'No')], string="Is Salary Advance", default="no", required=True)

    has_employee = fields.Selection(CATEGORY_SELECTION, string="Employee", default="no", required=True)
    has_system_id = fields.Selection(CATEGORY_SELECTION, string="System ID", default="no", required=True)
    has_job_title_sl = fields.Selection(CATEGORY_SELECTION, string="Job Title", default="no", required=True)
    has_job_grade = fields.Selection(CATEGORY_SELECTION, string="Job Grade", default="no", required=True)
    has_total_monthly_salary = fields.Selection(CATEGORY_SELECTION, string="Total Monthly Salary", default="no",
                                                required=True)
    has_request_year = fields.Selection(CATEGORY_SELECTION, string="Request Year", default="no",
                                        required=True)
    has_request_month = fields.Selection(CATEGORY_SELECTION, string="Request Month", default="no",
                                         required=True)
    has_request_amount = fields.Selection(CATEGORY_SELECTION, string="Request Amount", default="no",
                                          required=True)
    has_salary_advance_reason = fields.Selection(CATEGORY_SELECTION, string="Request Reason", default="no",
                                                 required=True)
    has_salary_advance_ref = fields.Selection(CATEGORY_SELECTION, string="Reference Number", default="no",
                                              required=True)

    # has_approved_amount = fields.Selection(CATEGORY_SELECTION, string="Approved Amount", default="no",
    #                                        required=True)
    # has_approved_month = fields.Selection(CATEGORY_SELECTION, string="Approved Month", default="no",
    #                                       required=True)
    # has_approved_year = fields.Selection(CATEGORY_SELECTION, string="Approved Year", default="no",
    #                                      required=True)
    # has_company_id = fields.Selection(CATEGORY_SELECTION, string="Company", default="no",
    #                                   required=True)
