# -*- coding: utf-8 -*-
{
    'name': "Import Employee Documents",

    'summary': """
        This module will import csv data of the employee documents""",

    'description': """
        This module will import csv data of the employee documents
    """,

    'author': "My Company",
    'website': "http://www.yourcompany.com",

    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['hr_document_custom','hr_employee_custom'],

    # always loaded
    'data': [
        'data/ir_sequence_data.xml',
        "views/import_employee_documents_views.xml",
        "security/ir.model.access.csv",
    ],

}
