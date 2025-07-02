from odoo import models, fields, api
from datetime import datetime
import logging

# Inisialisasi logger
_logger = logging.getLogger(__name__)

class QCPassISO(models.Model):
    _name = 'qc.pass.iso'
    _description = 'Quality Controll Pass ISO'
    _inherit        = ['mail.thread', 'mail.activity.mixin']
    _rec_name       = 'customer'
    _order          = 'id DESC'
    
    customer        = fields.Many2one('res.partner', string="Company Name", domain="[('is_company', '=', True)]")
    iso_reference = fields.Many2one('tsi.iso', string="App Form")
    iso_reference_check = fields.Boolean(string="QC Pass Key")
    noted_iso = fields.Text('QC Noted ISO')
    application_review_ids   = fields.Many2many('tsi.iso.review', string="App Review")
    application_review_check = fields.Boolean(string="QC Pass Key")
    noted_iso_review = fields.Text('QC Noted Review')
    sale_order_id = fields.Many2one('sale.order', string="Sale Order")
    sale_order_check = fields.Boolean(string="QC Pass Key")
    noted_iso_sales = fields.Text('QC Noted Sales')
    program_id = fields.Many2many('ops.program', string="OPS Program")
    program_check = fields.Boolean(string="QC Pass Key")
    noted_iso_program = fields.Text('QC Noted Ops Program')
    plan_id = fields.Many2many('ops.plan', string="OPS Plan")
    plan_check = fields.Boolean(string="QC Pass Key")
    noted_iso_plan = fields.Text('QC Noted Ops Plan')
    report_id = fields.Many2many('ops.report', string="OPS Report")
    report_check = fields.Boolean(string="QC Pass Key")
    noted_iso_report = fields.Text('QC Noted Ops Report')
    review_id = fields.Many2many('ops.review', string="OPS Reccomendation")
    review_check = fields.Boolean(string="QC Pass Key")
    noted_iso_ops_review = fields.Text('QC Noted Ops Review')
    sertifikat_id = fields.Many2many('ops.sertifikat', string="OPS Sertifikat")
    sertifikat_check = fields.Boolean(string="QC Pass Key")
    noted_iso_sertifikat = fields.Text('QC Noted Ops Sertifikat')

    @api.model
    def load_views(self, views, options=None):
        self.create_ows_on_open()
        return super(QCPassISO, self).load_views(views, options)
        
    def create_ows_on_open(self):
        partners = self.env['res.partner'].search([("is_company", "=", True)])

        for partner in partners:
            # Mencari data ISO berdasarkan customer (partner.id) dari model tsi.iso
            for iso in self.env["tsi.iso"].search([('customer', '=', partner.id)]):
                # Mengambil semua iso_review yang terkait dengan partner
                iso_reviews = self.env["tsi.iso.review"].search([('customer', '=', partner.id)])

                # Membuat list untuk menyimpan semua iso_review.id
                iso_review_ids = iso_reviews.ids  # Mendapatkan semua id dari iso_review yang terkait

                # Mengambil semua ops.program yang terkait dengan partner
                ops_program = self.env["ops.program"].search([('customer', '=', partner.id)])
                # Membuat list untuk menyimpan semua ops.program.id
                ops_program_ids = ops_program.ids  # Mendapatkan semua id dari ops.program yang terkait

                # Mengambil semua ops.plan yang terkait dengan partner
                ops_plan = self.env["ops.plan"].search([('customer', '=', partner.id)])
                # Membuat list untuk menyimpan semua ops.plan.id
                ops_plan_ids = ops_plan.ids  # Mendapatkan semua id dari ops.plan yang terkait

                # Mengambil semua ops.report yang terkait dengan partner
                ops_report = self.env["ops.report"].search([('customer', '=', partner.id)])
                # Membuat list untuk menyimpan semua ops.report.id
                ops_report_ids = ops_report.ids  # Mendapatkan semua id dari ops.report yang terkait

                # Mengambil semua ops.review yang terkait dengan partner
                ops_review = self.env["ops.review"].search([('nama_customer', '=', partner.id)])
                # Membuat list untuk menyimpan semua ops.review.id
                ops_review_ids = ops_review.ids  # Mendapatkan semua id dari ops.review yang terkait
                
                # Mengambil semua ops.sertifikat yang terkait dengan partner
                ops_sertifikat = self.env["ops.sertifikat"].search([('nama_customer', '=', partner.id)])
                # Membuat list untuk menyimpan semua ops.sertifikat.id
                ops_sertifikat_ids = ops_sertifikat.ids  # Mendapatkan semua id dari ops.sertifikat yang terkait

                for sale_order in self.env["sale.order"].search([('partner_id', '=', partner.id)]):
                    # Cek apakah sudah ada data qc.pass.iso yang sesuai
                    existing_qc_pass_iso = self.env['qc.pass.iso'].search([
                        ('iso_reference', '=', iso.id),  # Pencarian berdasarkan iso_reference
                        ('application_review_ids', 'in', iso_review_ids),  # Pencarian berdasarkan application_review_ids
                        ('sale_order_id', '=', sale_order.id),  # Pencarian berdasarkan sale_order_id
                        ('program_id', 'in', ops_program_ids),
                        ('plan_id', 'in', ops_plan_ids),
                        ('report_id', 'in', ops_report_ids),
                        ('review_id', 'in', ops_review_ids),
                        ('sertifikat_id', 'in', ops_sertifikat_ids),
                    ])

                    if existing_qc_pass_iso:
                        # Jika sudah ada, cek apakah ada perubahan data
                        current_vals = existing_qc_pass_iso.read([
                            'iso_reference', 'application_review_ids', 'sale_order_id', 
                            'program_id', 'plan_id', 'report_id', 'review_id', 'sertifikat_id'
                        ])[0]

                        # Hanya lakukan update jika ada perubahan data
                        new_vals = {
                            "customer": partner.id,  # Update customer
                            "iso_reference": iso.id,  # Update iso_reference
                            "application_review_ids": [(6, 0, iso_review_ids)],  # Menambahkan banyak iso_review_id yang terhubung
                            "sale_order_id": sale_order.id,  # Set sale_order_id yang terhubung
                            "program_id": [(6, 0, ops_program_ids)],
                            "plan_id": [(6, 0, ops_plan_ids)],
                            "report_id": [(6, 0, ops_report_ids)],
                            "review_id": [(6, 0, ops_review_ids)],
                            "sertifikat_id": [(6, 0, ops_sertifikat_ids)],
                        }

                        # Bandingkan nilai yang ada dengan nilai baru
                        if current_vals != new_vals:
                            existing_qc_pass_iso.write(new_vals)
                    else:
                        # Jika belum ada, maka buat data baru
                        self.env['qc.pass.iso'].create({
                            "customer": partner.id,  # Set customer
                            "iso_reference": iso.id,  # Set iso_reference
                            "application_review_ids": [(6, 0, iso_review_ids)],  # Menambahkan banyak iso_review_id yang terhubung
                            "sale_order_id": sale_order.id,  # Set sale_order_id yang terhubung
                            "program_id": [(6, 0, ops_program_ids)],
                            "plan_id": [(6, 0, ops_plan_ids)],
                            "report_id": [(6, 0, ops_report_ids)],
                            "review_id": [(6, 0, ops_review_ids)],
                            "sertifikat_id": [(6, 0, ops_sertifikat_ids)],
                        })


class QCPassISPO(models.Model):
    _name = 'qc.pass.ispo'
    _description = 'Quality Controll Pass ISPO'
    _inherit        = ['mail.thread', 'mail.activity.mixin']
    _rec_name       = 'customer'
    _order          = 'id DESC'

    customer        = fields.Many2one('res.partner', string="Company Name", domain="[('is_company', '=', True)]")
    ispo_reference = fields.Many2one('tsi.ispo', string="App Form")
    ispo_reference_check = fields.Boolean(string="Select ISO Reference")
    application_review_ispo_ids   = fields.Many2many('tsi.ispo.review', string="App Review")
    application_review_ispo_check = fields.Boolean(string="Select Review")
    sale_order_id = fields.Many2one('sale.order', string="Sale Order")
    sale_order_check = fields.Boolean(string="Select Sale Order")
    program_ispo_id = fields.Many2many('ops.program.ispo', string="OPS Program")
    program_check = fields.Boolean(string="Select OPS Program")
    plan_ispo_id = fields.Many2many('ops.plan.ispo', string="OPS Plan")
    plan_check = fields.Boolean(string="Select OPS Plan")
    report_ispo_id = fields.Many2many('ops.report.ispo', string="OPS Report")
    report_check = fields.Boolean(string="Select OPS Report")
    review_ispo_id = fields.Many2many('ops.review.ispo', string="OPS Reccomendation")
    review_check = fields.Boolean(string="Select OPS Recommendation")
    sertifikat_ispo_id = fields.Many2many('ops.sertifikat.ispo', string="OPS Sertifikat")
    sertifikat_check = fields.Boolean(string="Select Operation Sertifikat")

    @api.model
    def load_views(self, views, options=None):
        self.create_ows_ispo_on_open()
        return super(QCPassISPO, self).load_views(views, options)
    
    def create_ows_ispo_on_open(self):
        partners = self.env['res.partner'].search([("is_company", "=", True)])

        for partner in partners:
            # Mencari data ISO berdasarkan customer (partner.id) dari model tsi.iso
            for ispo in self.env["tsi.ispo"].search([('customer', '=', partner.id)]):
                # Mengambil semua iso_review yang terkait dengan partner
                ispo_reviews = self.env["tsi.ispo.review"].search([('customer', '=', partner.id)])

                # Membuat list untuk menyimpan semua iso_review.id
                ispo_review_ids = ispo_reviews.ids  # Mendapatkan semua id dari iso_review yang terkait


                # Mengambil semua ops.program yang terkait dengan partner
                ops_program_ispo = self.env["ops.program.ispo"].search([('customer', '=', partner.id)])
                # Membuat list untuk menyimpan semua ops.program.id
                ops_program_ispo_ids = ops_program_ispo.ids  # Mendapatkan semua id dari ops.program yang terkait

                # Mengambil semua ops.plan yang terkait dengan partner
                ops_plan_ispo = self.env["ops.plan.ispo"].search([('customer', '=', partner.id)])
                # Membuat list untuk menyimpan semua ops.plan.id
                ops_plan_ispo_ids = ops_plan_ispo.ids  # Mendapatkan semua id dari ops.program yang terkait

                # Mengambil semua ops.report yang terkait dengan partner
                ops_report_ispo = self.env["ops.report.ispo"].search([('customer', '=', partner.id)])
                # Membuat list untuk menyimpan semua ops.report.id
                ops_report_ispo_ids = ops_report_ispo.ids  # Mendapatkan semua id dari ops.report yang terkait

                # Mengambil semua ops.report yang terkait dengan partner
                ops_review_ispo = self.env["ops.review.ispo"].search([('nama_customer', '=', partner.id)])
                # Membuat list untuk menyimpan semua ops.review.id
                ops_review_ispo_ids = ops_review_ispo.ids  # Mendapatkan semua id dari ops.report yang terkait
                
                # Mengambil semua ops.sertifikat yang terkait dengan partner
                ops_sertifikat_ispo = self.env["ops.sertifikat.ispo"].search([('nama_customer', '=', partner.id)])
                # Membuat list untuk menyimpan semua ops.sertifikat.id
                ops_sertifikat_ispo_ids = ops_sertifikat_ispo.ids  # Mendapatkan semua id dari ops.sertifikat yang terkait
                for sale_order in self.env["sale.order"].search([('partner_id', '=', partner.id)]):
                    # Cari qc.pass.iso berdasarkan referensi ISO dari tsi.iso, bukan berdasarkan customer
                    existing_qc_pass_ispo = self.env['qc.pass.ispo'].search([
                        ('ispo_reference', '=', ispo.id),  # Pencarian berdasarkan iso_reference
                        ('application_review_ispo_ids', 'in', ispo_review_ids),  # Pencarian berdasarkan application_review_ids
                        ('sale_order_id', '=', sale_order.id),  # Pencarian berdasarkan sale_order_id
                        ('program_ispo_id', 'in', ops_program_ispo_ids),
                        ('plan_ispo_id', 'in', ops_plan_ispo_ids),
                        ('report_ispo_id', 'in', ops_report_ispo_ids),
                        ('review_ispo_id', 'in', ops_review_ispo_ids),
                        ('sertifikat_ispo_id', 'in', ops_sertifikat_ispo_ids),
                    ])
                    
                    if existing_qc_pass_ispo:
                        # Jika sudah ada, lakukan update
                        existing_qc_pass_ispo.write({
                            "customer": partner.id,  # Update customer
                            "ispo_reference": ispo.id,  # Update ispo_reference
                            "application_review_ispo_ids": [(6, 0, ispo_review_ids)],  # Menambahkan banyak iso_review_id yang terhubung
                            "sale_order_id": sale_order.id,  # Set sale_order_id yang terhubung
                            "program_ispo_id": [(6, 0, ops_program_ispo_ids)],
                            "plan_ispo_id": [(6, 0, ops_plan_ispo_ids)],
                            "report_ispo_id": [(6, 0, ops_report_ispo_ids)],
                            "review_ispo_id": [(6, 0, ops_review_ispo_ids)],
                            "sertifikat_ispo_id": [(6, 0, ops_sertifikat_ispo_ids)],
                        })
                    else:
                        # Jika belum ada, buat data baru
                        self.env['qc.pass.ispo'].create({
                            "customer": partner.id,  # Set customer
                            "ispo_reference": ispo.id,  # Update ispo_reference
                            "application_review_ispo_ids": [(6, 0, ispo_review_ids)],  # Menambahkan banyak iso_review_id yang terhubung
                            "sale_order_id": sale_order.id,  # Set sale_order_id yang terhubung
                            "program_ispo_id": [(6, 0, ops_program_ispo_ids)],
                            "plan_ispo_id": [(6, 0, ops_plan_ispo_ids)],
                            "report_ispo_id": [(6, 0, ops_report_ispo_ids)],
                            "review_ispo_id": [(6, 0, ops_review_ispo_ids)],
                            "sertifikat_ispo_id": [(6, 0, ops_sertifikat_ispo_ids)],
                        })

class QCPassISOSurveillance(models.Model):
    _name = 'qc.pass.iso.surveillance'
    _description = 'Quality Controll Pass ISO Surveillance'
    _inherit        = ['mail.thread', 'mail.activity.mixin']
    _rec_name       = 'customer'
    _order          = 'id DESC'
    
    customer        = fields.Many2one('res.partner', string="Company Name", domain="[('is_company', '=', True)]")
    audit_request_iso = fields.Many2many('tsi.audit.request', string="Audit Request")
    audit_request_iso_reference_check = fields.Boolean(string="QC Pass Key")
    audit_request_noted_iso = fields.Text('QC Noted ISO')
    application_review_ids   = fields.Many2many('tsi.iso.review', string="App Review")
    application_review_check = fields.Boolean(string="QC Pass Key")
    noted_iso_review = fields.Text('QC Noted Review')
    sale_order_id = fields.Many2one('sale.order', string="Sale Order")
    sale_order_check = fields.Boolean(string="QC Pass Key")
    noted_iso_sales = fields.Text('QC Noted Sales')
    program_id = fields.Many2many('ops.program', string="OPS Program")
    program_check = fields.Boolean(string="QC Pass Key")
    noted_iso_program = fields.Text('QC Noted Ops Program')
    plan_id = fields.Many2many('ops.plan', string="OPS Plan")
    plan_check = fields.Boolean(string="QC Pass Key")
    noted_iso_plan = fields.Text('QC Noted Ops Plan')
    report_id = fields.Many2many('ops.report', string="OPS Report")
    report_check = fields.Boolean(string="QC Pass Key")
    noted_iso_report = fields.Text('QC Noted Ops Report')
    review_id = fields.Many2many('ops.review', string="OPS Reccomendation")
    review_check = fields.Boolean(string="QC Pass Key")
    noted_iso_ops_review = fields.Text('QC Noted Ops Review')
    sertifikat_id = fields.Many2many('ops.sertifikat', string="OPS Sertifikat")
    sertifikat_check = fields.Boolean(string="QC Pass Key")
    noted_iso_sertifikat = fields.Text('QC Noted Ops Sertifikat')

    @api.model
    def load_views(self, views, options=None):
        self.create_ows_on_open()
        return super(QCPassISOSurveillance, self).load_views(views, options)
    
    def create_ows_on_open(self):
        partners = self.env['res.partner'].search([("is_company", "=", True)])

        for partner in partners:
            # Mencari data ISO berdasarkan customer (partner.id) dari model tsi.iso
            for audit_request in self.env["tsi.audit.request"].search([('partner_id', '=', partner.id)]):
                # Membuat list untuk menyimpan semua iso_review.id
                audit_request_ids = audit_request.ids  # Mendapatkan semua id dari iso_review yang terkait

                # Mengambil semua ops.program yang terkait dengan partner
                ops_program = self.env["ops.program"].search([('customer', '=', partner.id)])
                # Membuat list untuk menyimpan semua ops.program.id
                ops_program_ids = ops_program.ids  # Mendapatkan semua id dari ops.program yang terkait

                # Mengambil semua ops.plan yang terkait dengan partner
                ops_plan = self.env["ops.plan"].search([('customer', '=', partner.id)])
                # Membuat list untuk menyimpan semua ops.plan.id
                ops_plan_ids = ops_plan.ids  # Mendapatkan semua id dari ops.program yang terkait

                # Mengambil semua ops.report yang terkait dengan partner
                ops_report = self.env["ops.report"].search([('customer', '=', partner.id)])
                # Membuat list untuk menyimpan semua ops.report.id
                ops_report_ids = ops_report.ids  # Mendapatkan semua id dari ops.report yang terkait

                # Mengambil semua ops.report yang terkait dengan partner
                ops_review = self.env["ops.review"].search([('nama_customer', '=', partner.id)])
                # Membuat list untuk menyimpan semua ops.review.id
                ops_review_ids = ops_review.ids  # Mendapatkan semua id dari ops.report yang terkait
                
                # Mengambil semua ops.sertifikat yang terkait dengan partner
                ops_sertifikat = self.env["ops.sertifikat"].search([('nama_customer', '=', partner.id)])
                # Membuat list untuk menyimpan semua ops.sertifikat.id
                ops_sertifikat_ids = ops_sertifikat.ids  # Mendapatkan semua id dari ops.sertifikat yang terkait
                for sale_order in self.env["sale.order"].search([('partner_id', '=', partner.id)]):
                    # Cari qc.pass.iso berdasarkan referensi ISO dari tsi.iso, bukan berdasarkan customer
                    existing_qc_pass_iso = self.env['qc.pass.iso'].search([
                        ('audit_request_iso', 'in', audit_request_ids),  # Pencarian berdasarkan application_review_ids
                        ('sale_order_id', '=', sale_order.id),  # Pencarian berdasarkan sale_order_id
                        ('program_id', 'in', ops_program_ids),
                        ('plan_id', 'in', ops_plan_ids),
                        ('report_id', 'in', ops_report_ids),
                        ('review_id', 'in', ops_review_ids),
                        ('sertifikat_id', 'in', ops_sertifikat_ids),
                    ])
                    
                    if existing_qc_pass_iso:
                        # Jika sudah ada, lakukan update
                        existing_qc_pass_iso.write({
                            "customer": partner.id,  # Update customer
                            "audit_request_iso": [(6, 0, audit_request_ids)],  # Menambahkan banyak iso_review_id yang terhubung
                            "sale_order_id": sale_order.id,  # Set sale_order_id yang terhubung
                            "program_id": [(6, 0, ops_program_ids)],
                            "plan_id": [(6, 0, ops_plan_ids)],
                            "report_id": [(6, 0, ops_report_ids)],
                            "review_id": [(6, 0, ops_review_ids)],
                            "sertifikat_id": [(6, 0, ops_sertifikat_ids)],
                        })
                    else:
                        # Jika belum ada, buat data baru
                        self.env['qc.pass.iso.surveillance'].create({
                            "customer": partner.id,  # Set customer
                            "audit_request_iso": [(6, 0, audit_request_ids)],  # Menambahkan banyak iso_review_id yang terhubung
                            "sale_order_id": sale_order.id,  # Set sale_order_id yang terhubung
                            "program_id": [(6, 0, ops_program_ids)],
                            "plan_id": [(6, 0, ops_plan_ids)],
                            "report_id": [(6, 0, ops_report_ids)],
                            "review_id": [(6, 0, ops_review_ids)],
                            "sertifikat_id": [(6, 0, ops_sertifikat_ids)],
                        })

class QCPassISPOSurveillance(models.Model):
    _name = 'qc.pass.ispo.surveillance'
    _description = 'Quality Controll Pass ISPO Surveillance'
    _inherit        = ['mail.thread', 'mail.activity.mixin']
    _rec_name       = 'customer'
    _order          = 'id DESC'
    
    customer        = fields.Many2one('res.partner', string="Company Name", domain="[('is_company', '=', True)]")
    audit_request_ispo = fields.Many2many('tsi.audit.request', string="Audit Request")
    audit_request_ispo_reference_check = fields.Boolean(string="QC Pass Key")
    audit_request_noted_iso = fields.Text('QC Noted ISO')
    sale_order_id = fields.Many2one('sale.order', string="Sale Order")
    sale_order_check = fields.Boolean(string="QC Pass Key")
    noted_iso_sales = fields.Text('QC Noted Sales')
    program_ispo_id = fields.Many2many('ops.program', string="OPS Program")
    program_check = fields.Boolean(string="QC Pass Key")
    noted_iso_program = fields.Text('QC Noted Ops Program')
    plan_ispo_id = fields.Many2many('ops.plan', string="OPS Plan")
    plan_check = fields.Boolean(string="QC Pass Key")
    noted_iso_plan = fields.Text('QC Noted Ops Plan')
    report_ispo_id = fields.Many2many('ops.report', string="OPS Report")
    report_check = fields.Boolean(string="QC Pass Key")
    noted_iso_report = fields.Text('QC Noted Ops Report')
    review_ispo_id = fields.Many2many('ops.review', string="OPS Reccomendation")
    review_check = fields.Boolean(string="QC Pass Key")
    noted_iso_ops_review = fields.Text('QC Noted Ops Review')
    sertifikat_ispo_id = fields.Many2many('ops.sertifikat', string="OPS Sertifikat")
    sertifikat_check = fields.Boolean(string="QC Pass Key")
    noted_iso_sertifikat = fields.Text('QC Noted Ops Sertifikat')

    @api.model
    def load_views(self, views, options=None):
        self.create_ows_on_open()
        return super(QCPassISPOSurveillance, self).load_views(views, options)
    
    def create_ows_on_open(self):
        partners = self.env['res.partner'].search([("is_company", "=", True)])

        for partner in partners:
            # Mencari data ISO berdasarkan customer (partner.id) dari model tsi.iso
            for audit_request_ispo in self.env["tsi.audit.request.ispo"].search([('partner_id', '=', partner.id)]):
                # Membuat list untuk menyimpan semua iso_review.id
                audit_request_ispo_ids = audit_request_ispo.ids  # Mendapatkan semua id dari iso_review yang terkait

                # Mengambil semua ops.program yang terkait dengan partner
                ops_program_ispo = self.env["ops.program.ispo"].search([('customer', '=', partner.id)])
                # Membuat list untuk menyimpan semua ops.program.id
                ops_program_ispo_ids = ops_program_ispo.ids  # Mendapatkan semua id dari ops.program yang terkait

                # Mengambil semua ops.plan yang terkait dengan partner
                ops_plan_ispo = self.env["ops.plan.ispo"].search([('customer', '=', partner.id)])
                # Membuat list untuk menyimpan semua ops.plan.id
                ops_plan_ispo_ids = ops_plan_ispo.ids  # Mendapatkan semua id dari ops.program yang terkait

                # Mengambil semua ops.report yang terkait dengan partner
                ops_report_ispo = self.env["ops.report.ispo"].search([('customer', '=', partner.id)])
                # Membuat list untuk menyimpan semua ops.report.id
                ops_report_ispo_ids = ops_report_ispo.ids  # Mendapatkan semua id dari ops.report yang terkait

                # Mengambil semua ops.report yang terkait dengan partner
                ops_review_ispo = self.env["ops.review.ispo"].search([('nama_customer', '=', partner.id)])
                # Membuat list untuk menyimpan semua ops.review.id
                ops_review_ispo_ids = ops_review_ispo.ids  # Mendapatkan semua id dari ops.report yang terkait
                
                # Mengambil semua ops.sertifikat yang terkait dengan partner
                ops_sertifikat_ispo = self.env["ops.sertifikat.ispo"].search([('nama_customer', '=', partner.id)])
                # Membuat list untuk menyimpan semua ops.sertifikat.id
                ops_sertifikat_ispo_ids = ops_sertifikat_ispo.ids  # Mendapatkan semua id dari ops.sertifikat yang terkait
                for sale_order in self.env["sale.order"].search([('partner_id', '=', partner.id)]):
                    # Cari qc.pass.iso berdasarkan referensi ISO dari tsi.iso, bukan berdasarkan customer
                    existing_qc_pass_iso = self.env['qc.pass.iso'].search([
                        ('audit_request_ispo', 'in', audit_request_ispo_ids),  # Pencarian berdasarkan application_review_ids
                        ('sale_order_id', '=', sale_order.id),  # Pencarian berdasarkan sale_order_id
                        ('program_ispo_id', 'in', ops_program_ispo_ids),
                        ('plan_ispo_id', 'in', ops_plan_ispo_ids),
                        ('report_ispo_id', 'in', ops_report_ispo_ids),
                        ('review_ispo_id', 'in', ops_review_ispo_ids),
                        ('sertifikat_ispo_id', 'in', ops_sertifikat_ispo_ids),
                    ])
                    
                    if existing_qc_pass_iso:
                        # Jika sudah ada, lakukan update
                        existing_qc_pass_iso.write({
                            "customer": partner.id,  # Update customer
                            "audit_request_ispo": [(6, 0, audit_request_ispo_ids)],  # Menambahkan banyak iso_review_id yang terhubung
                            "sale_order_id": sale_order.id,  # Set sale_order_id yang terhubung
                            "program_ispo_id": [(6, 0, ops_program_ispo_ids)],
                            "plan_ispo_id": [(6, 0, ops_plan_ispo_ids)],
                            "report_ispo_id": [(6, 0, ops_report_ispo_ids)],
                            "review_ispo_id": [(6, 0, ops_review_ispo_ids)],
                            "sertifikat_ispo_id": [(6, 0, ops_sertifikat_ispo_ids)],
                        })
                    else:
                        # Jika belum ada, buat data baru
                        self.env['qc.pass.iso.surveillance'].create({
                            "customer": partner.id,  # Set customer
                            "audit_request_ispo": [(6, 0, audit_request_ispo_ids)],  # Menambahkan banyak iso_review_id yang terhubung
                            "sale_order_id": sale_order.id,  # Set sale_order_id yang terhubung
                            "program_ispo_id": [(6, 0, ops_program_ispo_ids)],
                            "plan_ispo_id": [(6, 0, ops_plan_ispo_ids)],
                            "report_ispo_id": [(6, 0, ops_report_ispo_ids)],
                            "review_ispo_id": [(6, 0, ops_review_ispo_ids)],
                            "sertifikat_ispo_id": [(6, 0, ops_sertifikat_ispo_ids)],
                        })