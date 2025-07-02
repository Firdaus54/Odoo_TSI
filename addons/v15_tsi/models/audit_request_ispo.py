from odoo import models, fields, api

class AuditRequestISPO(models.Model):
    _name           = 'tsi.audit.request.ispo'
    _description    = 'Audit Request'
    _inherit        = ['mail.thread', 'mail.activity.mixin']
    _order          = 'id DESC'

    name            = fields.Char(string="Document No",  readonly=True)
    audit_stage = fields.Selection([
                            ('surveilance1',     'Surveilance 1'),
                            ('surveilance2',     'Surveilance 2'),
                            ('surveilance3',     'Surveilance 3'),
                            ('surveilance4',     'Surveilance 4'),
                            ('recertification', 'Recertification'),
                        ], string='Audit Stage')

    iso_standard_ids    = fields.Many2many('tsi.iso.standard', string='Standards', readonly=True)

    partner_id          = fields.Many2one('res.partner', 'Company Name', readonly=True)
    invoicing_address   = fields.Char(string="Invoicing Address", )
    office_address      = fields.Char(string='Office Address')
    telp                = fields.Char(string='Telp')
    email               = fields.Char(string='Email')
    website             = fields.Char(string='Website')
    cellular            = fields.Char(string='Cellular')
    scope               = fields.Char(string='Scope')
    boundaries  = fields.Char(string="Boundaries")  
    number_site         = fields.Char(string='Number of Site')
    total_emp           = fields.Char(string='Total Employee')
    tipe_pembayaran     = fields.Selection([
                            ('termin',     'Termin'),
                            ('lunasawal',     'Lunas Di Awal'),
                            ('lunasakhir', 'Lunas Di Akhir'),
                        ], string='Tipe Pembayaran',)
    mandays             = fields.Char(string='Mandays')
    no_kontrak          = fields.Char(string='Nomor Kontrak')
    iso_reference       = fields.Many2one('tsi.iso', string="Application Form", readonly=True)
    sales_reference     = fields.Many2one('sale.order', string="Sales Reference", readonly=True)
    review_reference    = fields.Many2many('tsi.iso.review', string="Review Reference", readonly=True)
    crm_reference       = fields.Many2one('tsi.crm', string="CRM Reference", readonly=True)
    lines_audit_request_ispo = fields.One2many('audit_request_ispo.line', 'reference_id', string='Audit Lines')
    state           =fields.Selection([
                            ('request',         'Request'),
                            ('reject',          'Reject'),
                            ('approve',         'Approve'),
                            ('approve_so',      'Approve SO'),
                            ('approve_quot',    'Approve Quotation'),
                        ], string='Status', readonly=True, copy=False, index=True, tracking=True, default='request')
    is_amendment = fields.Boolean(string="Is Amendment Contract?")
    contract_type = fields.Selection([
        ('new', 'New Contract'),
        ('amendment', 'Amandement Contract'),
    ], string="Contract Type", help="Select the type of contract",)

    @api.model
    def create(self, vals):
        sequence = self.env['ir.sequence'].next_by_code('tsi.audit.request.ispo')
        vals['name'] = sequence or _('New')
        result = super(AuditRequestISPO, self).create(vals)
        return result

    def set_reject(self):
        self.write({'state': 'reject'})            
        return True

    def set_request(self):
        self.write({'state': 'request'})            
        return True

    def set_approve(self):
        self.write({'state': 'approve'})            
        return True

    def create_sales(self):
        self.write({'state': 'approve_quot'})            

        return {
            'name': "Create Quotation",
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'tsi.wizard_audit_quotation',
            'view_id': self.env.ref('v15_tsi.tsi_wizard_audit_quotation_view').id,
            'target': 'new'
        }

    def create_quot(self):
        self.write({'state': 'approve_so'})            
        return {
            'name': "Create Quotation",
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'tsi.wizard_audit_quotation',
            'view_id': self.env.ref('v15_tsi.tsi_wizard_audit_quotation_view').id,
            'target': 'new'
        }
    
    def create_quotation(self):
        return {
            'name': "Create Quotation",
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'tsi.wizard_audit_request',
            'view_id': self.env.ref('v15_tsi.tsi_wizard_audit_request_view').id,
            'target': 'new'
        }

    def generate_ops(self):
        
        sale_order = self.env['sale.order'].create({
            'partner_id': self.partner_id.id,
            'iso_reference': self.iso_reference.id,
            'application_review_iso_ids': [(6, 0, self.review_reference.ids)],
            'iso_standard_ids': [(6, 0, self.iso_standard_ids.ids)],
            'contract_type': self.contract_type,
            'nomor_kontrak': self.no_kontrak,  # Mengisi nomor_kontrak
            'nomor_quotation': self.no_kontrak,  # Mengisi nomor_quotation
            # 'tipe_pembayaran': self.tipe_pembayaran,
            # 'template_quotation': self.template_quotation,
            # 'dokumen_sosialisasi': self.dokumen_sosialisasi,
            # 'file_name': self.file_name,
            # 'file_name1': self.file_name1,
        })

        for line in self.lines_audit_request:
            product = line.product_id  
            
            self.env['sale.order.line'].create({
                'order_id': sale_order.id,  
                'product_id': product.id if product else False, 
                'audit_tahapan': line.audit_tahapan,
                'tahun': line.tahun,
                'price_unit': line.price,
            })

        # for line in self.lines_audit_request:
        #     self.env['tsi.order.options'].create({
        #         'ordered_id': sale_order.id,
        #         # 'product_id': line.product_id.id,
        #         'audit_tahapans': line.audit_tahapan,
        #         'tahun_audit': line.tahun,
        #         'price_units': line.price,
        #         # 'product_uom_qty': 1.0,  
        #         # 'tax_id': [(6, 0, line.product_id.taxes_id.ids)] 
        #     })

        # sale_order.action_confirm()

        sale_order.write({'state': 'sent'}) 

        return True

class AuditRequestISPOLines(models.Model):
    _name         = 'audit_request_ispo.line'
    _description  = 'Audit Request Line'
    _inherit      = ['mail.thread', 'mail.activity.mixin']

    reference_id  = fields.Many2one('tsi.audit.request.ispo', string="Reference")
    product_id    = fields.Many2one('product.product', string='Product')
    audit_tahapan = fields.Selection([
                            ('Initial Audit',         'Initial Audit'),
                            ('Surveillance 1', 'Surveillance 1'),
                            ('Surveillance 2', 'Surveillance 2'),
                            ('Recertefication', 'Recertefication'),],
                            string='Audit Stage', index=True, tracking=True)
    price         = fields.Float(string='Price')
    tahun         = fields.Char("Tahun", tracking=True)
    fee = fields.Float(string='Fee')
    percentage = fields.Float(string='Percentage', compute='_compute_percentage', store=True)

    @api.depends('price', 'fee')
    def _compute_percentage(self):
        for record in self:
            if record.price > 0:
                record.percentage = (record.fee / record.price) * 100
            else:
                record.percentage = 0
