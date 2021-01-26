# -*- coding: utf-8 -*-
{
    'name': "Chatter User Filter",

    'summary': """ Filter Chatter message based on user and the model """,

    'description': """
       Filter Chatter message based on user and the model
    """,

    'author': "TechUltra Solutions Pvt. Ltd.",
    'website': "https://www.techultrasolutions.com/",

    'category': 'Uncategorized',
    'version': '0.2',

    # any module necessary for this one to work correctly
    'depends': ['mail', 'base_setup'],

    # always loaded
    'data': ['views/res_config.xml'],
    # only loaded in demonstration mode
}
