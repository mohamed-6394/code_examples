# -*- coding: utf-8 -*-
{
    'name': "letter_guarantee",

    'summary': """
        Letter of guarantee """,

    'description': """
        Letter of guarantee 
    """,

    'author': "Mohamed Ahmed",
    'website': "",
    'category': 'Accounting',
    'version': '1.0',

    # any module necessary for this one to work correctly
    'depends': ['base', 'account_accountant', 'sale_management'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/letter_guarantee_views.xml',
        'views/sequence.xml',
        'views/ir_cron.xml',
        'wizard/wizard.xml',
    ],
}