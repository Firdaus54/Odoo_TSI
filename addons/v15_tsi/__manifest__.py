# -*- coding: utf-8 -*-
{
    'name': "TSI Certification",

    'summary': """
        ERP for TSI Certification""",

    'description': """
        Long description of module's purpose
    """,

    'author': "TSICertification",
    'website': "http://www.tsicertification.com",
    'version': '15.0.0.0',
    'category': 'Application',
    'sequence': 2,
    'installable': True,
    'auto_install': False,
    'application': True,
    'license': 'AGPL-3',

    # any module necessary for this one to work correctly
    'depends': ['base','mail','contacts','hr','hr_attendance','website','sale','account'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'security/iso_security.xml',
        'report/report_quotation.xml',
        'report/report_data.xml',
        'views/ispo.xml',
        'views/iso_form.xml',
        'views/iso_review.xml',
        'views/ispo_review.xml',
        'views/ispo_form.xml',
        'views/iso_param.xml',
        'views/iso_risk.xml',
        'views/iso.xml',
        'views/crm.xml',
        'views/param.xml',
        'views/ops_ows.xml',
        'views/task_pd.xml',
        'views/task_project_plan.xml',
        'views/workflow_tracker.xml',
        'views/sistem_perundangan.xml',
        'views/document_control.xml',
        'views/ops_program.xml',
        'views/ops_program_ispo.xml',
        'views/ops_plan.xml',
        'views/ops_plan_ispo.xml',
        'views/ops_report.xml',
        'views/ops_report_ispo.xml',
        'views/ops_review.xml',
        'views/ops_review_ispo.xml',
        'views/ops_sertifikat.xml',
        'views/ops_sertifikat_ispo.xml',
        'views/sertifikat_delivery.xml',
        'views/audit_notification.xml',
        'views/audit_notification_ispo.xml',
        'views/audit_request.xml',
        'views/audit_request_ispo.xml',
        'views/temuan_kan.xml',
        'views/qc_pass.xml',
        'views/cron_job_sertifikat.xml',
        'views/cron_job_sertifikat.xml',
        'wizards/wizard_quotation.xml',
        'wizards/wizard_quotation_form.xml',
        'wizards/wizard_quotation_ispo.xml',
        'wizards/wizard_quotation_app_ispo.xml',
        'wizards/account_move.xml',
        'wizards/wizard_audit.xml',
        'wizards/wizard_audit_request.xml',
        'wizards/wizard_audit_quotation.xml',
        'views/history_kontrak.xml',
        'views/kontrak_history.xml',
        'views/views.xml',
        'views/email_templates.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'v15_tsi/static/src/css/workflow.css',
            'v15_tsi/static/src/js/month_year_picker.js',
            'web/static/lib/jquery.ui/jquery-ui.js',
            'web/static/lib/jquery.ui/jquery-ui.css',
        ],
    },
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
