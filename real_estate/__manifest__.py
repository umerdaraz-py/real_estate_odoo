# -*- coding: utf-8 -*-
{
    'name': "Real-Estate Management",

    'summary': """
        Real Estate Management""",

    'description': """
        Real Estate Management
    """,

    'author': "Umer Daraz",
    'website': "https://www.yourcompany.com",
    'sequence': '1',
    'category': 'Category',
    'version': '1.0',

    # any module necessary for this one to work correctly
    'depends': ['base'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/estate_property_views.xml',
        'views/estate_menus.xml',
        'views/estate_property_offer_views.xml',
        'views/res_users_views.xml'
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
