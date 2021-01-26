# -*- coding: utf-8 -*-
{
    'name': "Leaves Balance",

    'summary': """ Leaves Balance""",

    'description': """ Leaves Balance""",

    'author': "TechUltra Solutions ",
    'website': "http://www.techultrasolutions.com",

    'category': 'Uncategorized',
    'version': '1.0.3',

    # any module necessary for this one to work correctly
    'depends': ['base', 'hr_payroll', 'hr_contract_custom'],

    # always loaded
    'data': ['security/ir.model.access.csv',
             'views/leaves_balance_view.xml'],
    # only loaded in demonstration mode
}
