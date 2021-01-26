# -*- coding: utf-8 -*-

{
    'name': 'Microsoft Azure SSO OAuth2',
    'version': '13.0.1.5',
    'author': 'Solutions2use',
    'maintainer': 'Solutions2use',
    'support': 'info@solutions2use.com',
    'website': 'https://www.solutions2use.com',
    'images': ['static/description/app_logo.jpg', 'static/description/icon.png'],
    'price': 39.0,
    'currency': 'EUR',
    'category': 'Tools',
    'license': 'OPL-1',
    'summary': 'Microsoft office365 SSO OAuth2',
    'description': """
Allow users to login with MicroSoft OAuth2 Provider.
=============================================
""",
    'depends': ['auth_oauth'],
    'data': [
        'views/auth_oauth_views.xml',
        'data/auth_oauth_data.xml',
        'security/ir.model.access.csv',
    ],
}
