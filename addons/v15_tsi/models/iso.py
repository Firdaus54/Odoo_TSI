from base64 import standard_b64decode
from odoo import models, fields, api, SUPERUSER_ID, _
from datetime import datetime, timedelta, date
from num2words import num2words
import logging
import roman
import requests
import re
from odoo.exceptions import UserError, RedirectWarning, ValidationError, except_orm, Warning

_logger = logging.getLogger(__name__)

MONTH_SELECTION = [
    ('01', 'Januari'), ('02', 'Februari'), ('03', 'Maret'),
    ('04', 'April'), ('05', 'Mei'), ('06', 'Juni'),
    ('07', 'Juli'), ('08', 'Agustus'), ('09', 'September'),
    ('10', 'Oktober'), ('11', 'November'), ('12', 'Desember')
]

YEAR_SELECTION = [
    ('2025', '2025'), ('2026', '2026'), ('2027', '2027'),
    ('2028', '2028'), ('2029', '2029'), ('2030', '2030'),
    ('2031', '2031'), ('2032', '2032'), ('2033', '2033'),
    ('2034', '2034'), ('2035', '2035'), ('2036', '2036')
]


class ISO(models.Model):
    _name           = "tsi.iso"
    _inherit        = ['portal.mixin', 'mail.thread', 'mail.activity.mixin']
    _description    = "Application Form"
    _order          = 'id DESC'

    doctype         = fields.Selection([
                            ('iso',  'ISO'),
                            ('ispo',   'ISPO'),
                        ], string='Doc Type', index=True, )
    reference       = fields.Many2one('tsi.iso.review', string="Reference")
    # status_sales = fields.Selection([
    #     ('draft', 'Quotation'),
    #     ('sent', 'Confirm to Closing'),
    #     ('sale', 'Sales Order'),
    #     ('done', 'Locked'),
    #     ('cancel', 'Cancelled'),
    #     ], string='Status Sales', readonly=True, copy=False, index=True, tracking=3, default='draft', related="sales_reference.state")
    # audit_status = fields.Selection([
    #     ('program', 'Program'),
    #     ('plan', 'Plan'),
    #     ('report', 'Report'),
    #     ('recommendation', 'Recommendation'),
    #     ('certificate', 'Certificate'),
    #     ('draft', 'Draft'),
    #     ('done', 'Done')],
    #     string='Audit Status', related="sales_reference.audit_status", store=True)
    user_id = fields.Many2one(
        'res.users', string='Created By', index=True, tracking=2, default=lambda self: self.env.user,
        domain=lambda self: "[('groups_id', '=', {}), ('share', '=', False), ('company_ids', '=', company_id)]"
        )
    company_id = fields.Many2one('res.company', 'Company', required=True, index=True, default=lambda self: self.env.company)
    sales_person       = fields.Many2one('res.users', string="Sales Person")
    name            = fields.Char(string="Document No",  readonly=True, tracking=True)
    customer        = fields.Many2one('res.partner', string="Company Name", domain="[('is_company', '=', True)]")
    alamat          = fields.Char(string="Alamat", tracking=True)
    issue_date      = fields.Date(string="Issued Date", default=datetime.today(), tracking=True)    
    multisite       = fields.Text(string="Permohonan Multisite")
    contact_name    = fields.Many2one('res.partner', string="Nama Contact")
    
    company_name        = fields.Char(string="Company", tracking=True)
    office_address      = fields.Char(string="Office Address", tracking=True)
    invoicing_address   = fields.Char(string="Invoicing Address", tracking=True)
    contact_person      = fields.Char(string="Contact Person", tracking=True,)
    
    jabatan         = fields.Char(string="Position", tracking=True)
    telepon         = fields.Char(string="Telephone", tracking=True)
    fax             = fields.Char(string="Fax", tracking=True)
    email           = fields.Char(string="Email", tracking=True)
    website         = fields.Char(string="Website", tracking=True)
    cellular        = fields.Char(string="Celular", tracking=True)
    certification   = fields.Selection([
                            ('Single Site',  'SINGLE SITE'),
                            ('Multi Site',   'MULTI SITE'),
                        ], string='Certification Type', index=True, readonly=True, tracking=True )

    iso_standard_ids    = fields.Many2many('tsi.iso.standard', string='Standards', tracking=True, domain="[('standard', 'in', ['iso'])]")
    iso_standard_other   = fields.Char(string="Other Standards")

    outsourced_activity = fields.Text(string="Outsourced Activity", tracking=True)


    is_associate        = fields.Boolean(string='Associate')    
    associate_id        = fields.Many2one('res.partner', "Associate Name", domain = [('is_company','=',False)])
    associate_name     = fields.Char(string='Associate Name', tracking=True)
    email_associate     = fields.Char(string='Email', tracking=True)
    phone_associate     = fields.Char(string='No Telp', tracking=True)

    #Frenchise
    is_franchise        = fields.Boolean(string='Frenchise')    
    franchise_id        = fields.Many2one('res.partner', "Frenchise Name", domain = [('is_company','=',True)])
    email_franchise     = fields.Char(string='Email', tracking=True)
    phone_franchise     = fields.Char(string='No Telp', tracking=True)

    iso_hazard_ids      = fields.Many2many('tsi.hazard',        string='Hazards')
    iso_hazard_other    = fields.Char(string="Other Hazard")

    iso_env_aspect_ids  = fields.Many2many('tsi.env_aspect',    string='Environmental Aspect')
    iso_aspect_other    = fields.Char(string="Other Aspect")

    # ea_code             = fields.Many2one('tsi.ea_code', string="EA Code")
    ea_code_9001        = fields.Many2many('tsi.ea_code', 'rel_tsi_iso_ea_9001', string="EA Code Existing")
    accreditation       = fields.Many2one('tsi.iso.accreditation', string="Accreditation")
    complexity          = fields.Selection([
                            ('Na',  'NA'),
                            ('Limited',   'Limited'),
                            ('Low',   'Low'),
                            ('Medium',   'Medium'),
                            ('High',   'High'),
                        ], string='Complexity', index=True, )

    # ea_code_14001           = fields.Many2one('tsi.ea_code', string="EA Code")
    ea_code_14001_1        = fields.Many2many('tsi.ea_code', 'rel_tsi_iso_ea_14001', string="EA Code Existing")
    accreditation_14001     = fields.Many2one('tsi.iso.accreditation', string="Accreditation")
    complexity_14001        = fields.Selection([
                            ('Na',  'NA'),
                            ('Limited',   'Limited'),
                            ('Low',   'Low'),
                            ('Medium',   'Medium'),
                            ('High',   'High'),
                        ], string='Complexity', index=True, )
    salesinfo_site_14001    = fields.One2many('tsi.iso.additional_salesinfo', 'reference_id2', string="Additional Info", index=True)

    #ISO27001:2013
    # ea_code_27001           = fields.Many2one('tsi.ea_code', string="EA Code")
    ea_code_27001_1        = fields.Many2many('tsi.ea_code', 'rel_tsi_iso_ea_27001', string="EA Code Existing")
    accreditation_27001     = fields.Many2one('tsi.iso.accreditation', string="Accreditation")
    complexity_27001        = fields.Selection([
                            ('Na',  'NA'),
                            ('Limited',   'Limited'),
                            ('Low',   'Low'),
                            ('Medium',   'Medium'),
                            ('High',   'High'),
                        ], string='Complexity', index=True, )
    salesinfo_site_27001    = fields.One2many('tsi.iso.additional_salesinfo', 'reference_id3', string="Additional Info", index=True)

    #ISO27001:2022
    # ea_code_27001_2022           = fields.Many2one('tsi.ea_code', string="EA Code")
    ea_code_27001_2022_1        = fields.Many2many('tsi.ea_code', 'rel_tsi_iso_ea_27001_2022', string="EA Code Existing")
    accreditation_27001_2022     = fields.Many2one('tsi.iso.accreditation', string="Accreditation")
    complexity_27001_2022        = fields.Selection([
                            ('Na',  'NA'),
                            ('Limited',   'Limited'),
                            ('Low',   'Low'),
                            ('Medium',   'Medium'),
                            ('High',   'High'),
                        ], string='Complexity', index=True, )
    salesinfo_site_27001_2022    = fields.One2many('tsi.iso.additional_salesinfo', 'reference_id12', string="Additional Info", index=True)

    #ISO27017
    # ea_code_27017           = fields.Many2one('tsi.ea_code', string="EA Code")
    ea_code_27017_1        = fields.Many2many('tsi.ea_code', 'rel_tsi_iso_ea_27017', string="EA Code Existing")
    accreditation_27017     = fields.Many2one('tsi.iso.accreditation', string="Accreditation")
    complexity_27017        = fields.Selection([
                            ('Na',  'NA'),
                            ('Limited',   'Limited'),
                            ('Low',   'Low'),
                            ('Medium',   'Medium'),
                            ('High',   'High'),
                        ], string='Complexity', index=True, )
    salesinfo_site_27017    = fields.One2many('tsi.iso.additional_salesinfo', 'reference_id13', string="Additional Info", index=True)

    #ISO27018
    # ea_code_27018           = fields.Many2one('tsi.ea_code', string="EA Code")
    ea_code_27018_1        = fields.Many2many('tsi.ea_code', 'rel_tsi_iso_ea_27018', string="EA Code Existing")
    accreditation_27018     = fields.Many2one('tsi.iso.accreditation', string="Accreditation")
    complexity_27018        = fields.Selection([
                            ('Na',  'NA'),
                            ('Limited',   'Limited'),
                            ('Low',   'Low'),
                            ('Medium',   'Medium'),
                            ('High',   'High'),
                        ], string='Complexity', index=True, )
    salesinfo_site_27018    = fields.One2many('tsi.iso.additional_salesinfo', 'reference_id14', string="Additional Info", index=True)

    #ISO27701
    # ea_code_27701           = fields.Many2one('tsi.ea_code', string="EA Code")
    ea_code_27701_1        = fields.Many2many('tsi.ea_code', 'rel_tsi_iso_ea_27701', string="EA Code Existing")
    accreditation_27701     = fields.Many2one('tsi.iso.accreditation', string="Accreditation")
    complexity_27701        = fields.Selection([
                            ('Na',  'NA'),
                            ('Limited',   'Limited'),
                            ('Low',   'Low'),
                            ('Medium',   'Medium'),
                            ('High',   'High'),
                        ], string='Complexity', index=True, )
    salesinfo_site_27701    = fields.One2many('tsi.iso.additional_salesinfo', 'reference_id15', string="Additional Info", index=True)

    

    # ea_code_45001           = fields.Many2one('tsi.ea_code', string="EA Code")
    ea_code_45001_1        = fields.Many2many('tsi.ea_code', 'rel_tsi_iso_ea_45001', string="EA Code Existing")
    accreditation_45001     = fields.Many2one('tsi.iso.accreditation', string="Accreditation")
    complexity_45001        = fields.Selection([
                            ('Na',  'NA'),
                            ('Limited',   'Limited'),
                            ('Low',   'Low'),
                            ('Medium',   'Medium'),
                            ('High',   'High'),
                        ], string='Complexity', index=True, )
    salesinfo_site_45001    = fields.One2many('tsi.iso.additional_salesinfo', 'reference_id4', string="Additional Info", index=True)

    food_category_22000     = fields.Many2one('tsi.food_category', string="Food Category")
    accreditation_22000     = fields.Many2one('tsi.iso.accreditation', string="Accreditation")
    complexity_22000        = fields.Selection([
                            ('Na',  'NA'),
                            ('Limited',   'Limited'),
                            ('Low',   'Low'),
                            ('Medium',   'Medium'),
                            ('High',   'High'),
                        ], string='Complexity', index=True, )
    salesinfo_site_22000    = fields.One2many('tsi.iso.additional_salesinfo', 'reference_id5', string="Additional Info", index=True)

    food_category_22000     = fields.Many2one('tsi.food_category', string="Food Category")
    accreditation_haccp     = fields.Many2one('tsi.iso.accreditation', string="Accreditation")
    complexity_haccp        = fields.Selection([
                            ('Na',  'NA'),
                            ('Limited',   'Limited'),
                            ('Low',   'Low'),
                            ('Medium',   'Medium'),
                            ('High',   'High'),
                        ], string='Complexity', index=True, )
    salesinfo_site_haccp    = fields.One2many('tsi.iso.additional_salesinfo', 'reference_id6', string="Additional Info", index=True)

    # scope 
    scope       = fields.Text('Scope', )
    boundaries  = fields.Text( string="Boundaries", default="All related area, department & functions within scope")
    cause       = fields.Text('Mandatory SNI', )
    isms_doc    = fields.Text('ISMS Document', )

    # personnel
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

    # management 
    last_audit      = fields.Text('Last Audit', )
    last_review     = fields.Text('Last Review', )


    tx_site_count   = fields.Integer('Number of Site',)
    upload_file     = fields.Binary('Attachment')
    file_name       = fields.Char('Filename')
    tx_remarks      = fields.Char('Remarks', )

    # maturity
    start_implement     = fields.Char(string="Start of Implementation", )

    mat_consultancy     = fields.Selection([('YES', 'YES'),('NO', 'NO')], string="Use of Consultants", )
    mat_certified       = fields.Selection([('YES', 'YES'),('NO', 'NO')], string="Certified System", )
    other_system         = fields.Char(string='Other System')
    # mat_certified_cb    = fields.Selection([('YES', 'YES'),('NO', 'NO')], string="Certified CB", )
    # mat_tools           = fields.Selection([('YES', 'YES'),('NO', 'NO')], string="Continual Improvement", )
    # mat_national        = fields.Selection([('YES', 'YES'),('NO', 'NO')], string="National Certified", )
    # mat_more            = fields.Selection([('YES', 'YES'),('NO', 'NO')], string="Setup More Standard", )

    txt_mat_consultancy = fields.Char(string="Tx Consultancy", )
    txt_mat_certified   = fields.Char(string="Tx Certified", )
    # txt_mat_certified_cb    = fields.Char(string="Tx Certified CB", )
    # txt_mat_tools       = fields.Char(string="Tx Continual Improvement", )
    # txt_mat_national    = fields.Char(string="Tx National Certified", )
    # txt_mat_more        = fields.Char(string="Tx Setup More Standard", )

    # integrated audit
    show_integreted_yes = fields.Boolean(string='Show YES', default=False)
    show_integreted_no  = fields.Boolean(string='Show NO', default=False)
    integreted_audit    = fields.Selection([('YES', 'YES'),('NO', 'NO')], string="Integrated Audit",)
    int_review          = fields.Selection([('YES', 'YES'),('NO', 'NO')], string="Management Review", )
    int_internal        = fields.Selection([('YES', 'YES'),('NO', 'NO')], string="Internal Audit", )
    int_policy          = fields.Selection([('YES', 'YES'),('NO', 'NO')], string="Risk & Opportunity Management", )
    int_system          = fields.Selection([('YES', 'YES'),('NO', 'NO')], string="Responsibilities", )
    int_instruction     = fields.Selection([('YES', 'YES'),('PARTIAL', 'PARTIAL'),('NO', 'NO')], string="Procedures", )
    int_improvement     = fields.Selection([('YES', 'YES'),('PARTIAL', 'PARTIAL'),('NO', 'NO')], string="Work Instructions", )
    int_planning        = fields.Selection([('YES', 'YES'),('PARTIAL', 'PARTIAL'),('NO', 'NO')], string="Manual", )
    # int_support         = fields.Selection([('YES', 'YES'),('NO', 'NO')], string="Supports", )

    # additional iso 14001
    iso_14001_environmental = fields.Text(string="Significant Enviornmental Aspects", default="Limbah Kantor, Kimia, Oli\nKonsumsi listrik, air, solar\nEmisi gas buang, Panas" )
    iso_14001_legal         = fields.Text(string="Specific Relevant Obligations", default="PerMenLHK no.6 / 2021 ttg Limbah B3\nPP No. 22 / 2021 ttg Penyelenggaraan Perlindungan dan Pengelolaan LH")

    # additional iso 45001
    iso_45001_ohs           = fields.Text(string="Significant Hazard / OHS Risks", )
    iso_45001_legal         = fields.Text(string="45001 Legal Obligations", )

    # additional iso 27001
    iso_27001_total_emp     = fields.Char(string='Total Employee', )
    iso_27001_bisnistype    = fields.Selection([
                                ('A', 'Organization works in non-critical business sectors and non-regulated sectors'),
                                ('B', 'Organization has customers in critical business sectors'),
                                ('C', 'Organization works in critical business sectors')
                                ], string='Business type and regulatory requirements', )
    iso_27001_process       = fields.Selection([
                                ('A', 'Standard processes with standard and repetitive tasks; lots of persons doing work under the organization control carrying out the same tasks; few products or services'),
                                ('B', 'Standard but non-repetitive processes, with high number of products or services'),
                                ('C', 'Complex processes, high number of products and services, many business units included in the scope of certification')
                                ], string='Process and Task', )
    iso_27001_mgmt_system   = fields.Selection([
                                ('A', 'ISMS is already well established and/or other management systems are in place'),
                                ('B', 'Some elements of other management systems are implemented, others not'),
                                ('C', 'No other management system implemented at all, the ISMS is new and not established')
                                ], string='Management system establishment level', )
    iso_27001_number_process= fields.Selection([
                                ('A', 'Only one key business process with few interfaces and few business units involved'),
                                ('B', '2–3 simple business processes with few interfaces and few business units involved'),
                                ('C', 'More than 2 complex processes with many interfaces and business units involved')
                                ], string='Number of processes and services', )
    iso_27001_infra         = fields.Selection([
                                ('A', 'Few or highly standardized IT platforms, servers, operating systems, databases, networks, etc'),
                                ('B', 'Several different IT platforms, servers, operating systems, databases, networks'),
                                ('C', 'Many different IT platforms, servers, operating systems, databases, networks')
                                ], string='IT infrastructure complexity', )
    iso_27001_sourcing      = fields.Selection([
                                ('A', 'Little or no dependency on outsourcing or suppliers'),
                                ('B', 'Some dependency on outsourcing or suppliers, related to some but not all important business activities'),
                                ('C', 'High dependency on outsourcing or suppliers, large impact on important business activities')
                                ], string='Dependency on outsourcing and suppliers, including cloud services', )
    iso_27001_itdevelopment = fields.Selection([
                                ('A', 'None or a very limited in-house system/application development'),
                                ('B', 'Some in-house or outsourced system/application development for some important business purposes'),
                                ('C', 'Extensive in-house or outsourced system/application development for important business purposes')
                                ], string='Information System development', )
    iso_27001_itsecurity    = fields.Selection([
                                ('A', 'Only little sensitive or confidential information, low availability requirements'),
                                ('B', 'Higher availability requirements or some sensitive / confidential information'),
                                ('C', 'Higher amount of sensitive or confidential information or high availability requirements')
                                ], string='	Information security requirements confidentiality, integrity and availability(CIA)')
    iso_27001_asset         = fields.Selection([
                                ('A', 'Few critical assets (in terms of CIA)'),
                                ('B', 'Some critical assets'),
                                ('C', 'Many critical assets')
                                ], string='Number of critical assets', )
    iso_27001_drc           = fields.Selection([
                                ('A', 'Low availability requirements and no or one alternative DR site'),
                                ('B', 'Medium or High availability requirements and no or one alternative DR site'),
                                ('C', 'High availability requirements e.g. 24/7 services, Several alternative DR sites,Several Data Centers')
                                ], string='Number of sites and number of Disaster Recovery (DR) sites', )
    # additional iso 27001:2022
    iso_27001_bisnistype_2022    = fields.Selection([
                                ('A', 'Organization works in non-critical business sectors and non-regulated sectors'),
                                ('B', 'Organization has customers in critical business sectors'),
                                ('C', 'Organization works in critical business sectors')
                                ], string='Business type and regulatory requirements', )
    iso_27001_process_2022       = fields.Selection([
                                ('A', 'Standard processes with standard and repetitive tasks; lots of persons doing work under the organization control carrying out the same tasks; few products or services'),
                                ('B', 'Standard but non-repetitive processes, with high number of products or services'),
                                ('C', 'Complex processes, high number of products and services, many business units included in the scope of certification')
                                ], string='Process and Task', )
    iso_27001_mgmt_system_2022   = fields.Selection([
                                ('A', 'ISMS is already well established and/or other management systems are in place'),
                                ('B', 'Some elements of other management systems are implemented, others not'),
                                ('C', 'No other management system implemented at all, the ISMS is new and not established')
                                ], string='Management system establishment level', )
    iso_27001_number_process_2022= fields.Selection([
                                ('A', 'Only one key business process with few interfaces and few business units involved'),
                                ('B', '2–3 simple business processes with few interfaces and few business units involved'),
                                ('C', 'More than 2 complex processes with many interfaces and business units involved')
                                ], string='Number of processes and services', )
    iso_27001_infra_2022         = fields.Selection([
                                ('A', 'Few or highly standardized IT platforms, servers, operating systems, databases, networks, etc'),
                                ('B', 'Several different IT platforms, servers, operating systems, databases, networks'),
                                ('C', 'Many different IT platforms, servers, operating systems, databases, networks')
                                ], string='IT infrastructure complexity', )
    iso_27001_sourcing_2022      = fields.Selection([
                                ('A', 'Little or no dependency on outsourcing or suppliers'),
                                ('B', 'Some dependency on outsourcing or suppliers, related to some but not all important business activities'),
                                ('C', 'High dependency on outsourcing or suppliers, large impact on important business activities')
                                ], string='Dependency on outsourcing and suppliers, including cloud services', )
    iso_27001_itdevelopment_2022 = fields.Selection([
                                ('A', 'None or a very limited in-house system/application development'),
                                ('B', 'Some in-house or outsourced system/application development for some important business purposes'),
                                ('C', 'Extensive in-house or outsourced system/application development for important business purposes')
                                ], string='Information System development', )
    iso_27001_itsecurity_2022    = fields.Selection([
                                ('A', 'Only little sensitive or confidential information, low availability requirements'),
                                ('B', 'Higher availability requirements or some sensitive / confidential information'),
                                ('C', 'Higher amount of sensitive or confidential information or high availability requirements')
                                ], string='	Information security requirements confidentiality, integrity and availability(CIA)')
    iso_27001_asset_2022         = fields.Selection([
                                ('A', 'Few critical assets (in terms of CIA)'),
                                ('B', 'Some critical assets'),
                                ('C', 'Many critical assets')
                                ], string='Number of critical assets', )
    iso_27001_drc_2022           = fields.Selection([
                                ('A', 'Low availability requirements and no or one alternative DR site'),
                                ('B', 'Medium or High availability requirements and no or one alternative DR site'),
                                ('C', 'High availability requirements e.g. 24/7 services, Several alternative DR sites,Several Data Centers')
                                ], string='Number of sites and number of Disaster Recovery (DR) sites', )
    
    # additional iso 27018
    iso_27001_bisnistype_27018    = fields.Selection([
                                ('A', 'Organization works in non-critical business sectors and non-regulated sectors'),
                                ('B', 'Organization has customers in critical business sectors'),
                                ('C', 'Organization works in critical business sectors')
                                ], string='Business type and regulatory requirements', )
    iso_27001_process_27018       = fields.Selection([
                                ('A', 'Standard processes with standard and repetitive tasks; lots of persons doing work under the organization control carrying out the same tasks; few products or services'),
                                ('B', 'Standard but non-repetitive processes, with high number of products or services'),
                                ('C', 'Complex processes, high number of products and services, many business units included in the scope of certification')
                                ], string='Process and Task', )
    iso_27001_mgmt_system_27018   = fields.Selection([
                                ('A', 'ISMS is already well established and/or other management systems are in place'),
                                ('B', 'Some elements of other management systems are implemented, others not'),
                                ('C', 'No other management system implemented at all, the ISMS is new and not established')
                                ], string='Management system establishment level', )
    iso_27001_number_process_27018= fields.Selection([
                                ('A', 'Only one key business process with few interfaces and few business units involved'),
                                ('B', '2–3 simple business processes with few interfaces and few business units involved'),
                                ('C', 'More than 2 complex processes with many interfaces and business units involved')
                                ], string='Number of processes and services', )
    iso_27001_infra_27018         = fields.Selection([
                                ('A', 'Few or highly standardized IT platforms, servers, operating systems, databases, networks, etc'),
                                ('B', 'Several different IT platforms, servers, operating systems, databases, networks'),
                                ('C', 'Many different IT platforms, servers, operating systems, databases, networks')
                                ], string='IT infrastructure complexity', )
    iso_27001_sourcing_27018      = fields.Selection([
                                ('A', 'Little or no dependency on outsourcing or suppliers'),
                                ('B', 'Some dependency on outsourcing or suppliers, related to some but not all important business activities'),
                                ('C', 'High dependency on outsourcing or suppliers, large impact on important business activities')
                                ], string='Dependency on outsourcing and suppliers, including cloud services', )
    iso_27001_itdevelopment_27018 = fields.Selection([
                                ('A', 'None or a very limited in-house system/application development'),
                                ('B', 'Some in-house or outsourced system/application development for some important business purposes'),
                                ('C', 'Extensive in-house or outsourced system/application development for important business purposes')
                                ], string='Information System development', )
    iso_27001_itsecurity_27018    = fields.Selection([
                                ('A', 'Only little sensitive or confidential information, low availability requirements'),
                                ('B', 'Higher availability requirements or some sensitive / confidential information'),
                                ('C', 'Higher amount of sensitive or confidential information or high availability requirements')
                                ], string='	Information security requirements confidentiality, integrity and availability(CIA)')
    iso_27001_asset_27018         = fields.Selection([
                                ('A', 'Few critical assets (in terms of CIA)'),
                                ('B', 'Some critical assets'),
                                ('C', 'Many critical assets')
                                ], string='Number of critical assets', )
    iso_27001_drc_27018           = fields.Selection([
                                ('A', 'Low availability requirements and no or one alternative DR site'),
                                ('B', 'Medium or High availability requirements and no or one alternative DR site'),
                                ('C', 'High availability requirements e.g. 24/7 services, Several alternative DR sites,Several Data Centers')
                                ], string='Number of sites and number of Disaster Recovery (DR) sites', )
    
    # additional iso 27017
    iso_27001_bisnistype_27017    = fields.Selection([
                                ('A', 'Organization works in non-critical business sectors and non-regulated sectors'),
                                ('B', 'Organization has customers in critical business sectors'),
                                ('C', 'Organization works in critical business sectors')
                                ], string='Business type and regulatory requirements', )
    iso_27001_process_27017       = fields.Selection([
                                ('A', 'Standard processes with standard and repetitive tasks; lots of persons doing work under the organization control carrying out the same tasks; few products or services'),
                                ('B', 'Standard but non-repetitive processes, with high number of products or services'),
                                ('C', 'Complex processes, high number of products and services, many business units included in the scope of certification')
                                ], string='Process and Task', )
    iso_27001_mgmt_system_27017   = fields.Selection([
                                ('A', 'ISMS is already well established and/or other management systems are in place'),
                                ('B', 'Some elements of other management systems are implemented, others not'),
                                ('C', 'No other management system implemented at all, the ISMS is new and not established')
                                ], string='Management system establishment level', )
    iso_27001_number_process_27017= fields.Selection([
                                ('A', 'Only one key business process with few interfaces and few business units involved'),
                                ('B', '2–3 simple business processes with few interfaces and few business units involved'),
                                ('C', 'More than 2 complex processes with many interfaces and business units involved')
                                ], string='Number of processes and services', )
    iso_27001_infra_27017         = fields.Selection([
                                ('A', 'Few or highly standardized IT platforms, servers, operating systems, databases, networks, etc'),
                                ('B', 'Several different IT platforms, servers, operating systems, databases, networks'),
                                ('C', 'Many different IT platforms, servers, operating systems, databases, networks')
                                ], string='IT infrastructure complexity', )
    iso_27001_sourcing_27017      = fields.Selection([
                                ('A', 'Little or no dependency on outsourcing or suppliers'),
                                ('B', 'Some dependency on outsourcing or suppliers, related to some but not all important business activities'),
                                ('C', 'High dependency on outsourcing or suppliers, large impact on important business activities')
                                ], string='Dependency on outsourcing and suppliers, including cloud services', )
    iso_27001_itdevelopment_27017 = fields.Selection([
                                ('A', 'None or a very limited in-house system/application development'),
                                ('B', 'Some in-house or outsourced system/application development for some important business purposes'),
                                ('C', 'Extensive in-house or outsourced system/application development for important business purposes')
                                ], string='Information System development', )
    iso_27001_itsecurity_27017    = fields.Selection([
                                ('A', 'Only little sensitive or confidential information, low availability requirements'),
                                ('B', 'Higher availability requirements or some sensitive / confidential information'),
                                ('C', 'Higher amount of sensitive or confidential information or high availability requirements')
                                ], string='	Information security requirements confidentiality, integrity and availability(CIA)')
    iso_27001_asset_27017         = fields.Selection([
                                ('A', 'Few critical assets (in terms of CIA)'),
                                ('B', 'Some critical assets'),
                                ('C', 'Many critical assets')
                                ], string='Number of critical assets', )
    iso_27001_drc_27017           = fields.Selection([
                                ('A', 'Low availability requirements and no or one alternative DR site'),
                                ('B', 'Medium or High availability requirements and no or one alternative DR site'),
                                ('C', 'High availability requirements e.g. 24/7 services, Several alternative DR sites,Several Data Centers')
                                ], string='Number of sites and number of Disaster Recovery (DR) sites', )
    
    # additional iso 27701
    iso_27001_bisnistype_27701    = fields.Selection([
                                ('A', 'Organization works in non-critical business sectors and non-regulated sectors'),
                                ('B', 'Organization has customers in critical business sectors'),
                                ('C', 'Organization works in critical business sectors')
                                ], string='Business type and regulatory requirements', )
    iso_27001_process_27701       = fields.Selection([
                                ('A', 'Standard processes with standard and repetitive tasks; lots of persons doing work under the organization control carrying out the same tasks; few products or services'),
                                ('B', 'Standard but non-repetitive processes, with high number of products or services'),
                                ('C', 'Complex processes, high number of products and services, many business units included in the scope of certification')
                                ], string='Process and Task', )
    iso_27001_mgmt_system_27701   = fields.Selection([
                                ('A', 'ISMS is already well established and/or other management systems are in place'),
                                ('B', 'Some elements of other management systems are implemented, others not'),
                                ('C', 'No other management system implemented at all, the ISMS is new and not established')
                                ], string='Management system establishment level', )
    iso_27001_number_process_27701= fields.Selection([
                                ('A', 'Only one key business process with few interfaces and few business units involved'),
                                ('B', '2–3 simple business processes with few interfaces and few business units involved'),
                                ('C', 'More than 2 complex processes with many interfaces and business units involved')
                                ], string='Number of processes and services', )
    iso_27001_infra_27701         = fields.Selection([
                                ('A', 'Few or highly standardized IT platforms, servers, operating systems, databases, networks, etc'),
                                ('B', 'Several different IT platforms, servers, operating systems, databases, networks'),
                                ('C', 'Many different IT platforms, servers, operating systems, databases, networks')
                                ], string='IT infrastructure complexity', )
    iso_27001_sourcing_27701      = fields.Selection([
                                ('A', 'Little or no dependency on outsourcing or suppliers'),
                                ('B', 'Some dependency on outsourcing or suppliers, related to some but not all important business activities'),
                                ('C', 'High dependency on outsourcing or suppliers, large impact on important business activities')
                                ], string='Dependency on outsourcing and suppliers, including cloud services', )
    iso_27001_itdevelopment_27701 = fields.Selection([
                                ('A', 'None or a very limited in-house system/application development'),
                                ('B', 'Some in-house or outsourced system/application development for some important business purposes'),
                                ('C', 'Extensive in-house or outsourced system/application development for important business purposes')
                                ], string='Information System development', )
    iso_27001_itsecurity_27701    = fields.Selection([
                                ('A', 'Only little sensitive or confidential information, low availability requirements'),
                                ('B', 'Higher availability requirements or some sensitive / confidential information'),
                                ('C', 'Higher amount of sensitive or confidential information or high availability requirements')
                                ], string='	Information security requirements confidentiality, integrity and availability(CIA)')
    iso_27001_asset_27701         = fields.Selection([
                                ('A', 'Few critical assets (in terms of CIA)'),
                                ('B', 'Some critical assets'),
                                ('C', 'Many critical assets')
                                ], string='Number of critical assets', )
    iso_27001_drc_27701           = fields.Selection([
                                ('A', 'Low availability requirements and no or one alternative DR site'),
                                ('B', 'Medium or High availability requirements and no or one alternative DR site'),
                                ('C', 'High availability requirements e.g. 24/7 services, Several alternative DR sites,Several Data Centers')
                                ], string='Number of sites and number of Disaster Recovery (DR) sites', )

    # additional iso 22000:2018 
    iso_22000_hazard_no     = fields.Char(string='Total No of Hazard', )
    iso_22000_hazard_desc   = fields.Text(string='Hazard Description', )
    iso_22000_process_no    = fields.Char(string='Total No of Process', )
    iso_22000_process_desc  = fields.Text(string='Process Description', )
    iso_22000_tech_no       = fields.Char(string='Total No of Tech', )
    iso_22000_tech_desc     = fields.Text(string='Tech Description', )
    
    # multisite 
    site_name               = fields.Char(string='Site Name', )
    site_address            = fields.Text(string='Site Address', )
    site_emp_total          = fields.Char(string='Total Site Employee', )
    site_activity           = fields.Text(string='Site Activity', )


    state           =fields.Selection([
                            ('new',         'New'),
                            ('waiting',     'Waiting Verify'),
                            ('review',      'Review'),
                            ('approved',    'Verify Head'),
                            ('reject',      'Reject'),
                            ('quotation',   'Quotation'),
                        ], string='Status', readonly=True, copy=False, index=True, tracking=True, default='new')
    audit_stage = fields.Selection([
                            ('initial',         'Initial Assesment'),
                            ('recertification', 'Recertification'),
                            ('transfer_surveilance',    'Transfer Assesment from Surveilance'),
                            ('transfer_recert',         'Transfer Assesment from Recertification'),
                        ], string='Audit Stage', index=True, )

    audit_similarities = fields.Selection([
                            ('similar',         'Similar Activities processes'),
                            ('diferences',      'Diferences between Activities'),
                        ], string='Multisite Similarities', index=True, )

    lingkup = fields.Selection([
                            ('baru',   'Sertifikasi Awal / Baru'),
                            ('ulang', 'Re-Sertifikasi'),
                            ('perluasan',  'Perluasan Ruang Lingkup'),
                            ('transfer',  'Transfer CB / LS'),
                        ], string='Ruang Lingkup', index=True, )
    kepemilikan = fields.Selection([
                            ('bumn',    'BUMN'),
                            ('individu','INDIVIDU'),
                            ('swasta',  'SWASTA'),
                            ('kud',     'KUD'),
                        ], string='Kepemilikan', index=True, )

    count_review        = fields.Integer(string="Count Review", compute="compute_state", store=True)
    count_quotation     = fields.Integer(string="Count Quotation", compute="compute_state", store=True)
    count_sales         = fields.Integer(string="Count Sales", compute="compute_state", store=True)
    count_invoice       = fields.Integer(string="Count Invoice", compute="compute_state", store=True)

    doc_count = fields.Integer(compute='_compute_attached_docs_count', string="Number of attached documents")


# ISPO RELATED fields
    permohonan     = fields.Selection([
                            ('baru',   'Sertifikasi Awal / Baru'),
                            ('ulang', 'Re-Sertifikasi'),
                            ('perluasan',  'Perluasan Ruang Lingkup'),
                            ('transfer',  'Transfer CB / LS'),
                        ], string='Ruang Lingkup', index=True, )
    lingkup = fields.Selection([
                            ('kebun',   'KEBUN'),
                            ('pabrik', 'Pabrik'),
                            ('integrasi',  'Integrasi'),
                        ], string='Ruang Lingkup', index=True, )
    tipe_tanah = fields.Selection([
                            ('tidak_gambut',   'Tidak Bergambut'),
                            ('gambut', 'Gambut'),
                        ], string='Tipe Tanah', index=True, )
    sebaran_tanah = fields.Selection([
                            ('tidak',       'Tidak berbatasan langsung dengan lahan negara/ masyarakat'),
                            ('berbatasan',  'Berbatasan dengan lahan negara/  Kawasan lindung namun terdapat Batasan alam yang jelas'),
                            ('lindung',     'Sebagian atau seluruhnya berada pada Kawasan Linding'),
                        ], string='Sebaran Geografis', index=True, )
    tipe_kegiatan = fields.Selection([
                            ('tidak',       'Tidak ada peremajaan'),
                            ('ada',  'Ada peremajaan'),
                        ], string='Tipe Kegiatan', index=True, )
    topografi = fields.Selection([
                            ('datar',       'Datar'),
                            ('bukit',  'Berbukit'),
                        ], string='Topografi Tanah', index=True, )

    is_kebun_pabrik     = fields.Boolean(string='Kebun / Pabrik')
                        
    legal_lokasi        = fields.Char(string='Ijin Lokasi', )
    legal_iup           = fields.Char(string='Ijin IUP', )
    legal_spup          = fields.Char(string='Ijin SPUP', )
    legal_itubp         = fields.Char(string='Ijin ITBUP', )
    legal_prinsip       = fields.Char(string='Ijin Prinsip', )
    legal_menteri       = fields.Char(string='Ijin Menteri', )
    legal_bkpm          = fields.Char(string='Ijin BKPM', )

    perolehan_a         = fields.Char(string='APL', )
    perolehan_b         = fields.Char(string='HPK', )
    perolehan_c         = fields.Char(string='Tanah Adat', )
    perolehan_d         = fields.Char(string='Tanah Lain', )

    legal_hgu           = fields.Char(string='HGU / HGB', )
    legal_amdal         = fields.Char(string='Izin Lingkungan - AMDAL', )

    is_plasma_swadaya   = fields.Boolean(string='Plasma / Swadaya', )

    kebun_sertifikat    = fields.Char(string='Sertifikat Tanah', )
    kebun_penetapan     = fields.Char(string='Penetapan', )
    kebun_std           = fields.Char(string='Surat Tanda Daftar', )
    kebun_pembentukan   = fields.Char(string='Pembentukan', )
    kebun_konversi      = fields.Char(string='Konversi', )
    kebun_kesepakatan   = fields.Char(string='Kesepakatan', )

    sertifikat_ispo     = fields.Text(string='Sertifikat ISPO', )

    tani_nama           = fields.Char(string='Nama Kelompok Tani', )
    tani_adrt           = fields.Char(string='Akta Pendirian', )
    tani_pembentukan    = fields.Char(string='Pembentukan Kelompok Tani', )
    tani_rko            = fields.Char(string='Rencana Kegiatan', )
    tani_kegiatan       = fields.Char(string='Laporan Kegiatan', )
    tani_jumlah         = fields.Char(string='Jumlah Petani', )
    tani_area           = fields.Char(string='Total Area', )
    tani_tertanam       = fields.Char(string='Area Tertanam', )
    tani_tbs            = fields.Char(string='Produksi TBS', )

    peta_lokasi         = fields.Char(string='Peta Lokasi', )

    add_nama_perusahaan = fields.Char(string='Perusahaan Konsultan', )
    add_sertifikasi     = fields.Char(string='Sertifikasi Lain', )
    add_pic             = fields.Char(string='Personal Perusahaan Yang sudah pelatihan Auditor ISPO', )
    add_kendali         = fields.Boolean(string='Tim Kendali Internal', )
    add_kendali_jml     = fields.Integer(string='Tim Kendali Internal Jumlah', )
    add_auditor         = fields.Boolean(string='Auditor Internal', )
    add_auditor_jml     = fields.Integer(string='Auditor Internal Jumlah', )

    # ispo_kebun          = fields.One2many('tsi.ispo.kebun', 'reference', string="Kebun", index=True)
    # ispo_pabrik         = fields.One2many('tsi.ispo.pabrik', 'reference', string="Pabrik", index=True)
    # ispo_pemasok        = fields.One2many('tsi.ispo.pemasok', 'reference', string="Pemasok", index=True)
    ispo_sertifikat     = fields.One2many('tsi.ispo.sertifikat', 'reference', string="Sertifikat", index=True)


    mandays_ori_lines   = fields.One2many('tsi.iso.mandays_app', 'reference_id', string="Mandays Original", index=True)
    lines_initial       = fields.One2many('tsi.iso.initial', 'reference_id', string="Lines Initial", index=True)
    lines_surveillance  = fields.One2many('tsi.iso.surveillance', 'reference_id', string="Lines SUrveillance", index=True)
    mandays_pa          = fields.One2many('tsi.iso.mandays.pa_app', 'reference_id', string="PA", index=True)
    mandays_justify     = fields.One2many('tsi.iso.mandays.justification_app', 'reference_id', string="Justification", index=True)

    partner_site        = fields.One2many('tsi.iso.site', 'reference_id', string="Personnel Situation", index=True)

    show_salesinfo      = fields.Boolean(string='Additional Info', default=False)
    salesinfo_site      = fields.One2many('tsi.iso.additional_salesinfo', 'reference_id', string="Additional Info", index=True)
    
    show_14001          = fields.Boolean(string='Show 14001', default=False)    
    iso_14001_env_aspect    = fields.Text(string='Environmental Aspects', )
    iso_14001_obligation    = fields.Text(string='14001 Legal Obligation', )

    show_45001          = fields.Boolean(string='Show 45001', default=False)    
    iso_45001_key_hazard    = fields.Text(string='Significant Hazard / OHS Risks', default="Bahan Mekanik, Eelktrik\nBahaya Api, Ketinggian, Ledakan, Kimia")
    iso_45001_obligation    = fields.Text(string='Specific Relevant Obligations', default="PerMenNaker No.5/2018 ttg K3 Lingkungan Kerja\nPerMenNaker No.8/2020 ttg K3 Pesawat Angkut & Angkat" )

    show_27001          = fields.Boolean(string='Show 27001', default=False)
    show_27701          = fields.Boolean(string='Show 27701', default=False) 
    show_27017          = fields.Boolean(string='Show 27017', default=False) 
    show_27018          = fields.Boolean(string='Show 27018', default=False)   
    show_27001_2022          = fields.Boolean(string='Show 27001', default=False)    
    additional_27001    = fields.One2many('tsi.iso.additional_27001', 'reference_id', string="Additional Info for ISO 27001", index=True)
    additional_27701    = fields.One2many('tsi.iso.additional_27001', 'reference_id3', string="Additional Info for ISO 27701", index=True)
    additional_27017    = fields.One2many('tsi.iso.additional_27001', 'reference_id1', string="Additional Info for ISO 27017", index=True)
    additional_27018    = fields.One2many('tsi.iso.additional_27001', 'reference_id2', string="Additional Info for ISO 27018", index=True)

    show_31000          = fields.Boolean(string='Show 31000', default=False)    
    salesinfo_site_31000    = fields.One2many('tsi.iso.additional_salesinfo', 'reference_id7', string="Additional Info", index=True)

    show_9994          = fields.Boolean(string='Show 9994', default=False)
    salesinfo_site_9994    = fields.One2many('tsi.iso.additional_salesinfo', 'reference_id8', string="Additional Info", index=True)
    
    show_gdp        = fields.Boolean(string='Show GDP', default=False)
    ea_code_gdp        = fields.Many2many('tsi.ea_code', 'rel_tsi_iso_ea_gdp', string="EA Code Existing")
    accreditation_gdp       = fields.Many2one('tsi.iso.accreditation', string="Accreditation")
    complexity_gdp          = fields.Selection([
                            ('Na',  'NA'),
                            ('Limited',   'Limited'),
                            ('Low',   'Low'),
                            ('Medium',   'Medium'),
                            ('High',   'High'),
                        ], string='Complexity', index=True, )
    salesinfo_site_gdp    = fields.One2many('tsi.iso.additional_salesinfo', 'reference_id17', string="Additional Info", index=True)

    show_56001        = fields.Boolean(string='Show GDP', default=False)
    ea_code_56001        = fields.Many2many('tsi.ea_code', 'rel_tsi_iso_ea_56001', string="EA Code Existing")
    accreditation_56001       = fields.Many2one('tsi.iso.accreditation', string="Accreditation")
    complexity_56001          = fields.Selection([
                            ('Na',  'NA'),
                            ('Limited',   'Limited'),
                            ('Low',   'Low'),
                            ('Medium',   'Medium'),
                            ('High',   'High'),
                        ], string='Complexity', index=True, )
    salesinfo_site_56001    = fields.One2many('tsi.iso.additional_salesinfo', 'reference_id18', string="Additional Info", index=True)

    show_13485        = fields.Boolean(string='Show 13485', default=False)
    show_37301        = fields.Boolean(string='Show 13485', default=False)
    show_smk        = fields.Boolean(string='Show 13485', default=False)
    show_19649        = fields.Boolean(string='Show 19649', default=False)
    show_ce        = fields.Boolean(string='Show CE', default=False)
    show_19650        = fields.Boolean(string='Show 19650', default=False)
    show_196502        = fields.Boolean(string='Show 19650', default=False)
    show_196503        = fields.Boolean(string='Show 19650', default=False)
    show_196504        = fields.Boolean(string='Show 19650', default=False)
    show_196505        = fields.Boolean(string='Show 19650', default=False)
    show_21000        = fields.Boolean(string='Show 13485', default=False)
    salesinfo_site_13485    = fields.One2many('tsi.iso.additional_salesinfo', 'reference_id11', string="Additional Info", index=True)
    salesinfo_site_19649    = fields.One2many('tsi.iso.additional_salesinfo', 'reference_id25', string="Additional Info", index=True)
    salesinfo_site_ce    = fields.One2many('tsi.iso.additional_salesinfo', 'reference_id19', string="Additional Info", index=True)
    salesinfo_site_19650    = fields.One2many('tsi.iso.additional_salesinfo', 'reference_id20', string="Additional Info", index=True)
    salesinfo_site_196502    = fields.One2many('tsi.iso.additional_salesinfo', 'reference_id21', string="Additional Info", index=True)
    salesinfo_site_196503    = fields.One2many('tsi.iso.additional_salesinfo', 'reference_id22', string="Additional Info", index=True)
    salesinfo_site_196504    = fields.One2many('tsi.iso.additional_salesinfo', 'reference_id23', string="Additional Info", index=True)
    salesinfo_site_196505    = fields.One2many('tsi.iso.additional_salesinfo', 'reference_id24', string="Additional Info", index=True)
    # ea_code_13485             = fields.Many2one('tsi.ea_code', string="EA Code")
    ea_code_13485_1        = fields.Many2many('tsi.ea_code', 'rel_tsi_iso_ea_13485', string="EA Code Existing")
    accreditation_13485       = fields.Many2one('tsi.iso.accreditation', string="Accreditation")
    accreditation_19649       = fields.Many2one('tsi.iso.accreditation', string="Accreditation")
    accreditation_ce       = fields.Many2one('tsi.iso.accreditation', string="Accreditation")
    accreditation_19650       = fields.Many2one('tsi.iso.accreditation', string="Accreditation")
    accreditation_196502       = fields.Many2one('tsi.iso.accreditation', string="Accreditation")
    accreditation_196503       = fields.Many2one('tsi.iso.accreditation', string="Accreditation")
    accreditation_196504       = fields.Many2one('tsi.iso.accreditation', string="Accreditation")
    accreditation_196505       = fields.Many2one('tsi.iso.accreditation', string="Accreditation")
    complexity_13485          = fields.Selection([
                            ('Na',  'NA'),
                            ('Limited',   'Limited'),
                            ('Low',   'Low'),
                            ('Medium',   'Medium'),
                            ('High',   'High'),
                        ], string='Complexity', index=True, )
    cause_13485       = fields.Text('Mandatory SNI',)
    notes_13485       = fields.Text('Notes', )
    notes_19649       = fields.Text('Notes', )
    notes_ce       = fields.Text('Notes', )
    notes_19650       = fields.Text('Notes', )
    notes_196502      = fields.Text('Notes', )
    notes_196503      = fields.Text('Notes', )
    notes_196504       = fields.Text('Notes', )
    notes_196505       = fields.Text('Notes', )
    show_37001        = fields.Boolean(string='Show 31000', default=False)
    salesinfo_site_37001    = fields.One2many('tsi.iso.additional_salesinfo', 'reference_id9', string="Additional Info", index=True)
    accreditation_37001     = fields.Many2one('tsi.iso.accreditation', string="Accreditation")
    notes_37001     = fields.Char('Notes')

    show_22301        = fields.Boolean(string='Show 22301', default=False)
    salesinfo_site_22301    = fields.One2many('tsi.iso.additional_salesinfo', 'reference_id16', string="Additional Info", index=True)
    accreditation_22301     = fields.Many2one('tsi.iso.accreditation', string="Accreditation")
    notes_22301     = fields.Char('Notes')

    akre            = fields.Many2one('tsi.iso.accreditation', string="Accreditation")
    specific        = fields.Char(string='Specific Requirements')
    additional      = fields.Char(string='Additional Notes')

    show_haccp          = fields.Boolean(string='Show HACCP', default=False)    
    additional_haccp    = fields.One2many('tsi.iso.additional_haccp', 'reference_id', string="Additional HACCP", index=True)
    #additional HCCp
    hazard_number_site1      = fields.Char(string='Number of hazard')
    hazard_number_site2       = fields.Char(string='Number of hazard')
    hazard_number_site3       = fields.Char(string='Number of hazard')
    hazard_describe_site1     = fields.Char(string='Describe Hazard')
    hazard_describe_site2     = fields.Char(string='Describe Hazard')
    hazard_describe_site3     = fields.Char(string='Describe Hazard')
    process_number_site1      = fields.Char(string='Number of process')
    process_number_site2      = fields.Char(string='Number of process')
    process_number_site3      = fields.Char(string='Number of process')
    process_describe_site1    = fields.Char(string='Describe Process')
    process_describe_site2    = fields.Char(string='Describe Process')
    process_describe_site3    = fields.Char(string='Describe Process')
    tech_number_site1         = fields.Char(string='Number of technology')
    tech_number_site2         = fields.Char(string='Number of technology')
    tech_number_site3         = fields.Char(string='Number of technology')
    tech_describe_site1       = fields.Char(string='Describe Technology')
    tech_describe_site2       = fields.Char(string='Describe Technology')
    tech_describe_site3       = fields.Char(string='Describe Technology')

    show_22000           = fields.Boolean(string='Show 22000', default=False) 
    show_fscc           = fields.Boolean(string='Show 22000', default=False) 

    show_ispo           = fields.Boolean(string='Show ISPO', default=False)   
    sertifikasi_baru = fields.Boolean(string='Sertifikasi Awal/Baru')
    re_sertifikasi = fields.Boolean(string='Re-Sertifikasi')
    perluasan = fields.Boolean(string='Perluasan Ruang Lingkup')
    transfer = fields.Boolean(string='Transfer CB/LS') 

    segment_id      = fields.Many2many('res.partner.category', string='Segment')
    kategori        = fields.Selection([
                            ('bronze',  'Bronze'),
                            ('silver',  'Silver'),
                            ('gold',    'Gold'),
                        ], string='Category', index=True)
    declaration     = fields.Text(string='Declaration')
    user_signature  = fields.Binary(string='Signature')

    sale_order_id = fields.Many2one('sale.order', string="Sale Order")
    nomor_kontrak = fields.Char(string='Nomor Kontrak', readonly=True)
    audit_id = fields.Many2one('audit.notification', string="Audit")
    # sale_order_status = fields.Selection([
    #     ('draft', 'Quotation'),
    #     ('sent', 'Confirm to Closing'),
    #     ('sale', 'Sales Order'),
    #     ('done', 'Locked'),
    #     ('cancel', 'Cancelled'),
    #     ], string='Order Status', readonly=True, copy=False, index=True, tracking=3, default='draft', compute='_compute_sale_order_status',)
    # Field Selection untuk Legalitas
    legalitas_type = fields.Selection([
        ('integrasi', 'Integrasi'),
        ('kebun', 'Kebun'),
        ('pabrik', 'Pabrik'),
        ('swadaya_plasma', 'Swadaya/Plasma'),
    ], string='Tipe Legalitas')

    # Field-field tambahan untuk Integrasi
    hgu = fields.Char(string='Hak Guna Usaha (HGU)')
    hgb = fields.Char(string='Hak Guna Bangunan (HGB)')
    iup = fields.Char(string='IUP / IUPB / Izin prinsip/BKPM/OSS/ITUK/ITUBP/SPUP')
    pup = fields.Selection([
        ('kelas_i', 'Kelas I'),
        ('kelas_ii', 'Kelas II'),
        ('kelas_iii', 'Kelas III'),
    ], string='PUP / Kelas Kebun')
    izin_lingkungan_integrasi = fields.Char(string='Izin Lingkungan (Integrasi)')
    luas_lahan = fields.Float(string='Luas Lahan')
    kapasitas_pabrik = fields.Float(string='Kapasitas Pabrik')
    izin_lokasi = fields.Char(string='Izin Lokasi')
    apl = fields.Char(string='APL / Pelepasan Kawasan Hutan/Tukar Menukar Kawasan/Tanah Adat/Ulayat')
    risalah_panitia = fields.Char(string='Risalah Panitia A/B')
    lahan_gambut = fields.Char(string='Lahan Gambut / Mineral')
    peta = fields.Char(string='Peta – Peta')

    # Field-field tambahan untuk Kebun
    hgu_kebun = fields.Char(string='Hak Guna Usaha (HGU)')
    iupb = fields.Char(string='IUPB / Izin prinsip/BKPM/OSS/ITUK/ITUBP/SPUP')
    izin_lingkungan_kebun = fields.Char(string='Izin Lingkungan')

    # Field-field tambahan untuk Pabrik
    hgb_pabrik = fields.Char(string='Hak Guna Bangunan (HGB)')
    kapasitas_pabrik_pabrik = fields.Float(string='Kapasitas Pabrik')

    # Field-field tambahan untuk Swadaya/Plasma
    shm = fields.Char(string='SHM/Kepemilikan Lahan Yang diakui Pemerintah')
    stdb = fields.Char(string='STDB')
    sppl = fields.Char(string='SPPL')
    akta_pendirian = fields.Char(string='Akta Pendirian dan SK Kemenhumkam')
    kebun_lines       = fields.One2many('tsi.kebun', 'reference', string="Kebun")
    pabrik_lines       = fields.One2many('tsi.pabrik', 'reference', string="Pabrik")

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
    ], string='Status Sales', compute='_compute_state', store=True, tracking=True, related="sale_order_id.state")

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
        string='Audit Status', related="sale_order_id.audit_status", store=True)
    
    status_klien = fields.Selection([
        ('New', 'New'),
        ('active', 'Active'),
        ('suspend', 'Suspend'),
        ('withdraw', 'Withdrawn'),
        ('Re-Active', 'Re-Active'),
        ('Double', 'Double'),
    ], string='State', store=True, default="New")

    # @api.constrains('customer')
    # def _check_customer_name_format(self):
    #     for record in self:
    #         customer_name = record.customer.name

    #         # 1. Validasi apakah nama dimulai dengan "PT " atau "CV " tanpa titik.
    #         if customer_name.startswith("PT "):
    #             # Validasi untuk PT
    #             if re.search(r'\b(pt\.|pt\.?)\b', customer_name, re.IGNORECASE):
    #                 raise ValidationError("Nama perusahaan tidak boleh mengandung format yang salah seperti 'PT.' atau 'Pt.'.")
    #         elif customer_name.startswith("CV "):
    #             # Validasi untuk CV
    #             if re.search(r'\b(cv\.|cv\.?)\b', customer_name, re.IGNORECASE):
    #                 raise ValidationError("Nama perusahaan tidak boleh mengandung format yang salah seperti 'CV.' atau 'Cv.'.")
    #         else:
    #             raise ValidationError("Nama perusahaan harus dimulai dengan 'PT ' atau 'CV ' (tanpa titik).")
            
    #         # 2. Pastikan nama depan dimulai dengan huruf kapital
    #         name_parts = customer_name.split(" ", 1)
    #         if len(name_parts) > 1:
    #             first_name = name_parts[1]
    #             if not first_name[0].isupper():
    #                 raise ValidationError("Nama depan perusahaan harus dimulai dengan huruf kapital.")

    

    def compute_state(self):
        for rec in self:
            if rec.sale_order_id and rec.sale_order_id.nomor_kontrak:
                rec.nomor_kontrak = rec.sale_order_id.nomor_kontrak
    
    def compute_state(self):
        for rec in self:
            if rec.sale_order_id and rec.sale_order_id.state_sales:
                rec.state = rec.sale_order_id.state_sales

    def compute_state(self):
        for rec in self:
            if rec.sale_order_id and rec.sale_order_id.audit_status:
                rec.audit_status = rec.sale_order_id.audit_status
    

    @api.depends('name')
    def _compute_audit_status(self):
        for record in self:
            if record.id:
                sale_order = self.env['sale.order'].search([
                    ('iso_reference', '=', record.name),
                    ('state', '=', 'sale')
                ], limit=1)

                record.audit_status = sale_order.audit_status if sale_order else False

    @api.depends('name')
    def _compute_state(self):
        for record in self:
            if record.id:
                sale_order = self.env['sale.order'].search([
                    ('iso_reference', '=', record.name)
                ], limit=1)

                if sale_order:
                    record.state_sales = sale_order.state
                else:
                    record.state_sales = False


    # @api.depends('sale_order_id')
    # def _compute_sale_order_status(self):
    #     for record in self:
    #         if record.sale_order_id:
    #             record.sale_order_status = record.sale_order_id.state
    #         else:
    #             record.sale_order_status = 'draft'  # Ganti dengan status default jika diperlukan

    @api.onchange('certification')
    def _onchange_certification(self):
        if self.certification == 'Single Site':
            self.tx_site_count = 1
        elif self.certification == 'Multi Site':
            self.tx_site_count = False  # Anda dapat mengganti dengan nilai default yang sesuai untuk multi-site

    @api.onchange('customer')
    def _onchange_customer(self):
        if self.customer:
            if self.customer.office_address:
                self.office_address = self.customer.office_address;
            if self.customer.contact_person:
                self.contact_person = self.customer.contact_person;
            if self.customer.invoice_address:
                self.invoicing_address = self.customer.invoice_address;
            if self.customer.phone:
                self.telepon = self.customer.phone;
            if self.customer.email:
                self.email = self.customer.email;
            if self.customer.website:
                self.website = self.customer.website;
    
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
                obj.show_fscc = False
                obj.show_22301 = False
                obj.show_31000 = False
                obj.show_37001 = False
                obj.show_13485 = False
                obj.show_19649 = False
                obj.show_smk = False
                obj.show_ce = False
                obj.show_19650 = False
                obj.show_196502 = False
                obj.show_196503 = False
                obj.show_196504 = False
                obj.show_196505 = False
                obj.show_21000 = False  
                obj.show_37301 = False
                obj.show_9994 = False
                obj.show_gdp = False
                obj.show_56001 = False
                obj.show_ispo = False               
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
                    if standard.name == 'ISO 27001:2013' :
                        if obj.show_salesinfo != True :
                            obj.show_salesinfo = False
                        obj.show_27001 = True
                    if standard.name == 'ISO 27001:2022' :
                        if obj.show_salesinfo != True :
                            obj.show_salesinfo = False
                        obj.show_27001_2022 = True
                    if standard.name == 'ISO 27701:2019' :
                        if obj.show_salesinfo != True :
                            obj.show_salesinfo = False
                        obj.show_27701 = True
                    if standard.name == 'ISO 27017:2015' :
                        if obj.show_salesinfo != True :
                            obj.show_salesinfo = False
                        obj.show_27017 = True
                    if standard.name == 'ISO 27018:2019' :
                        if obj.show_salesinfo != True :
                            obj.show_salesinfo = False
                        obj.show_27018 = True
                    if standard.name == 'ISO 22000:2018' :
                        if obj.show_salesinfo != True :
                            obj.show_salesinfo = False
                        obj.show_22000 = True
                    if standard.name == 'FSCC' :
                        if obj.show_salesinfo != True :
                            obj.show_salesinfo = False
                        obj.show_fscc = True
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
                    if standard.name == 'IATF 16949' :
                        if obj.show_salesinfo != True :
                            obj.show_salesinfo = False
                        obj.show_19649 = True
                    if standard.name == 'ISO 37301:2021' :
                        if obj.show_salesinfo != True :
                            obj.show_salesinfo = False
                        obj.show_37301 = True
                    if standard.name == 'ISO 9994:2018' :
                        if obj.show_salesinfo != True :
                            obj.show_salesinfo = False
                        obj.show_9994 = True
                    if standard.name == 'GDP' :
                        if obj.show_salesinfo != True :
                            obj.show_salesinfo = False
                        obj.show_gdp = True
                    if standard.name == 'ISO 56001:2024' :
                        if obj.show_salesinfo != True :
                            obj.show_salesinfo = False
                        obj.show_56001 = True
                    if standard.name == 'ISO 37001:2016' :
                        if obj.show_salesinfo != True :
                            obj.show_salesinfo = False
                        obj.show_37001 = True
                    if standard.name == 'SMK3' :
                        if obj.show_salesinfo != True :
                            obj.show_salesinfo = False
                        obj.show_smk = True
                    if standard.name == 'CE Marking' :
                        if obj.show_salesinfo != True :
                            obj.show_salesinfo = False
                        obj.show_ce = True
                    if standard.name == 'ISO 19650:2018' :
                        if obj.show_salesinfo != True :
                            obj.show_salesinfo = False
                        obj.show_19650 = True
                    if standard.name == 'ISO 19650-2:2018' :
                        if obj.show_salesinfo != True :
                            obj.show_salesinfo = False
                        obj.show_196502 = True
                    if standard.name == 'ISO 19650-3:2020' :
                        if obj.show_salesinfo != True :
                            obj.show_salesinfo = False
                        obj.show_196503 = True
                    if standard.name == 'ISO 19650-4:2022' :
                        if obj.show_salesinfo != True :
                            obj.show_salesinfo = False
                        obj.show_196504 = True
                    if standard.name == 'ISO 19650-5:2020' :
                        if obj.show_salesinfo != True :
                            obj.show_salesinfo = False
                        obj.show_196505 = True
                    if standard.name == 'ISO 21000:2018' :
                        if obj.show_salesinfo != True :
                            obj.show_salesinfo = False
                        obj.show_21000 = True
                    if standard.name == 'ISPO' :
                        if obj.show_ispo != True :
                            obj.show_ispo = False
                        obj.show_ispo = True
                    elif standard.name == 'ISO 9001:2015' :
                        obj.show_salesinfo = True
                    #else :
                    #    obj.show_salesinfo = True

    def _compute_attached_docs_count(self):
        attachment_obj = self.env['ir.attachment']
        for task in self:
            task.doc_count = attachment_obj.search_count([
                '&', ('res_model', '=', 'tsi.iso'), ('res_id', '=', task.id)
            ])

    def attached_docs_view_action(self):
        self.ensure_one()
        domain = [
            '&', ('res_model', '=', 'tsi.iso'), ('res_id', 'in', self.ids),
        ]
        return {
            'name': _('Attachments'),
            'domain': domain,
            'res_model': 'ir.attachment',
            'type': 'ir.actions.act_window',
            'view_id': False,
            'view_mode': 'kanban,tree,form',
            'view_type': 'form',
            'help': _('''<p class="oe_view_nocontent_create">
                        Documents are attached to the tasks of your project.</p>
                    '''),
            'limit': 80,
            'context': "{'default_res_model': '%s','default_res_id': %d}" % (self._name, self.id)
        }

    @api.depends('customer')
    def compute_state(self):
        for obj in self:
            if obj.id :
                review = self.env['tsi.iso.review'].search_count([('reference.id', '=', obj.id)])
                if review :
                    obj.count_review = review

                count_quotation = self.env['sale.order'].search_count([('iso_reference.id', '=', obj.id),('state', '=', 'draft')])
                if count_quotation :
                    obj.count_quotation = count_quotation

                count_sales     = self.env['sale.order'].search_count([('iso_reference.id', '=', obj.id),('state', '=', 'sale')])
                if count_sales :
                    obj.count_sales = count_sales

                count_invoice   = self.env['account.move'].search_count([('iso_reference.id', '=', obj.id)])
                if count_invoice :
                    obj.count_invoice = count_invoice
    
    # @api.depends('customer')
    # def compute_state_sale(self):
    #     for obj in self:
    #         if obj.id :
    #             count_sales     = self.env['sale.order'].search_count([('iso_reference.id', '=', obj.id),('state', '=', 'sale')])
    #             if count_sales :
    #                 obj.count_sales = count_sales


                # obj.count_review    = self.env['tsi.iso.review'].search_count([('reference.id', '=', obj.id)])
                # obj.count_quotation = self.env['sale.order'].search_count([('iso_reference.id', '=', obj.id)])
                # obj.count_sales     = self.env['sale.order'].search_count([('iso_reference.id', '=', obj.id),('state', '=', 'sale')])
                # obj.count_invoice   = self.env['account.move'].search_count([('iso_reference.id', '=', obj.id)])

                # obj.count_patrol = self.env['kontrak.checkpoint'].search_count([('id', 'in', obj.check_lines.ids)])

    def get_iso_review(self):
            self.ensure_one()
            return {
                'type': 'ir.actions.act_window',
                'name': 'Review',
                'view_mode': 'tree,form',
                'res_model': 'tsi.iso.review',
                'domain': [('reference', '=', self.id)],
                'context': "{'create': True}"
            }

    def get_iso_quotation(self):
            self.ensure_one()
            return {
                'type': 'ir.actions.act_window',
                'name': 'Quotation',
                'view_mode': 'tree,form',
                'res_model': 'sale.order',
                'domain': [('iso_reference', '=', self.id)],
                'context': "{'create': True}"
            }

    def get_iso_sales(self):
            self.ensure_one()
            return {
                'type': 'ir.actions.act_window',
                'name': 'Sales',
                'view_mode': 'tree,form',
                'res_model': 'sale.order',
                'domain': [('iso_reference', '=', self.id),('state', '=', 'sale')],
                'context': "{'create': True}"
            }

    def get_iso_invoice(self):
            self.ensure_one()
            return {
                'type': 'ir.actions.act_window',
                'name': 'Review',
                'view_mode': 'tree,form',
                'res_model': 'account.move',
                'domain': [('iso_reference', '=', self.id)],
                'context': "{'create': True}"
            }

    @api.model
    def create(self, vals):
        sequence = self.env['ir.sequence'].next_by_code('tsi.iso')
        vals['name'] = sequence or _('New')

        if 'customer' not in vals:
            partner = self.env['res.partner'].search([('name', '=', vals.get('company_name'))])
            if not partner:
                partner = self.env['res.partner'].create({
                    'name': vals['company_name'],
                    'company_type': 'company'
                })
            vals['customer'] = partner.id

  
        record = super(ISO, self).create(vals)
        record.update_franchise_contacts()
        record.update_associate_contacts()
        return record

    def write(self, vals):
        res = super(ISO, self).write(vals)
        self.update_franchise_contacts()
        self.update_associate_contacts()
        return res
    
    def update_associate_contacts(self):
        for record in self:
            if record.associate_id:
                contact_vals = {
                    'partner_ids': record.associate_id.id,
                    'name_associates': record.customer.id,
                    'address_associates': record.customer.office_address,
                    'phone_associates': record.phone_associate,
                    'email_associates': record.email_associate,
                }
                contact_associate = self.env['res.partner.custom.contacts'].search([
                    ('partner_ids', '=', record.associate_id.id),
                    ('name_associates', '=', record.customer.id),
                ], limit=1)

                if contact_associate:
                    contact_associate.write(contact_vals)
                else:
                    # self.env['res.partner.custom.contacts'].create(contact_vals)
                    contact_associate = self.env['res.partner.custom.contacts'].create(contact_vals)
                    
                update_contact_vals = {
                    'partner_ids': record.customer.id,
                    'name_associates': record.associate_id.id,
                    'address_associates': record.associate_id.office_address,
                    'phone_associates': record.phone_associate,
                    'email_associates': record.email_associate,
                }
                update_contact_customer = self.env['res.partner.custom.contacts'].search([
                    ('partner_ids', '=', record.customer.id),
                    ('name_associates', '=', record.associate_id.id),
                ], limit=1)
                if update_contact_customer:
                    update_contact_customer.write(update_contact_vals)
                    
                else:
                    # self.env['res.partner.custom.contacts'].create(update_contact_vals)
                    update_contact_customer = self.env['res.partner.custom.contacts'].create(update_contact_vals)


    def update_franchise_contacts(self):
        for record in self:
            if record.franchise_id:
                contact_vals = {
                    'partner_id': record.franchise_id.id,
                    'name_franchise': record.customer.id,
                    'address_franchise': record.customer.office_address,
                    'phone_franchise': record.phone_franchise,
                    'email_franchise': record.email_franchise,
                }
                self.customer.write({'contact_client': True})
                self.customer.write({'is_franchise': True})
                self.customer.write({'is_associate': True})
                # self.customer.write({'pic_id': True})
                self.franchise_id.write({'contact_client': False})
                
                contact_franchise = self.env['res.partner.contact.franchise'].search([
                    ('partner_id', '=', record.franchise_id.id),
                    ('name_franchise', '=', record.customer.id),
                ], limit=1)

                if contact_franchise:
                    contact_franchise.write(contact_vals)
                    
                else:
                    self.env['res.partner.contact.franchise'].create(contact_vals)
                    
                update_contact_vals = {
                    'partner_id': record.customer.id,
                    'name_franchise': record.franchise_id.id,
                    'address_franchise': record.franchise_id.office_address,
                    'phone_franchise': record.phone_franchise,
                    'email_franchise': record.email_franchise,
                }
                update_contact_customer_fr = self.env['res.partner.contact.franchise'].search([
                    ('partner_id', '=', record.customer.id),
                    ('name_franchise', '=', record.franchise_id.id),
                ], limit=1)

                if update_contact_customer_fr:
                    update_contact_customer_fr.write(update_contact_vals)
                else:
                    self.env['res.partner.contact.franchise'].create(update_contact_vals)
                
    

    def create_open_iso(self):
        if self.iso_standard_ids :
            for standard in self.iso_standard_ids :

                self.env['tsi.iso.review'].create({
                    'reference'         : self.id,
                    'certification'     : self.certification,
                    'doctype'           : self.doctype,
                    'iso_standard_ids'  : standard,
                    # 'total_emp'         : self.total_emp,          
                    # 'site_office'       : self.site_office,     
                    # 'off_location'      : self.off_location,   
                    # 'head_office'       : self.head_office,        
                    # 'number_site'       : self.number_site,
                    # 'scope'             : self.scope,
                    'website'           : self.website,
                    'office_address'    : self.office_address,
                    'invoicing_address' : self.invoicing_address,
                    'contact_person'    : self.contact_person,
                    'jabatan'           : self.jabatan,
                    'telepon'           : self.telepon,
                    'fax'               : self.fax,
                    'tx_site_count'     : self.tx_site_count,
                    'tx_remarks'        : self.tx_remarks,
                    'email'             : self.email,
                    'cellular'          : self.cellular,
                    # 'boundaries'        : self.boundaries,
                    'cause'             : self.cause,
                    'stage_audit'       : self.audit_stage,
                    'part_time'         : self.part_time,
                    'subcon'            : self.subcon,
                    'unskilled'         : self.unskilled,
                    'seasonal'          : self.seasonal,
                    'shift_number'      : self.shift_number,
                    'outsource_proc'    : self.outsource_proc,
                    'outsourced_activity': self.outsourced_activity,
                    'start_implement'   : self.start_implement,
                    'mat_consultancy'   : self.mat_consultancy,
                    'mat_certified'     : self.mat_certified,
                    'other_system'     : self.other_system,
                    # 'mat_certified_cb'  : self.mat_certified_cb,
                    # 'mat_tools'         : self.mat_tools,
                    # 'mat_national'      : self.mat_national,
                    # 'mat_more'          : self.mat_more,
                    'txt_mat_consultancy': self.txt_mat_consultancy,
                    'txt_mat_certified' : self.txt_mat_certified,
                    # 'txt_mat_certified_cb': self.txt_mat_certified_cb,
                    # 'txt_mat_tools'     : self.txt_mat_tools,
                    # 'txt_mat_national'  : self.txt_mat_national,
                    # 'txt_mat_more'      : self.txt_mat_more,
                    'int_review'        : self.int_review,
                    'int_internal'      : self.int_internal,
                    'int_policy'        : self.int_policy,
                    'int_system'        : self.int_system,
                    'int_instruction'   : self.int_instruction,
                    'int_improvement'   : self.int_improvement,
                    'int_planning'      : self.int_planning,
                    # 'int_support'       : self.int_support,
                    'ea_code'           : self.ea_code.id,
                    'accreditation'     : self.accreditation.id,
                    'ea_code_14001'     : self.ea_code_14001.id,
                    'accreditation_14001' : self.accreditation_14001.id,
                    'ea_code_27001'           : self.ea_code_27001.id,
                    'accreditation_27001'     : self.accreditation_27001.id,
                    'ea_code_45001'           : self.ea_code_45001.id,
                    'accreditation_45001'     : self.accreditation_45001.id,
                    # 'ea_code_22000'           : self.ea_code_22000.id,
                    # 'accreditation_22000'     : self.accreditation_22000.id,
                    # 'ea_code_haccp'           : self.ea_code_haccp.id,
                    # 'accreditation_haccp'     : self.accreditation_haccp.id,
                    # 'partner_site'     : self.partner_site.id,
                    'complexity_22000'  : self.complexity_22000,
                    'complexity'        : self.complexity,
                    'complexity_14001'  : self.complexity_14001,
                    'complexity_27001'  : self.complexity_27001,
                    'complexity_45001'  : self.complexity_45001,
                    'complexity_haccp'  : self.complexity_haccp,
                    'show_salesinfo'    : self.show_salesinfo,
                    'show_14001'        : self.show_14001,
                    'show_45001'        : self.show_45001,
                    'show_27001'        : self.show_27001,
                    'show_haccp'        : self.show_haccp,
                    'show_22000'        : self.show_22000,
                    'show_37001'        : self.show_37001,
                    # 'iso_27001_bisnistype' : self.iso_27001_bisnistype,
                    # 'iso_27001_process' : self.iso_27001_process,
                    # 'iso_27001_mgmt_system' : self.iso_27001_mgmt_system,
                    # 'iso_27001_number_process' : self.iso_27001_number_process,
                    # 'iso_27001_infra'  : self.iso_27001_infra,
                    # 'iso_27001_sourcing'  : self.iso_27001_sourcing,
                    # 'iso_27001_itdevelopment'  : self.iso_27001_itdevelopment,
                    # 'iso_27001_itsecurity'  : self.iso_27001_itsecurity,
                    # 'iso_27001_asset'  : self.iso_27001_asset,
                    # 'iso_27001_drc'  : self.iso_27001_drc,
                    'iso_14001_env_aspect' : self.iso_14001_env_aspect,
                    'iso_14001_obligation' : self.iso_14001_obligation,
                    'iso_45001_key_hazard' : self.iso_45001_key_hazard,
                    'iso_45001_obligation' : self.iso_45001_obligation,
                    'show_integreted_yes'  : self.show_integreted_yes,
                    'integreted_audit'    : self.integreted_audit

                })
        self.compute_state()

    # def create_open_iso(self):
    #     if self.salesinfo_site_22000 :
    #         for salesinfo in self.salesinfo_site_22000 :

    #             self.env['tsi.iso.review'].create({
    #                 'salesinfo_site_22000'  : salesinfo.reference_id4
    #             })
    #     self.compute_state()

    def create_quotation(self):
        return {
            'name': "Create Quotation",
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'tsi.wizard_quotation.app',
            'view_id': self.env.ref('v15_tsi.tsi_wizard_quotation_app_view').id,
            'target': 'new'
        }

    def create_open_quotation(self):

        self.env['sale.order'].create({
            'iso_reference' : self.id,
            'partner_id' : self.customer.id,
        })
        self.compute_state()

    	# return {
        #     'res_model':'tsi.iso.review',
        #     'res_id':self.id,
        #     'type':'ir.actions.act_window',
        #     'view_mode':'form',
        #     'view_id':self.env.ref('v15_tsi.tsi_iso_review_view_form').id,
        # }

    def update_to_contact(self):
        # Calculate total_emp from partner_site
        total_emp = sum(int(site.total_emp) for site in self.partner_site)

        # Determine EA Codes to use
        ea_codes = []
        if self.ea_code:
            ea_codes.append(self.ea_code.id)
        if self.ea_code_14001:
            ea_codes.append(self.ea_code_14001.id)
        if self.ea_code_27001:
            ea_codes.append(self.ea_code_27001.id)
        if self.ea_code_45001:
            ea_codes.append(self.ea_code_45001.id)

        # Update contact information in self.customer
        self.customer.write({
            'phone': self.telepon,
            'office_address': self.office_address,
            'invoice_address': self.invoicing_address,
            'website': self.website,
            'email': self.email,
            'boundaries': self.boundaries,
            'scope': self.scope,
            'number_site': self.tx_site_count,
            'kategori': self.kategori,
            'jabatan': self.jabatan,
            'is_associate': self.is_associate,
            'associate_id': self.associate_id.id,
            'is_franchise': self.is_franchise,
            'food_category': self.food_category_22000.id,
            'category_id': self.segment_id,
            'total_emp': total_emp,
            'contact_person': self.contact_person,
            'user_id': self.sales_person.id,
            'ea_code_ids': [(6, 0, ea_codes)],  # Set many2many field
            'status_klien': self.status_klien,
        })

        # Update or create site lines in tsi.site_partner
        site_partner_obj = self.env['tsi.site_partner']
        for site in self.partner_site:
            existing_site = site_partner_obj.search([('partner_id', '=', self.customer.id), ('jenis', '=', site.type)])
            values = {
                'partner_id': self.customer.id,
                'jenis': site.type,
                'alamat': site.address,
                'telp': site.reference_id.telepon,
                'jumlah_karyawan': int(site.total_emp or 0),
            }
            if existing_site:
                existing_site.write(values)
            else:
                site_partner_obj.create(values)

        return True

    
    


    def set_to_running(self):
        self.write({'state': 'waiting'})
        self.ensure_one()
        action = self.env['ir.actions.actions']._for_xml_id('v15_tsi.tsi_iso_action')
        action.update({
            'context': {'default_customer': self.customer.id},
            'view_mode': 'form',
            'view_id': self.env.ref('v15_tsi.tsi_iso_view_tree').id,
            'target': [(self.env.ref('v15_tsi.tsi_iso_view_tree').id, 'tree')],
        })
        return action

    def set_to_closed(self):
        # self.create_open_iso()
        self.write({'state': 'approved'}) 
        action = self.env['ir.actions.actions']._for_xml_id('v15_tsi.tsi_iso_action')
        action.update({
            'context': {'default_customer': self.customer.id},
            'view_mode': 'form',
            'view_id': self.env.ref('v15_tsi.tsi_iso_view_tree').id,
            'target': [(self.env.ref('v15_tsi.tsi_iso_view_tree').id, 'tree')],
        })
        # Membuat rekaman baru di model qc.pass.iso
        self.env['qc.pass.iso'].create({
            'customer': self.customer.id,  # Menggunakan ID customer yang sudah ada
            'iso_reference': self.id,  # Menggunakan nilai iso_reference, misalnya menggunakan nama dari objek ini
        })
        return True

    def set_to_draft(self):
        self.write({'state': 'reject'})
        self.ensure_one()
        action = self.env['ir.actions.actions']._for_xml_id('v15_tsi.tsi_iso_action')
        action.update({
            'context': {'default_customer': self.customer.id},
            'view_mode': 'form',
            'view_id': self.env.ref('v15_tsi.tsi_iso_view_tree').id,
            'target': [(self.env.ref('v15_tsi.tsi_iso_view_tree').id, 'tree')],
        })
        return action
    
    def set_to_revice(self):
        self.write({
            'state': 'approved',
            'state_sales': 'waiting_verify_operation',
            })
        review_records = self.env['tsi.iso.review'].search([('customer', '=', self.customer.id)])
        # Update state dan state_sales sekaligus
        review_records.write({
            'state': 'revice',
            'state_sales': 'waiting_verify_operation',
        })        
        return True

    def set_to_quotation(self):
        self.write({'state': 'quotation'})            
        return True
    
    

# class ISPOKebun(models.Model):
#     _name           = 'tsi.ispo.kebun'
#     _description    = 'ISPO Kebun'

#     reference       = fields.Many2one('tsi.iso', string="Reference")
#     name            = fields.Char(string='Nama Kebun')
#     lokasi          = fields.Text(string='Lokasi')
#     karyawan        = fields.Char(string='Jumlah Karyawan')
#     luas            = fields.Char(string='Luas HGU')
#     tahun_tanam     = fields.Char(string='Tahun Tanam')
#     keterangan      = fields.Text(string='Keterangan')

# class ISPOPabrik(models.Model):
#     _name           = 'tsi.ispo.pabrik'
#     _description    = 'ISPO Pabrik'

#     reference       = fields.Many2one('tsi.iso', string="Reference")
#     name            = fields.Char(string='Nama Pabrik')
#     lokasi          = fields.Text(string='Lokasi')
#     karyawan        = fields.Char(string='Jumlah Karyawan')
#     luas            = fields.Char(string='Koordinat GPS')
#     tahun_tanam     = fields.Char(string='Kapasitas')
#     keterangan      = fields.Text(string='Volume Tahunan')

# class ISPOSertifikat(models.Model):
#     _name           = 'tsi.ispo.sertifikat'
#     _description    = 'ISPO Sertifikat'

#     reference       = fields.Many2one('tsi.iso', string="Reference")
#     name            = fields.Char(string='Nama Sertifikat')
#     nomor           = fields.Char(string='Nomor Sertifikat')

class ISOLineInitial(models.Model):
    _name           = 'tsi.iso.initial'
    _description    = 'ISO Line Initial'

    reference_id    = fields.Many2one('tsi.iso', string="Reference")
    reference_id_ispo    = fields.Many2one('tsi.ispo', string="Reference")
    product_id = fields.Many2one(
        'product.product', string='Product',)
    # tax_id = fields.Many2many('account.tax', string='Taxes', context={'active_test': False})
    audit_stage     = fields.Selection([
                            ('Initial Audit',         'Initial Audit'),
                            ('Recertification', 'Recertification'),],
                            string='Audit Stage', index=True, )
    price = fields.Float(string='Price')
    tahun = fields.Char("Tahun")
    fee = fields.Float(string='Fee')
    percentage = fields.Float(string='Percentage', compute='_compute_percentage', store=True)
    in_pajak = fields.Boolean("Include Pajak")
    ex_pajak = fields.Boolean("Exclude Pajak")

    @api.onchange('in_pajak', 'ex_pajak')
    def _onchange_pajak(self):
        for rec in self:
            # Cegah dua checkbox aktif bersamaan
            if rec.in_pajak and rec.ex_pajak:
                rec.ex_pajak = False  # Biar gak bentrok logika

            # Kalau in_pajak dicentang → hitung harga tanpa pajak
            if rec.in_pajak:
                rec.price = rec.price / 1.11 if rec.price else 0.0

            # Kalau ex_pajak dicentang → tidak ubah price (anggap sudah harga asli)
            elif rec.ex_pajak:
                pass  # Harga tetap

            # Kalau dua-duanya gak dicentang → anggap harga asli
            elif not rec.in_pajak and not rec.ex_pajak:
                pass  # Harga tetap


    @api.depends('price', 'fee')
    def _compute_percentage(self):
        for line in self:
            if line.price:
                line.percentage = line.fee /(line.price - line.fee) 
            else:
                line.percentage = 0

class ISOLinesSurveillance(models.Model):
    _name           = 'tsi.iso.surveillance'
    _description    = 'ISO Line Surveillance'

    reference_id    = fields.Many2one('tsi.iso', string="Reference")
    reference_id_ispo    = fields.Many2one('tsi.ispo', string="Reference")
    audit_stage     = fields.Selection([
                            ('Surveillance 1', 'Surveillance 1'),
                            ('Surveillance 2', 'Surveillance 2'),],
                            string='Audit Stage', index=True, )
    audit_stage_ispo     = fields.Selection([
                            ('Surveillance 1', 'Surveillance 1'),
                            ('Surveillance 2', 'Surveillance 2'),
                            ('Surveillance 3', 'Surveillance 3'),
                            ('Surveillance 4', 'Surveillance 4'),],
                            string='Audit Stage', index=True, )
    price = fields.Float(string='Price')
    # tax_id = fields.Many2many('account.tax', string='Taxes', context={'active_test': False})
    tahun = fields.Char("Tahun")
    fee = fields.Float(string='Fee')
    percentage = fields.Float(string='Percentage', compute='_compute_percentage', store=True)
    hidden_in_review = fields.Boolean(string='Hidden in Review', default=True)

    @api.depends('price', 'fee')
    def _compute_percentage(self):
        for line in self:
            if line.price:
                line.percentage = (line.fee / line.price)
            else:
                line.percentage = 0

class ISOAccreditation(models.Model):
    _name           = 'tsi.iso.accreditation'
    _description    = 'Accreditation'

    name            = fields.Char(string='Name')
    description     = fields.Char(string='Description')

class ISOSite(models.Model):
    _name           = 'tsi.iso.site'
    _description    = 'Site'

    reference_id    = fields.Many2one('tsi.iso', string="Reference")
    nama_site       = fields.Char(string='Nama Site')
    type            = fields.Char(string='Type(HO, Factory etc)')
    address         = fields.Char(string='Address')
    product         = fields.Char(string='Product / Process / Activities')
    permanent       = fields.Char(string='Permanent & Contract')
    total_active    = fields.Char(string='Total No. of Active Temporary Project Sites (see attachment for detai)')
    total_emp       = fields.Integer(string='Total No. of Effective Employees')
    emp_total       = fields.Integer(string='Total No. of All Employees')
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

class ISOSalesinfo(models.Model):
    _name           = 'tsi.iso.additional_salesinfo'
    _description    = 'Salesinfo'

    reference_id    = fields.Many2one('tsi.iso', string="Reference")
    reference_id2    = fields.Many2one('tsi.iso', string="Reference")
    reference_id3    = fields.Many2one('tsi.iso', string="Reference")
    reference_id4    = fields.Many2one('tsi.iso', string="Reference")
    reference_id5    = fields.Many2one('tsi.iso', string="Reference")
    reference_id6   = fields.Many2one('tsi.iso', string="Reference")
    reference_id7   = fields.Many2one('tsi.iso', string="Reference")
    reference_id8   = fields.Many2one('tsi.iso', string="Reference")
    reference_id9   = fields.Many2one('tsi.iso', string="Reference")
    reference_id10   = fields.Many2one('tsi.ispo', string="Reference")
    reference_id11   = fields.Many2one('tsi.iso', string="Reference")
    reference_id12   = fields.Many2one('tsi.iso', string="Reference")
    reference_id13   = fields.Many2one('tsi.iso', string="Reference")
    reference_id14   = fields.Many2one('tsi.iso', string="Reference")
    reference_id15   = fields.Many2one('tsi.iso', string="Reference")
    reference_id16   = fields.Many2one('tsi.iso', string="Reference")
    reference_id17   = fields.Many2one('tsi.iso', string="Reference")
    reference_id18   = fields.Many2one('tsi.iso', string="Reference")
    reference_id19   = fields.Many2one('tsi.iso', string="Reference")
    reference_id20   = fields.Many2one('tsi.iso', string="Reference")
    reference_id21   = fields.Many2one('tsi.iso', string="Reference")
    reference_id22   = fields.Many2one('tsi.iso', string="Reference")
    reference_id23   = fields.Many2one('tsi.iso', string="Reference")
    reference_id24   = fields.Many2one('tsi.iso', string="Reference")
    reference_id25   = fields.Many2one('tsi.iso', string="Reference")
    nama_site       = fields.Char(string='Nama Site')
    stage_1         = fields.Char(string='Stage 1')
    stage_2         = fields.Char(string='Stage 2')
    surveilance_1   = fields.Char(string='Surveillance 1')
    surveilance_2   = fields.Char(string='Surveillance 2')
    surveilance_3   = fields.Char(string='Surveillance 3')
    surveilance_4   = fields.Char(string='Surveillance 4')
    surveilance_5   = fields.Char(string='Surveillance 5')
    recertification = fields.Char(string='Recertification')
    recertification_1 = fields.Char(string='Recertification 1')
    recertification_2 = fields.Char(string='Recertification 2')
    remarks         = fields.Char(string='Remarks')

class ISO27001(models.Model):
    _name           = 'tsi.iso.additional_27001'
    _description    = '27001 Info'

    reference_id    = fields.Many2one('tsi.iso', string="Reference")
    reference_id1    = fields.Many2one('tsi.iso', string="Reference")
    reference_id2    = fields.Many2one('tsi.iso', string="Reference")
    reference_id3    = fields.Many2one('tsi.iso', string="Reference")
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
    
    

class ISOHACCP22000(models.Model):
    _name           = 'tsi.iso.additional_haccp'
    _description    = 'HACCP 22000'

    reference_id        = fields.Many2one('tsi.iso', string="Reference")
    hazard_number       = fields.Char(string='Number of hazard')
    hazard_describe     = fields.Char(string='Describe Hazard')
    process_number      = fields.Char(string='Number of process')
    process_describe    = fields.Char(string='Describe Process')
    tech_number         = fields.Char(string='Number of technology')
    tech_describe       = fields.Char(string='Describe Technology')


class ISPOPemasok(models.Model):
    _name           = 'tsi.ispo.pemasok'
    _description    = 'ISPO Pemasok'

    reference       = fields.Many2one('tsi.iso', string="Reference")
    name            = fields.Char(string='Nama Pemasok')
    lokasi          = fields.Text(string='Lokasi')
    total_area      = fields.Char(string='Total Area')
    total_tertanam  = fields.Char(string='Area Tertanam')
    produksi        = fields.Char(string='Produksi TBS')
    koordinat       = fields.Char(string='Koordinat GPS')

class ISOStandard(models.Model):
    _name           = 'tsi.iso.standard'
    _inherit        = ['portal.mixin', 'mail.thread', 'mail.activity.mixin']
    _description    = 'Standard'

    name            = fields.Char(string='Nama')
    description     = fields.Char(string='Description')
    standard        = fields.Selection([
                            ('iso',  'ISO'),
                            ('ispo',  'ISPO'),
                        ], string='Standard', index=True)

class ISOStandard(models.Model):
    _name           = 'tsi.iso.tahapan'
    _inherit        = ['portal.mixin', 'mail.thread', 'mail.activity.mixin']
    _description    = 'Tahapan Audit'

    name            = fields.Char(string='Nama')
    description     = fields.Char(string='Description')

class ISOStandard(models.Model):
    _name           = 'tsi.tahapan.audit'
    _inherit        = ['portal.mixin', 'mail.thread', 'mail.activity.mixin']
    _description    = 'Tahapan'

    nama            = fields.Char(string='Nama')
    deskripsi     = fields.Char(string='Description')

class ISOBoundaries(models.Model):
    _name           = 'tsi.iso.boundaries'
    _inherit        = ['portal.mixin', 'mail.thread', 'mail.activity.mixin']
    _description    = 'Boundaries'

    name            = fields.Char(string='Nama')
    description     = fields.Char(string='Description')

# class ISOStandard(models.Model):
#     _name           = 'tsi.iso.akreditasi'
#     _inherit        = ['portal.mixin', 'mail.thread', 'mail.activity.mixin']
#     _description    = 'Tahapan'

#     nama            = fields.Char(string='Nama')
#     deskripsi    = fields.Char(string='Description')

class EACode(models.Model):
    _name           = 'tsi.ea_code'
    _description    = 'EA Code'
    _inherit        = ['portal.mixin', 'mail.thread', 'mail.activity.mixin']

    name            = fields.Char(string='Nama', )
    description     = fields.Char(string='Description', )
    iso_standard_ids = fields.Many2many('tsi.iso.standard', string='Standards', )

class FoodCategory(models.Model):
    _name           = 'tsi.food_category'
    _description    = 'Food Category'
    _inherit        = ['portal.mixin', 'mail.thread', 'mail.activity.mixin']

    name            = fields.Char(string='Nama', )
    description     = fields.Char(string='Description', )
    iso_standard_ids = fields.Many2many('tsi.iso.standard', string='Standards', )

class Risk(models.Model):
    _name           = 'tsi.iso.risk'
    _description    = 'Risk'

    name            = fields.Char(string='Nama')
    value           = fields.Integer(string='Value')


class SalesOrder(models.Model):
    _inherit        = 'sale.order'

    # def _default_end_of_month(self):
    #     today = date.today()
    #     last_day = (today.replace(day=28) + timedelta(days=4)).replace(day=1) - timedelta(days=1)
    #     return last_day

    def get_end_of_month_choices(self):
        options = []
        today = date.today()
        year = today.year
        month = today.month

        # Tentukan apakah bulan ini masih aktif atau sudah lewat
        if month == 12:
            next_month = date(year + 1, 1, 1)
        else:
            next_month = date(year, month + 1, 1)
        end_of_this_month = next_month - timedelta(days=1)

        # Kalau sudah lewat, mulai dari bulan depan
        if today > end_of_this_month:
            month += 1
            if month > 12:
                month = 1
                year += 1

        # Tetapkan jumlah total bulan yang ingin ditampilkan (misalnya 32 bulan)
        total_months = 32

        for i in range(total_months):
            y = year + ((month + i - 1) // 12)
            m = ((month + i - 1) % 12) + 1

            if m == 12:
                next_month = date(y + 1, 1, 1)
            else:
                next_month = date(y, m + 1, 1)
            last_day = next_month - timedelta(days=1)

            options.append((last_day.isoformat(), last_day.strftime('%d %B %Y')))

        return options

    iso_reference   = fields.Many2one('tsi.iso', string="Reference")
    iso_notification   = fields.Many2one('audit.notification', string="Notification")
    reference_request_ids = fields.Many2many('tsi.audit.request', string='Audit Request', tracking=True)
    ispo_reference   = fields.Many2one('tsi.ispo', string="Reference")
    ispo_notification   = fields.Many2one('audit.notification.ispo', string="Notification")
    reference_request_ispo_ids = fields.Many2many('tsi.audit.request.ispo', string='Audit Request', tracking=True)
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
        string='Audit Status', compute='_compute_status_audit', store=True)
    application_review_ids   = fields.Many2many('tsi.iso.review', string="Review")
    application_review_ispo_ids   = fields.Many2many('tsi.ispo.review', string="Review")
    template_quotation        = fields.Binary('Attachment')
    dokumen_sosialisasi        = fields.Binary('Organization Chart')
    file_name       = fields.Char('Filename')
    file_name1       = fields.Char('Filename Dokumen')
    doctype         = fields.Selection([
                            ('iso',  'ISO'),
                            ('ispo',   'ISPO'),
                        ], string='Doc Type', related='iso_reference.doctype', readonly=True, index=True)

    segment_id          = fields.Many2many('res.partner.category', string='Segment')
    nomor_quotation     = fields.Char(string='Nomor Quotation', tracking=True)
    nomor_kontrak       = fields.Char(string='Nomor Kontrak', tracking=True)
    iso_standard_ids    = fields.Many2many('tsi.iso.standard', string='Standards',  store=True)
    standard_names = fields.Char(string='Standard Names', compute='_compute_standard_names', store=True)
    kategori        = fields.Selection([
                            ('bronze',  'Bronze'),
                            ('silver',  'Silver'),
                            ('gold',    'Gold'),
                        ], string='Kategori', index=True)

    tipe_pembayaran     = fields.Selection([
                            ('termin',     'Termin'),
                            ('lunasawal',   'Lunas di Awal'),
                            ('lunasakhir',  'Lunas di Akhir')
                        ], string='Tipe Pembayaran', tracking=True)
    sale_order_options = fields.One2many('tsi.order.options', 'ordered_id', string='Optional Product', index=True)
    nomor_customer = fields.Char(string='Customer ID', default='New', readonly=True, copy=False)
    state = fields.Selection(selection_add=[
        ('draft', 'Quotation'),
        ('cliennt_approval', 'Client Approval'),
        ('waiting_verify_operation', 'Aplication Review'),
        ('create_kontrak', 'Create Kontrak'),
        ('sent', 'Confirm to Closing'),
        ('sale', 'Sales Order'),
        ('done', 'Locked'),
        ('cancel', 'Lost'),
        ('application_form', 'Application Form'),
        ], string='Status', readonly=True, copy=False, index=True, tracking=3, default='draft')
    show_iso_fields = fields.Boolean(compute='_compute_show_fields', store=False)
    show_ispo_fields = fields.Boolean(compute='_compute_show_fields', store=False)
    contract_type = fields.Selection([
        ('new', 'New Contract'),
        ('amendment', 'Amandement Contract'),
    ], string="Contract Type", help="Select the type of contract", required=False)
    hide_contract_type = fields.Boolean(compute='_compute_hide_contract_type', store=False)
    show_confirm_button = fields.Boolean(compute='_compute_show_confirm_button', store=False)
    total_sales_by_salesperson = fields.Float(compute='_compute_total_sales_by_salesperson', string='Total Sales by Salesperson', store=True)
    status_klien = fields.Selection([
        ('New', 'New'),
        ('active', 'Active'),
        ('suspend', 'Suspend'),
        ('withdraw', 'Withdrawn'),
        ('Re-Active', 'Re-Active'),
        ('Double', 'Double'),
    ], string='State', store=True, default="New")

    sales_person = fields.Many2one(
        'res.users', string='Salesperson', readonly=False, index=True, tracking=2, compute='_compute_sales_person')
    date_order = fields.Datetime(string='Order Date', required=True, readonly=False, index=True, states={'draft': [('readonly', False)], 'sent': [('readonly', False)]}, copy=False, default=fields.Datetime.now, help="Creation date of draft/sent orders,\nConfirmation date of confirmed orders.")
    # Field dengan tipe Date untuk menyimpan data lengkap
    # tgl_perkiraan_mulai = fields.Date(string="Estimated Audit Start Date")
    tgl_perkiraan_selesai = fields.Date(string="Plan of audit date",store=True, help="Wajib isi akhir bulan (misalnya 31, 30, atau 28)")
    tgl_perkiraan_audit_selesai = fields.Selection(
        selection=lambda self: self.get_end_of_month_choices(),
        string="Plan of audit date"
    )
    # month = fields.Selection(MONTH_SELECTION, string="Bulan")
    # year = fields.Selection(YEAR_SELECTION, string="Tahun")
    terbit_invoice = fields.Selection([
        ('Direct', 'Direct'),
        ('Associate', 'Associate'),
    ], string="Terbit Invoice")
    associate_name = fields.Many2one('res.partner', compute='_compute_associate', readonly=False, string="Associate Name")

    @api.depends('iso_standard_ids')
    def _compute_standard_names(self):
        for record in self:
            record.standard_names = ', '.join(record.iso_standard_ids.mapped('name'))

    @api.constrains('tgl_perkiraan_selesai')
    def _check_end_of_month(self):
        for rec in self:
            if rec.tgl_perkiraan_selesai:
                chosen = rec.tgl_perkiraan_selesai
                last_day = (chosen.replace(day=28) + timedelta(days=4)).replace(day=1) - timedelta(days=1)
                if chosen != last_day:
                    raise ValidationError("Tanggal harus diisi pada akhir bulan (misalnya 30/31/28).")

    @api.depends('iso_notification.audit_state')
    def _compute_status_audit(self):
        for record in self:
            record.audit_status = record.iso_notification.audit_state if record.iso_notification else False

    @api.depends('iso_reference', 'ispo_reference')
    def _compute_associate(self):
        for record in self:
            if record.iso_reference:
                record.associate_name = record.iso_reference.associate_id
            elif record.ispo_reference:
                # Anda bisa sesuaikan behavior di sini
                # Misalnya, jika ispo_reference ada, ambil sales_person dari ispo_reference
                record.associate_name = record.ispo_reference.associate_id
            else:
                record.associate_name = False

    @api.depends('iso_reference', 'ispo_reference')
    def _compute_sales_person(self):
        for record in self:
            if record.iso_reference:
                record.sales_person = record.iso_reference.sales_person
            elif record.ispo_reference:
                # Anda bisa sesuaikan behavior di sini
                # Misalnya, jika ispo_reference ada, ambil sales_person dari ispo_reference
                record.sales_person = record.ispo_reference.sales_person
            else:
                record.sales_person = False

    @api.model
    def _default_sales_person(self):
        return self.env.user

    @api.depends('order_line.price_total')
    def _compute_total_sales_by_salesperson(self):
        for order in self:
            order.total_sales_by_salesperson = sum(order.order_line.mapped('price_total'))

    def _compute_show_confirm_button(self):
        for order in self:
            iso_standards = order.iso_standard_ids.mapped('name')
            order.show_confirm_button = any(standard in iso_standards for standard in [
                'ISO 9001', 'ISO 14001', 'ISO 45001', 'ISO 22000', 'ISO 27001', 'HACCP', 'ISO 31000', 'ISO 13485',
            ])

    def _compute_hide_contract_type(self):
        for order in self:
            order.hide_contract_type = any(line.audit_tahapan == 'Initial Audit' for line in order.order_line)

    @api.depends('iso_standard_ids')
    def _compute_show_fields(self):
        iso_standards = self.iso_standard_ids.mapped('standard')

        # Set boolean fields based on the presence of specific standards
        self.show_iso_fields = any(
            standard in iso_standards for standard in [
                'iso',
            ]
        )
        self.show_ispo_fields = 'ispo' in iso_standards
    

    @api.model
    def create(self, vals):
        self.write({
            'state' : 'sale',
        })
        if vals.get('nomor_customer', 'New') == 'New':
            seq_number = self.env['ir.sequence'].next_by_code('customer.id') or 'New'
            vals['nomor_customer'] = 'TSI-%s-%s' %(datetime.today().year, seq_number)
            result = super(SalesOrder, self).create(vals)
        return result
    
    # def write(self, vals):
    #     # Simpan nilai audit_status sebelumnya
    #     previous_status = {rec.id: rec.audit_status for rec in self}
    #     result = super(SalesOrder, self).write(vals)
    #     for rec in self:
    #         if (
    #             previous_status.get(rec.id) != 'certificate'
    #             and rec.audit_status == 'certificate'
    #         ):
    #             rec.generate_crm()
    #     return result
    

    def action_confirm(self):
        res = super(SalesOrder, self).action_confirm()
        for order in self:
            # Validasi: Field 'terbit_invoice' harus diisi sebelum konfirmasi
            if not order.terbit_invoice:
                raise UserError(_("Field 'Terbit Invoice' wajib diisi sebelum mengkonfirmasi!"))

            # Update nomor_customer jika belum ada
            if order.state == 'sale' and not order.partner_id.nomor_customer:
                order.partner_id.nomor_customer = order.nomor_customer
            
            # Periksa audit_tahapan di order_line untuk menentukan perubahan status_klien
            if order.state == 'sale' and order.partner_id.status_klien == 'active':
                for line in order.order_line:
                    if line.audit_tahapan == 'Initial Audit':
                        # Jika ada 'Initial Audit', ubah status_klien menjadi 'new'
                        order.partner_id.status_klien = 'New'
                        break
                    elif line.audit_tahapan in ['Surveillance 1', 'Surveillance 2']:
                        # Jika ada Surveillance, biarkan status tetap 'active'
                        pass

            # Cek apakah ada order line dengan 'Initial Audit'
            initial_audit_required = any(
                line.audit_tahapan == 'Initial Audit' for line in order.order_line
            )
            if initial_audit_required and not order.template_quotation:
                raise UserError(_("Harus isi Template Quotation sebelum mengkonfirmasi!"))
            
            # Cek apakah ada order line dengan audit_stage 'surveillance'
            surveillance_required = any(
                line.audit_tahapan in ['Surveillance 1', 'Surveillance 2', 'Recertification'] for line in order.order_line
            )

            # Cek apakah contract_type terisi dengan 'new' atau 'amendment'
            if surveillance_required and order.contract_type in ['new', 'amendment']:
                if not order.template_quotation:
                    raise UserError(_("Field Template Quotation wajib diisi untuk contract type 'New' atau 'Amendment'."))
            
            # ✅ Tambahkan validasi untuk Recertification
            recert_required = any(
                line.audit_tahapan == 'Recertification' for line in order.order_line
            )
            if recert_required and not order.template_quotation:
                raise UserError(_("Field Template Quotation wajib diisi untuk tahap Recertification."))
            
            # Pastikan tipe_pembayaran diisi
            if not order.tipe_pembayaran:
                raise UserError('Mohon tentukan tipe pembayaran')

            # Jika iso_reference tidak diisi, buat audit.notification tanpa ISO reference
            if not order.iso_reference:
                if order.iso_standard_ids:
                    notification_without_iso = self.env['audit.notification'].create({
                        'customer': order.partner_id.id,
                        'sales_order_id': order.id,
                        'tipe_pembayaran': order.tipe_pembayaran,
                        'iso_standard_ids': [(6, 0, order.iso_standard_ids.ids)],
                    })
                    order.iso_notification = notification_without_iso.id

                    for standard in order.iso_standard_ids:
                        # Jika tipe pembayaran lunas di awal/akhir, buat program dan report
                        if order.tipe_pembayaran in ['lunasawal', 'lunasakhir']:
                            program = self.env['ops.program'].create({
                                'sales_order_id': order.id,
                                'iso_standard_ids': [(6, 0, [standard.id])],
                                'type_client': order.tipe_pembayaran,
                                'notification_id': notification_without_iso.id,
                                'customer': order.partner_id.id,
                                'dokumen_sosialisasi': order.dokumen_sosialisasi,
                                'file_name1': order.file_name1,
                                'contract_number': order.nomor_kontrak,
                            })
                            report = self.env['ops.report'].create({
                                'sales_order_id': order.id,
                                'iso_standard_ids': [(6, 0, [standard.id])],
                                'notification_id': notification_without_iso.id,
                                'customer': order.partner_id.id
                            })
                        else:
                            # Buat program dan report tanpa lunasawal/lunasakhir
                            program = self.env['ops.program'].create({
                                'sales_order_id': order.id,
                                'iso_standard_ids': [(6, 0, [standard.id])],
                                'type_client': order.tipe_pembayaran,
                                'notification_id': notification_without_iso.id,
                                'customer': order.partner_id.id,
                                'dokumen_sosialisasi': order.dokumen_sosialisasi,
                                'file_name1': order.file_name1,
                                'contract_number': order.nomor_kontrak,
                            })
                else:
                    raise UserError('Tidak ada standar ISO yang terkait.')
            
            # Jika iso_reference diisi, buat audit.notification dengan ISO reference
            else:
                notification_with_iso = self.env['audit.notification'].create({
                    'iso_reference': order.iso_reference.id,
                    'customer': order.partner_id.id,
                    'sales_order_id': order.id,
                    'tipe_pembayaran': order.tipe_pembayaran,
                    'iso_standard_ids': [(6, 0, order.iso_standard_ids.ids)] if order.iso_standard_ids else False,
                })
                order.iso_notification = notification_with_iso.id

                # Jika ada ISO standards, buat program dan report
                if order.iso_standard_ids:
                    for standard in order.iso_standard_ids:
                        if order.tipe_pembayaran in ['lunasawal', 'lunasakhir']:
                            program = self.env['ops.program'].create({
                                'iso_reference': order.iso_reference.id,
                                'sales_order_id': order.id,
                                'iso_standard_ids': [(6, 0, [standard.id])],
                                'type_client': order.tipe_pembayaran,
                                'notification_id': notification_with_iso.id,
                                'customer': order.partner_id.id,
                                'dokumen_sosialisasi': order.dokumen_sosialisasi,
                                'file_name1': order.file_name1,
                                'contract_number': order.nomor_kontrak,
                            })
                            report = self.env['ops.report'].create({
                                'iso_reference': order.iso_reference.id,
                                'sales_order_id': order.id,
                                'iso_standard_ids': [(6, 0, [standard.id])],
                                'notification_id': notification_with_iso.id,
                                'customer': order.partner_id.id
                            })
                        else:
                            program = self.env['ops.program'].create({
                                'iso_reference': order.iso_reference.id,
                                'sales_order_id': order.id,
                                'iso_standard_ids': [(6, 0, [standard.id])],
                                'type_client': order.tipe_pembayaran,
                                'notification_id': notification_with_iso.id,
                                'customer': order.partner_id.id,
                                'dokumen_sosialisasi': order.dokumen_sosialisasi,
                                'file_name1': order.file_name1,
                                'contract_number': order.nomor_kontrak,
                            })

            # Jika iso_reference tidak diisi, buat audit.notification tanpa ISO reference
            if not order.ispo_reference:
                if order.iso_standard_ids:
                    notification_without_ispo = self.env['audit.notification.ispo'].create({
                        'customer': order.partner_id.id,
                        'sales_order_id': order.id,
                        'tipe_pembayaran': order.tipe_pembayaran,
                        'iso_standard_ids': [(6, 0, order.iso_standard_ids.ids)],
                    })
                    order.ispo_notification = notification_without_ispo.id

                    # Jika tipe pembayaran lunas di awal/akhir, buat program dan report
                    for standard in order.iso_standard_ids:
                        if order.tipe_pembayaran in ['lunasawal', 'lunasakhir']:
                            program = self.env['ops.program.ispo'].create({
                                'sales_order_id': order.id,
                                'iso_standard_ids': [(6, 0, [standard.id])],
                                'type_client': order.tipe_pembayaran,
                                'notification_id': notification_without_ispo.id,
                                'customer': order.partner_id.id,
                                'dokumen_sosialisasi': order.dokumen_sosialisasi,
                                'file_name1': order.file_name1,
                                'contract_number': order.nomor_kontrak,
                            })
                            report = self.env['ops.report.ispo'].create({
                                'sales_order_id': order.id,
                                'iso_standard_ids': [(6, 0, [standard.id])],
                                'notification_id': notification_without_ispo.id,
                                'customer': order.partner_id.id
                            })
                        else:
                            # Buat program dan report tanpa lunasawal/lunasakhir
                            program = self.env['ops.program.ispo'].create({
                                'sales_order_id': order.id,
                                'iso_standard_ids': [(6, 0, [standard.id])],
                                'type_client': order.tipe_pembayaran,
                                'notification_id': notification_without_ispo.id,
                                'customer': order.partner_id.id,
                                'dokumen_sosialisasi': order.dokumen_sosialisasi,
                                'file_name1': order.file_name1,
                                'contract_number': order.nomor_kontrak,
                            })
                else:
                    raise UserError('Tidak ada standar ISPO yang terkait.')
            else:
                # Jika ispo_reference diisi, buat notification dengan ISPO reference
                notification_with_ispo = self.env['audit.notification.ispo'].create({
                    'ispo_reference': order.ispo_reference.id,
                    'customer': order.partner_id.id,
                    'sales_order_id': order.id,
                    'tipe_pembayaran': order.tipe_pembayaran,
                    'iso_standard_ids': [(6, 0, order.iso_standard_ids.ids)] if order.iso_standard_ids else False,
                })
                order.ispo_notification = notification_with_ispo.id

                # Buat program dan report dengan ispo_reference
                if order.iso_standard_ids:
                    for standard in order.iso_standard_ids:
                        if order.tipe_pembayaran in ['lunasawal', 'lunasakhir']:
                            program = self.env['ops.program.ispo'].create({
                                'ispo_reference': order.ispo_reference.id,
                                'sales_order_id': order.id,
                                'iso_standard_ids': [(6, 0, [standard.id])],
                                'type_client': order.tipe_pembayaran,
                                'notification_id': notification_with_ispo.id,
                                'customer': order.partner_id.id,
                                'dokumen_sosialisasi': order.dokumen_sosialisasi,
                                'file_name1': order.file_name1,
                                'contract_number': order.nomor_kontrak,
                            })
                            report = self.env['ops.report.ispo'].create({
                                'ispo_reference': order.ispo_reference.id,
                                'sales_order_id': order.id,
                                'iso_standard_ids': [(6, 0, [standard.id])],
                                'notification_id': notification_with_ispo.id,
                                'customer': order.partner_id.id
                            })
                        else:
                            program = self.env['ops.program.ispo'].create({
                                'ispo_reference': order.ispo_reference.id,
                                'sales_order_id': order.id,
                                'iso_standard_ids': [(6, 0, [standard.id])],
                                'type_client': order.tipe_pembayaran,
                                'notification_id': notification_with_ispo.id,
                                'customer': order.partner_id.id,
                                'dokumen_sosialisasi': order.dokumen_sosialisasi,
                                'file_name1': order.file_name1,
                                'contract_number': order.nomor_kontrak,
                            })
                            
        return res
    
    def action_confirm_ispo(self):
        res = True  # Inisialisasi nilai kembalian
        for order in self:
            if order.state == 'sale' and not order.partner_id.nomor_customer:
                order.partner_id.nomor_customer = order.nomor_customer

            # Cek apakah ada order line dengan audit_stage 'Initial Audit'
            initial_audit_required = any(
                line.audit_tahapan == 'Initial Audit' for line in order.order_line
            )

            if initial_audit_required and not order.template_quotation:
                raise UserError(_("Harus isi Template Quotation sebelum mengkonfirmasi ISPO!"))

            # Ensure tipe_pembayaran is set
            if not order.tipe_pembayaran:
                raise UserError('Mohon tentukan tipe pembayaran')

            # Cek apakah ada ISO reference
            if order.ispo_reference and order.ispo_reference.iso_standard_ids:
                ispo_standards = self._get_ispo_standards()
                if any(standard.id in ispo_standards for standard in order.ispo_reference.iso_standard_ids):
                    notification = self.env['audit.notification.ispo'].create({
                        'ispo_reference': order.ispo_reference.id,
                        'customer': order.partner_id.id,
                        'sales_order_id': order.id,
                        'tipe_pembayaran': order.tipe_pembayaran,
                        'iso_standard_ids': order.ispo_reference.iso_standard_ids,
                    })
                    order.ispo_notification = notification.id
                    
                    for standard in order.ispo_reference.iso_standard_ids:
                        if standard.id in ispo_standards:
                            is_partial = order.tipe_pembayaran in ['lunasawal', 'lunasakhir']
                            self._create_ops_entries_ispo(order, standard, notification, is_partial=is_partial)
                else:
                    raise UserError('Tidak ada ISPO standard yang terkait dengan referensi ISPO.')

            else:
                raise UserError('Tidak ada ISPO reference yang terkait.')

        return res

    def _get_iso_standards(self):
        # Return a list of ISO standard IDs
        return self.env['tsi.iso.standard'].search([('name', 'in', ['ISO 9001', 'ISO 14001', 'ISO 45001', 'ISO 20001', 'ISO 27001', 'ISO 37001', 'ISO 22000', 'HACCP'])]).ids

    def _get_ispo_standards(self):
        # Return a list of ISPO standard IDs
        return self.env['tsi.iso.standard'].search([('name', 'in', ['ISPO'])]).ids

    def _create_ops_entries(self, order, standard, notification, is_partial):
        if is_partial:
            program = self.env['ops.program'].create({
                'iso_reference': order.iso_reference.id,
                'sales_order_id': order.id,
                'iso_standard_ids': standard,
                'contract_number': order.nomor_kontrak,
                'notification_id': notification.id,
                'dokumen_sosialisasi': order.dokumen_sosialisasi,
                'file_name1': order.file_name1,
            })
            report = self.env['ops.report'].create({
                'iso_reference': order.iso_reference.id,
                'sales_order_id': order.id,
                'iso_standard_ids': standard,
                'notification_id': notification.id
            })
        else:
            program = self.env['ops.program'].create({
                'iso_reference': order.iso_reference.id,
                'sales_order_id': order.id,
                'iso_standard_ids': standard,
                'notification_id': notification.id,
                'dokumen_sosialisasi': order.dokumen_sosialisasi,
                'file_name1': order.file_name1,
            })
    
    def _create_ops_entries_no_reference(self, order, standard, notification_without_iso, is_partial):
        if is_partial:
            program = self.env['ops.program'].create({
                # 'iso_reference': order.iso_reference.id,
                'sales_order_id': order.id,
                'iso_standard_ids': standard,
                'contract_number': order.nomor_kontrak,
                'notification_id': notification_without_iso.id,
                'dokumen_sosialisasi': order.dokumen_sosialisasi,
                'file_name1': order.file_name1,
            })
            report = self.env['ops.report'].create({
                # 'iso_reference': order.iso_reference.id,
                'sales_order_id': order.id,
                'iso_standard_ids': standard,
                'notification_id': notification_without_iso.id
            })
        else:
            program = self.env['ops.program'].create({
                # 'iso_reference': order.iso_reference.id,
                'sales_order_id': order.id,
                'iso_standard_ids': standard,
                'notification_id': notification_without_iso.id,
                'dokumen_sosialisasi': order.dokumen_sosialisasi,
                'file_name1': order.file_name1,
            })

    def _create_ops_entries_ispo(self, order, standard, notification, is_partial):
        if is_partial:
            program = self.env['ops.program.ispo'].create({
                'ispo_reference': order.ispo_reference.id,
                'sales_order_id': order.id,
                'iso_standard_ids': standard,
                'contract_number': order.nomor_kontrak,
                'notification_id': notification.id,
                'dokumen_sosialisasi': order.dokumen_sosialisasi,
                'file_name1': order.file_name1,
            })
            report = self.env['ops.report.ispo'].create({
                'ispo_reference': order.ispo_reference.id,
                'sales_order_id': order.id,
                'iso_standard_ids': standard,
                'notification_id': notification.id
            })
        else:
            program = self.env['ops.program.ispo'].create({
                'ispo_reference': order.ispo_reference.id,
                'sales_order_id': order.id,
                'iso_standard_ids': standard,
                'notification_id': notification.id,
                'dokumen_sosialisasi': order.dokumen_sosialisasi,
                'file_name1': order.file_name1,
            })


    def action_approve_quotation(self):
        # Ubah state menjadi 'sent'
        self.write({'state': 'cliennt_approval'})
        return True
    
    def action_cancel_client(self):
        # Ubah state menjadi 'sent'
        self.write({'state': 'cancel'})
        return True
    
    def action_negotation(self):
        # Ubah state menjadi 'sent'
        self.write({'state': 'draft'})
        return True
    
    # def action_approval_client(self):
    #     self.create_iso()
    #     # Ubah state menjadi 'sent'
    #     self.write({'state': 'waiting_verify_operation'})
    #     return True

    # def create_iso(self):
    #     # Periksa apakah ada iso_standard_ids di sale.order
    #     if self.iso_standard_ids:
    #         # Iterasi setiap standar di iso_standard_ids
    #         for standard in self.iso_standard_ids:
    #             # Buat record di model tsi.iso.review untuk setiap standar
    #             self.env['tsi.iso.review'].create({
    #                 'reference': self.iso_reference.id,  # Referensi ISO
    #                 'iso_standard_ids': [(4, standard.id)],  # Tambahkan standard ID
    #             })

    def action_approval_client(self):
        # Validasi untuk memastikan bahwa tanggal perkiraan mulai dan selesai sudah diisi
        if not self.tgl_perkiraan_audit_selesai:
            raise UserError("Harap isi Plan of audit date sebelum melanjutkan.")
        self.create_reviews()
        # Ubah state menjadi 'waiting_verify_operation'
        self.write({'state': 'waiting_verify_operation'})
        return True

    def create_reviews(self):
        # Filter standar ISO dan ISPO berdasarkan tipe, misalnya menggunakan field `standard_type`
        iso_standards = self.iso_standard_ids.filtered(lambda s: s.standard == 'iso')
        ispo_standards = self.iso_standard_ids.filtered(lambda s: s.standard == 'ispo')

        # Jika ada standar ISO, buat review untuk ISO
        if iso_standards:
            for standard in iso_standards:
                self.create_iso_review(standard)
        
        # Jika ada standar ISPO, buat review untuk ISPO
        if ispo_standards:
            for standard in ispo_standards:
                self.create_ispo_review(standard)

    def create_iso_review(self, standard):
        # Buat record di model tsi.iso.review untuk setiap standar ISO
        self.env['tsi.iso.review'].create({
            'reference': self.iso_reference.id,  # Referensi ISO
            'iso_standard_ids': [(4, standard.id)],  # Tambahkan standar ISO ID
            # 'tgl_perkiraan_mulai': self.tgl_perkiraan_mulai,
            'tgl_perkiraan_selesai': datetime.strptime(self.tgl_perkiraan_audit_selesai, "%Y-%m-%d").date()
            if self.tgl_perkiraan_audit_selesai else False,
        })

    def create_ispo_review(self, standard):
        # Buat record di model tsi.ispo.review untuk setiap standar ISPO
        self.env['tsi.ispo.review'].create({
            'reference': self.ispo_reference.id,  # Referensi ISPO
            'iso_standard_ids': [(4, standard.id)],  # Tambahkan standar ISPO ID
            # 'tgl_perkiraan_mulai': self.tgl_perkiraan_mulai,
            'tgl_perkiraan_selesai': datetime.strptime(self.tgl_perkiraan_audit_selesai, "%Y-%m-%d").date()
            if self.tgl_perkiraan_audit_selesai else False,
        })


    # def set_nomor_kontrak(self):
    #     if not self.nomor_kontrak :
    #         if self.iso_reference :
    #             current = datetime.now()
    #             year    = current.strftime('%Y')

    #             if self.iso_reference.doctype == 'ispo' :
    #                 mmyy        = current.strftime('%m/%y')
    #                 tahun       = current.strftime('%y')
    #                 bulan       = current.strftime('%m')
    #                 bulan_roman = roman.toRoman(int(bulan))

    #                 sequence    = self.env['ir.sequence'].next_by_code('tsi.ispo.kontrak')
    #                 nomor       = str(sequence) + '/TSI/SPK-ISPO/' + str(bulan_roman) + '/' + str(tahun)

    #             else :                
    #                 sequence    = self.env['ir.sequence'].next_by_code('tsi.iso.kontrak')
    #                 nomor       = 'TSI-' + str(sequence) + '.16.01/' + str(year)


    #             self.write({'nomor_kontrak': nomor})            

    #     return True
    
    def set_nomor_kontrak(self):
        if not self.nomor_kontrak:
            if self.iso_standard_ids:
                # Assuming iso_standard_ids is a many2one or many2many field and you want to check for 'ispo' within it
                iso_ispo = any(standard.name == 'ISPO' for standard in self.iso_standard_ids)
            else:
                iso_ispo = False

            current = datetime.now()
            year = current.strftime('%Y')

            if iso_ispo:
                mmyy = current.strftime('%m/%y')
                tahun = current.strftime('%y')
                bulan = current.strftime('%m')
                bulan_roman = roman.toRoman(int(bulan))

                sequence = self.env['ir.sequence'].next_by_code('tsi.ispo.kontrak')
                nomor = f"{sequence}/TSI/SPK-ISPO/{bulan_roman}/{tahun}"
            else:
                sequence = self.env['ir.sequence'].next_by_code('tsi.iso.kontrak')
                nomor = f"TSI-{sequence}.16.01/{year}"

            self.write({'nomor_kontrak': nomor})

        return True

    def set_nomor_quotation(self):
        if not self.nomor_quotation :
            if self.iso_standard_ids:
                # Assuming iso_standard_ids is a many2one or many2many field and you want to check for 'ispo' within it
                iso_ispo = any(standard.name == 'ISPO' for standard in self.iso_standard_ids)
            else:
                iso_ispo = False

            current = datetime.now()
            year = current.strftime('%Y')

            if iso_ispo:
                mmyy = current.strftime('%m/%y')
                tahun = current.strftime('%y')
                bulan = current.strftime('%m')
                bulan_roman = roman.toRoman(int(bulan))

                sequence    = self.env['ir.sequence'].next_by_code('tsi.ispo.kontrak')
                nomor       = 'TSI-' + str(sequence) + '.'+ str(bulan_roman) +'/' + str(tahun)
            else :                
                sequence    = self.env['ir.sequence'].next_by_code('tsi.iso.kontrak')
                nomor       = 'TSI-' + str(sequence) + '.16.01/' + str(year)

                self.write({'nomor_quotation': nomor})            

        return True

    def set_id_customer(self):
        # self.write({'state': 'quotation'})            
        return True

    # def generate_crm(self):
    #     if self.order_line :
    #         self.env['tsi.crm'].create({
    #             'partner_id'        : self.partner_id.id,
    #             'contract_number'   : self.nomor_kontrak,
    #             'segment'           : [(6, 0, self.segment_id.ids)],
    #             'contract_date'     : self.date_order.date(),
    #             'iso_standard_ids'  : self.iso_reference.iso_standard_ids,
    #             'review_reference'  : self.application_review_ids,
    #             'iso_reference'     : self.iso_reference.id,
    #             'sales_reference'   : self.id,
    #             'tahapan_audit'     : self.sale_order_options.mapped('tahapan_audit')[0] if self.sale_order_options.mapped('tahapan_audit') else False,
    #         })
    #     else :
    #         raise UserError('Mohon melengkapi data penjualan')

    def generate_crm(self):

        if self.audit_status != 'certificate':
            partner_name = self.partner_id.name or 'Partner tidak dikenal'
            raise UserError(f'{partner_name} belum terbit sertifikat.')

        if self.order_line:
            tahapan_audit_ids = []
            show_initial = False
            show_survilance1 = False
            show_survilance2 = False
            show_survilance3 = False
            show_survilance4 = False
            show_recertification = False

            # Create the history_kontrak record
            history_kontrak = self.env['tsi.history_kontrak'].create({
                'partner_id': self.partner_id.id,
                'no_kontrak': self.nomor_kontrak,
                'segment': self.segment_id.id,
                'tanggal_kontrak': self.date_order.date(),
                'iso_standard_ids': self.iso_reference.iso_standard_ids.ids,
                'review_reference': self.application_review_ids.ids,
                'iso_reference': self.iso_reference.id,
                'sales_reference': self.id,
            })

            # Iterate through sale.order.line
            for line in self.order_line:
                audit_tahapan = line.audit_tahapan
                price_unit = line.price_unit

                # Periksa apakah audit_stage adalah "Initial Audit"
                if audit_tahapan == 'Initial Audit' and self.audit_status == 'certificate':
                    # Update status_klien menjadi "active"
                    self.partner_id.write({'status_klien': 'active'})
                    show_initial = True
                    tahapan_field = 'tahapan_id'
                    mandays_field = 'mandays'
                else:
                    tahapan_field = 'tahapan_id'
                    mandays_field = 'mandays'

                # Ambil data dari model ops.sertifikat berdasarkan partner_id atau company_id
                sertifikat = self.env['ops.sertifikat'].search([
                    ('nama_customer', '=', self.partner_id.id)  
                ], limit=1)
                
                if sertifikat:
                    nomor_sertifikat = sertifikat.nomor_sertifikat
                    akre = sertifikat.akre_tes.id
                    initial_date = sertifikat.initial_date
                    issue_date = sertifikat.issue_date
                    validity_date = sertifikat.validity_date
                    expiry_date = sertifikat.expiry_date
                else:
                    nomor_sertifikat = False
                    akre = False
                    initial_date = False
                    issue_date = False
                    validity_date = False
                    expiry_date = False

                if audit_tahapan:
                    tahapan_audit = self.env['tsi.iso.tahapan'].search([('name', '=', audit_tahapan)], limit=1)
                    if tahapan_audit:
                        tahapan_audit_ids.append(tahapan_audit.id)

                        if audit_tahapan == 'Initial Audit':
                            show_initial = True
                            tahapan_field = 'tahapan_id'
                            mandays_field = 'mandays'
                            nomor_field = 'nomor_ia'
                            akre_field = 'accreditation'
                            initial_field = 'tanggal_sertifikat1'
                            issue_field = 'tanggal_sertifikat2'
                            validity_field = 'tanggal_sertifikat3'
                            expiry_field = 'tanggal_sertifikat'
                        # elif audit_tahapan == 'Surveillance 1':
                        #     show_survilance1 = True
                        #     tahapan_field = 'tahapan_id1'
                        #     mandays_field = 'mandays_s1'
                        #     nomor_field = 'nomor_s1'
                        #     akre_field = 'accreditation'
                        #     initial_field = 'initial_sertifikat_s_2'
                        # elif audit_tahapan == 'Surveillance 2':
                        #     show_survilance2 = True
                        #     tahapan_field = 'tahapan_id2'
                        #     mandays_field = 'mandays_s2'
                        #     nomor_field = 'nomor_s2'
                        #     akre_field = 'accreditation'
                        #     initial_field = 'tanggal_sertifikat_initial_s2'
                        # elif audit_tahapan == 'Surveillance 3':
                        #     show_survilance3 = True
                        #     tahapan_field = 'tahapan_id3'
                        #     mandays_field = 'mandays_s3'
                        #     nomor_field = 'nomor_s3'
                        #     akre_field = 'accreditation'
                        #     initial_field = 'initial_tanggal_sertifikat_s3'
                        # elif audit_tahapan == 'Surveillance 4':
                        #     show_survilance4 = True
                        #     tahapan_field = 'tahapan_id4'
                        #     mandays_field = 'mandays_s4'
                        #     nomor_field = 'nomor_s4'
                        #     akre_field = 'accreditation'
                        #     initial_field = 'initiall_s4'
                        # elif audit_tahapan == 'Recertification 1':
                        #     show_recertification = True
                        #     tahapan_field = 'tahapan_id_re'
                        #     mandays_field = 'mandays_rs'
                        #     nomor_field = 'nomor_re'
                        #     akre_field = 'accreditation'
                        #     initial_field = 'tanggal_sertifikat_initial_rs'

                        # Create records in tsi.iso.mandays_app for each iso_standard_id
                        for iso_standard in self.iso_reference.iso_standard_ids:
                            self.env['tsi.iso.mandays_app'].create({
                                tahapan_field: history_kontrak.id,
                                'standard': iso_standard.id,
                                mandays_field: price_unit,
                                nomor_field: nomor_sertifikat,
                                akre_field: akre,
                                initial_field: initial_date,
                                issue_field: issue_date,
                                validity_field: validity_date,
                                expiry_field: expiry_date,
                            })

            # Iterate through tsi.order.options
            option_records = self.env['tsi.order.options'].search([('ordered_id', '=', self.id)])
            for option in option_records:
                audit_tahapan = option.audit_tahapan
                price_unit = option.price_units

                # Ambil data dari model ops.sertifikat berdasarkan partner_id atau company_id
                sertifikat = self.env['ops.sertifikat'].search([
                    ('nama_customer', '=', self.partner_id.id)  # Gantilah partner_id dengan nama_customer
                ], limit=1)
                
                if sertifikat:
                    nomor_sertifikat = sertifikat.nomor_sertifikat
                    akre = sertifikat.akre_tes
                    initial_date = sertifikat.initial_date
                else:
                    nomor_sertifikat = False
                    akre = False
                    initial_date = False

                if audit_tahapan:
                    tahapan_audit = self.env['tsi.iso.tahapan'].search([('name', '=', audit_tahapan)], limit=1)
                    if tahapan_audit:
                        tahapan_audit_ids.append(tahapan_audit.id)

                        # Logic remains similar to the one above
                        if audit_tahapan == 'Surveillance 1':
                            show_survilance1 = True
                            tahapan_field = 'tahapan_id1'
                            mandays_field = 'mandays_s1'
                            nomor_field = 'nomor_s1'
                            akre_field = 'accreditation'
                            initial_field = 'initial_sertifikat_s_2'
                        elif audit_tahapan == 'Surveillance 2':
                            show_survilance2 = True
                            tahapan_field = 'tahapan_id2'
                            mandays_field = 'mandays_s2'
                            nomor_field = 'nomor_s2'
                            akre_field = 'accreditation'
                            initial_field = 'tanggal_sertifikat_initial_s2'
                        elif audit_tahapan == 'Surveillance 3':
                            show_survilance3 = True
                            tahapan_field = 'tahapan_id3'
                            mandays_field = 'mandays_s3'
                            nomor_field = 'nomor_s3'
                            akre_field = 'accreditation'
                            initial_field = 'initial_tanggal_sertifikat_s3'
                        elif audit_tahapan == 'Surveillance 4':
                            show_survilance4 = True
                            tahapan_field = 'tahapan_id4'
                            mandays_field = 'mandays_s4'
                            nomor_field = 'nomor_s4'
                            akre_field = 'accreditation'
                            initial_field = 'initiall_s4'
                        elif audit_tahapan == 'Recertification':
                            show_recertification = True
                            tahapan_field = 'tahapan_id_re'
                            mandays_field = 'mandays_rs'
                            nomor_field = 'nomor_re'
                            akre_field = 'accreditation'
                            initial_field = 'tanggal_sertifikat_initial_rs'

                        # Create records in tsi.iso.mandays_app for each iso_standard_id
                        for iso_standard in self.iso_reference.iso_standard_ids:
                            self.env['tsi.iso.mandays_app'].create({
                                tahapan_field: history_kontrak.id,
                                'standard': iso_standard.id,
                                mandays_field: price_unit,
                                # nomor_field: nomor_sertifikat,
                                # # akre_field: akre,
                                # initial_field: initial_date,
                            })

            # Update the history_kontrak with tahapan_audit_ids and visibility flags
            history_kontrak.write({
                'tahapan_audit_ids': [(6, 0, tahapan_audit_ids)],
                'show_initial': show_initial,
                'show_survilance1': show_survilance1,
                'show_survilance2': show_survilance2,
                'show_survilance3': show_survilance3,
                'show_survilance4': show_survilance4,
                'show_recertification': show_recertification,
            })

        else:
            raise UserError('Mohon melengkapi data penjualan')

    def generate_ops(self):
        if self.tipe_pembayaran :
            if self.iso_reference.iso_standard_ids :
                notification = self.env['audit.notification'].create({
                    'iso_reference'     : self.iso_reference.id,
                    'customer'          : self.partner_id.id,
                    'sales_order_id'    : self.id,
                    'tipe_pembayaran'    : self.tipe_pembayaran,
                    'iso_standard_ids'  : self.iso_reference.iso_standard_ids,
                })
                self.iso_notification = notification.id
                for standard in self.iso_reference.iso_standard_ids :
                    if self.tipe_pembayaran in ['lunasawal','lunasakhir'] :

                        program = self.env['ops.program'].create({
                            'iso_reference'     : self.iso_reference.id,
                            'sales_order_id'    : self.id,
                            'iso_standard_ids'  : standard,
                            'notification_id'   : notification.id     
                        })
                        plan = self.env['ops.plan'].create({
                            'iso_reference'     : self.iso_reference.id,
                            'sales_order_id'    : self.id,
                            'iso_standard_ids'  : standard,
                            'notification_id'   : notification.id,
                            'contract_number'   : self.nomor_kontrak,
                            'contract_date'     : self.date_order  
                        })
                        review = self.env['ops.review'].create({
                            'iso_reference'     : self.iso_reference.id,
                            'sales_order_id'    : self.id,
                            'iso_standard_ids'  : standard,
                            'notification_id'   : notification.id     
                        })
                        report = self.env['ops.report'].create({
                            'iso_reference'     : self.iso_reference.id,
                            'sales_order_id'    : self.id,
                            'iso_standard_ids'  : standard,
                            'notification_id'   : notification.id     
                        })
                        sertifikat = self.env['ops.sertifikat'].create({
                            'iso_reference'     : self.iso_reference.id,
                            'sales_order_id'    : self.id,
                            'iso_standard_ids'  : standard,
                            'notification_id'   : notification.id     
                        })
                    else :
                        program = self.env['ops.program'].create({
                            'iso_reference'     : self.iso_reference.id,
                            'sales_order_id'    : self.id,
                            'iso_standard_ids'  : standard,
                            'contract_number'   : self.nomor_kontrak,
                            'notification_id'   : notification.id,
                            'dokumen_sosialisasi': self.dokumen_sosialisasi,
                            'file_name1'        : self.file_name1     
                        })
                        # plan = self.env['ops.plan'].create({
                        #     'iso_reference'     : self.iso_reference.id,
                        #     'sales_order_id'    : self.id,
                        #     'iso_standard_ids'  : standard,
                        #     'notification_id'   : notification.id,
                        #     'contract_number'   : self.nomor_kontrak,
                        #     'contract_date'     : self.date_order
                        # })                        
        else :
            raise UserError('Mohon tentukan tipe pembayaran')   

                # notification.write({'plan_lines': [(4, plan.id)]})
                # notification.write({'program_lines': [(4, program.id)]})
                # notification.write({'review_lines': [(4, review.id)]})
                # notification.write({'report_lines': [(4, report.id)]})

        return True

class AccountMove(models.Model):
    _inherit            = 'account.move'

    iso_reference       = fields.Many2one('tsi.iso', string="Reference")
    ispo_reference       = fields.Many2one('tsi.ispo', string="Reference",)
    reference_request_ids = fields.Many2many('tsi.audit.request', string='Audit Request', tracking=True)
    reference_request_ispo_ids = fields.Many2many('tsi.audit.request.ispo', string='Audit Request', tracking=True)
    sale_reference      = fields.Many2one('sale.order', string="Sale Reference")
    iso_notification    = fields.Many2one('audit.notification',  string="Notification")
    ispo_notification    = fields.Many2one('audit.notification.ispo', related='sale_reference.ispo_notification', string="Notification")
    contract_number = fields.Char(string='Nomor Kontrak', compute='_compute_contract_number', store=True)
    noted = fields.Char('Noted')
    doctype         = fields.Selection([
                            ('ISO',  'ISO'),
                            ('ISPO',   'ISPO'),
                        ], string='Doc Type', index=True, )
    tipe_pembayaran     = fields.Selection([
                            ('termin',     'Termin'),
                            ('lunasawal',   'Lunas di Awal'),
                            ('lunasakhir',  'Lunas di Akhir')
                        ], string='Tipe Pembayaran', tracking=True, related="iso_notification.tipe_pembayaran", readonly=False)
    formatted_amount_total = fields.Char(string='Formatted Total', compute='get_formatted_amount_total')
    formatted_amount_untaxed = fields.Char(string='Formatted Total Untaxed', compute='get_formatted_amount_untaxed')
    formatted_amount_untaxeds = fields.Char(string='Formatted Total Untaxed', compute='get_formatted_amount_untaxeds')
    formatted_amount_tax = fields.Char(string='Formatted Total TAX', compute='get_formatted_amount_tax')
    currency_id = fields.Many2one('res.currency', string='Currency', tracking=True)
    amount_total_text = fields.Char(string='Amount Total in Words', compute='_compute_amount_total_text', tracking=True)
    thn = fields.Char(string='Invoice Year', compute='_compute_invoice_date_parts', tracking=True)
    mon = fields.Char(string='Invoice Month', compute='_compute_invoice_date_parts', tracking=True)
    formatted_price_units = fields.Char(string="Formatted Price Units", compute='_compute_formatted_price_units')
    iso_standard_ids    = fields.Many2many('tsi.iso.standard', string='Standards',  store=True)
    terbit_invoice = fields.Selection([
        ('Direct', 'Direct'),
        ('Associate', 'Associate'),
    ], string="Terbit Invoice")

    associate_name = fields.Many2one('res.partner', string="Associate Name")
    total_price_unit = fields.Float(string='Total Harga Satuan', compute='_compute_total_price_unit', store=True)
    formatted_total_price_unit = fields.Char(string="Total Harga Satuan (Format)", compute='_compute_formatted_price_unit')

    # Format Total Harga Satuan (Seperti format_amount_untaxed)
    def format_total_price_unit(self, amount):
        if amount is None:
            return '0'
        return '{:,.0f}'.format(amount).replace(',', '.')

    @api.depends('total_price_unit')
    def _compute_formatted_price_unit(self):
        for rec in self:
            rec.formatted_total_price_unit = self.format_total_price_unit(rec.total_price_unit)

    @api.depends('invoice_line_ids.price_unit')
    def _compute_total_price_unit(self):
        for move in self:
            move.total_price_unit = sum(line.price_unit for line in move.invoice_line_ids)

    @api.onchange('terbit_invoice')
    def _onchange_terbit_invoice(self):
        """Menampilkan partner_id & associate_name sesuai pilihan terbit_invoice"""
        if self.terbit_invoice == 'Associate':
            # Jika "Associate", tetap tampilkan partner_id dan wajibkan associate_name
            self.partner_id = self.partner_id  # Partner tetap ada
        else:
            # Jika "Direct", kosongkan associate_name
            self.associate_name = False


    def _compute_formatted_price_units(self):
        for move in self:
            # Mengambil semua formatted_price_unit dari invoice_line_ids
            formatted_prices = []
            for line in move.invoice_line_ids:
                formatted_prices.append(line.formatted_price_unit)
            move.formatted_price_units = ", ".join(formatted_prices)

    #Compute Angka Menjadi huruf
    @api.depends('amount_total')
    def _compute_amount_total_text(self):
        for move in self:
            move.amount_total_text = self._amount_to_text(move.amount_total)

    #Compute Angka Menjadi huruf
    def _amount_to_text(self, amount):
        # Convert amount to words in Indonesian
        words = num2words(amount, lang='id').replace('-', ' ')
        # Remove decimal part and add 'rupiah'
        words = words.split(' koma ')[0] + ' rupiah'
        return words

    #Format Amoun Total
    def format_amount(self, amount):
        if amount is None:
            return '0'
        return '{:,.0f}'.format(amount).replace(',', '.')

    #Format Amoun Total
    def get_formatted_amount_total(self):
        for record in self:
            record.formatted_amount_total = self.format_amount(record.amount_total)

    #Format Amoun Untaxed
    def format_amount_untaxed(self, amount):
        if amount is None:
            return '0'
        return '{:,.0f}'.format(amount).replace(',', '.')

    #Format Amoun Untaxed
    def get_formatted_amount_untaxed(self):
        for record in self:
            record.formatted_amount_untaxed = self.format_amount_untaxed(record.amount_untaxed)
    
    
    #Format Amoun Tax
    def get_formatted_amount_tax(self):
        for record in self:
            record.formatted_amount_tax = self.format_amount_tax(record.amount_tax_signed)

    #Format Amoun Tax    
    def format_amount_tax(self, amount):
        if amount is None:
            return '0'
        return '{:,.0f}'.format(amount).replace(',', '.')
    
    def action_post(self):
        for rec in self:
            try:
                _logger.info('Processing move ID: %s', rec.id)
                if rec.payment_id:
                    if rec.payment_id.state not in ['posted', 'cancel']:
                        _logger.info('Calling action_post for payment_id %s', rec.payment_id.id)
                        rec.payment_id.action_post()
                else:
                    _logger.info('Calling _post for move ID %s', rec.id)
                    rec._post(soft=False)
                
                # Menambahkan fitur untuk mengirim notifikasi
                _logger.info('Sending notification for move ID %s', rec.id)
                rec.send_post_notification()

                _logger.info('Move %s posted successfully.', rec.id)
            except UserError as e:
                _logger.error('UserError while posting move %s: %s', rec.id, str(e))
                raise
            except Exception as e:
                _logger.error('Error posting move %s: %s', rec.id, str(e))
                raise UserError(f'Error posting move {rec.id}: {str(e)}')
        return False
    
    def send_post_notification(self):
        for rec in self:
            # Logika untuk mengirim notifikasi, misalnya email
            _logger.info('Notifikasi: Move %s berhasil diposting.', rec.id)
            # Contoh email, Anda dapat menambahkan logika email di sini
            # self.env['mail.mail'].create({
            #     'subject': 'Move Posted',
            #     'body_html': f'<p>Move {rec.id} has been posted successfully.</p>',
            #     'email_to': 'example@example.com',
            # }).send()
    
    #Compute Bulan dan Tahun
    @api.depends('invoice_date')
    def _compute_invoice_date_parts(self):
        for move in self:
            if move.invoice_date:
                date = fields.Date.from_string(move.invoice_date)
                move.thn = date.strftime('%Y')
                move.mon = date.strftime('%m')
            else:
                move.thn = ''
                move.mon = ''

    @api.depends('invoice_origin')
    def _compute_contract_number(self):
        for invoice in self:
            if invoice.invoice_origin:
                sales_order = self.env['sale.order'].search([('name', '=', invoice.invoice_origin)], limit=1)
                if sales_order:
                    invoice.contract_number = sales_order.nomor_kontrak

    def set_lunas_dp(self):
        if self.sale_reference:
            # Cek tipe pembayaran
            if self.tipe_pembayaran == 'termin':
                # Jika tipe pembayaran 'termin', buat dua records
                for standard in self.iso_reference.iso_standard_ids:
                    # Mencari reference request yang cocok berdasarkan iso_standard_ids
                    matching_reference = self.reference_request_ids.filtered(
                        lambda r: standard.id in r.iso_standard_ids.ids  # Gunakan .ids untuk mengambil ID dari Many2many
                    )
                    reference_ids = matching_reference.ids if matching_reference else []

                    # Buat ops.report
                    self.env['ops.report'].create({
                        'iso_reference': self.iso_reference.id,
                        'reference_request_ids': [(6, 0, reference_ids)],  # Gunakan reference_ids yang benar
                        'sales_order_id': self.sale_reference.id,
                        'iso_standard_ids': [(6, 0, [standard.id])],
                        'notification_id': self.iso_notification.id
                    })
                
                # Buat satu lagi record untuk 'termin' jika perlu
                for standard in self.iso_reference.iso_standard_ids:
                    matching_reference = self.reference_request_ids.filtered(
                        lambda r: standard.id in r.iso_standard_ids.ids
                    )
                    reference_ids = matching_reference.ids if matching_reference else []

                    # Buat ops.report
                    self.env['ops.report'].create({
                        'iso_reference': self.iso_reference.id,
                        'reference_request_ids': [(6, 0, reference_ids)],  # Gunakan reference_ids yang benar
                        'sales_order_id': self.sale_reference.id,
                        'iso_standard_ids': [(6, 0, [standard.id])],
                        'notification_id': self.iso_notification.id
                    })

            elif self.tipe_pembayaran in ['lunasawal', 'lunasakhir']:
                # Jika tipe pembayaran 'lunasawal' atau 'lunasakhir', buat satu record
                for standard in self.iso_reference.iso_standard_ids:
                    self.env['ops.report'].create({
                        'iso_reference': self.iso_reference.id,
                        'sales_order_id': self.sale_reference.id,
                        'iso_standard_ids': [(6, 0, [standard.id])],
                        'notification_id': self.iso_notification.id
                    })

            # Proses untuk ISPO reference
            if self.ispo_reference:
                for standard in self.ispo_reference.iso_standard_ids:
                    self.env['ops.report.ispo'].create({
                        'ispo_reference': self.ispo_reference.id,
                        'sales_order_id': self.sale_reference.id,
                        'iso_standard_ids': [(6, 0, [standard.id])],
                        'notification_id': self.ispo_notification.id
                    })

            # Proses berdasarkan reference_request_ids jika ada
            if self.reference_request_ids:
                for reference_request in self.reference_request_ids:
                    for standard in reference_request.iso_standard_ids:
                        self.env['ops.report'].create({
                            'iso_reference': self.iso_reference.id,
                            'reference_request_ids': [(6, 0, [reference_request.id])],  # Gunakan reference_request.id
                            'sales_order_id': self.sale_reference.id,
                            'iso_standard_ids': [(6, 0, [standard.id])],
                            'notification_id': self.iso_notification.id
                        })

            # Proses untuk reference_request_ispo_ids jika ada
            if self.reference_request_ispo_ids:
                for standard in self.reference_request_ispo_ids.iso_standard_ids:
                    self.env['ops.report.ispo'].create({
                        'sales_order_id': self.sale_reference.id,
                        'iso_standard_ids': [(6, 0, [standard.id])],
                        'notification_id': self.ispo_notification.id
                    })

        return True


    def set_lunas_payment(self):
        for record in self:
            if record.iso_notification and record.iso_notification.audit_state != 'recommendation':
                raise UserError("Audit belum pada tahap Recommendation. Tidak bisa melanjutkan proses untuk Terbit Sertifikat.")

            if record.sale_reference:
                if record.iso_reference:
                    for standard in record.iso_reference.iso_standard_ids:
                        self.env['ops.sertifikat'].create({
                            'iso_reference': record.iso_reference.id,
                            'sales_order_id': record.sale_reference.id,
                            'iso_standard_ids': standard,
                            'notification_id': record.iso_notification.id
                        })
                    # Ubah status state menjadi 'done' pada ops.plan terkait dengan iso_notification
                    if self.iso_notification.review_lines:
                        self.iso_notification.review_lines.write({'state': 'done'})
                elif record.ispo_reference:
                    for standard in record.ispo_reference.iso_standard_ids:
                        self.env['ops.sertifikat.ispo'].create({
                            'ispo_reference': record.ispo_reference.id,
                            'sales_order_id': record.sale_reference.id,
                            'iso_standard_ids': standard,
                            'notification_id': record.ispo_notification.id
                        })

                else:
                    for standard in record.iso_standard_ids:
                        if standard.name == 'ISPO':
                            self.env['ops.sertifikat.ispo'].create({
                                'sales_order_id': record.sale_reference.id,
                                'iso_standard_ids': [(6, 0, [standard.id])],
                                'notification_id': record.ispo_notification.id,
                                'nama_customer' : record.sale_reference.partner_id.name
                            })
                        else:
                            self.env['ops.sertifikat'].create({
                                'sales_order_id': record.sale_reference.id,
                                'iso_standard_ids': [(6, 0, [standard.id])],
                                'notification_id': record.iso_notification.id,
                                'nama_customer' : record.sale_reference.partner_id.name
                            })
                            # Ubah status state menjadi 'done' pada ops.plan terkait dengan iso_notification
                            if self.iso_notification.review_lines:
                                self.iso_notification.review_lines.write({'state': 'done'})

        return True
    
    
    
    # @api.model
    # def create(self, vals):
    #     if 'invoice_origin' in vals:
    #         # Mencari Sale Order berdasarkan invoice_origin
    #         invoice = self.env['sale.order'].search([('name', '=', vals['invoice_origin'])], limit=1)
    #         if invoice:
    #             # Menetapkan ispo_reference dan ispo_notification
    #             if invoice.iso_reference:
    #                 vals['ispo_reference'] = invoice.iso_reference.id
    #             if invoice.iso_notification:
    #                 vals['ispo_notification'] = invoice.iso_notification.id

    #             # Menetapkan sale_reference
    #             vals['sale_reference'] = invoice.id

    #     return super(AccountMove, self).create(vals)

    @api.model
    def create(self, vals):
        if 'invoice_origin' in vals:
            sale_order = self.env['sale.order'].search([('name', '=', vals['invoice_origin'])], limit=1)
            if sale_order:
                if sale_order.iso_reference:
                    vals['iso_reference'] = sale_order.iso_reference
                    vals['iso_notification'] = sale_order.iso_notification
                
                if sale_order.ispo_reference:
                    vals['ispo_reference'] = sale_order.ispo_reference
                    vals['ispo_notification'] = sale_order.ispo_notification

                if sale_order.reference_request_ids:
                    vals['reference_request_ids'] = [(6, 0, sale_order.reference_request_ids.ids)]
                    vals['iso_notification'] = sale_order.iso_notification

                if sale_order.reference_request_ispo_ids:
                    vals['reference_request_ispo_ids'] = [(6, 0, sale_order.reference_request_ispo_ids.ids)]
                    vals['ispo_notification'] = sale_order.ispo_notification

                if sale_order.iso_standard_ids:
                    vals['iso_standard_ids'] = [(6, 0, sale_order.iso_standard_ids.ids)]

                vals['sale_reference'] = sale_order.id

        return super(AccountMove, self).create(vals)

class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    audit_tahapan = fields.Selection([
                            ('Initial Audit', 'Initial Audit'),
                            ('Surveillance 1', 'Surveillance 1'),
                            ('Surveillance 2', 'Surveillance 2'),
                            ('Recertefication', 'Recertefication'),],
                            string='Audit Stage', index=True, )
    tahun = fields.Integer(string="Tahun")
    price_unit = fields.Float(string='Unit Price', digits='Product Price')
    formatted_price_unit = fields.Char(string='Formatted Unit Price', compute='_compute_formatted_price_unit')
    in_pajak = fields.Boolean("Include Pajak")
    ex_pajak = fields.Boolean("Exclude Pajak")

    @api.onchange('price_unit', 'in_pajak', 'tax_id')
    def _compute_price_with_tax(self):
        if self.in_pajak:
            # Mengambil tarif pajak yang pertama dari tax_id (misalnya 11%)
            if self.tax_id:
                tax_rate = self.tax_id.amount / 100  # Mengambil rate pajak dari tax_id dan mengubah menjadi persen (11% menjadi 0.11)
                # Menghitung harga sebelum pajak
                price_before_tax = self.price_unit / (1 + tax_rate)
                self.price_subtotal = price_before_tax * self.product_uom_qty  # Harga subtotal sebelum pajak
                # Menghitung pajak yang harus dihitung berdasarkan harga sebelum pajak
                self.tax_amount = self.price_subtotal * tax_rate
            else:
                self.tax_amount = 0
        elif self.ex_pajak:
            # Jika harga tidak termasuk pajak, maka gunakan harga unit seperti biasa
            self.price_subtotal = self.price_unit * self.product_uom_qty
            self.tax_amount = 0  # Pajak dihitung secara terpisah nanti

    # Method untuk menghitung pajak terhitung
    def _compute_tax_amount(self):
        if not self.in_pajak: 
            # Jika harga tidak termasuk pajak, pajak dihitung berdasarkan `price_unit` dan `tax_id`
            if self.tax_id:
                tax_rate = self.tax_id.amount / 100
                self.tax_amount = self.price_unit * tax_rate

    def _compute_formatted_price_unit(self):
        for line in self:
            # Format harga dalam Rupiah, tambahkan tanda minus jika harga negatif
            if line.price_unit < 0:
                line.formatted_price_unit = "({:,.0f})".format(abs(line.price_unit)).replace(',', '.')
            else:
                line.formatted_price_unit = "{:,.0f}".format(line.price_unit).replace(',', '.')

class ResPartnerBank(models.Model):
    _inherit = 'res.partner.bank'

    code = fields.Char(string='Bank Code', index=True, )
    branch = fields.Char(string="Bank Branch")

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'
    _order = 'order_id, ordered_id, sequence, id'

    cek_crm = fields.Boolean(string='To CRM')
    audit_tahapan = fields.Selection([
                            ('Initial Audit',         'Initial Audit'),
                            ('Surveillance 1', 'Surveillance 1'),
                            ('Surveillance 2', 'Surveillance 2'),
                            ('Recertification', 'Recertification'),],
                            string='Audit Stage', index=True, )
    initial_id = fields.Many2one('tsi.iso.initial', string="Surveillance Line")
    # tahapan = fields.Selection([
    #                         ('survilance 1', 'Survillance 1'),
    #                         ('survilance 2', 'Survillance 2'),
    #                         ('survilance 3', 'Survillance 3'),
    #                         ('survilance 4', 'Survillance 4'),],
    #                         string='Audit Stage', index=True, )
    tahun           = fields.Char("Tahun")
    ordered_id  = fields.Many2one('sale.order', string='Optional Product', required=True, ondelete='cascade', index=True, copy=False)
    price_units = fields.Float(string="Price Unit", required=True)
    quanty      = fields.Float(string="Quantity", required=True, default=1.0)
    in_pajak = fields.Boolean("Include Pajak")
    ex_pajak = fields.Boolean("Exclude Pajak")
    # sale_order_line_id = fields.Many2one('sale.order', string='Optional Product')

    @api.onchange('in_pajak', 'ex_pajak')
    def _onchange_in_ex_pajak(self):
        for rec in self:
            # Pastikan hanya satu checkbox yang aktif
            if rec.in_pajak and rec.ex_pajak:
                rec.ex_pajak = False

            # Kalau in_pajak dicentang → hitung harga tanpa pajak
            if rec.in_pajak:
                rec.price_unit = rec.price_unit / 1.11 if rec.price_unit else 0.0

            # Kalau ex_pajak dicentang → biarkan price_unit apa adanya
            elif rec.ex_pajak:
                pass  # Tidak diubah

            # Kalau tidak dicentang keduanya → biarkan juga
            elif not rec.in_pajak and not rec.ex_pajak:
                pass

    def _prepare_invoice_line(self, **optional_values):
        """
        Prepare the dict of values to create the new invoice line for a sales order line.

        :param qty: float quantity to invoice
        :param optional_values: any parameter that should be added to the returned invoice line
        """
        self.ensure_one()
        res = {
            'display_type': self.display_type,
            'sequence': self.sequence,
            'name': self.name,
            'audit_tahapan': self.audit_tahapan,
            'product_id': self.product_id.id,
            'product_uom_id': self.product_uom.id,
            'quantity': self.qty_to_invoice,
            'discount': self.discount,
            'price_unit': self.price_unit,
            'tax_ids': [(6, 0, self.tax_id.ids)],
            'sale_line_ids': [(4, self.id)],
        }
        if self.order_id.analytic_account_id and not self.display_type:
            res['analytic_account_id'] = self.order_id.analytic_account_id.id
        if self.analytic_tag_ids and not self.display_type:
            res['analytic_tag_ids'] = [(6, 0, self.analytic_tag_ids.ids)]
        if optional_values:
            res.update(optional_values)
        if self.display_type:
            res['account_id'] = False
        return res


    class SaleOrderOptions(models.Model):
        _name = 'tsi.order.options'
        _order = 'ordered_id'

        ordered_id = fields.Many2one('sale.order', string="Optional Product")
        surveillance_id = fields.Many2one('tsi.iso.surveillance', string="Surveillance Line")
        tahun_audit = fields.Char("Tahun")
        tahapan_audit = fields.Selection([
                            ('Surveillance 1', 'Surveillance 1'),
                            ('Surveillance 2', 'Surveillance 2'),
                            ('Surveillance 3', 'Surveillance 3'),
                            ('Surveillance 4', 'Surveillance 4'),
                            ('Recertification', 'Recertification'),],
                            string='Audit Stage', index=True, )
        audit_tahapan = fields.Selection([
                            ('Surveillance 1', 'Surveillance 1'),
                            ('Surveillance 2', 'Surveillance 2'),
                            ('Surveillance 3', 'Surveillance 3'),
                            ('Surveillance 4', 'Surveillance 4'),
                            ('Recertification', 'Recertification'),],
                            string='Audit Stage', index=True, )
        price_units = fields.Float(string="Price Unit", required=True,)
        quanty      = fields.Float(string="Quantity", required=True, default=1.0)
        # tax_id = fields.Many2many('account.tax', string='Taxes', context={'active_test': False})

class MandaysAuditor(models.Model):
        _name           = 'mandays.auditor'
        _description    = 'Mandays Auditor'
        _rec_name       = 'name_auditor'

        name_auditor    = fields.Many2one('hr.employee', 
                                string="Nama Audior",
                                domain="[('department_id.name', 'in', ['OPERATION ICT', 'OPERATION XMS', 'Auditor Subcont'])]")
        auditor_ir      = fields.Boolean("Auditor Internal")
        auditor_er      = fields.Boolean("Auditor External")
        harga_mandays   = fields.Float("Harga Mandays")