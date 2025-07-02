# -*- coding: utf-8 -*-
from odoo import models, fields, api
from datetime import datetime

class assets_register(models.Model):
    _name           = 'assets.register'
    _inherit        = 'mail.thread'
    _description    = 'Assets Register'
    _rec_name       = 'name'

    doc_no          = fields.Char(string="Nomor Formulir")
    rev_no          = fields.Char(string="Revisi")
    tanggal         = fields.Date(default=datetime.today(), string="Tanggal")
    klasifikasi     = fields.Char(string="Klasifikasi")

    kode            = fields.Char(string="Kode", required=True)
    layanan         = fields.Char(string="Layanan", required=True)
    name            = fields.Char(string="Nama Asset", required=True)
    sub_klasifikasi = fields.Char(string="Sub Klasifikasi", required=True)
    pemilik         = fields.Char(string="Pemilik", required=True)
    pemegang        = fields.Char(string="Pemegang", required=True)
    lokasi          = fields.Char(string="Lokasi")
    masa_berlaku    = fields.Char(string="Masa Berlaku")
    metode          = fields.Char(string="Metode Penghapusan")
    
    confidentiality = fields.Integer(string="Confidentiality", required=True)
    integrity       = fields.Integer(string="Integrity", required=True)
    availability    = fields.Integer(string="Availability", required=True)
    value           = fields.Float(string="Value", compute='_calc_value', readonly=True)
    keterangan      = fields.Text(string="Keterangan", required=True)

    @api.depends('confidentiality', 'integrity', 'availability')
    def _calc_value(self):
        for r in self:
            r.value = ( r.confidentiality + r.integrity + r.availability ) / 3

class access(models.Model):
    _name           = 'assets.access'
    _inherit        = 'mail.thread'
    _description    = 'Access Matrix'
    _rec_name       = 'unit_kerja'

    unit_kerja      = fields.Char(string="Unit Kerja", required=True)
    sub_unit_kerja  = fields.Char(string="Sub Unit Kerja", required=True)
    user_level      = fields.Char(string="User Level", required=True)
    role            = fields.Char(string="Role")

    access_line     = fields.One2many('assets.access_line', 'access_line_id', string='Access')
    pegawai_line    = fields.Many2many('hr.employee', ondelete='cascade', string="Nama Pegawai")

class access_line(models.Model):
    _name           = 'assets.access_line'
    _description    = 'Risk Klasifikasi Line'
    access_line_id  = fields.Many2one('assets.access', ondelete='cascade')
    access_name     = fields.Many2one('assets.def_asset', ondelete='cascade')
    # nama            = fields.Char(string="Access Name")
    access_c        = fields.Boolean(string="Create")
    access_r        = fields.Boolean(string="Read")
    access_u        = fields.Boolean(string="Update")
    access_d        = fields.Boolean(string="Delete")
    access_r_1      = fields.Boolean(string="Restrict")

class def_asset(models.Model):
    _name           = 'assets.def_asset'
    _description    = 'Asset'
    _rec_name       = 'name'

    name            = fields.Char(string="Nama", required=True)
