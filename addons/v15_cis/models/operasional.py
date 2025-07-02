from odoo import models, fields, api

class Incident(models.Model):
    _name           = "cis.incident"
    _inherit        = ['mail.thread', 'mail.activity.mixin']
    _description    = "Incident"

    project_name    = fields.Many2one('cis.kontrak', string="Project",)
    name            = fields.Char( required=True, string="Name",  help="")
    description     = fields.Text( string="Deskripsi",  help="")
    file_bin        = fields.Binary('Attachment')
    file_name       = fields.Char('Filename')
    state           = fields.Selection([
                            ('new',   'New'),
                            ('process', 'Process'),
                            ('done',  'Done'),
                        ], string='Status', readonly=True, copy=False, index=True, tracking=True, default='new')

    def set_to_process(self):
        self.write({'state': 'process'})            
        return True

    def set_to_done(self):
        self.write({'state': 'done'})            
        return True

    def set_to_new(self):
        self.write({'state': 'new'})            
        return True

class TapScan(models.Model):
    _name           = 'cis.tapscan'
    _description    = 'Tapscan'
    _rec_name       = 'object_ssid'
    _order          = "tap_date desc"

    project_name    = fields.Many2one('cis.kontrak', string="Project",)
    object_ssid     = fields.Char(string='SSID')
    description     = fields.Text(string='Description')
    tap_date        = fields.Datetime(default=lambda self: fields.datetime.now(), string="Date")
    file_bin        = fields.Binary('Attachment')
    file_name       = fields.Char('Filename')        

class JobOrder(models.Model):
    _name           = 'cis.job_order'
    _description    = 'Job Order'
    _inherit        = 'mail.thread'

    project_name    = fields.Many2one('cis.kontrak', string="Project",)
    name            = fields.Char(string='Title',)
    description     = fields.Text(string='Description',)
    file_bin        = fields.Binary('Attachment')
    file_name       = fields.Char('Filename',)
    state           = fields.Selection([
                            ('new',   'New'),
                            ('process', 'Process'),
                            ('done',  'Done'),
                        ], string='Status', readonly=True, copy=False, index=True, tracking=True, default='new')

    def set_to_process(self):
        self.write({'state': 'process'})            
        return True

    def set_to_done(self):
        self.write({'state': 'done'})            
        return True

    def set_to_new(self):
        self.write({'state': 'new'})            
        return True

class CleaningActivity(models.Model):
    _name           = 'cis.cleaning_activity'
    _description    = 'Cleaning Activity'
    _rec_name       = 'activity_id'
    _order          = 'activity_date desc'

    project_name    = fields.Many2one('cis.kontrak', string="Project",)
    object_ssid     = fields.Char(string='SSID')
    activity_id     = fields.Many2one('cis.activity', string="Activity", required=True)
    description     = fields.Text(string='Description')
    activity_date   = fields.Datetime(default=lambda self: fields.datetime.now(), string="Date")
    pic_before      = fields.Binary('Before')
    pic_progress    = fields.Binary('On Progress')
    pic_after       = fields.Binary('After')
