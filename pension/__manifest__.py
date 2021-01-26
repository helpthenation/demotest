# -*- coding: utf-8 -*-
{
    'name': "pension",

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
    'version': '1.1.0',

    # any module necessary for this one to work correctly
    'depends': ['base', 'hr_payroll', 'hr_contract_custom'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        # 'data/data.xml',
        'views/pension_rule_views.xml',
        'views/pension_line_rule_views.xml',
        'wizard/pension_report_wizard_view.xml',
        'report/hr_payroll_menu.xml',
        'report/pension_report.xml',

    ],
}
