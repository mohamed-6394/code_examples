{
    'name': "weighbridge",

    'summary': """
        Integrate with Weighbridge Machine via DB""",

    'description': """
        Integrate with Weighbridge Machine via DB
        Weighbridge Machine is to measure cars and compute data of specific weight details of plate number, driver name, date and time
    """,

    'author': "Mohamed Ahmed",
    'website': "",
    'category': 'Extra Tools',
    'version': '1.0',

    # any module necessary for this one to work correctly
    'depends': ['base', 'sale', 'purchase', 'stock', 'mrp'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/weighbridge_views.xml',
        'views/sequence.xml',
        'views/weighbridge_machines_view.xml',
    ],
}
