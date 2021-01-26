# -*- coding: utf-8 -*-
{
    'name': "housing_loan_approvals",

    'summary': """
    
        """,

    'description': """
        Housing Loan Approvals
    """,

    'author': "My Company",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # for the full list
    'category': 'Uncategorized',
    'version': '1.3.3',

    # any module necessary for this one to work correctly
    'depends': ['hr_employee_custom', 'hr_approvals', 'security_groups'],

    # always loaded
    'data': ['data/housing_loan_data.xml',
             'views/approve_request.xml',
             'views/housing_loan_view.xml',
             'views/hr_employee_view.xml',
             'security/ir.model.access.csv',
             'reports/reports.xml',
             'reports/report_template.xml',
             'views/payment_plans_view.xml',
             ],
    'installable': True,
    'application': True,
}
