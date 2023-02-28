# -*- coding: utf-8 -*-
{
    'name': "multiple sale order",

    'summary': """
        Create Multiple Sales Order""",

    'description': """
        Create Multiple Sales Order
    """,

    'author': "Mohamed Ahmed",
    'website': "",
    'category': 'Sales',
    'version': '1.0',

    # any module necessary for this one to work correctly
    'depends': ['base', 'sale_management'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/multiple_so_view.xml',
    ],
}
