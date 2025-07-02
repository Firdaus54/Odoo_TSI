# -*- coding: utf-8 -*-
from odoo import models, fields, api
from datetime import datetime

class kinerja_kinerja(models.Model):
    _name           = 'kinerja.kinerja'
    _inherit        = 'mail.thread'
    _description    = 'Kinerja'
    _rec_name       = 'nomor_dokumen'

    nomor_dokumen   = fields.Char(string="No Dokumen", required=True)
    subject         = fields.Char(string="Subject")
    nomor_revisi    = fields.Char(string="No Revisi", required=True)
    berlaku_mulai   = fields.Date(string="Tanggal")
    dibuat          = fields.Char(string="Dibuat Oleh", required=True)
    diperiksa       = fields.Char(string="Diperiksa Oleh", required=True)
    disetujui       = fields.Char(string="Disetujui Oleh", required=True)
    kinerja_line    = fields.One2many('kinerja.kinerja_line', 'kinerja_line_id', string='Kinerja')

class kinerja_line(models.Model):
    _name           = 'kinerja.kinerja_line'
    _description    = 'Kinerja Line'

    kinerja_line_id = fields.Many2one('kinerja.kinerja', ondelete='cascade')
    department      = fields.Char(string="Departemen", required=True)
    tolok_ukur      = fields.Char(string="Tolok Ukur", required=True)
    supporting      = fields.Char(string="Supporting Data")
    metode          = fields.Char(string="Metode Perhitungan")
    periode         = fields.Char(string="Periode")
    target          = fields.Char(string="Target") 
    action          = fields.Text(string="Action Plan")
    pic             = fields.Char(string="PIC")
    target          = fields.Integer(string="Target")
    actual          = fields.Integer(string="Actual")

# Planning
class planning(models.Model):
    _name = 'kinerja.planning'
    _inherit        = 'mail.thread'
    _description    = 'Planning'
    name            = fields.Char(required=True)
    dep_name        = fields.Many2one('hr.department', ondelete='cascade', string="Auditee", required=True)
    kpi_what        = fields.Char(string="What")
    kpi_who         = fields.Char(string="Who")
    kpi_when        = fields.Char(string="When")
    kpi_how         = fields.Text(string="How")
    kpi_resource    = fields.Char(string="Resource")
    kpi_input       = fields.Text(string="Input")
    kpi_output      = fields.Char(string="Output")
    file_bin        = fields.Binary('Attachment')
    file_name       = fields.Char('Filename')

# Monitoring
class monitoring(models.Model):
    _name = 'kinerja.monitoring'
    _inherit        = 'mail.thread'
    _description    = 'Monitoring'
    _rec_name       = 'dep_name'
    dep_name        = fields.Many2one('hr.department', ondelete='cascade', string="Department", required=True)
    month           = fields.Char(string="month")
    objective_id    = fields.Many2one('kinerja.planning', ondelete='cascade', string="Objective", required=True)
    result          = fields.Text(string="result")
    corrective      = fields.Text(string="corrective")
    pic_kpi         = fields.Many2one('hr.employee', ondelete='cascade', string="Auditor")
    kpi_status      = fields.Selection(selection=[('Open', 'Open'),('Close', 'Close')])
