from odoo import models, fields, api
from datetime import datetime

class incident_cat(models.Model):
    _name = 'incident.incident_cat'
    _inherit        = 'mail.thread'
    _description    = 'Category'
    name            = fields.Char(required=True, string="Name")
    description     = fields.Text(string="Description")

# Incident Report
class incident(models.Model):
    _name = 'incident.incident'
    _inherit        = 'mail.thread'
    _description    = 'Incident'
    name            = fields.Char(required=True, string="Name")
    kpi_what        = fields.Char(string="What")
    kpi_who         = fields.Char(string="Who")
    kpi_when        = fields.Char(string="When")
    kpi_how         = fields.Text(string="How")
    kpi_resource    = fields.Char(string="Resource")
    kpi_status      = fields.Selection(selection=[('Open', 'Open'),('Close', 'Close')], required=True, string="Status")
    file_bin        = fields.Binary('Attachment')
    file_name       = fields.Char('Filename')
    category        = fields.Many2one('incident.incident_cat', ondelete='cascade', string="Category")

class nonconform(models.Model):
    _name           = 'incident.nonconform'
    _inherit        = 'mail.thread'
    _description    = 'Noconformities'
    _rec_name       = 'nomor'
    nomor           = fields.Char(required=True, string="Nomor")
    tanggal         = fields.Date(default=datetime.today(), string="Tanggal")
    auditor_id      = fields.Many2one('hr.employee', ondelete='cascade', string="Auditor", required=True)
    auditee_id      = fields.Many2one('hr.employee', ondelete='cascade', string="Auditee", required=True)
    kategori        = fields.Selection(selection=[('Major', 'Major'),('Minor', 'Minor'),('Observasi', 'Observasi')], string="Category")
    kriteria        = fields.Char(required=True, string="Criteri")
    identifikasi    = fields.Text(required=True, string="Identification")
    analisa         = fields.Text(required=True, string="Analisa")
    close_date      = fields.Date(default=datetime.today(), string='Close Date')
