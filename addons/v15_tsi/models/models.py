# -*- coding: utf-8 -*-

# from odoo import models, fields, api


# class v15_tsi(models.Model):
#     _name = 'v15_tsi.v15_tsi'
#     _description = 'v15_tsi.v15_tsi'

#     name = fields.Char()
#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         for record in self:
#             record.value2 = float(record.value) / 100
