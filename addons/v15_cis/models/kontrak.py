from odoo import models, fields, api

class Kontrak(models.Model):
    _name           = "cis.kontrak"
    _inherit        = ['mail.thread', 'mail.activity.mixin']
    _description    = "Kontrak"

    name            = fields.Char( required=True, string="Name",  help="")
    description     = fields.Text( string="Deskripsi",  help="")
    customer        = fields.Many2one('res.partner', string="Customer", domain="[('is_company', '=', True)]")
    from_date       = fields.Date(default=fields.Date.today, string="From Date", required='true')
    to_date         = fields.Date(string="To Date", required='true')
    pic             = fields.Many2one('hr.employee', string="PIC")
    user_contact    = fields.Many2one('res.partner', string="Customer Contact", domain="[('parent_id', '=', customer)]")
    count_report    = fields.Integer(string='Count Report', default=0, compute="_compute_state")
    count_order     = fields.Integer(string='Count Order',  default=0, compute="_compute_state")
    count_patrol    = fields.Integer(string='Count Patrol', default=0, compute="_compute_state")
    state           = fields.Selection([
                            ('draft',   'Draft'),
                            ('running', 'Running'),
                            ('closed',  'Closed'),
                        ], string='Status', readonly=True, copy=False, index=True, tracking=True, default='draft')
    client_tag_type = fields.Selection([
                            ('barcode',   'Barcode'),
                            ('qrcode', 'QR Code'),
                            ('nfc',  'NFC Tag'),
                            ('rfid',  'RFID Tag'),
                        ], string='Tag Type', index=True)
    contract_type   = fields.Selection([
                            ('security',    'Security Service'),
                            ('cleaning',    'Cleaning Services'),
                        ], string='Contract Type', index=True)
    pic_lines       = fields.One2many('cis.petugas', 'kontrak_id', string="Petugas")
    check_lines     = fields.One2many('cis.checkpoint', 'kontrak_id', string="Checkpoint")
    activity_lines  = fields.One2many('cis.activity', 'kontrak_id', string="Activity")

    def _compute_state(self):
        for obj in self:
            obj.count_report = self.env['msg.report'].search_count([('project_name.id', '=', obj.id)])
            obj.count_order  = self.env['msg.order'].search_count([('project_name.id', '=', obj.id)])
            obj.count_patrol = self.env['msg.checkin'].search_count([('project_name.id', '=', obj.id)])

    def set_to_running(self):
        self.write({'state': 'running'})            
        return True

    def set_to_closed(self):
        self.write({'state': 'closed'})            
        return True

    def set_to_draft(self):
        self.write({'state': 'draft'})            
        return True

class Petugas(models.Model):
    _name           = 'cis.petugas'
    _description    = 'Petugas'
    _rec_name       = 'petugas'

    kontrak_id    = fields.Many2one('cis.kontrak', ondelete='cascade', string="Kontrak", )
    partner_id      = fields.Many2one('res.partner', string="Partner")
    petugas         = fields.Many2one('res.partner', string="Petugas", domain="[('parent_id', '=', partner_id)]")
    posisi          = fields.Selection([
                            ('petugas', 'Petugas'),
                            ('komandan', 'Komandan regu'),
                        ], string='Posisi')
    aktif           = fields.Selection([
                            ('aktif', 'Aktif'),
                            ('inaktif', 'Inaktif'),
                        ], string='Aktif')

class Checkpoint(models.Model):
    _name           = 'cis.checkpoint'
    _description    = 'Checkpoint'
    _rec_name       = 'lokasi'

    kontrak_id  = fields.Many2one('cis.kontrak', string="Kontrak", ondelete='cascade')
    object_ssid     = fields.Char(string='SSID')
    lokasi          = fields.Char(string='Lokasi') 
    keterangan      = fields.Text(string='Keterangan') 
    aktif           = fields.Selection([
                            ('aktif', 'Aktif'),
                            ('inaktif', 'Inaktif'),
                        ], string='Aktif')

class Activity(models.Model):
    _name           = 'cis.activity'
    _description    = 'Activity'

    kontrak_id      = fields.Many2one('cis.kontrak', string="Kontrak", ondelete='cascade')
    name            = fields.Char(string='Name')
    keterangan      = fields.Text(string='Keterangan') 
    aktif           = fields.Selection([
                            ('aktif', 'Aktif'),
                            ('inaktif', 'Inaktif'),
                        ], string='Aktif')                        