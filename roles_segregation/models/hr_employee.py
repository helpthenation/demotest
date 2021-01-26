from odoo import fields, models, api, _
from odoo.exceptions import ValidationError
from lxml import etree
from datetime import datetime
from dateutil import relativedelta
import json


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
        res = super(HrEmployee, self).fields_view_get(view_id=view_id, view_type=view_type, toolbar=toolbar,
                                                      submenu=submenu)
        if view_type == 'form':
            doc = etree.XML(res['arch'])
            for field in res['fields']:
                if self.env.user.has_group('roles_segregation.group_hc_compensation_and_benefits'):
                    field_list = ['lang', 'firstname', 'resume_line_ids', 'address_id', 'coach_id',
                                  'expense_manager_id', 'leave_manager_id', 'resource_calendar_id', 'tz',
                                  'document_o2m', 'dependents', 'housing_ids', 'notice_ids', 'middlename', 'lastname',
                                  'arabic_name', 'image_1920', 'reject_reason', 'contract_employment_type', 'title',
                                  'mobile_phone', 'work_phone', 'work_email', 'work_location', 'parent_id']
                    if field in field_list:
                        for node in doc.xpath("//field[@name='%s']" % field):
                            node.set("readonly", "1")
                            modifiers = json.loads(node.get("modifiers"))
                            modifiers['readonly'] = True
                            node.set("modifiers", json.dumps(modifiers))
            res['arch'] = etree.tostring(doc, encoding='unicode')
        return res
