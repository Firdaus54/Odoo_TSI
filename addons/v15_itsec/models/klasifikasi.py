# -*- coding: utf-8 -*-
from odoo import models, fields, api
from datetime import datetime

class klas_matrix(models.Model):
    _name           = 'klas.matrix'
    _description    = 'Matrix Klasifikasi'
    _inherit        = 'mail.thread'

    name            = fields.Char(string="Klasifikasi", required=True)
    description     = fields.Text(string="Keterangan", required=True)

class klas_pic(models.Model):
    _name           = 'klas.pic'
    _inherit        = 'mail.thread'
    _description    = 'Penanggung Jawab'
    _rec_name       = 'klasifikasi'

    klasifikasi     = fields.Many2one('klas.matrix', ondelete='cascade', string="Klasifikasi", required=True)
    jenis_informasi = fields.Text(string="Jenis Informasi", required=True)
    pic_nama        = fields.Char(string="Penanggung Jawab")
    pic_jabatan     = fields.Char(string="Jabatan")
    pic_departemen  = fields.Char(string="Departemen")

class klas_penanganan(models.Model):
    _name           = 'klas.penanganan'
    _description    = 'Penanganan'
    _inherit        = 'mail.thread'
    _rec_name       = 'topik'

    subject         = fields.Char(string="Subject", required=True)
    topik           = fields.Char(string="Topik", required=True)    
    klas_line       = fields.One2many('klas.klas_line', 'klas_line_id', string='Klasifikasi')

class klas_klas_line(models.Model):
    _name           = 'klas.klas_line'
    _description    = 'Penanganan Line'
    klas_line_id    = fields.Many2one('klas.penanganan', ondelete='cascade')
    klasifikasi     = fields.Many2one('klas.matrix', ondelete='cascade', string="Klasifikasi", required=True)
    penanganan      = fields.Text(string="Penanganan", required=True)
