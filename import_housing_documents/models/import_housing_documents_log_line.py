# -*- coding: utf-8 -*-

from odoo import models, fields


class ImportHousingDocumentsLogLine(models.Model):
    _name = 'import.housing.documents.log.line'
    _description = 'Import Housing Documents Log Line'

    import_log_id = fields.Many2one('import.housing.documents', string='Import_Employee')
    line_no = fields.Integer(string='Line Number')
    message = fields.Char(string='Message')
