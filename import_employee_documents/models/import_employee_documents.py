# -*- coding: utf-8 -*-
import base64
import logging
import csv
from io import StringIO, BytesIO
from odoo.exceptions import Warning
from odoo.modules.module import get_module_resource

_logger = logging.getLogger(__name__)
from odoo import models, fields, api, _


class ImportEmployeeDocuments(models.Model):
    _name = 'import.employee.documents'
    _description = 'Import Employee Documents'

    choose_file = fields.Binary('Choose File', required=True)
    datas = fields.Binary('File')
    file_name = fields.Char('File Name')
    date = fields.Datetime('Date', default=fields.Datetime.now)
    name = fields.Char(string='Name')
    state = fields.Selection([
        ('pending', 'Pending '),
        ('done', 'Done'),
    ], string='Status', copy=False, default='pending')
    log_line_ids = fields.One2many('import.employee.documents.log.line', 'import_log_id', string='Log Lines')
    attachment_path = fields.Char(string="Attachment Path", required=True)

    @api.model
    def create(self, vals):
        """
        set name through sequence while creating log record
        :param vals:
        :return:
        """
        vals['name'] = self.env.ref('import_employee_documents.seq_import_log').next_by_id() or 'New'
        result = super(ImportEmployeeDocuments, self).create(vals)
        return result

    def import_employee_data(self):
        """
        Import Data from the csv
        :return:
        """

        if not self.choose_file:
            raise Warning("File Not Found To Import")
        if self.file_name and self.file_name[-3:] != 'csv':
            raise Warning("Please Provide Only .csv File to Import !!!")

        self.write({'datas': self.choose_file})
        self._cr.commit()
        import_file = BytesIO(base64.decodestring(self.datas))
        csvf = StringIO(import_file.read().decode())
        reader = csv.DictReader(csvf, delimiter=',')
        data = []
        for line in reader:
            data.append(line)

        if data:
            keys = []
            data_vals = []
            header_data = data[0]
            doc_type = data[0].get('Document Type')
            for key, value in header_data.items():
                keys.append(key)
                data_vals.append(value)

            if doc_type == 'Visa':
                headers = ['Document Type', 'externalCode', 'effectiveStartDate', 'Date of Issue', 'Date of Expiry',
                           'Visa Place of Issue',
                           'Visa Number',
                           'Visa Sponsor', 'Visa Job Title', 'Visa Unified Number', 'effectiveEndDate',
                           'fileName-Attachment']
                for header in headers:
                    if header not in keys:
                        raise Warning(
                            "File Header is not correct you have to give this file headers :'Document Type', 'externalCode', 'effectiveStartDate', 'Date of Issue', 'Date of Expiry','Visa Place of Issue','Visa Number','Visa Sponsor', 'Visa Job Title', 'Visa Unified Number', 'effectiveEndDate','fileName-Attachment' ")
                self.do_import_visa_data(data)

            elif doc_type == 'Passport':
                headers = ['Document Type', 'externalCode', 'effectiveStartDate', 'Date of Issue', 'Date of Expiry',
                           'Passport Country of Issue',
                           'Passport Place of Issue',
                           'Passport No', 'Passport Unified Number', 'effectiveEndDate', 'fileName-Attachment']
                for header in headers:
                    if header not in keys:
                        raise Warning(
                            "File Header is not correct you have to give this file headers :'Document Type', 'externalCode', 'effectiveStartDate', 'Date of Issue', 'Date of Expiry','Passport Country of Issue','Passport Place of Issue ','Passport No', 'Passport Unified Number', 'effectiveEndDate', 'fileName-Attachment' ")
                self.do_import_passport_data(data)

            elif doc_type == 'Emirates ID':
                headers = ['Document Type', 'externalCode', 'effectiveStartDate', 'Date of Expiry', 'Emirates ID No',
                           'effectiveEndDate', 'fileName-Attachment']
                for header in headers:
                    if header not in keys:
                        raise Warning(
                            "File Header is not correct you have to give this file headers :'Document Type', 'externalCode', 'effectiveStartDate', 'Date of Expiry', 'Emirates ID No','effectiveEndDate', 'fileName-Attachment' ")
                self.do_import_emirate_id_data(data)

            elif doc_type == 'Family Book':
                headers = ['Document Type', 'externalCode', 'effectiveStartDate', 'Family No', 'Date of Issue',
                           'effectiveEndDate', 'fileName-Attachment']
                for header in headers:
                    if header not in keys:
                        raise Warning(
                            "File Header is not correct you have to give this file headers :'Document Type', 'externalCode', 'effectiveStartDate', 'Family No', 'Date of Issue','effectiveEndDate', 'fileName-Attachment' ")

                self.do_import_family_data(data)
            return {'effect': {'fadeout': 'slow',
                               'message': "Yeah %s, It's Done,"
                                          "You can check import logs for further details."
                                          % self.env.user.name,
                               'img_url': '/web/static/src/img/smile.svg', 'type': 'rainbow_man'
                               }
                    }

    def do_import_visa_data(self, data):
        """
        Import data for the Documents type of "Visa"
        :param data: dict of data
        :return:
        """
        if data:
            line_no = 1

            try:
                for row in data:
                    line_no += 1
                    system_id_val = row.get('externalCode')
                    if system_id_val != '':
                        # Get Document type
                        document_type = row.get('Document Type')
                        document_type_id = self.env['document.types'].search([('name', '=', document_type)])
                        issue_date_val = row.get('Date of Issue')
                        issue_date_val = self.date_replace(issue_date_val)
                        date_of_expiry = row.get('Date of Expiry')
                        date_of_expiry = self.date_replace(date_of_expiry)
                        place_of_issue = row.get('Visa Place of Issue')
                        visa_number = row.get('Visa Number')
                        visa_sponsor = row.get('Visa Sponsor')
                        job_title = row.get('Visa Job Title')
                        unified_number = row.get('Visa Unified Number')
                        attachments_id_val = row.get('fileName-Attachment')

                        system_id = self.env['hr.employee'].search([('system_id', '=', system_id_val)])
                        if not system_id:
                            val = {
                                'import_log_id': self.id,
                                'line_no': int(line_no),
                                'message': "System Id %s not found for any employee" % system_id_val
                            }
                            self.env['import.employee.documents.log.line'].create(val)
                        else:
                            text_file_path = get_module_resource('import_employee_documents', self.attachment_path,
                                                                 attachments_id_val)
                            if not text_file_path:
                                val = {
                                    'import_log_id': self.id,
                                    'line_no': int(line_no),
                                    'message': 'Attachment not found in directory: %s' % attachments_id_val
                                }
                                self.env['import.employee.documents.log.line'].create(val)
                            else:
                                pdf_file = open(text_file_path, 'rb')
                                pdf_file_encode = base64.b64encode(pdf_file.read())
                                if pdf_file_encode:
                                    attachment = self.env['ir.attachment'].create({
                                        'name': attachments_id_val,
                                        'type': 'binary',
                                        'datas': pdf_file_encode,
                                        'res_model': self._name,
                                        'res_id': self.id
                                    })
                                    if attachment:
                                        attachment.write(
                                            {'res_model': 'hr.employee',
                                             'res_id': system_id.id})
                                    else:
                                        log_val = {
                                            'import_log_id': self.id,
                                            'line_no': int(line_no),
                                            'message': 'Attachment not found in directory: %s' % attachments_id_val
                                        }
                                        self.env['import.employee.documents.log.line'].create(log_val)
                                    folder = self.env['documents.folder'].search([('is_default_folder', '=', True)],
                                                                                 limit=1)
                                    doc_vals = {
                                        'related_employee': system_id[0].id,
                                        'document_type_id': document_type_id.id,
                                        'name': attachments_id_val,
                                        'owner_id': self.create_uid.id,
                                        'issue_date': issue_date_val,
                                        'expiry_date': date_of_expiry,
                                        'visa_sponsor': visa_sponsor,
                                        'visa_job_title': job_title,
                                        'visa_place_issue': place_of_issue,
                                        'visa_file_no': visa_number,
                                        'visa_unified_no': unified_number,
                                        'folder_id': folder.id,
                                        'attachment_id': attachment.id,
                                    }
                                    if system_id[0].own_document_o2m:
                                        flag = False
                                        if not flag:
                                            new_doc = self.env['documents.document'].create(doc_vals)
                                            new_doc.state_approve()

                                            log_val = {
                                                'import_log_id': self.id,
                                                'line_no': int(line_no),
                                                'message': "Record Created with System id %s" % system_id_val
                                            }
                                            self.env['import.employee.documents.log.line'].create(log_val)
                                    else:
                                        new_doc = self.env['documents.document'].create(doc_vals)
                                        new_doc.state_approve()

                                        log_val = {
                                            'import_log_id': self.id,
                                            'line_no': int(line_no),
                                            'message': "Record Created with System id %s" % system_id_val
                                        }
                                        self.env['import.employee.documents.log.line'].create(log_val)
                            self.env.cr.commit()

            except Exception as e:
                _logger.info(e)
                return False

    @api.model
    def date_replace(self, date):
        """
        Replace date into the YY-MM-DD format
        :param date: date
        :return: date
        """
        date = date.replace("[", '').replace("]", '')
        date = date.replace('/', '-')
        date = date.split('-')
        if len(date[2]) != 4:
            date[2] = "20" + date[2]
        date = date[2] + "-" + date[0] + "-" + date[1]
        return date

    def do_import_family_data(self, data):
        """
        Import data for the Documents type of "Family data"
        :param data: dict of data
        :return:
        """
        if data:
            line_no = 1

            try:
                for row in data:
                    line_no += 1
                    system_id_val = row.get('externalCode')
                    if system_id_val != '':
                        # Get Document type
                        document_type = row.get('Document Type')
                        document_type_id = self.env['document.types'].search([('name', '=', document_type)])
                        issue_date_val = row.get('Date of Issue')
                        issue_date_val = self.date_replace(issue_date_val)
                        family_number = row.get('Family No')
                        attachments_id_val = row.get('fileName-Attachment')

                        system_id = self.env['hr.employee'].search([('system_id', '=', system_id_val)])
                        if not system_id:
                            val = {
                                'import_log_id': self.id,
                                'line_no': int(line_no),
                                'message': "System Id %s not found for any employee" % system_id_val
                            }
                            self.env['import.employee.documents.log.line'].create(val)
                        else:
                            text_file_path = get_module_resource('import_employee_documents', self.attachment_path,
                                                                 attachments_id_val)
                            if not text_file_path:
                                val = {
                                    'import_log_id': self.id,
                                    'line_no': int(line_no),
                                    'message': 'Attachment not found in directory: %s' % attachments_id_val
                                }
                                self.env['import.employee.documents.log.line'].create(val)
                            else:
                                pdf_file = open(text_file_path, 'rb')
                                pdf_file_encode = base64.b64encode(pdf_file.read())
                                if pdf_file_encode:
                                    attachment = self.env['ir.attachment'].create({
                                        'name': attachments_id_val,
                                        'type': 'binary',
                                        'datas': pdf_file_encode,
                                        'res_model': self._name,
                                        'res_id': self.id
                                    })
                                    if attachment:
                                        attachment.write(
                                            {'res_model': 'hr.employee',
                                             'res_id': system_id.id})
                                    else:
                                        log_val = {
                                            'import_log_id': self.id,
                                            'line_no': int(line_no),
                                            'message': 'Attachment not found in directory: %s' % attachments_id_val
                                        }
                                        self.env['import.employee.documents.log.line'].create(log_val)
                                    folder = self.env['documents.folder'].search([('is_default_folder', '=', True)],
                                                                                 limit=1)
                                    doc_vals = {
                                        'related_employee': system_id[0].id,
                                        'document_type_id': document_type_id.id,
                                        'name': attachments_id_val,
                                        'owner_id': self.create_uid.id,
                                        'issue_date': issue_date_val,
                                        'family_book': family_number,
                                        'folder_id': folder.id,
                                        'attachment_id': attachment.id,
                                    }
                                    if system_id[0].own_document_o2m:
                                        flag = False
                                        if not flag:
                                            new_doc = self.env['documents.document'].create(doc_vals)
                                            new_doc.state_approve()

                                            log_val = {
                                                'import_log_id': self.id,
                                                'line_no': int(line_no),
                                                'message': "Record Created with System id %s" % system_id_val
                                            }
                                            self.env['import.employee.documents.log.line'].create(log_val)
                                    else:
                                        new_doc = self.env['documents.document'].create(doc_vals)
                                        new_doc.state_approve()

                                        log_val = {
                                            'import_log_id': self.id,
                                            'line_no': int(line_no),
                                            'message': "Record Created with System id %s" % system_id_val
                                        }
                                        self.env['import.employee.documents.log.line'].create(log_val)
                            self.env.cr.commit()

            except Exception as e:
                _logger.info(e)
                return False

    def do_import_emirate_id_data(self, data):
        """
        Import data for the Documents type of "Emirate Id"
        :param data: dict of data
        :return:
        """
        if data:
            line_no = 1

            try:
                for row in data:
                    line_no += 1
                    system_id_val = row.get('externalCode')
                    if system_id_val != '':
                        # Get Document type
                        document_type = row.get('Document Type')
                        document_type_id = self.env['document.types'].search([('name', '=', document_type)])

                        # Remain in the csv
                        # issue_date_val = row.get('Issue Date')
                        # issue_date_val = self.date_replace(issue_date_val)
                        date_of_expiry = row.get('Date of Expiry')
                        date_of_expiry = self.date_replace(date_of_expiry)
                        emirates_id_number = row.get('Emirates ID No')
                        attachments_id_val = row.get('fileName-Attachment')

                        system_id = self.env['hr.employee'].search([('system_id', '=', system_id_val)])
                        if not system_id:
                            val = {
                                'import_log_id': self.id,
                                'line_no': int(line_no),
                                'message': "System Id %s not found for any employee" % system_id_val
                            }
                            self.env['import.employee.documents.log.line'].create(val)
                        else:
                            text_file_path = get_module_resource('import_employee_documents', self.attachment_path,
                                                                 attachments_id_val)
                            if not text_file_path:
                                val = {
                                    'import_log_id': self.id,
                                    'line_no': int(line_no),
                                    'message': 'Attachment not found in directory: %s' % attachments_id_val
                                }
                                self.env['import.employee.documents.log.line'].create(val)
                            else:
                                pdf_file = open(text_file_path, 'rb')
                                pdf_file_encode = base64.b64encode(pdf_file.read())
                                if pdf_file_encode:
                                    attachment = self.env['ir.attachment'].create({
                                        'name': attachments_id_val,
                                        'type': 'binary',
                                        'datas': pdf_file_encode,
                                        'res_model': self._name,
                                        'res_id': self.id
                                    })
                                    if attachment:
                                        attachment.write(
                                            {'res_model': 'hr.employee',
                                             'res_id': system_id.id})
                                    else:
                                        log_val = {
                                            'import_log_id': self.id,
                                            'line_no': int(line_no),
                                            'message': 'Attachment not found in directory: %s' % attachments_id_val
                                        }
                                        self.env['import.employee.documents.log.line'].create(log_val)
                                    folder = self.env['documents.folder'].search([('is_default_folder', '=', True)],
                                                                                 limit=1)
                                    doc_vals = {
                                        'related_employee': system_id[0].id,
                                        'document_type_id': document_type_id.id,
                                        'name': attachments_id_val,
                                        'owner_id': self.create_uid.id,
                                        # 'issue_date': issue_date_val,
                                        'expiry_date': date_of_expiry,
                                        'emirates_id': emirates_id_number,
                                        'folder_id': folder.id,
                                        'attachment_id': attachment.id,
                                    }
                                    if system_id[0].own_document_o2m:
                                        flag = False
                                        if not flag:
                                            new_doc = self.env['documents.document'].create(doc_vals)
                                            new_doc.state_approve()

                                            log_val = {
                                                'import_log_id': self.id,
                                                'line_no': int(line_no),
                                                'message': "Record Created with System id %s" % system_id_val
                                            }
                                            self.env['import.employee.documents.log.line'].create(log_val)
                                    else:
                                        new_doc = self.env['documents.document'].create(doc_vals)
                                        new_doc.state_approve()

                                        log_val = {
                                            'import_log_id': self.id,
                                            'line_no': int(line_no),
                                            'message': "Record Created with System id %s" % system_id_val
                                        }
                                        self.env['import.employee.documents.log.line'].create(log_val)
                            self.env.cr.commit()

            except Exception as e:
                _logger.info(e)
                return False

    def do_import_passport_data(self, data):
        """
        Import data for the Documents type of "Passport"
        :param data: dict of data
        """
        if data:
            line_no = 1

            try:
                for row in data:
                    line_no += 1
                    system_id_val = row.get('externalCode')
                    if system_id_val != '':

                        # Get Document type
                        document_type = row.get('Document Type')
                        document_type_id = self.env['document.types'].search([('name', '=', document_type)])
                        issue_date_val = row.get('Date of Issue')
                        issue_date_val = self.date_replace(issue_date_val)
                        expiry_date_val = row.get('Date of Expiry')
                        expiry_date_val = self.date_replace(expiry_date_val)
                        passport_country_issue_val = row.get('Passport Country of Issue')
                        passport_place_issue_val = row.get('Passport Place of Issue')
                        passport_number_val = row.get('Passport No')
                        password_unified_number_val = row.get('Passport Unified Number')
                        attachments_id_val = row.get('fileName-Attachment')

                        system_id = self.env['hr.employee'].search([('system_id', '=', system_id_val)])
                        if not system_id:
                            val = {
                                'import_log_id': self.id,
                                'line_no': int(line_no),
                                'message': "System Id %s not found for any employee" % system_id_val
                            }
                            self.env['import.employee.documents.log.line'].create(val)
                        else:
                            text_file_path = get_module_resource('import_employee_documents', self.attachment_path,
                                                                 attachments_id_val)
                            if not text_file_path:
                                val = {
                                    'import_log_id': self.id,
                                    'line_no': int(line_no),
                                    'message': 'Attachment not found in directory: %s' % attachments_id_val
                                }
                                self.env['import.employee.documents.log.line'].create(val)
                            else:
                                pdf_file = open(text_file_path, 'rb')
                                pdf_file_encode = base64.b64encode(pdf_file.read())
                                if pdf_file_encode:
                                    attachment = self.env['ir.attachment'].create({
                                        'name': attachments_id_val,
                                        'type': 'binary',
                                        'datas': pdf_file_encode,
                                        'res_model': self._name,
                                        'res_id': self.id
                                    })
                                    if attachment:

                                        attachment.write(
                                            {'res_model': 'hr.employee',
                                             'res_id': system_id.id})
                                    else:
                                        log_val = {
                                            'import_log_id': self.id,
                                            'line_no': int(line_no),
                                            'message': 'Attachment not found in directory: %s' % attachments_id_val
                                        }
                                        self.env['import.employee.documents.log.line'].create(log_val)

                                    passport_country_issue_id = self.env['res.country'].search(
                                        [('name', '=', passport_country_issue_val)])
                                    if not passport_country_issue_id:
                                        log_val = {
                                            'import_log_id': self.id,
                                            'line_no': int(line_no),
                                            'message': 'Passport Country Issue not valid: %s' % passport_country_issue_val
                                        }
                                        self.env['import.employee.documents.log.line'].create(log_val)
                                    folder = self.env['documents.folder'].search([('is_default_folder', '=', True)],
                                                                                 limit=1)
                                    doc_vals = {
                                        'related_employee': system_id[0].id,
                                        'document_type_id': document_type_id.id,
                                        'name': attachments_id_val,
                                        'owner_id': self.create_uid.id,
                                        'issue_date': issue_date_val,
                                        'expiry_date': expiry_date_val,
                                        'passport_country_issue': passport_country_issue_id.id,
                                        'passport_place_issue': passport_place_issue_val,
                                        'passport_no': passport_number_val,
                                        'passport_unified_no': password_unified_number_val,
                                        'folder_id': folder.id,
                                        'attachment_id': attachment.id,
                                    }
                                    if system_id[0].own_document_o2m:
                                        flag = False
                                        if not flag:
                                            new_doc = self.env['documents.document'].create(doc_vals)
                                            new_doc.state_approve()

                                            log_val = {
                                                'import_log_id': self.id,
                                                'line_no': int(line_no),
                                                'message': "Record Created with System id %s" % system_id_val
                                            }
                                            self.env['import.employee.documents.log.line'].create(log_val)
                                    else:
                                        new_doc = self.env['documents.document'].create(doc_vals)
                                        new_doc.state_approve()

                                        log_val = {
                                            'import_log_id': self.id,
                                            'line_no': int(line_no),
                                            'message': "Record Created with System id %s" % system_id_val
                                        }
                                        self.env['import.employee.documents.log.line'].create(log_val)
                            self.env.cr.commit()

                return True

            except Exception as e:
                _logger.info(e)
                return False
