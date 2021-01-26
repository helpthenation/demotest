from odoo import fields, models, api, _
from odoo.exceptions import UserError, ValidationError
from datetime import datetime as datetime
from dateutil.relativedelta import relativedelta

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


class ApprovalRequest(models.Model):
    _inherit = 'approval.request'

    # History fields
    can_create_advance_salary_history = fields.Boolean('Can Create Advance Salary History',
                                                       compute='_compute_create_advance_salary_history',
                                                       default=False,
                                                       store=True)

    advance_salary_history_ids = fields.One2many('advance.salary.history', inverse_name='advance_salary_request_id',
                                                 string='Advance Salary History', required=False)

    # Related fields
    is_salary_advance = fields.Selection(related='category_id.is_salary_advance')
    has_employee = fields.Selection(related='category_id.has_employee')
    has_system_id = fields.Selection(related='category_id.has_system_id')
    has_job_title_sl = fields.Selection(related='category_id.has_job_title_sl')
    has_job_grade = fields.Selection(related='category_id.has_job_grade')
    has_total_monthly_salary = fields.Selection(related='category_id.has_total_monthly_salary')
    has_request_year = fields.Selection(related='category_id.has_request_year')
    has_request_month = fields.Selection(related='category_id.has_request_month')
    has_request_amount = fields.Selection(related='category_id.has_request_amount')
    has_salary_advance_reason = fields.Selection(related='category_id.has_salary_advance_reason')
    has_salary_advance_ref = fields.Selection(related='category_id.has_salary_advance_ref')
    # has_approved_amount = fields.Selection(related='category_id.has_approved_amount')
    # has_approved_month = fields.Selection(related='category_id.has_approved_month')
    # has_approved_year = fields.Selection(related='category_id.has_approved_year')
    # has_company_id = fields.Selection(related='category_id.has_company_id')

    # Model fields
    salary_employee_id = fields.Many2one('hr.employee', string="Employee")
    system_id = fields.Char(related='salary_employee_id.system_id', string="Employee ID")
    job_title_sl = fields.Many2one(related='salary_employee_id.contract_id.job_title')
    job_grade = fields.Many2one(related='salary_employee_id.contract_id.job_grade')
    total_monthly_salary = fields.Monetary(string="Total Monthly Salary", currency_field='currency_id',
                                           compute='_compute_total_monthly_salary',
                                           store=True)
    request_year = fields.Selection(string="Year", selection=Year_Selection_Value,
                                    default=datetime.today().strftime("%Y"))
    request_month = fields.Selection(string='Request Month', selection=Month_Selection_Value,
                                     default=datetime.today().strftime("%m"))
    request_amount = fields.Monetary(string="Enter Advance Salary Amount", currency_field='currency_id')
    salary_advance_reason = fields.Text(string="Request Reason")
    currency_id = fields.Many2one('res.currency', string='Currency',
                                  default=lambda x: x.env.company.currency_id)
    salary_advance_ref = fields.Char(string="Reference Number")
    company_id = fields.Many2one('res.company', string='Company', required=True,
                                 default=lambda self: self.env.company)
    # approved_amount = fields.Monetary(string="Approved Amount", currency_field='currency_id')
    # approved_month = fields.Selection(string='Approved Month', selection=Month_Selection_Value)
    # approved_year = fields.Selection(string='Approved Year', selection=Year_Selection_Value)
    recovery_month = fields.Selection(related='request_month')

    # @api.depends('request_month')
    # def _compute_recovery_month(self):
    #     """
    #     @Author:Bhavesh Jadav TechUltra Solutions
    #     @Date: 14/12/2020
    #     @Func: Add recovery_month base on the request_month
    #     @Return:M/A
    #     """
    #     for rec in self:
    #         if rec.request_month:
    #             if self.request_month == '12':
    #                 rec.recovery_month = '01'
    #             else:
    #                 rec.recovery_month = str(int(self.request_month) + 1).zfill(2)

    @api.onchange('salary_employee_id')
    def onchange_request_name_subject(self):
        """
        :Author:Bhavesh Jadav TechUltra Solutions
        :Date:26/11/2020
        :Func:this method use for the add name with with company id
        :Return:list with name and company id
        """
        for request in self:
            if request.is_salary_advance == 'yes':
                request.name = str(request.category_id.name) + " - " + str(
                    request.salary_employee_id.name or '') + " - " + str(request.salary_employee_id.company_employee_id or '')

    @api.onchange('request_owner_id')
    def onchange_employee_advance(self):
        """
        Author:Bhavesh Jadav TechUltra solutions
        Date:  17/09/2020
        Func: for apply dynamic domain
        :return: domain
        """
        if self.env.user.employee_id:
            self.salary_employee_id = self.env.user.employee_id.id
            return {'domain': {'salary_employee_id': [('id', '=', self.env.user.employee_id.id)]}}
        else:
            # if the login user are not employee and the is in employee group then its blank
            return {'domain': {'salary_employee_id': [('id', 'in', [-1])]}}

    @api.depends('salary_employee_id')
    def _compute_total_monthly_salary(self):
        """
        :Author:Bhavesh Jadav TechUltra solutions
        :Date: 01/10/2020
        :Func:this method use for the set total monthly salary from the  contract wage
        :Return:N/A
        """
        for rec in self:
            total_monthly_salary = rec.salary_employee_id and rec.salary_employee_id.contract_id and rec.salary_employee_id.contract_id.wage or 0.0
            rec.total_monthly_salary = total_monthly_salary

    @api.onchange('salary_employee_id')
    def _get_default_salary(self):
        """
        :Author:Bhavesh Jadav TechUltra solutions
        :Date:01/10/2020
        :Func:this method use for the set the default request amount from the  contract wage
        :Return:N/A
        """
        for record in self:
            record.request_amount = record.salary_employee_id and record.salary_employee_id.contract_id.wage or 0.0

    # @api.onchange('request_amount')
    # def _get_approved_amount(self):
    #     """
    #     :Author:Bhavesh Jadav TechUltra solutions
    #     :Date:01/10/2020
    #     :Func:this method use for the set the approved amount from request amount
    #     :Return:N/A
    #     """
    #     for record in self:
    #         record.approved_amount = record.request_amount or 0.0

    # @api.onchange('request_month')
    # def _get_approved_month(self):
    #     """
    #     :Author:Bhavesh Jadav TechUltra solutions
    #     :Date:01/10/2020
    #     :Func:this method use for the set the approved month  from request month
    #     :Return:N/A
    #     """
    #     for record in self:
    #         record.approved_month = record.request_month or False

    # @api.onchange('request_year')
    # def _get_approved_year(self):
    #     """
    #     :Author:Bhavesh Jadav TechUltra solutions
    #     :Date:01/10/2020
    #     :Func:this method use for the set the approved year  from request year
    #     :Return:N/A
    #     """
    #     for record in self:
    #         record.approved_year = record.request_year or False

    def _check_request_day(self, vals):
        """
        :Author:Bhavesh Jadav TechUltra solutions
        :Date:01/10/2020
        :Func:This method use for the check validations base on the salary_advance_settings
        :Return:True/UserError
        """
        month = int(vals.get('request_month'))
        year = int(vals.get('request_year'))
        salary_employee_id = self.env['hr.employee'].browse(vals.get('salary_employee_id'))
        current_day = int(datetime.today().strftime("%d"))
        current_month = int(datetime.today().strftime("%m"))
        current_year = int(datetime.today().strftime("%Y"))
        salary_advance_rules = self.env['salary.advance.settings'].find_advance_salary_rule(
            contract_subgroup=salary_employee_id.contract_id.contract_subgroup)
        if year == current_year or year == current_year + 1:
            if month == current_month and year == current_year or month == current_month + 1 and year == current_year or year == current_year + 1 and month == 1 and current_month == 12:
                if current_month == month and current_day > salary_advance_rules.deadline_month_day:
                    raise UserError(_(
                        "Kindly note you have passed the cutoff date to request from current month you can request "
                        "from next month only"))
                return True
            else:
                raise UserError(_(
                    "Kindly note request from previous/future month is not allowed"))
        else:
            raise UserError(_(
                "Please select proper Year"))

    @api.model
    def create(self, vals):
        """
        :Author:Bhavesh Jadav TechUltra solutions
        :Date:01/10/2020
        :Func:supper call for the check validations
        :Return:Result of supper call or UserError
        """
        if self.category_id.browse(vals.get('category_id')).is_salary_advance == 'yes':
            if vals.get('request_amount') > self.salary_employee_id.browse(
                    vals.get('salary_employee_id')).contract_id.wage:
                raise UserError(_("Your request amount is more then you monthly salary you can not proceed "))
            self._check_request_day(vals=vals)
            # employee_id = self.salary_employee_id.browse(vals.get('salary_employee_id'))
            # name = vals.get('name') + '-' + str(employee_id.system_id) + '-' + str(employee_id.name)
            # vals.update({'name': name})
        res = super(ApprovalRequest, self).create(vals)
        return res

    def write(self, vals):
        """
        :Author:Bhavesh Jadav TechUltra solutions
        :Date: 23/11/2020
        :Func:Add validation for the request because the user can change the value after create
        :Return: result of the supper call
        """
        if self.category_id.is_salary_advance == 'yes':
            if vals.get('request_amount') and vals.get('request_amount') > self.salary_employee_id.contract_id.wage:
                raise UserError(_("Your request amount is more then you monthly salary you can not proceed "))
            if vals.get('request_year') or vals.get('request_month'):
                salary_employee_id = self.salary_employee_id
                current_day = int(datetime.today().strftime("%d"))
                current_month = int(datetime.today().strftime("%m"))
                current_year = int(datetime.today().strftime("%Y"))
                salary_advance_rules = self.env['salary.advance.settings'].find_advance_salary_rule(
                    contract_subgroup=salary_employee_id.contract_id.contract_subgroup)
                if vals.get('request_year'):
                    year = int(vals.get('request_year'))
                else:
                    year = int(self.request_year)
                if vals.get('request_month'):
                    month = int(vals.get('request_month'))
                else:
                    month = int(self.request_month)
                if year == current_year or year == current_year + 1:
                    if month == current_month and year == current_year or month == current_month + 1 and year == current_year or year == current_year + 1 and month == 1 and current_month == 12:
                        if current_month == month and current_day > salary_advance_rules.deadline_month_day:
                            raise UserError(_(
                                "Kindly note you have passed the cutoff date to request from current month you can "
                                "request "
                                "from next month only"))
                        return True
                    else:
                        raise UserError(_(
                            "Kindly note request from previous/future month is not allowed"))
                else:
                    raise UserError(_(
                        "Please select proper Year"))

        res = super(ApprovalRequest, self).write(vals)
        return res

    def _check_previous_request(self):
        """
        :Author:Bhavesh Jadav TechUltra solutions
        :Date:01/10/2020
        :Func:This method use for the check validations base on the salary_advance_settings
        :Return:True/UserError
        """
        domain = [('is_salary_advance', '=', 'yes'), ('category_id', '=', self.category_id.id),
                  ('salary_employee_id', '=', self.salary_employee_id.id),
                  ('request_status', 'in', ['pending', 'under_approval', 'approved']),
                  ('request_year', '=', self.request_year), ('request_month', '=', self.request_month)]
        if self.search_read(domain, ['id']):
            raise UserError(_(
                "Your not allowed to submit request because the request already submitted with the selected month "))
        domain.pop(-1)
        advance_salary_rule = self.env['salary.advance.settings'].find_advance_salary_rule(
            contract_subgroup=self.salary_employee_id.contract_id.contract_subgroup)
        if advance_salary_rule[0].bypass_employee_ids and advance_salary_rule[0].bypass_employee_ids.filtered(
                lambda e: e == self.salary_employee_id):
            return True
        salary_advance_requests = self.search_read(domain, ['id'])
        if salary_advance_requests and advance_salary_rule and advance_salary_rule[
            0].num_of_yearly_request <= len(salary_advance_requests):
            raise UserError(_(
                "Your Advance salary request limit  is over your not allowed to submit request please contact "
                "your higher authority"))
        return True

    def action_confirm(self):
        """
        :Author:Bhavesh Jadav TechUltra solutions
        :Date:01/10/2020
        :Func:supper call for the add reference number on submit and the  check validations base on the salary_advance_settings
        :Return:Result of supper call or UserError
        """
        if self.is_salary_advance == 'yes':
            self._check_previous_request()
            self._check_pending_bank_changes_request()
            salary_ref = self.env['ir.sequence'].next_by_code('salary.advance.auto.ref') or _('New')
            salary_ref = salary_ref + self.system_id
            self.salary_advance_ref = salary_ref
        res = super(ApprovalRequest, self).action_confirm()
        return res

    def _check_pending_bank_changes_request(self):
        """
        :Author:Bhavesh Jadav TechUltra solutions
        :Date: 23/11/2020
        :Func:If the employee have pending bank change request, salary advance should not be allowed to be submitted until the bank change request is approved
        :return: True and warning
        """
        category_id = self.env['approval.category'].search_read([('is_bank_changes_request', '=', 'yes')], ['id'])
        if category_id:
            pending_bank_change_request = self.env['approval.request'].search(
                [('employee_name', '=', self.salary_employee_id.id), ('category_id', '=', category_id[0].get('id')),
                 ('request_status', 'in', ['pending', 'under_approval'])])
            if pending_bank_change_request:
                raise UserError(_(
                    "You can't submit the request until your pending bank change request is approved/rejected."))

        return True

    def action_print_report_salary(self):
        """
        :Author:Bhavesh Jadav TechUltra solutions
        :Date:01/10/2020
        :Func:This method use for teh call report action from the button
        :Return:Report action xml id
        """
        return self.env.ref('salary_advance_approvals.report_salary_advance').report_action(self)

    @api.depends('request_status', 'is_salary_advance')
    def _compute_create_advance_salary_history(self):
        for rec in self:
            advance_salary_id = rec.env['advance.salary.history'].search([('advance_salary_request_id', '=', rec.id)])
            if rec.request_status == 'approved' and rec.is_salary_advance == 'yes' and not advance_salary_id:
                rec.can_create_advance_salary_history = True
            else:
                rec.can_create_advance_salary_history = False

    def create_advance_salary_history(self):
        advance_salary_history = self.env['advance.salary.history']
        advance_salary_history_vals = {
            'salary_employee_id': self.salary_employee_id and self.salary_employee_id.id or False,
            'total_monthly_salary': self.total_monthly_salary or 0.0,
            'request_year': self.request_year or False,
            'request_month': self.request_month or False,
            # 'approved_year': self.approved_year or False,
            'request_amount': self.request_amount or 0.0,
            # 'approved_amount': self.approved_amount or 0.0,
            # 'approved_month': self.approved_month or False,
            'salary_advance_reason': self.salary_advance_reason or '',
            'salary_advance_ref': self.salary_advance_ref or ''}
        advance_salary_history_id = advance_salary_history.create(advance_salary_history_vals)
        if advance_salary_history_id:
            self.advance_salary_history_ids = advance_salary_history_id

    def action_approve(self, approver=None):
        res = super(ApprovalRequest, self).action_approve(approver=approver)
        if self.is_salary_advance == 'yes' and self.request_status == 'approved':
            self.create_advance_salary_history()
        return res

    # Report method

    # def _salary_recovery_month(self):
    #     """
    #     :Author:Bhavesh Jadav TechUltra solutions
    #     :Date:02/10/2020
    #     :Func:This method use for the calculates recovery month for the salary base on the approved month
    #     :Return : recovery_month string
    #     """
    #     if self.approved_month == '12':
    #         recovery_month = '01'
    #     else:
    #         recovery_month = int(self.approved_month) + 1
    #     return dict(self._fields['approved_month'].selection).get(str(recovery_month))

# extra methods

# def _get_months(self, selected_year=False):
#     data = []
#     current_month = int(datetime.today().strftime("%m"))
#     current_day = int(datetime.today().strftime("%d"))
#     if selected_year:
#         selected_year = datetime.strptime(str(selected_year), "%Y")
#         current_month = 1
#     else:
#         selected_year = datetime.now()
#     month_list = [(selected_year + relativedelta(months=i)).strftime('%B') for i in
#                   range(13 - current_month)]
#     counter = 0
#     for month in month_list:
#         counter += 1
#         if current_day > 10 and counter == 1:
#             continue
#         data.append((month.lower(), month))
#     return data

# def _get_years(self):
#     data = []
#     current_year = int(datetime.today().strftime("%Y"))
#     for i in range(10):
#         data.append((current_year, current_year))
#         current_year += 1
#     return data
