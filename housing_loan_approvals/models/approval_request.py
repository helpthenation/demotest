from odoo import fields, models, api, _
from odoo.exceptions import Warning
import calendar
from dateutil.relativedelta import relativedelta
from datetime import datetime


class ApprovalRequest(models.Model):
    _inherit = 'approval.request'

    housing_loan_request = fields.One2many(
        comodel_name='housing.loan',
        inverse_name='related_approval_hl',
        string='Housing Loan',
        required=False)
    previous_history_ids = fields.One2many('housing.loan', 'related_approval_hl', string='Previous History')
    can_create_housing_loan = fields.Boolean('Create Housing Loan', compute='_compute_create_housing_loan',
                                             default=False,
                                             store=True)
    e_name = fields.Many2one('hr.employee', string="Employee Name")
    employee_id = fields.Char(related='e_name.company_employee_id', string="Employee Id")
    job_title_id = fields.Many2one(related='e_name.contract_id.job_title', string="Job Title")
    department_id = fields.Many2one(related='e_name.department_id', string="Dept/Section")
    grade_id = fields.Many2one(related='e_name.contract_id.job_grade', string="Grade")
    date_of_join = fields.Date(related='e_name.contract_id.date_start', string="Date of joining")
    monthly_housing_allowance = fields.Float(string="Monthly Housing Allowance", compute='_compute_allowance')
    yearly_housing_allowance = fields.Float(string="Yearly Housing Allowance")

    loan_amount = fields.Float(string='Loan Amount')
    mode_of_payment = fields.Selection(
        [('Cheque', 'Cheque'), ('Bank Transfer to Salary Account', 'Bank Transfer to Salary Account')],
        string="Mode of Payment")
    remarks = fields.Char(string="Remarks")
    currency_id = fields.Many2one('res.currency', 'Currency', default=lambda x: x.env.company.currency_id)
    rental_period = fields.Selection([('1 year', '1 year')],
                                     string='Rental period', default='1 year')

    tenancy_contract = fields.Selection([('Renewal of contract', 'Renewal of contract'),
                                         ('Renting a new accommodation', 'Renting a new accommodation')],
                                        string='Tenancy Type')
    rental_amount = fields.Float(string='Rental Amount')
    tenancy_contract_start_date = fields.Date(string='Start Date')
    tenancy_contract_end_date = fields.Date(string='End Date')

    emirate_id = fields.Many2one('res.country.state', string='Emirate', domain="[('city_code', '=', 'AE')]")
    town = fields.Char(string='Town')
    street = fields.Char(string="Street")
    build_no = fields.Char(string='Building')
    flat_vila_no = fields.Char(string='Flat/Villa No')
    tel_no = fields.Char(string='Tel. No')
    mobile_no = fields.Char(string='Mobile No')

    # signature = fields.Char(string='Signature')
    # sign_date = fields.Date(string='Date', default=fields.Date.today)

    utility_filename = fields.Char()
    tenancy_filename = fields.Char()
    security_filename = fields.Char()

    utility_bill = fields.Binary(string='Utility Bill', required=1, help='New Utility Bill under your name')
    tenancy_contract_file = fields.Binary(string="Tenancy Contract", required=1)
    security_cheque = fields.Binary(string="Security Cheque 'without date'", required=1,
                                    help='Security Cheque “without date”')
    effective_month_housing = fields.Selection(
        [('1', 'January'), ('2', 'February'), ('3', 'March'), ('4', 'April'), ('5', 'May'), ('6', 'June'),
         ('7', 'July'), ('8', 'August'), ('9', 'September'), ('10', 'October'), ('11', 'November'),
         ('12', 'December')], string='Effective Month')

    # Payment Plans
    payment_plans_ids = fields.One2many('payment.plans', 'approval_request_id', string='Payment Plans')

    # Bank Info
    hr_current_account_number = fields.Char(string='Current Account Number',
                                            readonly=True)
    hr_current_bank_name = fields.Many2one('res.bank', string='Current Bank Name', readonly=True)
    hr_current_iban = fields.Char(string="Current IBAN NO.", readonly=True)
    agree_check = fields.Boolean(default=False)
    agree_repayment_plan = fields.Boolean(string="confirm the repayment plan")

    def action_approve(self, approver=None):
        res = super(ApprovalRequest, self).action_approve(approver=approver)
        if self.is_housing_loan_request == 'yes' and self.request_status == 'approved':
            self.create_housing_loan()
        return res

    @api.onchange('effective_month_housing', 'effective_year_housing')
    def _onchange_check_month_housing(self):
        if self.effective_month_housing:
            month = datetime.now().month
            year = datetime.now().year
            if month > int(self.effective_month_housing) and year == int(self.effective_year_housing):
                raise Warning("You can't choose past month")

    @api.onchange('e_name')
    def _onchange_get_bank_info(self):
        for employee in self:
            if employee.is_housing_loan_request == 'yes':
                employee.name = str(employee.category_id.name) + " - " + str(
                    employee.e_name.name or '') + " - " + str(employee.e_name.company_employee_id or '')

        employee_id = self.env['hr.employee'].search([('id', '=', self.e_name.id)], limit=1)
        if employee_id:
            self.hr_current_bank_name = employee_id.current_bank_name.id or ''
            self.hr_current_iban = employee_id.iban or ''
            self.hr_current_account_number = employee_id.current_account_number or ''
        else:
            self.hr_current_account_number = ''
            self.hr_current_iban = ''

    @api.onchange('e_name')
    def _onchange_previous_history(self):
        if self:
            self.previous_history_ids = [(6, 0, [])]
            previous_loan_ids = self.env['housing.loan'].search(
                [('employee_name', '=', self.e_name.id)])
            if previous_loan_ids:
                self.previous_history_ids = previous_loan_ids

    @api.model
    def year_selection(self):
        year = datetime.now().year
        last_year = datetime.now().year + 10
        year_list = []
        while year != last_year:
            year_list.append((str(year), str(year)))
            year += 1
        return year_list

    effective_year_housing = fields.Selection(year_selection, string="Year", default=str(datetime.now().year))

    @api.depends('request_status', 'is_housing_loan_request')
    def _compute_create_housing_loan(self):
        for rec in self:
            resign = rec.env['housing.loan'].search([('related_approval_hl', '=', rec.id)])
            if rec.request_status == 'approved' and rec.is_housing_loan_request == 'yes' and not resign:
                rec.can_create_housing_loan = True
            else:
                rec.can_create_housing_loan = False

    @api.onchange('monthly_housing_allowance')
    def onchange_yearly_allowance(self):
        self.yearly_housing_allowance = self.monthly_housing_allowance * 12

    @api.onchange('request_owner_id')
    def onchange_employee_housing(self):
        """
        Author:Bhavesh Jadav TechUltra solutions
        Date:  17/09/2020
        Func: for apply dynamic domain
        :return: domain
        """
        if self.env.user.employee_id:
            self.e_name = self.env.user.employee_id.id
            return {'domain': {'e_name': [('id', '=', self.env.user.employee_id.id)]}}
        else:
            return {'domain': {'e_name': [('id', 'in', [-1])]}}

    @api.onchange('tenancy_contract_end_date')
    def onchange_date_restriction(self):
        if self.tenancy_contract_start_date and self.tenancy_contract_end_date:
            if self.tenancy_contract_start_date > self.tenancy_contract_end_date:
                raise Warning('End date must be greater then start date')

    @api.depends('e_name')
    def _compute_allowance(self):
        if self.e_name:
            if self.e_name.contract_id:
                if self.e_name.contract_id.related_compensation:
                    allowance = self.e_name.contract_id.mapped('related_compensation').filtered(
                        lambda description: description.component_description == 'Housing Allowance')
                    if allowance:
                        self.monthly_housing_allowance = allowance.amount
                else:
                    self.monthly_housing_allowance = '0.0'
            else:
                self.monthly_housing_allowance = '0.0'
        else:
            self.monthly_housing_allowance = '0.0'

    # related fields
    is_housing_loan_request = fields.Selection(related="category_id.is_housing_loan_request")
    has_e_name = fields.Selection(related="category_id.has_e_name")
    has_employee_id = fields.Selection(related="category_id.has_employee_id")
    has_job_title_id = fields.Selection(related="category_id.has_job_title_id")
    has_department_id = fields.Selection(related="category_id.has_department_id")
    has_grade_id = fields.Selection(related="category_id.has_grade_id")
    has_date_of_join = fields.Selection(related="category_id.has_date_of_join")
    has_monthly_housing_allowance = fields.Selection(related="category_id.has_monthly_housing_allowance")
    has_yearly_housing_allowance = fields.Selection(related="category_id.has_yearly_housing_allowance")
    has_loan_amount = fields.Selection(related="category_id.has_loan_amount")
    has_mode_of_payment = fields.Selection(related="category_id.has_mode_of_payment")
    has_remarks = fields.Selection(related="category_id.has_remarks")
    has_currency_id = fields.Selection(related="category_id.has_currency_id")
    has_rental_period = fields.Selection(related="category_id.has_rental_period")

    has_tenancy_contract = fields.Selection(related="category_id.has_tenancy_contract")
    has_rental_amount = fields.Selection(related="category_id.has_rental_amount")
    has_tenancy_contract_start_date = fields.Selection(related="category_id.has_tenancy_contract_start_date")
    has_tenancy_contract_end_date = fields.Selection(related="category_id.has_tenancy_contract_end_date")

    has_emirate_id = fields.Selection(related="category_id.has_emirate_id")
    has_town = fields.Selection(related="category_id.has_town")
    has_street = fields.Selection(related="category_id.has_street")
    has_build_no = fields.Selection(related="category_id.has_build_no")
    has_flat_vila_no = fields.Selection(related="category_id.has_flat_vila_no")
    has_tel_no = fields.Selection(related="category_id.has_tel_no")
    has_mobile_no = fields.Selection(related="category_id.has_mobile_no")

    # has_signature = fields.Selection(related="category_id.has_signature")
    # has_sign_date = fields.Selection(related="category_id.has_sign_date")

    has_utility_bill = fields.Selection(related="category_id.has_utility_bill")
    has_tenancy_contract_file = fields.Selection(related="category_id.has_tenancy_contract_file")
    has_security_cheque = fields.Selection(related="category_id.has_security_cheque")
    has_housing_effective_month_year = fields.Selection(related="category_id.has_housing_effective_month_year",
                                                        string='Loan Deduction Start Month')

    def create_housing_loan(self):
        """
            Author:Nimesh Jadav TechUltra solutions
            Date:  07/10/2020
            Func: Create record into the housing history
        """
        month = dict(self._fields['effective_month_housing'].selection).get(self.effective_month_housing)
        housing_history = self.env['housing.loan']
        bank_name_id = self.hr_current_bank_name and self.hr_current_bank_name.id
        housing_history_val = {'employee_name': self.e_name.id or '',
                               'employee_id': self.employee_id or '',
                               'job_title_id': self.job_title_id.id or '',
                               'department_id': self.department_id.id or '',
                               'grade_id': self.grade_id.id or '',
                               'date_of_join': self.date_of_join or '',
                               'monthly_housing_allowance': self.monthly_housing_allowance or '',
                               'yearly_housing_allowance': self.yearly_housing_allowance or '',
                               'effective_month_year': (month if month else '') + "  " + self.effective_year_housing,
                               'loan_amount': self.loan_amount or '',
                               'mode_of_payment': self.mode_of_payment or '',
                               'remarks': self.remarks or '',
                               'rental_period': self.rental_period or '',
                               'tenancy_contract': self.tenancy_contract or '',
                               'rental_amount': self.rental_amount or '',
                               'tenancy_contract_start_date': self.tenancy_contract_start_date or '',
                               'tenancy_contract_end_date': self.tenancy_contract_end_date or '',
                               'emirate_id': self.emirate_id.id or '',
                               'current_bank_name': bank_name_id or '',
                               'current_account_number': self.hr_current_account_number or '',
                               'current_iban': self.hr_current_iban or '',
                               'town': self.town or '',
                               'street': self.street or '',
                               'build_no': self.build_no or '',
                               'flat_vila_no': self.flat_vila_no or '',
                               'tel_no': self.tel_no or '',
                               'mobile_no': self.mobile_no or '',
                               # 'signature': self.signature or '',
                               # 'sign_date': self.sign_date or '',
                               'utility_bill': self.utility_bill or '',
                               'tenancy_contract_file': self.tenancy_contract_file or '',
                               'security_cheque': self.security_cheque or ''
                               }
        housing_request = housing_history.create(housing_history_val)
        if housing_request:
            self.housing_loan_request = housing_request
            repayment_plan_id = self.env['payment.plans'].search([('approval_request_id', '=', self.id)])
            for repayment in repayment_plan_id:
                repayment.write({'housing_loan_history_id': housing_request.id})
        return True

    def create_repayment(self):

        """
        Create record for the All Payment Plans
        :return: record set of the payment plan
        """

        payment_plan_obj = self.env['payment.plans']
        repayment_plans = payment_plan_obj.search([('approval_request_id', '=', self.id)])
        for repayment in repayment_plans:
            repayment.sudo().unlink()
        tag = 1
        loan_balance = payment = self.loan_amount
        date = self.tenancy_contract_start_date
        start_dt = self.tenancy_contract_start_date
        end_dt = self.tenancy_contract_end_date
        # if housing_request.rental_period == '1 year':
        #     plans = 13
        #     loan_replayment = housing_request.loan_amount / 12
        # elif housing_request.rental_period == "6 months":
        #     plans = 7
        #     loan_replayment = housing_request.loan_amount / 6
        # else:
        #     plans = 1
        #     loan_replayment = housing_request.loan_amount
        # r = relativedelta(housing_request.tenancy_contract_end_date,
        #                   housing_request.tenancy_contract_start_date)
        # months = r.months
        # year = r.years
        # if year >= 1:
        #     months += 12 * year
        if start_dt.year == end_dt.year:
            plans = (end_dt.month - start_dt.month) + 1
        else:
            start_months = (12 - start_dt.month) + 2
            end_months = end_dt.month
            year = (end_dt.year - start_dt.year) - 1
            plans = start_months + end_months + (12 * year)
        loan_replayment = self.loan_amount / (plans - 1)
        payment_plan_id = []
        for plan in range(plans):
            if tag == 1:
                start_date = str(date.year) + "-" + str(date.month) + "-" + "1"
                month = date.month
                year = date.year
                end_date = str(date.year) + "-" + str(date.month) + "-" + str(calendar.mdays[month])
                repayment = 0.0 if plans >= 1 else loan_replayment
                tag = 2
            else:
                repayment = loan_replayment
                if tag == 2:
                    date = date
                    tag = 3
                elif tag == 3:
                    date = date + relativedelta(months=1)
                month = date.month
                year = date.year
                start_date = str(year) + "-" + str(month) + "-" + "1"
                end_date = str(year) + "-" + str(month) + "-" + str(calendar.mdays[month])

            plans_val = {'approval_request_id': self.id,
                         'pay_year': year,
                         'pay_month': month,
                         'start_date': start_date,
                         'end_date': end_date,
                         'loan_balance': loan_balance,
                         'payment': payment,
                         'loan_repayment': repayment,
                         'reg_repayment': repayment}
            payment = 0.0
            loan_balance -= loan_replayment
            payment_plan_obj.create(plans_val)

        return True

    def action_confirm(self):

        if self.category_id.is_housing_loan_request == 'yes':
            # old_request = self.env['approval.request'].search(
            #     [('e_name', '=', self.e_name.id),
            #      ('loan_amount', '=', self.loan_amount),
            #      ('request_status', 'in', ('approved', 'pending', 'under_approval'))])

            # if len(old_request) > 0:
            #     raise Warning(_("You already have Same Request Submitted or Approved"))

            bank_change_ids = self.env['approval.request'].search(
                [('is_bank_changes_request', '=', 'yes'), ('employee_name', '=', self.e_name.id),
                 ('request_status', 'in', ['pending', 'under_approval'])])

            if bank_change_ids and self.mode_of_payment == 'Bank Transfer to Salary Account':
                raise Warning(_("You Can't submit request until your pending Bank Change request is Approved"))
            if not self.agree_check:
                raise Warning(_("Please mark as true, 'I hereby agree...'"))
            if not self.agree_repayment_plan:
                raise Warning(_("Please mark as true, 'Confirm the repayment plan'"))
            if self.loan_amount <= 0 and self.rental_amount <= 0:
                raise Warning(_("You cannot submit a request with the amount equal to 0"))
            if len(self.payment_plans_ids) == 0:
                raise Warning(_("You should compute the repayment plan before you submit request"))

            contract = self.env['hr.contract'].search([('employee_id', '=', self.employee_name.id)])
            # amount = 0
            # if contract:
            #     for compensation in contract.related_compensation:
            #         if compensation.code == '1001':
            #             amount = compensation.amount
            #             amount = amount * 12
            if self.yearly_housing_allowance <= self.loan_amount:
                raise Warning(_("You can't request loan amount more then yearly housing allowance"))
            # if self.rental_amount * 12 <= self.loan_amount:
            #     raise Warning(_("You can't request loan amount more then housing rental amount"))
        res = super(ApprovalRequest, self).action_confirm()
        return res

    def action_print_housing_loan_report(self):
        """
        :Author:Nimesh Jadav TechUltra solutions
        :Date:08/10/2020
        :Func:This method use to download housing loan report
        :Return:Report action xml id
        """
        return self.env.ref('housing_loan_approvals.report_housing_loan').report_action(self)
