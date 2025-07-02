# -*- coding: utf-8 -*-

# from odoo import models, fields, api


# class v14_tad_crm(models.Model):
#     _name = 'v14_tad_crm.v14_tad_crm'
#     _description = 'v14_tad_crm.v14_tad_crm'

#     name = fields.Char()
#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         for record in self:
#             record.value2 = float(record.value) / 100
