from odoo import fields, models, api


class PositionDefaultSignatures (models.Model):
    _name = 'hr.job.default.signature'

    name = fields.Many2one(
        comodel_name='res.users',
        string='User',
        required=True)
    sequence = fields.Integer(
        string='Sequence',
        required=False)


