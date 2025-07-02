from odoo import models, fields, api

class Tender(models.Model):
    _name           = 'tad.tender'
    _inherit        = ['mail.thread', 'mail.activity.mixin']
    _description    = 'Tender'

    name            = fields.Char( required=True, string="Name",  help="")
    description     = fields.Text( string="Deskripsi",  help="")
    customer        = fields.Many2one('res.partner', string="Customer", domain="[('is_company', '=', True)]")
    from_date       = fields.Date(default=fields.Date.today, string="From Date", required='true')
    to_date         = fields.Date(string="To Date", required='true')
    pic             = fields.Many2one('hr.employee', string="PIC")
    user_contact    = fields.Many2one('res.partner', string="User Contact", domain="[('parent_id', '=', customer)]")
    state           = fields.Selection([
                            ('draft',   'Draft'),
                            ('running', 'Running'),
                            ('closed',  'Closed'),
                        ], string='Status', readonly=True, copy=False, index=True, tracking=True, default='draft')
    jadwal_lines    = fields.One2many('tad.jadwal', 'tender_id', string="Jadwal")
    lampiran_lines  = fields.One2many('tad.lampiran', 'tender_id', string="Lampiran")

    def set_to_running(self):
        self.write({'state': 'running'})            
        return True

    def set_to_closed(self):
        self.write({'state': 'closed'})            
        return True

    def set_to_draft(self):
        self.write({'state': 'draft'})            
        return True


class Jadwal(models.Model):
    _name           = 'tad.jadwal'
    _description    = 'Petugas'

    tender_id       = fields.Many2one('tad.tender', ondelete='cascade', string="Tender", )
    name            = fields.Char(string="Kegiatan")
    from_date       = fields.Date(string="From Date")
    to_date         = fields.Date(string="To Date")

class Lampiran(models.Model):
    _name           = 'tad.lampiran'
    _description    = 'Lampiran'

    tender_id       = fields.Many2one('tad.tender', ondelete='cascade', string="Tender", )
    name            = fields.Char(string="Judul")
    file_bin        = fields.Binary('Attachment')
    file_name       = fields.Char('Filename')

