from odoo import models, fields, api, SUPERUSER_ID, _

class SertifikatDelivery(models.Model):
    _name           = 'sertifikat.delivery'
    _description    = 'Sertifikat Delivery'
    _order          = 'id DESC'

    name            = fields.Char(string='Document No')
    iso_reference   = fields.Many2one('tsi.iso', string="Reference")    
    criteria        = fields.Char(string='Criteria')
    objectives      = fields.Text(string='Objectives')
    iso_standard_ids    = fields.Many2many('tsi.iso.standard', string='Standards')
    sales_order_id      = fields.Many2one('sale.order', string="Sales Order",  readonly=True)    
    notification_id = fields.Many2one('audit.notification', string="Notification")    

    sertifikat_summary  = fields.One2many('ops.sertifikat_summary', 'sertifikat_id', string="Plan", index=True)
    state           = fields.Selection([
                            ('new',     'New'),
                            ('confirm', 'Confirm'),
                            ('done',    'Done')
                        ], string='Status', readonly=True, copy=False, index=True, default='new')


    @api.model
    def create(self, vals):
        sequence = self.env['ir.sequence'].next_by_code('sertifikat.delivery')
        vals['name'] = sequence or _('New')
        result = super(SertifikatDelivery, self).create(vals)
        return result

    def set_to_confirm(self):
        self.write({'state': 'confirm'})            
        return True

    def set_to_done(self):
        self.write({'state': 'done'})            
        return True

    def set_to_draft(self):
        self.write({'state': 'new'})            
        return True

class AuditSertifikatDetail(models.Model):
    _name           = 'ops.sertifikat_summary'
    _description    = 'Audit Sertifikat Summary'

    sertifikat_id       = fields.Many2one('ops.sertifikat', string="Sertifikat", ondelete='cascade', index=True)
    summary         = fields.Char(string='Summary')
    status          = fields.Char(string='Status')
