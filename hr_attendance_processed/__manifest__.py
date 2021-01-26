# -*- coding: utf-8 -*-
{
    'name': "hr_attendance_processed",

    'summary': """
        process Attendance with easy way""",

    'description': """
        process Attendance with easy way
    """,

    'author': "My Company",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'HR',
    'version': '1.1.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'hr_attendance', 'hr_employee_custom', 'planning'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/hr_attendance_processed_views.xml',
        'views/planning_slot_custom.xml',
        'views/resource_calender.xml',
        'views/amend_employee_shifts_wizard.xml',
        'cron/cron_job.xml',
    ],
    # only loaded in demonstration mode
}
