# -*- coding: utf-8 -*-
{
    'name': "insurance_taxes",

    'summary': """
        Compute Egyptian Insurance and Taxes """,

    'description': """
        Compute Egyptian Insurance and Taxes
    """,

    'author': "Mohamed Ahmed",
    'website': "",
    'category': 'Account',
    'version': '1.0',

    # any module necessary for this one to work correctly
    'depends': [
        'base',
        'hr_payroll',
        'hr_work_entry',
    ],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/taxes_views.xml',
    ],
}
