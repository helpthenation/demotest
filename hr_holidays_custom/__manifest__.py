# -*- coding: utf-8 -*-
{
    'name': "Hr Holidays Custom",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Long description of module's purpose
    """,

    'author': "My Company",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '1.1.3',

    # any module necessary for this one to work correctly
    'depends': ['hr_employee_custom', 'hr_holidays', 'hr_contract_custom', 'hr_payroll', 'base'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'data/carried_forward_settings_record.xml',
        'views/hr_leave_type_view.xml',
        'views/hr_leave_type_approver_view.xml',
        'views/hr_leave_allocation_view.xml',
        'views/hr_leave_approver_view.xml',
        'views/hr_leave.xml',
        'wizard/reject_request_wizard_view.xml',
        'views/hr_leave_reports.xml',
        'views/hr_leave_carried_forward_settings_view.xml',
        'cron/cron_job.xml'],
}
