from odoo import models, fields, api, _


class HrGratuity(models.Model):
    _name = 'hr.gratuity'

    name = fields.Char(string="Name")
    contract_type = fields.Selection([('permanent', 'Permanent'), ('contractor', 'Contractor')], string="Contract Type")
    reason = fields.Selection(
        [('termination', 'Termination'), ('resignation', 'Resignation'), ('resignation', 'Resignation'),
         ('end_of_contract', ' End of Contract'),
         ('absconded', 'Absconded')],
        string="Reason")
    from_year = fields.Integer(string="From Year")
    to_year = fields.Integer(string="To Year")
    number_of_years = fields.Selection(
        [('1_to_5_years', '1 to 5 years'),
         ('6_to_10_years', '6 to 10 years'),
         ('above_10_years', 'Above 10 years'),
         ('months', 'Months'),
         ('days', 'Days'),
         ('less_than_1_year', 'Less than 1 year'),
         ('1_to_3_years', '1 to 3 years'),
         ('3_to_5_years', '3 to 5 years'),
         ('more_than_5_years', 'More than 5 years'),
         ('completion_of_5_years', 'Completion of 5 years')], string="Number of Years")
    multiplier = fields.Integer(string="Multiplier")
    number_of_days = fields.Integer(string="Number of Days")

    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].next_by_code('hr.gratuity') or _('New')
        res = super(HrGratuity, self).create(vals)
        return res
