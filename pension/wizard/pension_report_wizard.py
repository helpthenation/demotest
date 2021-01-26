from odoo import fields, models, api
from datetime import datetime
import calendar
from odoo.exceptions import Warning


class HrPensionReportWizard(models.TransientModel):
    _name = 'hr.pension.report.wizard'
    _description = 'Pension Report'

    country_id = fields.Many2one('res.country', string='Country', required=True)
    month = fields.Selection(
        [('1', 'January'), ('2', 'February'), ('3', 'March'), ('4', 'April'), ('5', 'May'), ('6', 'June'),
         ('7', 'July'), ('8', 'August'), ('9', 'September'), ('10', 'October'), ('11', 'November'),
         ('12', 'December')], string='Month')

    @api.model
    def year_selection(self):
        year = datetime.now().year
        last_year = datetime.now().year + 10
        year_list = []
        while year != last_year:
            year_list.append((str(year), str(year)))
            year += 1
        return year_list

    year = fields.Selection(year_selection, string="Year", default=str(datetime.now().year))

    def generate_pension_report(self):
        """
                :Author:Nimesh Jadav TechUltra solutions
                :Date:12/11/2020
                :Func:This method use to download pension report
                :Return:Report action xml id
                """
        select_date_from = str(self.year) + "-" + str(self.month) + "-" + '1'
        select_date_to = str(self.year) + "-" + str(self.month) + "-" + str(calendar.mdays[int(self.month)])
        rec = self.env['hr.payslip'].search(
            [('employee_id.country_id', '=', self.country_id.id), ('date_from', '>=', select_date_from),
             ('date_to', '<=', select_date_to)])
        if rec:
            return self.env.ref('pension.action_report_pension').report_action(rec)
        else:
            raise Warning('No Payslip found for the selected Country and date')
