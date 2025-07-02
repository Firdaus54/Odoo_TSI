# -*- coding: utf-8 -*-
from odoo import models, fields, api
from datetime import datetime

class risk_register(models.Model):
    _name           = 'risk.register'
    _inherit        = 'mail.thread'
    _description    = 'Risk Register'
    _rec_name       = 'sub_klasifikasi'

    subject         = fields.Char(string="Subject", required=True)

    nomor           = fields.Char(string="Risk No")
    sub_klasifikasi = fields.Char(string="Sub Klasifikasi", required=True)
    ancaman         = fields.Char(string="Ancaman" )
    kerawanan       = fields.Char(string="Kerawanan" )

    d_finansial     = fields.Char(string="Finansial" )
    d_reputasi      = fields.Char(string="Reputasi" )
    d_hukum         = fields.Char(string="Hukum" )
    d_operasional   = fields.Char(string="Operasional" )

    awal_dampak     = fields.Integer(string="Dampak")
    awal_cenderung  = fields.Integer(string="Kecenderungan")
    awal_rnd        = fields.Integer(string="Resiko")
    awal_level      = fields.Char(string="Level Resiko Awal" )
    klasifikasi_line    = fields.One2many('risk.reff_line', 'reff_line_id', string='Pengendalian')
    kontrol         = fields.Char(string="Kontrol Saat ini" )

    akhir_dampak    = fields.Integer(string="Dampak Akhir")
    akhir_cenderung = fields.Integer(string="Kcenderungan Akhir")
    akhir_rnd       = fields.Integer(string="RND Akhir")
    akhir_level     = fields.Char(string="Level Resiko Akhir" )
    kriteria        = fields.Selection(selection=[
                        ('diterima', 'Diterima'),
                        ('ditransfer', 'Ditransfer'),
                        ('dihindari', 'Dihindari')], string="Kriteria Tindakan")

    tindakan        = fields.Char(string="Tindakan" )
    pic             = fields.Char(string="Penanggung Jawab" )
    source          = fields.Selection(selection=[
                        ('pentest', 'Pentest'),
                        ('audit', 'Audit'),
                        ('simulasi', 'Simulasi')], string="Source")

    def set_to_running(sample_file):
        self.write({'state' : 'approved'})
        return True


class risk_reff_line(models.Model):
    _name           = 'risk.reff_line'
    _description    = 'Risk Klasifikasi Line'
    reff_line_id    = fields.Many2one('risk.register', ondelete='cascade')
    refference      = fields.Many2one('reff.third', ondelete='cascade', string="Annex A ISO 27001 ver 2013")

# class risk_calc_matrix(models.Model):
#     _name           = 'risk.calc_matrix'
#     _inherit        = 'mail.thread'
#     _description    = 'Risk Matrix'
#     name            = fields.Char(required=True, string="Name")
#     min_val         = fields.Integer(string="Min Val")
#     max_val         = fields.Integer(string="Max Val")
#     category        = fields.Char(required=True, string="Category")
#     is_passed       = fields.Boolean("Passed", default=True, string="Passed")

class risk_kategori(models.Model):
    _name           = 'risk.kategori'
    _description    = 'Kategori Resiko'

    name                = fields.Char(string="Risk Level", required=True)
    bobot_from          = fields.Integer(string="Scores From" )
    bobot_to            = fields.Integer(string="Score To" )
    accepted            = fields.Char(string="Risk Accepted")
    audit_criteria      = fields.Char(string="Audit Criteria")
    pentest_criteria    = fields.Char(string="Pentest Criteria")
    color_code          = fields.Char(string="Color Code")
    risk_action         = fields.Char(string="Action" )

