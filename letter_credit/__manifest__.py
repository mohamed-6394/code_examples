# -*- coding: utf-8 -*-
{
    'name': "letter_credit",

    'summary': """
        Letter of credit """,

    'description': """
       Letter of credit 
    """,

    'author': "Mohamed Ahmed",
    'website': "",
    'category': 'Accounting',
    'version': '1.0',

    # any module necessary for this one to work correctly
    'depends': ['base', 'account_accountant'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/letter_credit_views.xml',
        'views/sequence.xml',
        'wizard/wizard.xml',
    ],
}