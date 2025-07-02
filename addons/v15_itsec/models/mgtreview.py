# -*- coding: utf-8 -*-

from odoo import models, fields, api
from datetime import datetime

# Notulen
class mgt_notulen(models.Model):
    _name           = 'mgt.notulen'
    _inherit        = 'mail.thread'
    _description    = 'Notulen'
    _rec_name       = 'nomor'
    nomor           = fields.Char(required=True, string="Nomor")
    tanggal         = fields.Date(default=datetime.today(), string="tanggal")
    agenda          = fields.Text(string="Agenda")
    file_bin        = fields.Binary('Attachment')
    file_name       = fields.Char('Filename')

# Undangan
class mgt_undangan(models.Model):
    _name           = 'mgt.undangan'
    _inherit        = 'mail.thread'
    _description    = 'Invitation'
    _rec_name       = 'nomor'
    nomor           = fields.Char(required=True, string="Nomor")
    att_list        = fields.Many2many('hr.employee', ondelete='cascade', string="Auditee", required=True)
    att_email       = fields.Text(string="Email")
    tanggal         = fields.Date(default=datetime.today(), string="Tanggal")
    waktu           = fields.Char(string="Waktu")
    location        = fields.Char(string="Location")
    agenda          = fields.Text(string="Agenda")

# Report
class mgt_mgtreport(models.Model):
    _name           = 'mgt.mgtreport'
    _inherit        = 'mail.thread'
    _description    = 'Management Report'
    _rec_name       = 'period'
    period          = fields.Char(required=True, string="Period")
    date_review     = fields.Date(default=datetime.today(), string="Date")
    qms_input       = fields.Char(string="Input")
    qms_output      = fields.Char(string="Output")
    recommendation  = fields.Text(required=True, string="Recommendation")
    status          = fields.Selection(selection=[('Open', 'Open'),('Close', 'Close')], required=True, string="Status")
    # action_plan    = fields.Many2one('qms_software.objective', ondelete='cascade', string="Action Plan")
    file_bin        = fields.Binary('Attachment')
    file_name       = fields.Char('Filename')
