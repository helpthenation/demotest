# -*- coding: utf-8 -*-

{
    'name': 'Contractors and Employees EOS',
    'description': 'Contractors and Employees End of Service',
    'version': '1.0.1',
    'summary': 'Contractors and Employees End of Service request for the Notice pay and Leave Encashment and Gratuity Payments ',
    'license': 'OPL-1',
    'author': 'TechUltra Solutions Pvt. Ltd.',
    'website': 'https://www.techultrasolutions.com/',
    'images': [],
    'category': 'uncategorized',
    'description': """Contractors and Employees End of Service request for the Notice pay and Leave Encashment and Gratuity 
    Payments  """,
    'depends': ['hr', 'hr_gratuity', 'hr_employee_custom', 'approvals', 'security_groups', 'hr_payroll',
                'res_company_custom'],
    'data': ['data/ir_sequence_data.xml',
             'data/ir_mail_activity.xml',
             'data/approval_category_data.xml',
             'data/ir_salary_rule.xml',
             'security/ir.model.access.csv',
             'reports/reports.xml',
             'reports/end_of_service_report.xml',
             'views/eos_reject_reason_view.xml',
             'views/end_of_service_view.xml',
             'views/end_of_service_settings_view.xml',
             'views/approval_category_view.xml'],
    'auto_install': False,
}
