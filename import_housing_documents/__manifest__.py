# -*- coding: utf-8 -*-
{
    'name': "Import Housing Documents",

    'summary': """
        This module will import csv data of the Housing documents""",

    'description': """
        This module will import csv data of the housing documents
    """,

    'author': "My Company",
    'website': "http://www.yourcompany.com",

    'category': 'HR',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['hr_document_custom','hr_employee_custom'],

    # always loaded
    'data': [
        'data/ir_sequence_data.xml',
        "views/import_housing_documents_views.xml",
        "security/ir.model.access.csv",
    ],

}
