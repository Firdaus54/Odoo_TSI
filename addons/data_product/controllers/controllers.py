# -*- coding: utf-8 -*-
# from odoo import http


# class DataProduct(http.Controller):
#     @http.route('/data_product/data_product/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/data_product/data_product/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('data_product.listing', {
#             'root': '/data_product/data_product',
#             'objects': http.request.env['data_product.data_product'].search([]),
#         })

#     @http.route('/data_product/data_product/objects/<model("data_product.data_product"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('data_product.object', {
#             'object': obj
#         })
