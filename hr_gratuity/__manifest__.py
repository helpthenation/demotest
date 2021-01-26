# -*- coding: utf-8 -*-
{
    'name': "Gratuity",

    'summary': """Gratuity""",

    'description': """Gratuity""",

    'author': "TechUltra Solutions ",
    'website': "http://www.techultrasolutions.com",

    'category': 'Uncategorized',
    'version': '1.0.2',

    # any module necessary for this one to work correctly
    'depends': ['base', 'security_groups', 'hr_contract_custom', 'hr_payroll'],

    # always loaded
    'data': ['security/ir.model.access.csv',
             'data/ir_sequence_data.xml',
             'data/gratuity_data.xml',
             'views/hr_gratuity_view.xml'],
    # only loaded in demonstration mode
}
