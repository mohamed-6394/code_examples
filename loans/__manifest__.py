# -*- coding: utf-8 -*-
{
    'name': "loans",

    'summary': """
        Loans Management""",

    'description': """
        Loans Management
    """,

    'author': "Mohamed Ahmed",
    'website': "",
    'category': 'Accounting',
    'version': '1.0',

    # any module necessary for this one to work correctly
    'depends': [
        'base',
        'hr',
        'hr_work_entry_contract',
        'account_accountant',
    ],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/views.xml',
        'views/loans_config_view.xml',
        'views/ir_cron.xml',
    ],
}
