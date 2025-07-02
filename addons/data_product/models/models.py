# -*- coding: utf-8 -*-

from odoo import models, fields, api


class DataProduct(models.Model):
    _name = 'data_product'
    _description = 'Data Product'

    name = fields.Char(string="Product Name", required=True) 
    price = fields.Float(string="Price", required=True) 
    description = fields.Text(string="Description")

