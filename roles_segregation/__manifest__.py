# -*- coding: utf-8 -*-

{
    'name': 'Roles Segregation',
    'description': 'Roles Segregation',
    'version': '0.1.0',
    'summary': 'Roles Segregation',
    'license': 'OPL-1',
    'author': 'TechUltra Solutions Pvt. Ltd.',
    'website': 'https://www.techultrasolutions.com/',
    'images': [],
    'category': 'uncategorized',
    'description': """ Roles Segregation""",
    'depends': ['security_groups', 'hr_appraisal', 'base', 'hr', 'hr_contract', 'hr_contract_custom',
                'employee_bank_approvals', 'housing_loan_approvals', 'salary_advance_approvals', 'hr_employee_custom',
                'approvals', 'survey', 'hr_exit_process', 'hr_appraisal_feedback', 'hr_appraisal_calibration',
                'website'],
    'data': [
        'security/ir_groups.xml',
        'security/ir.model.access.csv',
        'security/ir_rules.xml',
        'views/hr_appraisal_view.xml',
        'views/ir_menu.xml',
        'views/ir_views.xml',
        'views/templates.xml', ],
    'auto_install': False,
}

# depends
# security_groups for the assess group
# hr_appraisal for view and the group override
