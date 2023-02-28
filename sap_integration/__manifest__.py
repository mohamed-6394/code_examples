# -*- coding: utf-8 -*-
{
    'name': "SAP Integration",

    'summary': """
        Integrate with SAP B1""",

    'description': """
        Integrate with SAP B1 by APIs to get contacts, employees and push payslip data to SAP
    """,

    'author': "Mohamed Ahmed",
    'email': "mohamed.ahmed1263@gmail.com",
    'category': 'Extra Tools',
    'version': '1.0',

    # any module necessary for this one to work correctly
    'depends': ['base', 'contacts', 'hr', 'om_hr_payroll', 'account', 'analytic'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/sap_screen_views.xml',
        'views/hr_employee_views.xml',
        'views/analytic_account_views.xml',
        'views/hr_payslip_views.xml',
    ],
}
