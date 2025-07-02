# -*- coding: utf-8 -*-
{
    'name': "CRM Tender",

    'summary': """
        CRM Tender""",

    'description': """
        CRM Tender
    """,

    'author': "IHU",
    'website': "http://www.ihu.com",
    'version': '15.0.0.0',
    'category': 'Application',
    'sequence': 3,
    'installable': True,
    'auto_install': False,
    'application': True,
    'license': 'AGPL-3', 

    # any module necessary for this one to work correctly
    'depends': ['base','crm'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/tender.xml',
        'views/crm.xml',
        'views/views.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
