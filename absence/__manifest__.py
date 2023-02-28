# -*- coding: utf-8 -*-

{
    'name': "Absence",

    'summary': """
        Attendance Policy That compute late and over hours + absence""",

    'description': """
        Attendance Policy That compute late and over hours + absence
    """,

    'author': "Mohamed Ahmed",
    'website': "",
    'category': 'Attendances',
    'version': '1.0',

    # any module necessary for this one to work correctly
    'depends': ['base', 'hr', 'hr_attendance', 'hr_holidays'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/attendance_policy.xml',
        'views/absence.xml',
        'views/attendance.xml',
        'views/employee.xml',
    ],
}
