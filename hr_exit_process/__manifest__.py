# -*- coding: utf-8 -*-

# Part of Probuse Consulting Service Pvt Ltd. See LICENSE file for full copyright and licensing details.

{
    'name': 'HR Exit Process Management',
    'version': '1.1.11',
    'price': 15.0,
    'currency': 'EUR',
    'license': 'Other proprietary',
    'images': ['static/description/image1.jpg'],
    'live_test_url': 'https://youtu.be/WxKofWvXqjk',
    'category': 'Human Resources',
    'summary': 'Employee Out/Exit/Termination Process Management',
    'description': """
        Employee Exit process:
            ---> Configure CheckLists
            ---> Employee Exit Request
            ---> Employee Exit Checklists
            ---> Print Employee Exit Report 

Tags:
exit process
employee exit process
employee termination process
employee leave process
employee leave company
employee exit company
hr exit process
human resource exit process
checklist for exit process
Termination terminate
            """,
    'author': 'Probuse Consulting Service Pvt. Ltd.',
    'website': 'www.probuse.com',
    'depends': ['hr', 'hr_contract', 'survey', 'calendar', 'security_rules'],
    'data': [
        'security/hr_exit_security.xml',
        'security/ir.model.access.csv',
        'views/hr_exit_view.xml',
        'report/hr_exit_process_report.xml',
        'wizard/reject_request_wizard_view.xml',
        # 'wizard/reject_reason_mail_template.xml',
    ],
    'installable': True,
    'application': False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
