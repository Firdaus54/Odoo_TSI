# -*- coding: utf-8 -*-

# from odoo import models, fields, api


# class ykbut_culture_api(models.Model):
#     _name = 'ykbut_culture_api.ykbut_culture_api'
#     _description = 'ykbut_culture_api.ykbut_culture_api'

#     name = fields.Char()
#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         for record in self:
#             record.value2 = float(record.value) / 100
