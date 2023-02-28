# -*- coding: utf-8 -*-
{
    'name': "isams connector",

    'summary': """
        Integrate with Isams and get stuednts and parents""",

    'description': """
        Integrate with Isams and get stuednts and parents
    """,

    'author': "Mohamed Ahmed",
    'website': "",
    'category': 'Extra Tools',
    'version': '1.0',

    # any module necessary for this one to work correctly
    'depends': ['base'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/connector_screen_views.xml',
        'views/student_views.xml',
        'views/parents_views.xml',
        'views/res_partner_views.xml',
    ],
}
