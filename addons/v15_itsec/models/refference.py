# -*- coding: utf-8 -*-

from odoo import models, fields, api
from datetime import datetime

class reff_first(models.Model):
    _name           = 'reff.first'
    _inherit        = 'mail.thread'
    _description    = 'Refference'

    code            = fields.Char(string="Code", required=True)
    name            = fields.Char(string="Name", required=True)
    description     = fields.Text(string="Description")

    def name_get(self):
        res=[]
        for r in self:
            res.append((r.id, str(r.code) + ' : ' + r.name))
        return res

class reff_second(models.Model):
    _name           = 'reff.second'
    _inherit        = 'mail.thread'
    _description    = 'Refference'

    first           = fields.Many2one('reff.first', ondelete='cascade', string="Refference", required=True)
    code            = fields.Char(string="Code", required=True)
    name            = fields.Char(string="Name", required=True)
    description     = fields.Text(string="Description")

    def name_get(self):
        res=[]
        for r in self:
            res.append((r.id, str(r.code) + ' : ' + r.name))
        return res

class reff_third(models.Model):
    _name           = 'reff.third'
    _inherit        = 'mail.thread'
    _description    = 'Refference'

    first           = fields.Many2one('reff.first', ondelete='cascade', string="Refference", required=True)
    second          = fields.Many2one('reff.second', ondelete='cascade', string="Sub Refference", required=True)
    code            = fields.Char(string="Code", required=True)
    name            = fields.Char(string="Name", required=True)
    description     = fields.Text(string="Description")

    def name_get(self):
        res=[]
        for r in self:
            res.append((r.id, str(r.code) + ' : ' + r.name))
        return res
