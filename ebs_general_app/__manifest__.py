# -*- coding: utf-8 -*-
{
    'name': "ebs_general_app",

    'summary': """
        Archive all users non employees (Excluding HC Admins)
        """,

    'description': """
        Archive all users non employees (Excluding HC Admins)
    """,

    'author': "Ever Business Solutions",
    'website': "https://www.everbsgroup.com/",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',
        'cron/cron_job.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
