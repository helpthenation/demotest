# -*- coding: utf-8 -*-
{
    'name': "hr_appraisal",

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
    'version': '0.3',

    # any module necessary for this one to work correctly
    'depends': ['base', 'hr_appraisal', 'hr_core', 'hr_employee_custom'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'security/hr_appraisal_security.xml',
        'views/hr_appraisal_views.xml',
        'wizards/create_mass_appraisal_wiz_empty.xml',
        'wizards/create_mass_appraisal_wiz.xml',
        'wizards/log_note_wizard_view.xml',
        'views/appraisal_form_view.xml',
        'views/hr_appraisal_stage_view.xml',
        'views/hr_objective_view.xml',
        'views/hr_training_status_view.xml',
        'views/templates.xml',
        'report/appraisal_report.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
