# -*- coding: utf-8 -*-
{
    'name': "employee_bank_approvals",

    'summary': """
    
        """,

    'description': """
        Employee Bank Approvals
    """,

    'author': "My Company",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # for the full list
    'category': 'HR',
    'version': '13.0.0',

    # any module necessary for this one to work correctly
    'depends': ['hr_approvals','hr_document_custom'],

    # always loaded
    'data': ['data/data.xml',
             'views/employee_bank_approval_view.xml',
             'views/hr_employee_view.xml',
             'views/employee_bank_change.xml',
             'security/ir.model.access.csv',
             'reports/report_template.xml',
             'reports/reports.xml',
             ],
    'installable': True,
    'application': True,
}
