# -*- coding: utf-8 -*-

from odoo import models, fields, api


class Keluarga(models.Model):
    _name = 'keluarga'
    _description = 'Data Keluarga'

    name = fields.Char(string='Name', required=True)
    relation = fields.Selection([
        ('father', 'Ayah'), 
        ('mother', 'Ibu'), 
        ('spouse', 'Suami/Istri'), 
        ('child', 'Anak')], 
        string='Relation', help='Status Pernikahan')
    birthday = fields.Date(string='Birthday', required=True)
    sex = fields.Selection([('male', 'Laki-laki'), ('female', 'Perempuan')], string='Sex', required=True, help='Jenis Kelamin')
    marital = fields.Selection([
        ('single', 'Belum Menikah'), 
        ('married', 'Menikah'), 
        ('divorced', 'Cerai')], 
        string='Matrial Status', help='Status Pernikahan')
