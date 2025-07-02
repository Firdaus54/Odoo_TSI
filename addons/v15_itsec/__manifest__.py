# -*- coding: utf-8 -*-
{
    'name': "IT Security",

    'summary': """
        IT Security Audit""",

    'description': """
        Long description of module's purpose
    """,

    'author': "TSICertification",
    'website': "http://www.tsicertification.com",
    'version': '15.0.0.0',
    'category': 'Application',
    'sequence': 1,
    'installable': True,
    'auto_install': False,
    'application': True,
    'license': 'AGPL-3', 

    # any module necessary for this one to work correctly
    'depends': ['base','mail'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'security/tsi_security.xml',
        'views/formulir.xml',
        'views/backup.xml',
        'views/guidelines.xml',
        'views/employee.xml',
        'views/pentest.xml',
        'views/communication.xml',
        'views/bcp.xml',
        'views/mgtreview.xml',
        'views/incident.xml',
        'views/audit.xml',
        'views/vendor.xml',
        'views/kinerja.xml',
        'views/klasifikasi.xml',
        'views/assets.xml',
        'views/identifikasi.xml',
        'views/refference.xml',
        'views/risk.xml',
        'views/views.xml',
        'wizards/wizard_import_audit_log.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
