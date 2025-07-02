from base64 import standard_b64decode
from odoo import models, fields, api
from datetime import datetime, timedelta


class ISOReview(models.Model):
    _name           = "tsi.iso.review"
    _inherit        = ['mail.thread', 'mail.activity.mixin']
    _description    = "ISO Review"
    _order          = 'id DESC'

    def _get_default_iso(self):
        return self.env['sale.order'].search([('id','in',self.env.context.get('active_ids'))],limit=5).iso_standard_ids

    reference       = fields.Many2one('tsi.iso', string="Reference")
    sales_order_id = fields.Many2one('sale.order', string="Reference SO")
    doctype         = fields.Selection([
                            ('iso',  'ISO'),
                            ('ispo',   'ISPO'),
                        ], string='Doc Type', index=True, related='reference.doctype', store=True)

    customer        = fields.Many2one('res.partner', string="Customer", related='reference.customer', store=True)

    name            = fields.Char(string="Document No",  readonly=True)
    office_address      = fields.Char(string="Office Address", related="reference.office_address")
    invoicing_address   = fields.Char(string="Invoicing Address", related="reference.invoicing_address")
    received_date   = fields.Date(string="Issued Date", related="reference.issue_date", readonly=False)    
    review_date     = fields.Datetime(string="Verified Date", default=datetime.now(), readonly=False)    
    finish_date     = fields.Datetime(string="Approve Date", readonly=False,)    
    
    review_by       = fields.Many2one('res.users', string="Created By", related="reference.user_id")
    sales_person       = fields.Many2one('res.users', string="Sales Person", related="reference.sales_person")
    company_id = fields.Many2one('res.company', 'Company', required=True, index=True, default=lambda self: self.env.company)
    accreditation         = fields.Many2one('tsi.iso.accreditation', string="Accreditation")

    # company_name    = fields.Char(string="Company Name")
    # ea_code         = fields.Many2one(string="EA Code", related='reference.ea_code')
    contact_person  = fields.Char(string="Contact Person", related="reference.contact_person")
    jabatan         = fields.Char(string="Position", related="reference.jabatan")
    telepon         = fields.Char(string="Telephone", related="reference.telepon")
    fax             = fields.Char(string="Fax", related="reference.fax")
    email           = fields.Char(string="Email", related="reference.email")
    website         = fields.Char(string="Website", related="reference.website")
    cellular        = fields.Char(string="Celular", related="reference.cellular")
    # alt_scope       = fields.Text('Alt Scope', website_form_blacklisted=False)
    # alt_scope_id    = fields.Many2one('tsi.alt_scope',      string='Alt Scope')
    catatan             = fields.Text('Notes')

    scope           = fields.Text(string="Scope", related='reference.scope', store=True)
    boundaries  = fields.Text(string="Boundaries", related="reference.boundaries")
    cause       = fields.Text('Mandatory SNI', related='reference.cause')

    # personnel
    partner_site    = fields.One2many('tsi.iso.site', 'reference_id', string="Personnel Situation", index=True, related='reference.partner_site')
    head_office     = fields.Char(string="Head Office", )
    site_office     = fields.Char(string="Site Office", )
    off_location    = fields.Char(string="Off Location", )
    part_time       = fields.Char(string="Part Time", )
    subcon          = fields.Char(string="Sub Contractor", )
    unskilled       = fields.Char(string="Unskilled", )
    seasonal        = fields.Char(string="Seasonal", )
    total_emp       = fields.Char(string="Total Employee", )
    shift_number    = fields.Char(string="Shift", )
    number_site     = fields.Char(string="Number Site", )
    outsource_proc  = fields.Text('Outsourcing Process', )
    outsourced_activity = fields.Text(string="Outsourced Activity", )

    # maturity
    start_implement     = fields.Char(string="Start Implement", related='reference.start_implement')

    mat_consultancy     = fields.Selection([('YES', 'YES'),('NO', 'NO')], string="Use of Consultants", related='reference.mat_consultancy')
    mat_certified       = fields.Selection([('YES', 'YES'),('NO', 'NO')], string="Certified System", related='reference.mat_certified')
    other_system         = fields.Char(string='Other System', related='reference.other_system')
    # mat_certified_cb    = fields.Selection([('YES', 'YES'),('NO', 'NO')], string="Certified CB", )
    # mat_tools           = fields.Selection([('YES', 'YES'),('NO', 'NO')], string="Continual Improvement", )
    # mat_national        = fields.Selection([('YES', 'YES'),('NO', 'NO')], string="National Certified", )
    # mat_more            = fields.Selection([('YES', 'YES'),('NO', 'NO')], string="Setup More Standard", )

    txt_mat_consultancy = fields.Char(string="Tx Consultancy", related='reference.txt_mat_consultancy')
    txt_mat_certified   = fields.Char(string="Tx Certified", related='reference.txt_mat_certified')
    # txt_mat_certified_cb    = fields.Char(string="Tx Certified CB", )
    # txt_mat_tools       = fields.Char(string="Tx Continual Improvement", )
    # txt_mat_national    = fields.Char(string="Tx National Certified", )
    # txt_mat_more        = fields.Char(string="Tx Setup More Standard", )

    # integrated audit
    show_integreted_yes = fields.Boolean(string='Show YES', default=False)
    show_integreted_no  = fields.Boolean(string='Show NO', default=False)
    integreted_audit    = fields.Selection([('YES', 'YES'),('NO', 'NO')], string="Integrated Audit", related='reference.integreted_audit')
    int_review          = fields.Selection([('YES', 'YES'),('NO', 'NO')], string="Management Review", related='reference.int_review')
    int_internal        = fields.Selection([('YES', 'YES'),('NO', 'NO')], string="Internal Audit", related='reference.int_internal')
    int_policy          = fields.Selection([('YES', 'YES'),('NO', 'NO')], string="Risk & Opportunity Management", related='reference.int_policy')
    int_system          = fields.Selection([('YES', 'YES'),('NO', 'NO')], string="Responsibilities", related='reference.int_system')
    int_instruction     = fields.Selection([('YES', 'YES'),('PARTIAL', 'PARTIAL'),('NO', 'NO')], string="Procedures", related='reference.int_instruction')
    int_improvement     = fields.Selection([('YES', 'YES'),('PARTIAL', 'PARTIAL'),('NO', 'NO')], string="Work Instructions", related='reference.int_improvement')
    int_planning        = fields.Selection([('YES', 'YES'),('PARTIAL', 'PARTIAL'),('NO', 'NO')], string="Manual", related='reference.int_planning')
    # int_support         = fields.Selection([('YES', 'YES'),('NO', 'NO')], string="Supports", )

    
    stage_audit     = fields.Selection([
                            ('initial',         'Initial Assesment'),
                            ('recertification', 'Recertification'),
                            ('transfer_surveilance',    'Transfer Assesment from Surveilance'),
                            ('transfer_recert',         'Transfer Assesment from Recertification'),
                        ], string='Audit Stage', index=True, related="reference.audit_stage" )
    tx_site_count   = fields.Integer('Number of Site', )
    upload_file     = fields.Binary('Attachment', related="reference.upload_file")
    file_name       = fields.Char('Filename', related="reference.file_name")
    tx_remarks      = fields.Char('Remarks', related="reference.tx_remarks")
    certification   = fields.Selection([
                            ('Single Site',  'SINGLE SITE'),
                            ('Multi Site',   'MULTI SITE'),
                        ], string='Certification Type', index=True, readonly=True, related="reference.certification" )
    
    audit_type      = fields.Selection([
                            ('single',      'SINGLE AUDIT'),
                            ('join',        'JOIN AUDIT'),
                            ('combine',     'COMBINE AUDIT'),
                            ('integrated',  'INTEGRATED AUDIT'),
                        ], string='Audit Type', index=True)
    allowed_sampling    = fields.Char(string="Number of Sampling")

    proposed_aspect = fields.Char(string="Proposed Standard")
    proposed_desc   = fields.Char(string="Description")
    iso_standard_ids    = fields.Many2many('tsi.iso.standard', string='Standards', readonly=True, default=_get_default_iso,)

    # EMPLOYEE INFORMATION
    total_emp           = fields.Integer(string="Total Employee")
    site_emp_total      = fields.Integer(string='Total Site Employee')
    offsite_emp_total   = fields.Integer(string='Total OffSite Employee')
    ho_emp_total        = fields.Integer(string='Total HO Employee')
    number_of_site      = fields.Integer(string='Number of Site')

    mandays_ori_lines   = fields.One2many('tsi.iso.mandays', 'review_id', string="Mandays Original", index=True)
    mandays_isms_lines  = fields.One2many('tsi.iso.mandays.isms', 'review_id', string="Mandays ISMS", index=True)
    mandays_inte_lines  = fields.One2many('tsi.iso.mandays.integrated', 'review_id', string="Mandays Integrated", index=True)
    mandays_audit_time  = fields.One2many('tsi.iso.mandays.audit_time', 'review_id', string="Audit Time", index=True)
    mandays_justify     = fields.One2many('tsi.iso.mandays.justification', 'review_id', string="Justification", index=True)
    mandays_justify_isms     = fields.One2many('tsi.iso.mandays.justification.isms', 'review_id', string="Justification - ISMS", index=True)
    mandays_pa          = fields.One2many('tsi.iso.mandays.pa', 'review_id', string="PA", index=True)

# ISPO RELATED FIELD
    ispo_evaluasi       = fields.One2many('tsi.ispo.evaluasi', 'review_id', string="Evaluasi", index=True)
    ispo_nilai_skor     = fields.One2many('tsi.ispo.nilai_skor', 'review_id', string="Nilai Skor", index=True)
    ispo_justification  = fields.One2many('tsi.ispo.justification', 'review_id', string="Justification", index=True)
    ispo_mandays        = fields.One2many('tsi.ispo.mandays', 'review_id', string="Mandays", index=True)
    ispo_total_mandays  = fields.One2many('tsi.ispo.total_mandays', 'review_id', string="Total Mandays", index=True)

    sampling_pabrik     = fields.Boolean(string='Sampling Pabrik')
    sampling_kebun      = fields.Boolean(string='Sampling Kebun')


    state           = fields.Selection([
                            ('new',         'New'),
                            # ('review',      'Review'),
                            ('approved',    'Approved'),
                            ('revice',    'Revised'),
                            ('reject',      'Reject'),
                        ], string='Status', readonly=True, copy=False, index=True, tracking=True, default='new')
    
    # additional iso 14001
    iso_14001_environmental = fields.Text(string="Environmental Aspects", related='reference.iso_14001_environmental')
    iso_14001_legal         = fields.Text(string="14001 Legal Obligations", related='reference.iso_14001_legal')

    # additional iso 45001
    iso_45001_ohs           = fields.Text(string="OHS Risk", related='reference.iso_45001_ohs')
    iso_45001_legal         = fields.Text(string="45001 Legal Obligations", related='reference.iso_45001_legal')

    # additional iso 27001
    iso_27001_total_emp     = fields.Char(string='Total Employee', related='reference.iso_27001_total_emp')
    iso_27001_bisnistype    = fields.Selection([
                                ('A', 'Organization works in non-critical business sectors and non-regulated sectors'),
                                ('B', 'Organization has customers in critical business sectors'),
                                ('C', 'Organization works in critical business sectors')
                                ], string='Business type and regulatory requirements', related="reference.iso_27001_bisnistype")
    iso_27001_process       = fields.Selection([
                                ('A', 'Standard processes with standard and repetitive tasks; lots of persons doing work under the organization control carrying out the same tasks; few products or services'),
                                ('B', 'Standard but non-repetitive processes, with high number of products or services'),
                                ('C', 'Complex processes, high number of products and services, many business units included in the scope of certification')
                                ], string='Process and Task', related="reference.iso_27001_process")
    iso_27001_mgmt_system   = fields.Selection([
                                ('A', 'ISMS is already well established and/or other management systems are in place'),
                                ('B', 'Some elements of other management systems are implemented, others not'),
                                ('C', 'No other management system implemented at all, the ISMS is new and not established')
                                ], string='Management system establishment level', related="reference.iso_27001_mgmt_system" )
    iso_27001_number_process= fields.Selection([
                                ('A', 'Only one key business process with few interfaces and few business units involved'),
                                ('B', '2–3 simple business processes with few interfaces and few business units involved'),
                                ('C', 'More than 2 complex processes with many interfaces and business units involved')
                                ], string='Number of processes and services', related="reference.iso_27001_number_process")
    iso_27001_infra         = fields.Selection([
                                ('A', 'Few or highly standardized IT platforms, servers, operating systems, databases, networks, etc'),
                                ('B', 'Several different IT platforms, servers, operating systems, databases, networks'),
                                ('C', 'Many different IT platforms, servers, operating systems, databases, networks')
                                ], string='IT infrastructure complexity', related="reference.iso_27001_infra")
    iso_27001_sourcing      = fields.Selection([
                                ('A', 'Little or no dependency on outsourcing or suppliers'),
                                ('B', 'Some dependency on outsourcing or suppliers, related to some but not all important business activities'),
                                ('C', 'High dependency on outsourcing or suppliers, large impact on important business activities')
                                ], string='Dependency on outsourcing and suppliers, including cloud services', related="reference.iso_27001_sourcing")
    iso_27001_itdevelopment = fields.Selection([
                                ('A', 'None or a very limited in-house system/application development'),
                                ('B', 'Some in-house or outsourced system/application development for some important business purposes'),
                                ('C', 'Extensive in-house or outsourced system/application development for important business purposes')
                                ], string='Information System development', related="reference.iso_27001_itdevelopment")
    iso_27001_itsecurity    = fields.Selection([
                                ('A', 'Only little sensitive or confidential information, low availability requirements'),
                                ('B', 'Higher availability requirements or some sensitive / confidential information'),
                                ('C', 'Higher amount of sensitive or confidential information or high availability requirements')
                                ], string='	Information security requirements confidentiality, integrity and availability(CIA)', related="reference.iso_27001_itsecurity")
    iso_27001_asset         = fields.Selection([
                                ('A', 'Few critical assets (in terms of CIA)'),
                                ('B', 'Some critical assets'),
                                ('C', 'Many critical assets')
                                ], string='Number of critical assets', related="reference.iso_27001_asset")
    iso_27001_drc           = fields.Selection([
                                ('A', 'Low availability requirements and no or one alternative DR site'),
                                ('B', 'Medium or High availability requirements and no or one alternative DR site'),
                                ('C', 'High availability requirements e.g. 24/7 services, Several alternative DR sites,Several Data Centers')
                                ], string='Number of sites and number of Disaster Recovery (DR) sites', related="reference.iso_27001_drc")
    
    # additional iso 27001:2022
    iso_27001_bisnistype_2022    = fields.Selection([
                                ('A', 'Organization works in non-critical business sectors and non-regulated sectors'),
                                ('B', 'Organization has customers in critical business sectors'),
                                ('C', 'Organization works in critical business sectors')
                                ], string='Business type and regulatory requirements', related="reference.iso_27001_bisnistype_2022")
    iso_27001_process_2022       = fields.Selection([
                                ('A', 'Standard processes with standard and repetitive tasks; lots of persons doing work under the organization control carrying out the same tasks; few products or services'),
                                ('B', 'Standard but non-repetitive processes, with high number of products or services'),
                                ('C', 'Complex processes, high number of products and services, many business units included in the scope of certification')
                                ], string='Process and Task', related="reference.iso_27001_process_2022")
    iso_27001_mgmt_system_2022   = fields.Selection([
                                ('A', 'ISMS is already well established and/or other management systems are in place'),
                                ('B', 'Some elements of other management systems are implemented, others not'),
                                ('C', 'No other management system implemented at all, the ISMS is new and not established')
                                ], string='Management system establishment level', related="reference.iso_27001_mgmt_system_2022")
    iso_27001_number_process_2022= fields.Selection([
                                ('A', 'Only one key business process with few interfaces and few business units involved'),
                                ('B', '2–3 simple business processes with few interfaces and few business units involved'),
                                ('C', 'More than 2 complex processes with many interfaces and business units involved')
                                ], string='Number of processes and services', related="reference.iso_27001_number_process_2022")
    iso_27001_infra_2022         = fields.Selection([
                                ('A', 'Few or highly standardized IT platforms, servers, operating systems, databases, networks, etc'),
                                ('B', 'Several different IT platforms, servers, operating systems, databases, networks'),
                                ('C', 'Many different IT platforms, servers, operating systems, databases, networks')
                                ], string='IT infrastructure complexity', related="reference.iso_27001_infra_2022")
    iso_27001_sourcing_2022      = fields.Selection([
                                ('A', 'Little or no dependency on outsourcing or suppliers'),
                                ('B', 'Some dependency on outsourcing or suppliers, related to some but not all important business activities'),
                                ('C', 'High dependency on outsourcing or suppliers, large impact on important business activities')
                                ], string='Dependency on outsourcing and suppliers, including cloud services', related="reference.iso_27001_sourcing_2022")
    iso_27001_itdevelopment_2022 = fields.Selection([
                                ('A', 'None or a very limited in-house system/application development'),
                                ('B', 'Some in-house or outsourced system/application development for some important business purposes'),
                                ('C', 'Extensive in-house or outsourced system/application development for important business purposes')
                                ], string='Information System development', related="reference.iso_27001_itdevelopment_2022")
    iso_27001_itsecurity_2022    = fields.Selection([
                                ('A', 'Only little sensitive or confidential information, low availability requirements'),
                                ('B', 'Higher availability requirements or some sensitive / confidential information'),
                                ('C', 'Higher amount of sensitive or confidential information or high availability requirements')
                                ], string='	Information security requirements confidentiality, integrity and availability(CIA)', related="reference.iso_27001_itsecurity_2022")
    iso_27001_asset_2022         = fields.Selection([
                                ('A', 'Few critical assets (in terms of CIA)'),
                                ('B', 'Some critical assets'),
                                ('C', 'Many critical assets')
                                ], string='Number of critical assets', related="reference.iso_27001_asset_2022")
    iso_27001_drc_2022           = fields.Selection([
                                ('A', 'Low availability requirements and no or one alternative DR site'),
                                ('B', 'Medium or High availability requirements and no or one alternative DR site'),
                                ('C', 'High availability requirements e.g. 24/7 services, Several alternative DR sites,Several Data Centers')
                                ], string='Number of sites and number of Disaster Recovery (DR) sites', related="reference.iso_27001_drc_2022")
    
    # additional iso 27018
    iso_27001_bisnistype_27018    = fields.Selection([
                                ('A', 'Organization works in non-critical business sectors and non-regulated sectors'),
                                ('B', 'Organization has customers in critical business sectors'),
                                ('C', 'Organization works in critical business sectors')
                                ], string='Business type and regulatory requirements', related="reference.iso_27001_bisnistype_27018")
    iso_27001_process_27018       = fields.Selection([
                                ('A', 'Standard processes with standard and repetitive tasks; lots of persons doing work under the organization control carrying out the same tasks; few products or services'),
                                ('B', 'Standard but non-repetitive processes, with high number of products or services'),
                                ('C', 'Complex processes, high number of products and services, many business units included in the scope of certification')
                                ], string='Process and Task', related="reference.iso_27001_process_27018")
    iso_27001_mgmt_system_27018   = fields.Selection([
                                ('A', 'ISMS is already well established and/or other management systems are in place'),
                                ('B', 'Some elements of other management systems are implemented, others not'),
                                ('C', 'No other management system implemented at all, the ISMS is new and not established')
                                ], string='Management system establishment level', related="reference.iso_27001_mgmt_system_27018")
    iso_27001_number_process_27018= fields.Selection([
                                ('A', 'Only one key business process with few interfaces and few business units involved'),
                                ('B', '2–3 simple business processes with few interfaces and few business units involved'),
                                ('C', 'More than 2 complex processes with many interfaces and business units involved')
                                ], string='Number of processes and services', related="reference.iso_27001_number_process_27018")
    iso_27001_infra_27018         = fields.Selection([
                                ('A', 'Few or highly standardized IT platforms, servers, operating systems, databases, networks, etc'),
                                ('B', 'Several different IT platforms, servers, operating systems, databases, networks'),
                                ('C', 'Many different IT platforms, servers, operating systems, databases, networks')
                                ], string='IT infrastructure complexity', related="reference.iso_27001_infra_27018")
    iso_27001_sourcing_27018      = fields.Selection([
                                ('A', 'Little or no dependency on outsourcing or suppliers'),
                                ('B', 'Some dependency on outsourcing or suppliers, related to some but not all important business activities'),
                                ('C', 'High dependency on outsourcing or suppliers, large impact on important business activities')
                                ], string='Dependency on outsourcing and suppliers, including cloud services', related="reference.iso_27001_sourcing_27018")
    iso_27001_itdevelopment_27018 = fields.Selection([
                                ('A', 'None or a very limited in-house system/application development'),
                                ('B', 'Some in-house or outsourced system/application development for some important business purposes'),
                                ('C', 'Extensive in-house or outsourced system/application development for important business purposes')
                                ], string='Information System development', related="reference.iso_27001_itdevelopment_27018")
    iso_27001_itsecurity_27018    = fields.Selection([
                                ('A', 'Only little sensitive or confidential information, low availability requirements'),
                                ('B', 'Higher availability requirements or some sensitive / confidential information'),
                                ('C', 'Higher amount of sensitive or confidential information or high availability requirements')
                                ], string='	Information security requirements confidentiality, integrity and availability(CIA)', related="reference.iso_27001_itsecurity_27018")
    iso_27001_asset_27018         = fields.Selection([
                                ('A', 'Few critical assets (in terms of CIA)'),
                                ('B', 'Some critical assets'),
                                ('C', 'Many critical assets')
                                ], string='Number of critical assets', related="reference.iso_27001_asset_27018")
    iso_27001_drc_27018           = fields.Selection([
                                ('A', 'Low availability requirements and no or one alternative DR site'),
                                ('B', 'Medium or High availability requirements and no or one alternative DR site'),
                                ('C', 'High availability requirements e.g. 24/7 services, Several alternative DR sites,Several Data Centers')
                                ], string='Number of sites and number of Disaster Recovery (DR) sites', related="reference.iso_27001_drc_27018")
    
    # additional iso 27017
    iso_27001_bisnistype_27017    = fields.Selection([
                                ('A', 'Organization works in non-critical business sectors and non-regulated sectors'),
                                ('B', 'Organization has customers in critical business sectors'),
                                ('C', 'Organization works in critical business sectors')
                                ], string='Business type and regulatory requirements', related="reference.iso_27001_bisnistype_27017")
    iso_27001_process_27017       = fields.Selection([
                                ('A', 'Standard processes with standard and repetitive tasks; lots of persons doing work under the organization control carrying out the same tasks; few products or services'),
                                ('B', 'Standard but non-repetitive processes, with high number of products or services'),
                                ('C', 'Complex processes, high number of products and services, many business units included in the scope of certification')
                                ], string='Process and Task', related="reference.iso_27001_process_27017")
    iso_27001_mgmt_system_27017   = fields.Selection([
                                ('A', 'ISMS is already well established and/or other management systems are in place'),
                                ('B', 'Some elements of other management systems are implemented, others not'),
                                ('C', 'No other management system implemented at all, the ISMS is new and not established')
                                ], string='Management system establishment level', related="reference.iso_27001_mgmt_system_27017")
    iso_27001_number_process_27017= fields.Selection([
                                ('A', 'Only one key business process with few interfaces and few business units involved'),
                                ('B', '2–3 simple business processes with few interfaces and few business units involved'),
                                ('C', 'More than 2 complex processes with many interfaces and business units involved')
                                ], string='Number of processes and services', related="reference.iso_27001_number_process_27017" )
    iso_27001_infra_27017         = fields.Selection([
                                ('A', 'Few or highly standardized IT platforms, servers, operating systems, databases, networks, etc'),
                                ('B', 'Several different IT platforms, servers, operating systems, databases, networks'),
                                ('C', 'Many different IT platforms, servers, operating systems, databases, networks')
                                ], string='IT infrastructure complexity', related="reference.iso_27001_infra_27017")
    iso_27001_sourcing_27017      = fields.Selection([
                                ('A', 'Little or no dependency on outsourcing or suppliers'),
                                ('B', 'Some dependency on outsourcing or suppliers, related to some but not all important business activities'),
                                ('C', 'High dependency on outsourcing or suppliers, large impact on important business activities')
                                ], string='Dependency on outsourcing and suppliers, including cloud services', related="reference.iso_27001_sourcing_27017")
    iso_27001_itdevelopment_27017 = fields.Selection([
                                ('A', 'None or a very limited in-house system/application development'),
                                ('B', 'Some in-house or outsourced system/application development for some important business purposes'),
                                ('C', 'Extensive in-house or outsourced system/application development for important business purposes')
                                ], string='Information System development', related="reference.iso_27001_itdevelopment_27017")
    iso_27001_itsecurity_27017    = fields.Selection([
                                ('A', 'Only little sensitive or confidential information, low availability requirements'),
                                ('B', 'Higher availability requirements or some sensitive / confidential information'),
                                ('C', 'Higher amount of sensitive or confidential information or high availability requirements')
                                ], string='	Information security requirements confidentiality, integrity and availability(CIA)', related="reference.iso_27001_itsecurity_27017")
    iso_27001_asset_27017         = fields.Selection([
                                ('A', 'Few critical assets (in terms of CIA)'),
                                ('B', 'Some critical assets'),
                                ('C', 'Many critical assets')
                                ], string='Number of critical assets', related="reference.iso_27001_asset_27017")
    iso_27001_drc_27017           = fields.Selection([
                                ('A', 'Low availability requirements and no or one alternative DR site'),
                                ('B', 'Medium or High availability requirements and no or one alternative DR site'),
                                ('C', 'High availability requirements e.g. 24/7 services, Several alternative DR sites,Several Data Centers')
                                ], string='Number of sites and number of Disaster Recovery (DR) sites', related="reference.iso_27001_drc_27017")
    
    # additional iso 27701
    iso_27001_bisnistype_27701    = fields.Selection([
                                ('A', 'Organization works in non-critical business sectors and non-regulated sectors'),
                                ('B', 'Organization has customers in critical business sectors'),
                                ('C', 'Organization works in critical business sectors')
                                ], string='Business type and regulatory requirements', related="reference.iso_27001_bisnistype_27701")
    iso_27001_process_27701       = fields.Selection([
                                ('A', 'Standard processes with standard and repetitive tasks; lots of persons doing work under the organization control carrying out the same tasks; few products or services'),
                                ('B', 'Standard but non-repetitive processes, with high number of products or services'),
                                ('C', 'Complex processes, high number of products and services, many business units included in the scope of certification')
                                ], string='Process and Task', related="reference.iso_27001_process_27701")
    iso_27001_mgmt_system_27701   = fields.Selection([
                                ('A', 'ISMS is already well established and/or other management systems are in place'),
                                ('B', 'Some elements of other management systems are implemented, others not'),
                                ('C', 'No other management system implemented at all, the ISMS is new and not established')
                                ], string='Management system establishment level', related="reference.iso_27001_mgmt_system_27701")
    iso_27001_number_process_27701= fields.Selection([
                                ('A', 'Only one key business process with few interfaces and few business units involved'),
                                ('B', '2–3 simple business processes with few interfaces and few business units involved'),
                                ('C', 'More than 2 complex processes with many interfaces and business units involved')
                                ], string='Number of processes and services', related="reference.iso_27001_number_process_27701")
    iso_27001_infra_27701         = fields.Selection([
                                ('A', 'Few or highly standardized IT platforms, servers, operating systems, databases, networks, etc'),
                                ('B', 'Several different IT platforms, servers, operating systems, databases, networks'),
                                ('C', 'Many different IT platforms, servers, operating systems, databases, networks')
                                ], string='IT infrastructure complexity', related="reference.iso_27001_infra_27701")
    iso_27001_sourcing_27701      = fields.Selection([
                                ('A', 'Little or no dependency on outsourcing or suppliers'),
                                ('B', 'Some dependency on outsourcing or suppliers, related to some but not all important business activities'),
                                ('C', 'High dependency on outsourcing or suppliers, large impact on important business activities')
                                ], string='Dependency on outsourcing and suppliers, including cloud services', related="reference.iso_27001_sourcing_27701")
    iso_27001_itdevelopment_27701 = fields.Selection([
                                ('A', 'None or a very limited in-house system/application development'),
                                ('B', 'Some in-house or outsourced system/application development for some important business purposes'),
                                ('C', 'Extensive in-house or outsourced system/application development for important business purposes')
                                ], string='Information System development', related="reference.iso_27001_itdevelopment_27701")
    iso_27001_itsecurity_27701    = fields.Selection([
                                ('A', 'Only little sensitive or confidential information, low availability requirements'),
                                ('B', 'Higher availability requirements or some sensitive / confidential information'),
                                ('C', 'Higher amount of sensitive or confidential information or high availability requirements')
                                ], string='	Information security requirements confidentiality, integrity and availability(CIA)', related="reference.iso_27001_itsecurity_27701")
    iso_27001_asset_27701         = fields.Selection([
                                ('A', 'Few critical assets (in terms of CIA)'),
                                ('B', 'Some critical assets'),
                                ('C', 'Many critical assets')
                                ], string='Number of critical assets', related="reference.iso_27001_asset_27701")
    iso_27001_drc_27701           = fields.Selection([
                                ('A', 'Low availability requirements and no or one alternative DR site'),
                                ('B', 'Medium or High availability requirements and no or one alternative DR site'),
                                ('C', 'High availability requirements e.g. 24/7 services, Several alternative DR sites,Several Data Centers')
                                ], string='Number of sites and number of Disaster Recovery (DR) sites', related="reference.iso_27001_drc_27701")
    
    # additional iso 22000:2018 
    iso_22000_hazard_no     = fields.Char(string='Total No of Hazard', related='reference.iso_22000_hazard_no')
    iso_22000_hazard_desc   = fields.Text(string='Hazard Description', related='reference.iso_22000_hazard_desc')
    iso_22000_process_no    = fields.Char(string='Total No of Process', related='reference.iso_22000_process_no')
    iso_22000_process_desc  = fields.Text(string='Process Description', related='reference.iso_22000_process_desc')
    iso_22000_tech_no       = fields.Char(string='Total No of Tech', related='reference.iso_22000_tech_no')
    iso_22000_tech_desc     = fields.Text(string='Tech Description', related='reference.iso_22000_tech_desc')
    
    # ea_code             = fields.Many2one('tsi.ea_code', string="EA Code", related='reference.ea_code')
    ea_code_9001        = fields.Many2many('tsi.ea_code', 'rel_tsi_iso_review_ea_9001', string="EA Code Existing", related="reference.ea_code_9001")
    accreditation       = fields.Many2one('tsi.iso.accreditation', string="Accreditation", related='reference.accreditation')
    complexity          = fields.Selection([
                            ('Na',  'NA'),
                            ('Limited',   'Limited'),
                            ('Low',   'Low'),
                            ('Medium',   'Medium'),
                            ('High',   'High'),
                        ], string='Complexity' ,related='reference.complexity')

    # ea_code_14001           = fields.Many2one('tsi.ea_code', string="EA Code", related='reference.ea_code_14001')
    ea_code_14001_1        = fields.Many2many('tsi.ea_code', 'rel_tsi_iso_review_ea_14001', string="EA Code Existing", related="reference.ea_code_14001_1")
    accreditation_14001     = fields.Many2one('tsi.iso.accreditation', string="Accreditation", related='reference.accreditation_14001')
    complexity_14001        = fields.Selection([
                            ('Na',  'NA'),
                            ('Limited',   'Limited'),
                            ('Low',   'Low'),
                            ('Medium',   'Medium'),
                            ('High',   'High'),
                        ], string='Complexity' ,related='reference.complexity_14001')
    salesinfo_site_14001    = fields.One2many('tsi.iso.additional_salesinfo', 'reference_id2', string="Additional Info", index=True, related='reference.salesinfo_site_14001')

    # ea_code_27001           = fields.Many2one('tsi.ea_code', string="EA Code", )
    ea_code_27001_1        = fields.Many2many('tsi.ea_code', 'rel_tsi_iso_review_ea_27001', string="EA Code Existing", related="reference.ea_code_27001_1")
    accreditation_27001     = fields.Many2one('tsi.iso.accreditation', string="Accreditation", related='reference.accreditation_27001')
    complexity_27001        = fields.Selection([
                            ('Na',  'NA'),
                            ('Limited',   'Limited'),
                            ('Low',   'Low'),
                            ('Medium',   'Medium'),
                            ('High',   'High'),
                        ], string='Complexity' ,related='reference.complexity_27001')
    salesinfo_site_27001    = fields.One2many('tsi.iso.additional_salesinfo', 'reference_id3', string="Additional Info", index=True, related='reference.salesinfo_site_27001')

    #ISO27001:2022
    # ea_code_27001_2022           = fields.Many2one('tsi.ea_code', string="EA Code", related='reference.ea_code_27001_2022')
    ea_code_27001_2022_1        = fields.Many2many('tsi.ea_code', 'rel_tsi_iso_review_ea_27001_2022', string="EA Code Existing", related="reference.ea_code_27001_2022_1")
    accreditation_27001_2022     = fields.Many2one('tsi.iso.accreditation', string="Accreditation", related='reference.accreditation_27001_2022')
    complexity_27001_2022        = fields.Selection([
                            ('Na',  'NA'),
                            ('Limited',   'Limited'),
                            ('Low',   'Low'),
                            ('Medium',   'Medium'),
                            ('High',   'High'),
                        ], string='Complexity', index=True, related='reference.complexity_27001_2022')
    salesinfo_site_27001_2022    = fields.One2many('tsi.iso.additional_salesinfo', 'reference_id12', string="Additional Info", index=True, related='reference.salesinfo_site_27001_2022')

    #ISO27017
    # ea_code_27017           = fields.Many2one('tsi.ea_code', string="EA Code", related='reference.ea_code_27017')
    ea_code_27017_1        = fields.Many2many('tsi.ea_code', 'rel_tsi_iso_review_ea_27017', string="EA Code Existing", related="reference.ea_code_27017_1")
    accreditation_27017     = fields.Many2one('tsi.iso.accreditation', string="Accreditation", related='reference.accreditation_27017')
    complexity_27017        = fields.Selection([
                            ('Na',  'NA'),
                            ('Limited',   'Limited'),
                            ('Low',   'Low'),
                            ('Medium',   'Medium'),
                            ('High',   'High'),
                        ], string='Complexity', index=True, related='reference.complexity_27017', )
    salesinfo_site_27017    = fields.One2many('tsi.iso.additional_salesinfo', 'reference_id13', string="Additional Info", index=True, related='reference.salesinfo_site_27017')

    #ISO27018
    # ea_code_27018           = fields.Many2one('tsi.ea_code', string="EA Code", related='reference.ea_code_27018')
    ea_code_27018_1        = fields.Many2many('tsi.ea_code', 'rel_tsi_iso_review_ea_27018', string="EA Code Existing", related="reference.ea_code_27018_1")
    accreditation_27018     = fields.Many2one('tsi.iso.accreditation', string="Accreditation", related='reference.accreditation_27018')
    complexity_27018        = fields.Selection([
                            ('Na',  'NA'),
                            ('Limited',   'Limited'),
                            ('Low',   'Low'),
                            ('Medium',   'Medium'),
                            ('High',   'High'),
                        ], string='Complexity', index=True, related='reference.complexity_27018', )
    salesinfo_site_27018    = fields.One2many('tsi.iso.additional_salesinfo', 'reference_id14', string="Additional Info", index=True, related='reference.salesinfo_site_27018')

    #ISO27701
    # ea_code_27701           = fields.Many2one('tsi.ea_code', string="EA Code", related='reference.ea_code_27701')
    ea_code_27701_1        = fields.Many2many('tsi.ea_code', 'rel_tsi_iso_review_ea_27701', string="EA Code Existing", related="reference.ea_code_27701_1")
    accreditation_27701     = fields.Many2one('tsi.iso.accreditation', string="Accreditation", related='reference.accreditation_27701')
    complexity_27701        = fields.Selection([
                            ('Na',  'NA'),
                            ('Limited',   'Limited'),
                            ('Low',   'Low'),
                            ('Medium',   'Medium'),
                            ('High',   'High'),
                        ], string='Complexity', index=True, related='reference.complexity_27701', )
    salesinfo_site_27701    = fields.One2many('tsi.iso.additional_salesinfo', 'reference_id15', string="Additional Info", index=True, related='reference.salesinfo_site_27701')

    # ea_code_45001           = fields.Many2one('tsi.ea_code', string="EA Code", )
    ea_code_45001_1        = fields.Many2many('tsi.ea_code', 'rel_tsi_iso_review_ea_45001', string="EA Code Existing", related="reference.ea_code_45001_1")
    accreditation_45001     = fields.Many2one('tsi.iso.accreditation', string="Accreditation", related='reference.accreditation_45001')
    complexity_45001        = fields.Selection([
                            ('Na',  'NA'),
                            ('Limited',   'Limited'),
                            ('Low',   'Low'),
                            ('Medium',   'Medium'),
                            ('High',   'High'),
                        ], string='Complexity' ,related='reference.complexity_45001')
    salesinfo_site_45001    = fields.One2many('tsi.iso.additional_salesinfo', 'reference_id4', string="Additional Info", index=True, related='reference.salesinfo_site_45001')

    show_31000          = fields.Boolean(string='Show 31000', default=False)    
    salesinfo_site_31000    = fields.One2many('tsi.iso.additional_salesinfo', 'reference_id7', string="Additional Info", index=True)

    show_9994          = fields.Boolean(string='Show 9994', default=False)
    salesinfo_site_9994    = fields.One2many('tsi.iso.additional_salesinfo', 'reference_id8', string="Additional Info", index=True)

    food_category_22000           = fields.Many2one('tsi.food_category', string="Food Category", related='reference.food_category_22000')
    accreditation_22000     = fields.Many2one('tsi.iso.accreditation', string="Accreditation", related='reference.accreditation_22000')
    complexity_22000        = fields.Selection([
                            ('Na',  'NA'),
                            ('Limited',   'Limited'),
                            ('Low',   'Low'),
                            ('Medium',   'Medium'),
                            ('High',   'High'),
                        ], string='Complexity' ,related='reference.complexity_22000')
    salesinfo_site_22000    = fields.One2many('tsi.iso.additional_salesinfo', 'reference_id5', string="Additional Info", index=True, related='reference.salesinfo_site_22000')

    ea_code_haccp           = fields.Many2one('tsi.ea_code', string="EA Code", )
    accreditation_haccp     = fields.Many2one('tsi.iso.accreditation', string="Accreditation", related='reference.accreditation_haccp')
    complexity_haccp        = fields.Selection([
                            ('Na',  'NA'),
                            ('Limited',   'Limited'),
                            ('Low',   'Low'),
                            ('Medium',   'Medium'),
                            ('High',   'High'),
                        ], string='Complexity' ,related='reference.complexity_haccp')
    salesinfo_site_haccp    = fields.One2many('tsi.iso.additional_salesinfo', 'reference_id6', string="Additional Info", index=True, related='reference.salesinfo_site_haccp')
    
    show_salesinfo      = fields.Boolean(string='Additional Info', default=False, related="reference.show_salesinfo")
    salesinfo_site      = fields.One2many('tsi.iso.additional_salesinfo', 'reference_id', string="Additional Info", index=True, related='reference.salesinfo_site')
    
    show_14001          = fields.Boolean(string='Show 14001', default=False)    
    iso_14001_env_aspect    = fields.Text(string='Environmental Aspects', related='reference.iso_14001_env_aspect')
    iso_14001_obligation    = fields.Text(string='14001 Legal Obligation', related='reference.iso_14001_obligation')

    show_45001          = fields.Boolean(string='Show 45001', default=False)    
    iso_45001_key_hazard    = fields.Text(string='Significant Risk', )
    iso_45001_obligation    = fields.Text(string='Obligation', )

    show_gdp        = fields.Boolean(string='Show GDP', default=False, related="reference.show_gdp")
    ea_code_gdp        = fields.Many2many('tsi.ea_code', 'rel_tsi_iso_ea_gdp', string="EA Code Existing", related="reference.ea_code_gdp")
    accreditation_gdp       = fields.Many2one('tsi.iso.accreditation', string="Accreditation", related="reference.accreditation_gdp")
    complexity_gdp          = fields.Selection([
                            ('Na',  'NA'),
                            ('Limited',   'Limited'),
                            ('Low',   'Low'),
                            ('Medium',   'Medium'),
                            ('High',   'High'),
                        ], string='Complexity', index=True, related="reference.complexity_gdp" )
    salesinfo_site_gdp    = fields.One2many('tsi.iso.additional_salesinfo', 'reference_id17', string="Additional Info", index=True, related="reference.salesinfo_site_gdp")

    show_56001        = fields.Boolean(string='Show GDP', default=False, related="reference.show_56001")
    ea_code_56001        = fields.Many2many('tsi.ea_code', 'rel_tsi_iso_ea_56001', string="EA Code Existing", related="reference.ea_code_56001")
    accreditation_56001       = fields.Many2one('tsi.iso.accreditation', string="Accreditation", related="reference.accreditation_56001")
    complexity_56001          = fields.Selection([
                            ('Na',  'NA'),
                            ('Limited',   'Limited'),
                            ('Low',   'Low'),
                            ('Medium',   'Medium'),
                            ('High',   'High'),
                        ], string='Complexity', index=True, related="reference.complexity_56001" )
    salesinfo_site_56001    = fields.One2many('tsi.iso.additional_salesinfo', 'reference_id18', string="Additional Info", index=True, related="reference.salesinfo_site_56001")

    show_27001          = fields.Boolean(string='Show 27001', default=False, related="reference.show_27001")
    show_27701          = fields.Boolean(string='Show 27701', default=False, related="reference.show_27701") 
    show_27017          = fields.Boolean(string='Show 27017', default=False, related="reference.show_27017") 
    show_27018          = fields.Boolean(string='Show 27018', default=False, related="reference.show_27018") 
    show_27001_2022          = fields.Boolean(string='Show 27001', default=False, related="reference.show_27001_2022")    
    additional_27001    = fields.One2many('tsi.iso.additional_27001', 'reference_id', string="Additional Info for ISO 27001", index=True, related='reference.additional_27001')
    additional_27701    = fields.One2many('tsi.iso.additional_27001', 'reference_id3', string="Additional Info for ISO 27701", index=True, related='reference.additional_27701')
    additional_27017    = fields.One2many('tsi.iso.additional_27001', 'reference_id1', string="Additional Info for ISO 27017", index=True, related='reference.additional_27017')
    additional_27018    = fields.One2many('tsi.iso.additional_27001', 'reference_id2', string="Additional Info for ISO 27018", index=True, related='reference.additional_27018')

    show_37001        = fields.Boolean(string='Show 31000', default=False, related="reference.show_37001")
    salesinfo_site_37001    = fields.One2many('tsi.iso.additional_salesinfo', 'reference_id9', string="Additional Info", index=True, related='reference.salesinfo_site_37001')
    accreditation_37001     = fields.Many2one('tsi.iso.accreditation', string="Accreditation" , related="reference.accreditation_37001")
    notes_37001     = fields.Char('Notes', related="reference.notes_37001")

    show_22301        = fields.Boolean(string='Show 22301', default=False, related="reference.show_22301")
    salesinfo_site_22301    = fields.One2many('tsi.iso.additional_salesinfo', 'reference_id16', string="Additional Info", index=True, related="reference.salesinfo_site_22301")
    accreditation_22301     = fields.Many2one('tsi.iso.accreditation', string="Accreditation", related="reference.accreditation_22301")
    notes_22301     = fields.Char(string='Notes', related="reference.notes_22301")

    show_13485        = fields.Boolean(string='Show 13485', default=False, related="reference.show_13485")
    show_37301        = fields.Boolean(string='Show 37301', default=False, related="reference.show_37301")
    show_smk        = fields.Boolean(string='Show SMK', default=False, related="reference.show_smk")
    show_19649        = fields.Boolean(string='Show 19649', default=False, related="reference.show_19649")
    show_ce        = fields.Boolean(string='Show CE', default=False, related="reference.show_ce")
    show_19650        = fields.Boolean(string='Show 19650', default=False, related="reference.show_19650")
    show_196502        = fields.Boolean(string='Show 19650', default=False, related="reference.show_196502")
    show_196503        = fields.Boolean(string='Show 19650', default=False, related="reference.show_196503")
    show_196504        = fields.Boolean(string='Show 19650', default=False, related="reference.show_196504")
    show_196505        = fields.Boolean(string='Show 19650', default=False, related="reference.show_196505")
    show_21000        = fields.Boolean(string='Show 21000', default=False, related="reference.show_21000")
    salesinfo_site_13485    = fields.One2many('tsi.iso.additional_salesinfo', 'reference_id11', string="Additional Info", index=True,related="reference.salesinfo_site_13485")
    salesinfo_site_19649    = fields.One2many('tsi.iso.additional_salesinfo', string="Additional Info", index=True,related="reference.salesinfo_site_19649")
    salesinfo_site_ce    = fields.One2many('tsi.iso.additional_salesinfo', 'reference_id19', string="Additional Info", index=True,related="reference.salesinfo_site_ce")
    salesinfo_site_19650    = fields.One2many('tsi.iso.additional_salesinfo', string="Additional Info", index=True,related="reference.salesinfo_site_19650")
    salesinfo_site_196502    = fields.One2many('tsi.iso.additional_salesinfo', string="Additional Info", index=True,related="reference.salesinfo_site_196502")
    salesinfo_site_196503    = fields.One2many('tsi.iso.additional_salesinfo', string="Additional Info", index=True,related="reference.salesinfo_site_196503")
    salesinfo_site_196504    = fields.One2many('tsi.iso.additional_salesinfo', string="Additional Info", index=True,related="reference.salesinfo_site_196504")
    salesinfo_site_196505    = fields.One2many('tsi.iso.additional_salesinfo', string="Additional Info", index=True,related="reference.salesinfo_site_196505")
    # ea_code_13485             = fields.Many2one('tsi.ea_code', string="EA Code", related="reference.ea_code_13485")
    ea_code_13485_1        = fields.Many2many('tsi.ea_code', 'rel_tsi_iso_review_ea_13485', string="EA Code Existing", related="reference.ea_code_13485_1")
    accreditation_13485       = fields.Many2one('tsi.iso.accreditation', string="Accreditation",related="reference.accreditation_13485")
    accreditation_19649       = fields.Many2one('tsi.iso.accreditation', string="Accreditation",related="reference.accreditation_19649")
    accreditation_ce       = fields.Many2one('tsi.iso.accreditation', string="Accreditation",related="reference.accreditation_ce")
    accreditation_19650       = fields.Many2one('tsi.iso.accreditation', string="Accreditation",related="reference.accreditation_19650")
    accreditation_196502       = fields.Many2one('tsi.iso.accreditation', string="Accreditation",related="reference.accreditation_196502")
    accreditation_196503       = fields.Many2one('tsi.iso.accreditation', string="Accreditation",related="reference.accreditation_196503")
    accreditation_196504       = fields.Many2one('tsi.iso.accreditation', string="Accreditation",related="reference.accreditation_196504")
    accreditation_196505       = fields.Many2one('tsi.iso.accreditation', string="Accreditation",related="reference.accreditation_196505")
    complexity_13485          = fields.Selection([
                            ('Na',  'NA'),
                            ('Limited',   'Limited'),
                            ('Low',   'Low'),
                            ('Medium',   'Medium'),
                            ('High',   'High'),
                        ], string='Complexity', index=True,  related="reference.complexity_13485")
    cause_13485       = fields.Text('Mandatory SNI', related="reference.cause_13485")
    notes_19649       = fields.Text('Mandatory SNI', related="reference.notes_19649")
    notes_13485       = fields.Text('Notes', related="reference.notes_13485" )
    notes_ce       = fields.Text('Notes', related="reference.notes_ce" )
    notes_19650       = fields.Text('Notes', related="reference.notes_19650" )
    notes_196502       = fields.Text('Notes', related="reference.notes_196502" )
    notes_196503       = fields.Text('Notes', related="reference.notes_196503" )
    notes_196504       = fields.Text('Notes', related="reference.notes_196504" )
    notes_196505       = fields.Text('Notes', related="reference.notes_196505" )
    show_21000        = fields.Boolean(string='Show 13485', default=False)
    akre            = fields.Many2one('tsi.iso.accreditation', string="Accreditation", related="reference.akre")
    specific        = fields.Char(string='Specific Requirements', related="reference.specific")
    additional      = fields.Char(string='Additional Notes', related="reference.additional")

    show_haccp          = fields.Boolean(string='Show HACCP', default=False)    
    additional_haccp    = fields.One2many('tsi.iso.additional_haccp', 'reference_id', string="Additional HACCP", index=True, related='reference.additional_haccp')
    #additional HCCp
    hazard_number_site1      = fields.Char(string='Number of hazard', related='reference.hazard_number_site1')
    hazard_number_site2       = fields.Char(string='Number of hazard', related='reference.hazard_number_site2')
    hazard_number_site3       = fields.Char(string='Number of hazard', related='reference.hazard_number_site3')
    hazard_describe_site1     = fields.Char(string='Describe Hazard', related='reference.hazard_describe_site1')
    hazard_describe_site2     = fields.Char(string='Describe Hazard', related='reference.hazard_describe_site2')
    hazard_describe_site3     = fields.Char(string='Describe Hazard', related='reference.hazard_describe_site3')
    process_number_site1      = fields.Char(string='Number of process', related='reference.process_number_site1')
    process_number_site2      = fields.Char(string='Number of process', related='reference.process_number_site2')
    process_number_site3      = fields.Char(string='Number of process', related='reference.process_number_site3')
    process_describe_site1    = fields.Char(string='Describe Process', related='reference.process_describe_site1')
    process_describe_site2    = fields.Char(string='Describe Process', related='reference.process_describe_site2')
    process_describe_site3    = fields.Char(string='Describe Process', related='reference.process_describe_site3')
    tech_number_site1         = fields.Char(string='Number of technology', related='reference.tech_number_site1')
    tech_number_site2         = fields.Char(string='Number of technology', related='reference.tech_number_site2')
    tech_number_site3         = fields.Char(string='Number of technology', related='reference.tech_number_site3')
    tech_describe_site1       = fields.Char(string='Describe Technology', related='reference.tech_describe_site1')
    tech_describe_site2       = fields.Char(string='Describe Technology', related='reference.tech_describe_site2')
    tech_describe_site3       = fields.Char(string='Describe Technology', related='reference.tech_describe_site3')


    show_22000           = fields.Boolean(string='Show 22000', default=False, related='reference.show_22000')
    show_fscc           = fields.Boolean(string='Show 22000', default=False, related='reference.show_fscc') 
    show_ispo           = fields.Boolean(string='Show ISPO', default=False)
    segment_id      = fields.Many2many('res.partner.category', string='Segment', related='reference.segment_id')
    kategori        = fields.Selection([
                            ('bronze',  'Bronze'),
                            ('silver',  'Silver'),
                            ('gold',    'Gold'),
                        ], string='Category', index=True, related='reference.kategori')
    declaration     = fields.Text(string='Declaration')
    user_signature  = fields.Binary(string='Signature')  
    lines_initial       = fields.One2many('tsi.iso.initial', 'reference_id', string="Lines Initial", index=True, related="reference.lines_initial")
    lines_surveillance  = fields.One2many('tsi.iso.surveillance', 'reference_id', string="Lines SUrveillance", index=True, related="reference.lines_surveillance")
    # tgl_perkiraan_mulai = fields.Date(string="Estimated Audit Start Date")
    tgl_perkiraan_selesai = fields.Date(string="Plan of audit date",store=True)
    state_sales = fields.Selection([
        ('draft', 'Quotation'),
        ('cliennt_approval', 'Client Approval'),
        ('waiting_verify_operation', 'Waiting Verify Operation'),
        ('create_kontrak', 'Create Kontrak'),
        ('sent', 'Confirm to Closing'),
        ('sale', 'Sales Order'),
        ('done', 'Locked'),
        ('cancel', 'Cancelled'),
        ('application_form', 'Application Form'),
    ], string='Status Sales', compute='_compute_state', store=True, tracking=True, related="reference.state_sales")

    audit_status = fields.Selection([
        ('program', 'Program'),
        ('Stage-1', 'Stage-1'),
        ('Stage-2', 'Stage-2'),
        ('Surveillance1', 'Surveillance1'),
        ('Surveillance2', 'Surveillance2'),
        ('Recertification', 'Recertification'),
        ('plan', 'Plan'),
        ('report', 'Report'),
        ('recommendation', 'Recommendation'),
        ('certificate', 'Certificate'),
        ('draft', 'Draft'),
        ('done', 'Done')],
        string='Audit Status', related="reference.audit_status", store=True)

    def action_create_kontrak(self):
        # Cari record sale.order berdasarkan partner_id
        sale_order = self.env['sale.order'].search([('partner_id', '=', self.customer.id)], limit=1)  # Perbaikan di sini
        
        if not sale_order:
            raise UserError("Tidak ditemukan sale order untuk partner ini.")
        
        # Cari dokumen dari tsi.iso.review yang terkait dengan customer
        reviews = self.env['tsi.iso.review'].search([('customer', '=', self.customer.id)])
        
        if not reviews:
            raise UserError("Tidak ditemukan dokumen ISO Review untuk partner ini.")
        
        # Update state menjadi 'sent'
        sale_order.write({
            'state': 'sent',
            'application_review_ids': [(6, 0, reviews.ids)],  # Menambahkan dokumen ke field Many2many
        })

    @api.onchange('show_integreted_yes', 'show_integreted_no')
    def onchange_show_integrated(self):
        if self.integreted_audit == 'YES' and not self.show_integreted_yes:
            self.integreted_audit = False
        elif self.integreted_audit == 'NO' and not self.show_integreted_no:
            self.integreted_audit = False

    @api.onchange('integreted_audit')
    def onchange_integreted_audit(self):
        if self.integreted_audit == 'YES':
            self.show_integreted_yes = True
            self.show_integreted_no = False
        elif self.integreted_audit == 'NO':
            self.show_integreted_yes = False
            self.show_integreted_no = True 

    @api.onchange('iso_standard_ids')
    def _onchange_standards(self):
        for obj in self:
            if obj.iso_standard_ids :
                obj.show_14001 = False
                obj.show_45001 = False
                obj.show_27001 = False
                obj.show_27701 = False
                obj.show_27017 = False
                obj.show_27018 = False
                obj.show_27001_2022 = False
                obj.show_haccp = False
                obj.show_22000 = False
                obj.show_22301 = False
                obj.show_31000 = False
                obj.show_37001 = False
                obj.show_13485 = False
                obj.show_smk = False
                obj.show_21000 = False  
                obj.show_37301 = False
                obj.show_9994 = False
                # obj.show_ispo = False               
                obj.show_salesinfo = False
                for standard in obj.iso_standard_ids :
                    if standard.name == 'ISO 14001:2015' :
                        if obj.show_salesinfo != True :
                            obj.show_salesinfo = False
                        obj.show_14001 = True
                    if standard.name == 'ISO 45001:2018' :
                        if obj.show_salesinfo != True :
                            obj.show_salesinfo = False
                        obj.show_45001 = True
                    if standard.name == 'ISO/IEC 27001:2013' :
                        if obj.show_salesinfo != True :
                            obj.show_salesinfo = False
                        obj.show_27001 = True
                    if standard.name == 'ISO/IEC 27001:2022' :
                        if obj.show_salesinfo != True :
                            obj.show_salesinfo = False
                        obj.show_27001_2022 = True
                    if standard.name == 'ISO/IEC 27701:2019' :
                        if obj.show_salesinfo != True :
                            obj.show_salesinfo = False
                        obj.show_27701 = True
                    if standard.name == 'ISO/IEC 27017:2015' :
                        if obj.show_salesinfo != True :
                            obj.show_salesinfo = False
                        obj.show_27017 = True
                    if standard.name == 'ISO/IEC 27018:2019' :
                        if obj.show_salesinfo != True :
                            obj.show_salesinfo = False
                        obj.show_27018 = True
                    if standard.name == 'ISO 22000:2018' :
                        if obj.show_salesinfo != True :
                            obj.show_salesinfo = False
                        obj.show_22000 = True
                    if standard.name == 'ISO 22301:2019' :
                        if obj.show_salesinfo != True :
                            obj.show_salesinfo = False
                        obj.show_22301 = True
                    if standard.name == 'HACCP' :
                        if obj.show_salesinfo != True :
                            obj.show_salesinfo = False
                        obj.show_haccp = True
                    if standard.name == 'ISO 31000:2018' :
                        if obj.show_salesinfo != True :
                            obj.show_salesinfo = False
                        obj.show_31000 = True
                    if standard.name == 'ISO 13485:2016' :
                        if obj.show_salesinfo != True :
                            obj.show_salesinfo = False
                        obj.show_13485 = True
                    if standard.name == 'ISO 37301:2021' :
                        if obj.show_salesinfo != True :
                            obj.show_salesinfo = False
                        obj.show_37301 = True
                    if standard.name == 'ISO 9994:2018' :
                        if obj.show_salesinfo != True :
                            obj.show_salesinfo = False
                        obj.show_9994 = True
                    if standard.name == 'ISO 37001:2016' :
                        if obj.show_salesinfo != True :
                            obj.show_salesinfo = False
                        obj.show_37001 = True
                    if standard.name == 'SMK3' :
                        if obj.show_salesinfo != True :
                            obj.show_salesinfo = False
                        obj.show_smk = True
                    if standard.name == 'ISO 21000:2018' :
                        if obj.show_salesinfo != True :
                            obj.show_salesinfo = False
                        obj.show_21000 = True
                    # if standard.name == 'ISPO' :
                    #     if obj.show_ispo != True :
                    #         obj.show_ispo = False
                    #     obj.show_ispo = True
                    elif standard.name == 'ISO 9001:2015' :
                        obj.show_salesinfo = True

    @api.model
    def create(self, vals):
        sequence = self.env['ir.sequence'].next_by_code('tsi.iso.review')
        vals['name'] = sequence or _('New')
        result = super(ISOReview, self).create(vals)
        return result

    def create_quotation(self):
        return {
            'name': "Create Quotation",
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'tsi.wizard_quotation',
            'view_id': self.env.ref('v15_tsi.tsi_wizard_quotation_view').id,
            'target': 'new'
        }

    # def set_to_running(self):
    #     self.write({'state': 'approved'})            
    #     return return {
    #         'type': 'ir.actions.act_window',
    #         'view_type': 'form',
    #         'view_mode': 'form',
    #         'res_model': 'iso_review',
    #         'view_id': self.env.ref('v15_tsi.tsi_iso_review_view_tree').id,
    #         'target': [(self.env.ref('v15_tsi.tsi_iso_review_view_tree').id, 'tree')],
    #     }
    
    def set_to_running(self):
        for rec in self:
            rec.state = 'approved'
            rec.finish_date = fields.Datetime.now()

            # Tambahan: Ubah juga di TSI ISO
            if rec.reference:
                rec.reference.write({
                    'state_sales': 'create_kontrak',
                })

            # Pastikan hanya satu record saat membuka form
            rec.ensure_one()

            # Ambil action dari ir.actions.actions
            action = rec.env['ir.actions.actions']._for_xml_id('v15_tsi.tsi_iso_review_action')

            action.update({
                'context': {'default_customer': rec.customer.id},
                'view_mode': 'form',
                'view_id': rec.env.ref('v15_tsi.tsi_iso_review_view_tree').id,
                'target': [(rec.env.ref('v15_tsi.tsi_iso_review_view_tree').id, 'tree')],
            })

            return action  # return di dalam loop supaya hanya 1x dijalankan

        return True  # fallback kalau tidak ada record

    def set_to_reject(self):
        for rec in self:
            # Ubah state dan state_sales lokal
            rec.write({
                'state': 'reject',
                'state_sales': 'application_form',
            })

            # Ubah state_sales di reference (sale.order)
            if rec.sales_order_id:
                rec.sales_order_id.write({
                    'state': 'application_form',
                })

            # Ubah juga di TSI ISO
            if rec.reference:
                rec.reference.write({
                    'state': 'reject',
                    'state_sales': 'application_form',
                })

        return True


    def set_to_revice(self):
        self.write({'state': 'revice'})
        self.ensure_one()
        action = self.env['ir.actions.actions']._for_xml_id('v15_tsi.tsi_iso_review_action')
        action.update({
            'context': {'default_customer': self.customer.id},
            'view_mode': 'form',
            'view_id': self.env.ref('v15_tsi.tsi_iso_review_view_tree').id,
            'target': [(self.env.ref('v15_tsi.tsi_iso_review_view_tree').id, 'tree')],
        })
        return action

    def create_open_quotation(self):
        self.env['sale.order'].create({
            'iso_reference' : self.reference.id,
            'partner_id' : self.customer.id,
        })
        self.reference.compute_state()


    def set_to_closed(self):
        self.create_open_quotation()
        self.write({'state': 'approved'})
        self.write({'finish_date': fields.Datetime.now()})            
        return True

    def set_to_draft(self):
        self.write({'state': 'new'})            
        return True

class TSIISOReviewSalesInfoSite(models.Model):
    _name = 'tsi.iso.review.salesinfo_site'
    _description = 'TSI ISO Review Sales Info Site'

    review_id = fields.Many2one('tsi.iso.review', string='Review')
    review_id1    = fields.Many2one('tsi.iso.review', string='Review')
    review_id2   = fields.Many2one('tsi.iso.review', string='Review')
    review_id3    = fields.Many2one('tsi.iso.review', string='Review')
    review_id4    = fields.Many2one('tsi.iso.review', string='Review')
    review_id5    = fields.Many2one('tsi.iso.review', string='Review')
    nama_site = fields.Char(string='Name Site')
    stage_1 = fields.Char(string='Stage 1')
    stage_2 = fields.Char(string='Stage 2')
    surveilance_1 = fields.Char(string='Survillance 1')
    surveilance_2 = fields.Char(string='Survillance 2')
    recertification = fields.Char(string='Recertification')
    remarks = fields.Char(string='Remarks')

class TSIISOReviewSalesInfoSite(models.Model):
    _name = 'tsi.iso.review.additional_27001'
    _description = 'TSI ISO Review Additional 27001'

    review_id = fields.Many2one('tsi.iso.review', string='Review')
    nama_site       = fields.Char(string='Nama Site')
    employee        = fields.Char(string='Emp Included')
    it_aspect       = fields.Selection(string='Information Security', selection=[
                            ('identical',   'Mostly Identical'), 
                            ('extenct',     'Only to some extent identical'), 
                            ('differenct',  'Different'), 
                            ])
    it_explanation     = fields.Char(string='IT Explanation')
    isms_aspect     = fields.Selection(string='ISMS as sites', selection=[
                            ('identical',   'Identical, centrally managed'), 
                            ('differs',     'Differs in some respects'), 
                            ('separately',  'Managed separately'), 
                            ])
    isms_explanation     = fields.Char(string='ISMS Explanation')
    special         = fields.Char(string='Special Feature')

class TSIISOReviewSalesInfoSite(models.Model):
    _name = 'tsi.iso.review.site'
    _description = 'TSI ISO Review Site'

    review_id = fields.Many2one('tsi.iso.review', string='Review')
    nama_site       = fields.Char(string='Nama Site')
    type            = fields.Char(string='Type(HO, Factory etc)' )
    address         = fields.Char(string='Address')
    product         = fields.Char(string='Product / Process / Activities')
    # off_location    = fields.Char(string='Off-location')
    total_active    = fields.Char(string='Total No. of Active Temporary Project Sites (see attachment for detai)')
    total_emp       = fields.Char(string='Total No. of Employeesption')
    # part_time       = fields.Char(string='Part-time (4 hours / day)')
    subcon          = fields.Char(string='Subcontractor')
    other           = fields.Char(string='Others')
    remarks         = fields.Char(string='Remark')
    # unskilled       = fields.Char(string='Unskilled Temporary')
    # seasonal        = fields.Char(string='Seasonal Workers')
    non_shift       = fields.Char(string='Non shift')
    shift1          = fields.Char(string='Shift 1')
    shift2          = fields.Char(string='Shift 2')
    shift3          = fields.Char(string='Shift 3')
    differs         = fields.Char(string='Process Differs Across All Shifts')

class ISOReviewHACCP22000(models.Model):
    _name           = 'tsi.iso.review.additional_haccp'
    _description    = 'HACCP 22000'

    review_id        = fields.Many2one('tsi.iso.review', string="Reference")
    hazard_number       = fields.Char(string='Number of hazard')
    hazard_describe     = fields.Char(string='Describe Hazard')
    process_number      = fields.Char(string='Number of process')
    process_describe    = fields.Char(string='Describe Process')
    tech_number         = fields.Char(string='Number of technology')
    tech_describe       = fields.Char(string='Describe Technology')


class APPMandays(models.Model):
    _name           = 'tsi.iso.mandays_app'
    _description    = 'Mandays'

    reference_id    = fields.Many2one('tsi.iso', string="Reference", ondelete='cascade', index=True)
    tahapan_id      = fields.Many2one('tsi.history_kontrak', string="Tahapan")
    tahapan_id1      = fields.Many2one('tsi.history_kontrak', string="Tahapan")
    tahapan_id2      = fields.Many2one('tsi.history_kontrak', string="Tahapan")
    tahapan_id3      = fields.Many2one('tsi.history_kontrak', string="Tahapan")
    tahapan_id4      = fields.Many2one('tsi.history_kontrak', string="Tahapan")
    tahapan_id_re      = fields.Many2one('tsi.history_kontrak', string="Tahapan")
    standard        = fields.Many2one('tsi.iso.standard', string="Standard")
    risk            = fields.Many2one('tsi.iso.risk', string="Risk Category")
    mandays         = fields.Integer(string='Mandays')
    mandays_s1       = fields.Integer(string='Mandays')
    mandays_s2         = fields.Integer(string='Mandays')
    mandays_s3         = fields.Integer(string='Mandays')
    mandays_s4         = fields.Integer(string='Mandays')
    mandays_rs         = fields.Integer(string='Mandays')
    #initial
    nomor_ia    = fields.Char('Nomor Sertifikat')
    tanggal_sertifikat     = fields.Date(string="Expiry Date")
    tanggal_sertifikat1     = fields.Date(string="Initial Certification Date")
    tanggal_sertifikat2     = fields.Date(string="Certification Issue Date")
    tanggal_sertifikat3     = fields.Date(string="Certification Validity Date")
    #s1
    nomor_s1    = fields.Char('Nomor Sertifikat')
    tanggal_sertifikat_s1     = fields.Date(string="Expiry Date")
    initial_sertifikat_s_2     = fields.Date(string="Initial Certification Date")
    issue_sertifikat_s_3     = fields.Date(string="Certification Issue Date")
    validity_sertifikat_s_4     = fields.Date(string="Certification Validity Date")
    #s2
    nomor_s2    = fields.Char('Nomor Sertifikat')
    tanggal_sertifikat_s2     = fields.Date(string="Expiry Date")
    tanggal_sertifikat_initial_s2     = fields.Date(string="Initial Certification Date")
    tanggal_sertifikat_issued_s2     = fields.Date(string="Certification Issue Date")
    tanggal_sertifikat_validty_s2     = fields.Date(string="Certification Validity Date")
    #s3
    nomor_s3    = fields.Char('Nomor Sertifikat')
    tanggal_sertifikat_s3     = fields.Date(string="Expiry Date")
    initial_tanggal_sertifikat_s3     = fields.Date(string="Initial Certification Date")
    issued_tanggal_sertifikat_s3     = fields.Date(string="Certification Issue Date")
    validty_tanggal_sertifikat_s3     = fields.Date(string="Certification Validity Date")
    #s4
    nomor_s4    = fields.Char('Nomor Sertifikat')
    tanggal_sertifikat_s4     = fields.Date(string="Expiry Date")
    initiall_s4     = fields.Date(string="Initial Certification Date")
    issued_s4     = fields.Date(string="Certification Issue Date")
    validity_s4     = fields.Date(string="Certification Validity Date")
    #re
    nomor_re    = fields.Char('Nomor Sertifikat')
    tanggal_sertifikat_rs     = fields.Date(string="Expiry Date")
    tanggal_sertifikat_initial_rs     = fields.Date(string="Initial Certification Date")
    tanggal_sertifikat__issued_rs     = fields.Date(string="Certification Issue Date")
    tanggal_sertifikat_validty_rs     = fields.Date(string="Certification Validity Date")
    tahapan_audit_ids   = fields.Many2many('tsi.iso.tahapan', string='Tahapan', )
    audit_stage     = fields.Selection([
                            ('initial',     'Initial Audit'),
                            ('survey_1;',   'Surveillance 1'),
                            ('survey_2',    'Surveillance 2'),
                        ], string='Audit Stage', copy=False, index=True)
    accreditation   = fields.Many2one('tsi.iso.accreditation', string="Accreditation")
    display_type = fields.Selection(
        selection=[
            ('line_section', "Section"),
            ('line_note', "Note"),
        ],
        default=False)
    
    @api.onchange('tanggal_sertifikat1')
    def _onchange_tanggal_sertifikat1(self):
        for record in self:
            if record.tanggal_sertifikat1:
                # Set issue_date to initial_date
                record.tanggal_sertifikat2 = record.tanggal_sertifikat1
                
                # Calculate validity_date (initial_date + 3 years - 1 day)
                initial_datetime = datetime.combine(record.tanggal_sertifikat1, datetime.min.time())
                validity_datetime = initial_datetime + timedelta(days=(3*365) - 1)
                record.tanggal_sertifikat3 = validity_datetime.date()
                
                # Calculate expiry_date (initial_date + 1 year)
                expiry_datetime = initial_datetime + timedelta(days=365 - 1)
                record.tanggal_sertifikat = expiry_datetime.date()

    @api.onchange('initial_sertifikat_s_2')
    def _onchange_initial_sertifikat_s_2(self):
        for record in self:
            if record.initial_sertifikat_s_2:
                # Set issue_date to initial_date
                record.issue_sertifikat_s_3 = record.initial_sertifikat_s_2

                # Calculate validity_date (initial_date + 3 years - 1 day)
                initial_datetime = datetime.combine(record.initial_sertifikat_s_2, datetime.min.time())
                validity_datetime = initial_datetime + timedelta(days=(3*365) - 1)
                record.validity_sertifikat_s_4 = validity_datetime.date()

                # Calculate expiry_date (initial_date + 1 year)
                expiry_datetime = initial_datetime + timedelta(days=365 - 1)
                record.tanggal_sertifikat_s1 = expiry_datetime.date()

    @api.onchange('tanggal_sertifikat_initial_s2')
    def _onchange_tanggal_sertifikat_initial_s2(self):
        for record in self:
            if record.tanggal_sertifikat_initial_s2:
                # Set issue_date to initial_date
                record.tanggal_sertifikat_issued_s2 = record.tanggal_sertifikat_initial_s2

                # Calculate validity_date (initial_date + 3 years - 1 day)
                initial_datetime = datetime.combine(record.tanggal_sertifikat_initial_s2, datetime.min.time())
                validity_datetime = initial_datetime + timedelta(days=(3*365) - 1)
                record.tanggal_sertifikat_validty_s2 = validity_datetime.date()

                # Calculate expiry_date (initial_date + 1 year)
                expiry_datetime = initial_datetime + timedelta(days=365 - 1)
                record.tanggal_sertifikat_s2 = expiry_datetime.date()
    
    @api.onchange('initial_tanggal_sertifikat_s3')
    def _onchange_initial_tanggal_sertifikat_s3(self):
        for record in self:
            if record.initial_tanggal_sertifikat_s3:
                # Set issue_date to initial_date
                record.issued_tanggal_sertifikat_s3 = record.initial_tanggal_sertifikat_s3

                # Calculate validity_date (initial_date + 3 years - 1 day)
                initial_datetime = datetime.combine(record.initial_tanggal_sertifikat_s3, datetime.min.time())
                validity_datetime = initial_datetime + timedelta(days=(3*365) - 1)
                record.validty_tanggal_sertifikat_s3 = validity_datetime.date()

                # Calculate expiry_date (initial_date + 1 year)
                expiry_datetime = initial_datetime + timedelta(days=365 - 1)
                record.tanggal_sertifikat_s3 = expiry_datetime.date()

    @api.onchange('initiall_s4')
    def _onchange_initiall_s4(self):
        for record in self:
            if record.initiall_s4:
                # Set issue_date to initial_date
                record.issued_s4 = record.initiall_s4

                # Calculate validity_date (initial_date + 3 years - 1 day)
                initial_datetime = datetime.combine(record.initiall_s4, datetime.min.time())
                validity_datetime = initial_datetime + timedelta(days=(3*365) - 1)
                record.validity_s4 = validity_datetime.date()

                # Calculate expiry_date (initial_date + 1 year)
                expiry_datetime = initial_datetime + timedelta(days=365 - 1)
                record.tanggal_sertifikat_s4 = expiry_datetime.date()
    
    @api.onchange('tanggal_sertifikat_initial_rs')
    def _onchange_tanggal_sertifikat_initial_rs(self):
        for record in self:
            if record.tanggal_sertifikat_initial_rs:
                # Set issue_date to initial_date
                record.tanggal_sertifikat__issued_rs = record.tanggal_sertifikat_initial_rs

                # Calculate validity_date (initial_date + 3 years - 1 day)
                initial_datetime = datetime.combine(record.tanggal_sertifikat_initial_rs, datetime.min.time())
                validity_datetime = initial_datetime + timedelta(days=(3*365) - 1)
                record.tanggal_sertifikat_validty_rs = validity_datetime.date()

                # Calculate expiry_date (initial_date + 1 year)
                expiry_datetime = initial_datetime + timedelta(days=365 - 1)
                record.tanggal_sertifikat_rs = expiry_datetime.date()


class APPMandaysPA(models.Model):
    _name           = 'tsi.iso.mandays.pa_app'
    _description    = 'Mandays PA'

    reference_id    = fields.Many2one('tsi.iso', string="Reference", ondelete='cascade', index=True)
    standard        = fields.Many2one('tsi.iso.standard', string='Standard ISO')
    audit_stage     = fields.Selection([
                            ('stage_1',     'Stage 1'),
                            ('stage_2',     'Stage 2'),
                            ('survey_1;',   'Surveillance 1'),
                            ('survey_2',    'Surveillance 2'),
                            ('recert',      'ReCertification'),
                        ], string='Audit Stage', copy=False, index=True)
    aspect          = fields.Char(string='Significant Aspect')
    personnel       = fields.Many2one('hr.employee', string="Personnel")
    task            = fields.Selection([
                            ('lead',        'Lead Auditor'),
                            ('auditor',     'Auditor'),
                            ('technica;',   'Technical Expert'),
                            ('report',      'Reviewing Audit Report'),
                            ('decision',    'Certification Decision'),
                        ], string='Task', copy=False, index=True)
    remarks         = fields.Char(string='Remarks')


class ISOMandaysJustification(models.Model):
    _name           = 'tsi.iso.mandays.justification_app'
    _description    = 'Mandays Justification'

    reference_id    = fields.Many2one('tsi.iso', string="Reference", ondelete='cascade', index=True)
    name            = fields.Char(string='Reference')
    score_qms       = fields.Integer(string='QMS')
    score_ems       = fields.Integer(string='EMS')
    score_ohs       = fields.Integer(string='OHS')
    score_abms      = fields.Integer(string='ABMS')


class ISOMandays(models.Model):
    _name           = 'tsi.iso.mandays'
    _description    = 'Mandays'

    review_id       = fields.Many2one('tsi.iso.review', string="Review", ondelete='cascade', index=True)
    standard        = fields.Many2one('tsi.iso.standard', string="Standard")
    risk            = fields.Many2one('tsi.iso.risk', string="Risk Category")
    mandays         = fields.Integer(string='Mandays')
    audit_stage     = fields.Selection([
                            ('initial',     'Initial Audit'),
                            ('survey_1;',   'Surveillance 1'),
                            ('survey_2',    'Surveillance 2'),
                        ], string='Audit Stage', copy=False, index=True)

    
class ISOMandaysISMS(models.Model):
    _name           = 'tsi.iso.mandays.isms'
    _description    = 'Mandays ISMS'

    review_id       = fields.Many2one('tsi.iso.review', string="Review", ondelete='cascade', index=True)
    buss_complexity = fields.Char(string='Business Complexity')
    it_complexity   = fields.Char(string='IT Complexity')
    mandays         = fields.Integer(string='Mandays')
    

class ISOMandaysIntegrated(models.Model):
    _name           = 'tsi.iso.mandays.integrated'
    _description    = 'Mandays Interated'

    review_id       = fields.Many2one('tsi.iso.review', string="Review", ondelete='cascade', index=True)
    name            = fields.Char(string='Reference')
    mandays         = fields.Integer(string='Mandays')
    
class ISOMandaysAuditTime(models.Model):
    _name           = 'tsi.iso.mandays.audit_time'
    _description    = 'Mandays Audit Time'

    review_id       = fields.Many2one('tsi.iso.review', string="Review", ondelete='cascade', index=True)
    pivot           = fields.Integer(string='Pivot')
    initial         = fields.Integer(string='Initial Audit')
    surveillance    = fields.Integer(string='Surveillance')
    recert          = fields.Integer(string='Recert')

class ISOMandaysJustification(models.Model):
    _name           = 'tsi.iso.mandays.justification'
    _description    = 'Mandays Justification'

    review_id       = fields.Many2one('tsi.iso.review', string="Review", ondelete='cascade', index=True)
    name            = fields.Char(string='Reference')
    score_qms       = fields.Integer(string='QMS')
    score_ems       = fields.Integer(string='EMS')
    score_ohs       = fields.Integer(string='OHS')
    score_abms      = fields.Integer(string='ABMS')

class ISOMandaysJustificationISMS(models.Model):
    _name           = 'tsi.iso.mandays.justification.isms'
    _description    = 'Mandays Justification ISMS'

    review_id       = fields.Many2one('tsi.iso.review', string="Review", ondelete='cascade', index=True)
    name            = fields.Char(string='Reference')
    score_isms      = fields.Integer(string='ISMS')

class ISOMandaysPA(models.Model):
    _name           = 'tsi.iso.mandays.pa'
    _description    = 'Mandays PA'

    review_id       = fields.Many2one('tsi.iso.review', string="Review", ondelete='cascade', index=True)
    standard        = fields.Many2one('tsi.iso.standard', string='Standard ISO')
    audit_stage     = fields.Selection([
                            ('stage_1',     'Stage 1'),
                            ('stage_2',     'Stage 2'),
                            ('survey_1;',   'Surveillance 1'),
                            ('survey_2',    'Surveillance 2'),
                            ('recert',      'ReCertification'),
                        ], string='Audit Stage', copy=False, index=True)
    aspect          = fields.Char(string='Significant Aspect')
    personnel       = fields.Many2one('hr.employee', string="Personnel")
    task            = fields.Selection([
                            ('lead',        'Lead Auditor'),
                            ('auditor',     'Auditor'),
                            ('technica;',   'Technical Expert'),
                            ('report',      'Reviewing Audit Report'),
                            ('decision',    'Certification Decision'),
                        ], string='Task', copy=False, index=True)
    remarks         = fields.Char(string='Remarks')


class ISPOEvaluasi(models.Model):
    _name           = "tsi.ispo.evaluasi"
    _description    = "Evaluasi Isu"

    review_id       = fields.Many2one('tsi.iso.review', string="Review", ondelete='cascade', index=True)
    issue           = fields.Char(string='Issue')
    evaluasi        = fields.Char(string='Hasil Evaluasi')
    rekomendasi     = fields.Char(string='Rekomendasi')

class ISPONilaiSkor(models.Model):
    _name           = "tsi.ispo.nilai_skor"
    _description    = "Nilai Skor"

    review_id       = fields.Many2one('tsi.iso.review', string="Review", ondelete='cascade', index=True)
    skor_name       = fields.Char(string='Skor')
    skor_1          = fields.Char(string='Skor = 1')
    skor_2          = fields.Char(string='Skor = 2')
    skor_3          = fields.Char(string='Skor = 3')
    skor_nilai      = fields.Integer(string='Nilai Skor')

class ISPOJustification(models.Model):
    _name           = 'tsi.ispo.justification'
    _description    = 'ISPO Mandays Justification'

    review_id       = fields.Many2one('tsi.iso.review', string="Review", ondelete='cascade', index=True)
    name            = fields.Char(string='Parameter')
    standar         = fields.Integer(string='Standar')
    maksimal        = fields.Integer(string='Maksimal')
    score           = fields.Integer(string='Score')

class ISPOMandays(models.Model):
    _name           = 'tsi.ispo.mandays'
    _description    = 'ISPO Mandays'

    review_id       = fields.Many2one('tsi.iso.review', string="Review", ondelete='cascade', index=True)
    lingkup         = fields.Char(string='Ruang Lingkup')
    awal            = fields.Integer(string='Sertifikasi Awal')
    penilikan       = fields.Integer(string='Penilikan')
    resertifikai    = fields.Integer(string='Resertifikasi')

class ISPOTotalMandays(models.Model):
    _name           = 'tsi.ispo.total_mandays'
    _description    = 'ISPO Total Mandays'

    review_id       = fields.Many2one('tsi.iso.review', string="Review", ondelete='cascade', index=True)
    lingkup         = fields.Selection([
                            ('audit_1',        'Audit Tahap 1'),
                            ('audit_2',     'Audit Tahap 2'),
                            ('penilikan',   'Penilikan'),
                            ('resertifikasi',      'Resertifikasi'),
                        ], string='Ruang Lingkup', copy=False, index=True)
    kebun           = fields.Integer(string='Kebun')
    pabrik          = fields.Integer(string='Pabrik')
