# -*- coding: utf-8 -*-
{
    'name': "CIS Apps",

    'summary': """
        Outsourcing Management System""",

    'description': """
        Outsourcing Management System
    """,

    'author': "TSICertification",
    'website': "http://www.tsicertification.com",
    'version': '15.0.0.0',
    'category': 'Application',
    'sequence': 3,
    'installable': True,
    'auto_install': False,
    'application': True,
    'license': 'AGPL-3', 

    # any module necessary for this one to work correctly
    'depends': ['base','mail','contacts','hr'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/operasional.xml',
        'views/kontrak.xml',
        'views/views.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
