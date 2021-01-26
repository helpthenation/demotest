# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class ir_model(models.Model):
    _inherit = "ir.model"

    track = fields.Boolean('track', help='Track the changes on chatter?')


class mail_thread(models.AbstractModel):
    _inherit = "mail.thread"

    @api.model
    def _get_tracked_fields(self):
        if self.env['ir.model']._get(self._name).track:
            fields = self.fields_get()
            self.remove_exceptional_fields(fields=fields)
            dels = [f for f in fields if f in models.LOG_ACCESS_COLUMNS or f.startswith('_') or f == 'id']
            for x in dels:
                del fields[x]
            return fields
        else:
            return super(mail_thread, self)._get_tracked_fields()

    def remove_exceptional_fields(self, fields):
        """
        Author:Bhavesh Jadav TechUltra Solutions
        Date:13/10/2020
        Func:This emthod use for the remove compute fields from the fields duct
        Return :dict
        """
        fields_keys = fields.keys()
        exceptional_fields = []
        for fields_key in fields_keys:
            fields_val = fields.get(fields_key)
            if fields_val.get('depends'):
                # if fields_val.get('string') == 'Can See Eligible':
                exceptional_fields.append(fields_key)
        [fields.pop(fields_key) for fields_key in exceptional_fields]
        return fields
