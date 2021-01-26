# -*- coding: utf-8 -*-
{
    'name': 'Export Views Data XLS',
    'version': '1.0.3',
    'category': 'Apps',
    'author': 'TechUltra',
    'website': 'http://techultrasolutions.com',
    'license': 'AGPL-3',
    'depends': ['base', 'base_setup', 'hr_appraisal', 'base_address_city'],
    'data': ['cron/cron_job.xml',
             'security/ir.model.access.csv',
             'views/res_config.xml',
             'views/res_company.xml'
             ],

    'test': [],
    'demo': [],

    'installable': True,
    'active': False,
    'application': True,
}
