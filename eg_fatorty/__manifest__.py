# -*- coding: utf-8 -*-
{
    'name': "EG Fatorty",

    'summary': """Integrate With Egyptian e-Fatorty """,

    'description': """
        Integrate With Egyptian e-Fatorty
    """,

    'author': "Mohamed Ahmed",
    'website': "",
    'category': 'Accounting',
    'version': '1.0',

    # any module necessary for this one to work correctly
    'depends': ['base', 'sale', 'account', 'product', 'uom', 'sale_order_lot_selection'],

    # always loaded
    'data': [
        'security/groups.xml',
        'security/ir.model.access.csv',
        'data/uom.types.csv',
        'data/tax.types.csv',
        'data/tax.sub.types.csv',
        'views/company.xml',
        'views/partner.xml',
        'views/product.xml',
        'views/units.xml',
        'views/invoice.xml',

    ],

}
