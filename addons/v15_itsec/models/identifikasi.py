# -*- coding: utf-8 -*-
from odoo import models, fields, api
from datetime import datetime

class ident_identifikasi(models.Model):
    _name           = 'ident.identifikasi'
    _inherit        = 'mail.thread'
    _description    = 'Identifikasi'
    _rec_name       = 'nomor_dokumen'

    nomor_dokumen   = fields.Char(string="No Dokumen", required=True)
    nomor_revisi    = fields.Char(string="No Revisi", required=True)
    berlaku_mulai   = fields.Date(string="Berlaku Mulai")
    tahun           = fields.Char(string="Tahun", required=True)
    ident_line      = fields.One2many('ident.ident_line', 'ident_line_id', string='Identifikasi')

class ident_line(models.Model):
    _name           = 'ident.ident_line'
    _description    = 'Identifikasi Line'
    ident_line_id   = fields.Many2one('ident.identifikasi', ondelete='cascade')
    peraturan       = fields.Char(string="Peraturan", required=True)
    tentang         = fields.Text(string="Tentang", required=True)
    fungsi_terkait  = fields.Char(string="Fungsi Terkait", required=True)
    kepatuhan       = fields.Selection(selection=[('ya', 'Ya'),('tidak', 'Tidak')], string="Kepatuhan", required=True)
    tindak_lanjut   = fields.Text(string="Tindak Lanjut")
