# -*- coding: utf-8 -*-

from odoo import models, fields


class ImportEmployeeDocumentsLogLine(models.Model):
    _name = 'import.employee.documents.log.line'
    _description = 'Import Employee Documents Log Line'

    import_log_id = fields.Many2one('import.employee.documents', string='Import_Employee')
    line_no = fields.Integer(string='Line Number')
    message = fields.Char(string='Message')
