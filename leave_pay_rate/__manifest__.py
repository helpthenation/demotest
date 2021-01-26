# -*- coding: utf-8 -*-
{
    'name': "Leave Pay Rate",

    'summary': """ Leave Pay Rate""",

    'description': """ Leave Pay Rate""",

    'author': "TechUltra Solutions ",
    'website': "http://www.techultrasolutions.com",

    'category': 'Uncategorized',
    'version': '1.0.2',

    # any module necessary for this one to work correctly
    'depends': ['base', 'hr_payroll'],

    # always loaded
    'data': ['security/ir.model.access.csv',
             'views/leave_pay_rate_view.xml'],
    # only loaded in demonstration mode
}
