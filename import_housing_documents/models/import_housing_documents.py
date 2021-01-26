# -*- coding: utf-8 -*-
import base64
import logging
import csv
from io import StringIO, BytesIO
from odoo.exceptions import Warning
from odoo.modules.module import get_module_resource

_logger = logging.getLogger(__name__)
from odoo import models, fields, api, _


class ImportHousingDocuments(models.Model):
    _name = 'import.housing.documents'
    _description = 'Import Housing Documents'

    choose_file = fields.Binary('Choose File', required=True)
    datas = fields.Binary('File')
    file_name = fields.Char('File Name')
    date = fields.Datetime('Date', default=fields.Datetime.now)
    name = fields.Char(string='Name')
    state = fields.Selection([
        ('pending', 'Pending '),
        ('done', 'Done'),
    ], string='Status', copy=False, default='pending')
    log_line_ids = fields.One2many('import.housing.documents.log.line', 'import_log_id', string='Log Lines')
    attachment_path = fields.Char(string="Attachment Path", required=True)

    @api.model
    def create(self, vals):
        """
        set name through sequence while creating log record
        :param vals:
        :return:
        """
        vals['name'] = self.env.ref('import_housing_documents.seq_import_log').next_by_id() or 'New'
        result = super(ImportHousingDocuments, self).create(vals)
        return result

    def import_housing_data(self):
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
            header_data = data[0]
            for key, value in header_data.items():
                keys.append(key)

            headers = ['Difference','externalCode', 'effectiveStartDate', 'Building/Villa Name or Number',
                       'City', 'Start Date', 'End Date', 'Emirate', 'Yearly Rental  Value', 'Residential Type',
                       'Street',
                       'Tawtheeq Number', 'mdfSystemEffectiveEndDate', 'fileName-Attachment']
            for header in headers:
                if header not in keys:
                    raise Warning(
                        "File Header is not correct you have to give this file headers :'externalCode', "
                        "'effectiveStartDate', 'Building/Villa Name or Number','City', 'Start Date', "
                        "'End Date', 'Emirate', 'Yearly Rental Value', 'Residential Type', 'Street','Tawtheeq Number', "
                        "'mdfSystemEffectiveEndDate', 'fileName-Attachment'")
            self.do_import_housing_data(data)

            return {'effect': {'fadeout': 'slow',
                               'message': "Yeah %s, It's Done,"
                                          "You can check import logs for further details."
                                          % self.env.user.name,
                               'img_url': '/web/static/src/img/smile.svg', 'type': 'rainbow_man'
                               }
                    }

    def do_import_housing_data(self, data):
        """
        Import data housing data"
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
                        building_number = row.get('Building/Villa Name or Number')
                        city = row.get('City')
                        start_date = row.get('Start Date')
                        start_date = self.date_replace(start_date)
                        end_date = row.get('End Date')
                        end_date = self.date_replace(end_date)
                        emirate = row.get('Emirate')
                        yeary_rental_val = row.get('Yearly Rental  Value')
                        residential_type = row.get('Residential Type')
                        street = row.get('Street')
                        tawtheeq_number = row.get('Tawtheeq Number')
                        attachments_id_val = row.get('fileName-Attachment')

                        system_id = self.env['hr.employee'].search([('system_id', '=', system_id_val)])
                        if not system_id:
                            val = {
                                'import_log_id': self.id,
                                'line_no': int(line_no),
                                'message': "System Id %s not found for any employee" % system_id_val
                            }
                            self.env['import.housing.documents.log.line'].create(val)
                        else:
                            text_file_path = get_module_resource('import_housing_documents', self.attachment_path,
                                                                 attachments_id_val)
                            if not text_file_path:
                                val = {
                                    'import_log_id': self.id,
                                    'line_no': int(line_no),
                                    'message': 'Attachment not found in directory: %s' % attachments_id_val
                                }
                                self.env['import.housing.documents.log.line'].create(val)
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
                                            {'res_model': 'hr.housing.attachment',
                                             'res_id': system_id.id})
                                        housing_type_check = ""
                                        if residential_type == "Relative House":
                                            housing_type_check = "rel"
                                        elif residential_type == "Owned House":
                                            housing_type_check = "own"
                                        elif residential_type == "Non-Relative House":
                                            housing_type_check = "nre"
                                        elif residential_type == "Rental House":
                                            housing_type_check = "ren"

                                        housing_type_val = {'name': residential_type, housing_type_check: True}
                                        housing_type = self.env['hr.housing.type'].search(
                                            [('nre', '=', True), ('own', '=', True), ('rel', '=', True),
                                             ('ren', '=', True)], limit=1)
                                        housing_att_val = {'attachment_ids': attachment,
                                                           'name': housing_type.id}
                                        housing_attachment = self.env['hr.housing.attachment'].create(housing_att_val)
                                        city_id = self.env['res.country.state'].search(
                                            [('name', '=', emirate), ('city_code', '=', 'AE')])
                                        if not city_id:
                                            val = {
                                                'import_log_id': self.id,
                                                'line_no': int(line_no),
                                                'message': 'State/City not found for the Emirate : %s' % emirate
                                            }
                                            self.env['import.housing.documents.log.line'].create(val)
                                        else:
                                            doc_vals = {
                                                'employee_id': system_id[0].id,
                                                'city_id': city_id[0].id,
                                                'emirate_text': city,
                                                'housing_residential_type': housing_type_check,
                                                'housing_ownership': '',
                                                'from_date': start_date,
                                                'to_date': end_date,
                                                'yearly_rent_value': yeary_rental_val,
                                                'tawtheeq_number': tawtheeq_number,
                                                'attached_documents': housing_attachment,
                                            }
                                            if system_id[0]:
                                                new_doc = self.env['hr.housing'].create(doc_vals)
                                                new_doc.state_approve()

                                                log_val = {
                                                    'import_log_id': self.id,
                                                    'line_no': int(line_no),
                                                    'message': "Record Created with System id %s" % system_id_val
                                                }
                                                self.env['import.housing.documents.log.line'].create(log_val)
                                            else:
                                                log_val = {
                                                    'import_log_id': self.id,
                                                    'line_no': int(line_no),
                                                    'message': 'Attachment not found in directory: %s' % attachments_id_val
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
        date = date[2] + "-" + date[1] + "-" + date[0]
        return date
